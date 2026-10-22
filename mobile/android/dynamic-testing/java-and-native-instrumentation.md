# Java and Native Instrumentation

{% hint style="warning" %}
Complete [mandatory preflight](preflight-and-frida-setup.md#mandatory-preflight) and record an [unmodified baseline](methodology-and-baseline.md). The examples are templates for an authorized app, not universal bypass scripts. Adapt class names, signatures, library names, and paths to observed evidence.
{% endhint %}

## Attach or Spawn

```sh
frida --help
frida-ps -Uai
frida -U -n <process-name> -l <hook.js>
frida -U -f <package-name> -l <hook.js>
```

Use attach for an existing process and spawn for early checks. Select the actual process/PID, including app subprocesses. Current Frida CLI resumes a spawn by default; use `--pause` and REPL `%resume` when needed. The PDF's Frida `--no-pause` flag is obsolete; Objection has its own separate CLI options.

Frida 17 moved the Java bridge out of the core runtime. Current `frida` REPL / `frida-trace` tooling supplies it for these scripts. Custom agents loaded through bindings need a bundled `frida-java-bridge` dependency and `import Java from 'frida-java-bridge'`; installing the Python package alone does not bundle that agent dependency. Check [bridge setup](https://frida.re/docs/bridges/) when using custom loaders.

## Enumerate Before Selecting a Hook

Replace the example class with a real runtime class; JADX aliases may differ after obfuscation. Run in a Frida script/REPL:

```javascript
Java.perform(function () {
    console.log(JSON.stringify(Java.enumerateMethods('com.example.*!login/s')));
    const LoginManager = Java.use('com.example.auth.LoginManager');
    for (const method of LoginManager.login.overloads) {
        console.log(method.argumentTypes.map(type => type.className).join(', ') +
            ' -> ' + method.returnType.className);
    }
});
```

An invalid overload specification can throw an error; a valid but unused overload simply will not fire. Inner classes use `$`; Kotlin-generated methods and coroutine signatures may not resemble source-level functions.

## Observe Without Changing Behavior

This template assumes the observed `login(String, String)` overload. It calls the original exactly once, returns its result, and avoids logging passwords or tokens:

```javascript
Java.perform(function () {
    const LoginManager = Java.use('com.example.auth.LoginManager');
    const login = LoginManager.login.overload('java.lang.String', 'java.lang.String');
    login.implementation = function (username, password) {
        console.log('login(String, String) entered; arguments redacted');
        const result = login.call(this, username, password);
        console.log('login returned; correlate with the request and UI');
        return result;
    };
});
```

**Confirm:** trigger the exact flow, correlate the hook with the request/state change, then repeat without the hook. A method returning does not prove authentication succeeded. For an asynchronous method, inspect the eventual callback/result as well. Use synthetic values when argument/return inspection is necessary.

## Class or Hook Not Found

1. Check process/PID, bridge availability, actual runtime class name, and method signature.
2. Trigger dynamic feature/class loading, then use `Java.enumerateLoadedClassesSync()` or `Java.enumerateMethods('class-pattern!method-pattern/s')`.
3. Inspect `Java.enumerateClassLoadersSync()` and use `Java.ClassFactory.get(loader).use(className)` for the responsible loader; avoid changing the global loader blindly.
4. Check overriding implementations, Kotlin-generated methods, ART optimizations, and whether the flow actually executes. A hooked constructor only proves new instances are created, not that none already exist.
5. Follow JNI/native callers when relevant. A `native` declaration does not automatically make a Java method unhookable; direct native calls may bypass the Java entry point.

## Native / JNI Workflow

Use host ELF tools such as binutils `readelf`/`strings` or Android NDK LLVM equivalents. Extract the correct `.so` from the matching APK/split and preserve its hash:

```sh
unzip -l <app.apk> | grep '\.so$'
readelf -h <libtarget.so>
readelf -Ws <libtarget.so>
strings <libtarget.so> | grep -iE 'root|debug|crypto|verify'
```

Map an observed call from Java to JNI and the loaded module. `Process.enumerateModules()` lists modules regardless of whether the desired function is exported. For Frida 17+, use module-instance export lookup; the old static `Module.findExportByName` API was removed.

The observational template below handles already-loaded and later-loaded libraries. The symbol is illustrative and must exist in the target build:

```javascript
const moduleObserver = Process.attachModuleObserver({
    onAdded(module) {
        if (module.name !== 'libtarget.so') return;
        const target = module.findExportByName('Java_com_example_security_RootCheck_isRooted');
        if (target === null) {
            console.log('Target export absent; inspect symbols or JNI registration');
            return;
        }
        Interceptor.attach(target, {
            onLeave(retval) {
                console.log('Observed native return: ' + retval.toString());
            }
        });
    }
});
```

* Standard JNI methods receive `JNIEnv*` and receiver/class before declared parameters; arbitrary C functions and special native calling conventions differ. Verify argument and return types before reading pointers or changing results.
* Stripping often removes debug/local symbols but can leave dynamic exports. Dynamic `RegisterNatives` registration may require tracing the registration rather than searching `Java_*` names.
* If no suitable symbol exists, locate the function in Ghidra/radare2, map its virtual address relative to the image base, then add that offset to the runtime module base. Raw file offsets are not runtime offsets. Verify build hash, ABI, instruction boundary, and ARM/Thumb mode; never reuse an unexplained offset.
* Change a return value only after proving its semantics. `0` can mean success, failure, false, or a null pointer depending on the function.
* Preserve normal return/exception behavior during observation. Reduce logging on hot functions; crashes can be script/type/timing defects rather than anti-hooking.

References: [Frida JavaScript API](https://frida.re/docs/javascript-api/), [Frida 17 API changes](https://frida.re/news/2025/05/17/frida-17-0-0-released/), [Frida CLI implementation](https://github.com/frida/frida-tools/blob/main/frida_tools/repl.py).

## Native Review and Bounded Fuzzing

Inspect the exact libraries and ABI used at runtime, not merely one extracted `.so`. Use `readelf -h -l -d -Ws`, Ghidra/radare2, and the relevant NDK tooling; apply hardening scanners only when they support Android ELF conventions.

| Lead | Inspect / Test | Interpretation |
| --- | --- | --- |
| ELF hardening | Executable stack/segments, relocation protections, stack guards, compiler defenses | Interpret PIE/shared-object and symbol evidence correctly. Missing hardening raises exploitability concerns but is not proof of a memory-corruption bug. |
| Unsafe C/C++ operations | Copies, length arithmetic, formatting strings, allocation/free lifetime | Trace externally controlled buffers/lengths to the actual native function. Imports alone are insufficient. |
| JNI boundary | Byte-array lengths, string encoding, object/reference lifetime, exceptions, thread attachment | Match the real signature and marshaling path; JNI names may be dynamically registered. |
| Library search/loading | `dlopen`, `System.load`, extracted/downloaded libraries, writable directories | Prove control of the loaded path or contents; verify authenticity and rollback checks. |
| Native secrets / debug material | Symbols, embedded keys, debug paths, logs, signing routines | Debug symbols aid analysis but are not automatically a disclosure finding; establish exposed information or authority. |

For authorized fuzzing, isolate a parser/JNI entry point with a reproducible harness, small seed corpus, time/memory limits, and disposable data. Prefer existing engines such as libFuzzer with a compatible NDK/sanitizer build when source is available. Preserve crashing input, build/ABI, sanitizer/tombstone details, and a minimized reproducer; distinguish harness mistakes, ordinary parse rejection, local denial of service, and exploitable corruption. Do not fuzz production devices/services or claim remote code execution from a crash alone.

**Previous:** [Objection and Runtime Instrumentation](objection-and-runtime-instrumentation.md) | **Next:** [App Patching and Repackaging](app-patching.md)