# Java and Native Instrumentation

## Attach or Spawn

* <pre class="language-bash" data-line-numbers><code class="lang-bash">frida --help
  frida -U -n &#x3C;process-name> -l &#x3C;hook.js>
  frida -U -f &#x3C;package-name> -l &#x3C;hook.js>
  </code></pre>
* **Process/app listing:** [Frida connection check](preflight-and-frida-setup.md#verify-client-and-server-versions).
* Attach to existing processes; spawn for early checks. Select the actual process/PID, including subprocesses.
* Frida CLI resumes spawned processes by default; use `--pause` and REPL `%resume` when needed.
* Custom agents loaded through bindings need bundled `frida-java-bridge` and `import Java from 'frida-java-bridge'`.
* Installing the Python package alone does not bundle the agent dependency; follow [bridge setup](https://frida.re/docs/bridges/) for custom loaders.

## Enumerate Before Selecting a Hook

* Replace the example class with an observed runtime class; obfuscated JADX aliases may differ.
* Run in a Frida script:
  * ```javascript
    Java.perform(function () {
        console.log(JSON.stringify(Java.enumerateMethods('com.example.*!login/s')));
        const LoginManager = Java.use('com.example.auth.LoginManager');
        for (const method of LoginManager.login.overloads) {
            console.log(method.argumentTypes.map(type => type.className).join(', ') +
                ' -> ' + method.returnType.className);
        }
    });
    ```
* Invalid overload specification: may throw an error. Valid but unused overload: hook will not fire.
* Inner classes use `$`; Kotlin-generated methods and coroutine signatures may differ from source-level functions.

## Observe Without Changing Behavior

* **Required signature:** observed `login(String, String)` overload.
* Template behavior: call the original once, return its result, and avoid logging passwords/tokens.
  * ```javascript
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
* **Confirm:** trigger the exact flow, correlate the hook with the request/state change, and repeat without the hook.

## Class or Hook Not Found

1. Check process/PID, bridge availability, actual runtime class name, and method signature.
2. Trigger dynamic feature/class loading, then use `Java.enumerateLoadedClassesSync()` or `Java.enumerateMethods('class-pattern!method-pattern/s')`.
3. Inspect `Java.enumerateClassLoadersSync()` and use `Java.ClassFactory.get(loader).use(className)` for the responsible loader; avoid changing the global loader blindly.
4. Check overriding implementations, Kotlin-generated methods, ART optimizations, and whether the flow actually executes. A hooked constructor only proves new instances are created, not that none already exist.
5. Follow JNI/native callers when relevant. A `native` declaration does not automatically make a Java method unhookable; direct native calls may bypass the Java entry point.

## Native / JNI Workflow

* **Dependencies:** host ELF tools such as binutils `readelf`/`strings`, or Android NDK LLVM equivalents.
* Extract the correct `.so` from the matching APK/split.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">unzip -l &#x3C;app.apk> | grep '\.so$'
  readelf -h &#x3C;libtarget.so>
  readelf -Ws &#x3C;libtarget.so>
  strings &#x3C;libtarget.so> | grep -iE 'root|debug|crypto|verify'
  </code></pre>
* Trace the observed Java call through JNI to the loaded module.
* `Process.enumerateModules()` lists modules even when the target function is not exported.
* The template handles already-loaded and later-loaded libraries.
* Replace the illustrative symbol with one present in the target build.
  * ```javascript
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
* References: [Frida JavaScript API](https://frida.re/docs/javascript-api/), [Frida 17 API changes](https://frida.re/news/2025/05/17/frida-17-0-0-released/), [Frida CLI implementation](https://github.com/frida/frida-tools/blob/main/frida_tools/repl.py).

## Native Review and Bounded Fuzzing

* Inspect the libraries and ABI actually used at runtime, not merely one extracted `.so`.
* Use `readelf -h -l -d -Ws`, Ghidra/radare2, and relevant NDK tools.
* Use hardening scanners only when they support Android ELF conventions.

<table><thead><tr><th width="143.0001220703125">Lead</th><th>Inspect / Test</th><th>Interpretation</th></tr></thead><tbody><tr><td>ELF hardening</td><td>Executable stack/segments, relocation protections, stack guards, compiler defenses</td><td>Interpret PIE/shared-object and symbol evidence correctly. Missing hardening raises exploitability concerns but is not proof of a memory-corruption bug.</td></tr><tr><td>Unsafe C/C++ operations</td><td>Copies, length arithmetic, formatting strings, allocation/free lifetime</td><td>Trace externally controlled buffers/lengths to the actual native function. Imports alone are insufficient.</td></tr><tr><td>JNI boundary</td><td>Byte-array lengths, string encoding, object/reference lifetime, exceptions, thread attachment</td><td>Match the real signature and marshaling path; JNI names may be dynamically registered.</td></tr><tr><td>Library search/loading</td><td><code>dlopen</code>, <code>System.load</code>, extracted/downloaded libraries, writable directories</td><td>Prove control of the loaded path or contents; verify authenticity and rollback checks.</td></tr><tr><td>Native secrets / debug material</td><td>Symbols, embedded keys, debug paths, logs, signing routines</td><td>Debug symbols aid analysis but are not automatically a disclosure finding; establish exposed information or authority.</td></tr></tbody></table>

* **Fuzzing prerequisites:** authorization, isolated parser/JNI entry point, reproducible harness, small seed corpus, time/memory limits, and disposable data.
* With source, prefer an existing engine such as libFuzzer and a compatible NDK/sanitizer build.
* **Existing libFuzzer harness on a matching test device:** use the built executable and its known corpus; this is not a harness generator for arbitrary JNI methods.
    * ```bash
        adb push '<parser-fuzzer>' /data/local/tmp/parser-fuzzer
        adb push '<seed-corpus-directory>' /data/local/tmp/parser-corpus
        adb shell chmod 755 /data/local/tmp/parser-fuzzer
        adb shell /data/local/tmp/parser-fuzzer /data/local/tmp/parser-corpus -runs=100 -max_len=4096 -timeout=2 -rss_limit_mb=256
        ```
* Preserve crashing input, build/ABI, sanitizer/tombstone details, and a minimized reproducer.
* Distinguish harness errors, normal parse rejection, local denial of service, and exploitable corruption.
