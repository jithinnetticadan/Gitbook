# Java and Native Instrumentation

* **Custom hook workflows:** class/signature discovery, observational Java hooks, classloaders, JNI/native hooks, and native fuzzing.
* **Connect/load a script:** [Frida CLI or Objection](objection-and-runtime-instrumentation.md#attach-or-spawn).

## Custom Agent Setup

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

### Build a Parser Harness

* **Input:** parser source and a known valid record. Isolate a byte-buffer adapter with the real ownership/initialization contract; the example assumes `extern "C" int parse_record(const uint8_t*, size_t)` in `parser.cpp`. Replace that declaration/call with the actual API. A JNI method expecting `JNIEnv*`/Java objects cannot be called with a guessed byte-buffer signature.
* **`harness.cpp`:** libFuzzer supplies input generation and crash reproduction; the harness invokes the actual parser and preserves its normal rejection behavior.
    * ```cpp
        #include <cstddef>
        #include <cstdint>

        extern "C" int parse_record(const uint8_t* data, size_t length);

        extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t length) {
                if (length > 4096) return 0;
                parse_record(data, length);
                return 0;
        }
        ```
{% tabs %}
{% tab title="Linux" %}
* **Installed Android NDK, ARM64 Android API 26+:** set `ANDROID_NDK_HOME` to the actual NDK root. Compile the parser itself with sanitizer/coverage instrumentation; merely linking an uninstrumented vendor `.so` limits what ASan/libFuzzer can observe.
    * ```bash
        CXX="$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/bin/clang++"
        "$CXX" --target=aarch64-linux-android26 -g -O1 -fno-omit-frame-pointer -fsanitize=fuzzer,address -static-libstdc++ harness.cpp parser.cpp -o parser-fuzzer
        RESOURCE_DIR="$("$CXX" -print-resource-dir)"
        adb push "$RESOURCE_DIR/lib/linux/libclang_rt.asan-aarch64-android.so" /data/local/tmp/
        mkdir -p seed-corpus
        cp known-valid-record.bin seed-corpus/seed
        ```
{% endtab %}
{% tab title="Windows" %}
* **Installed NDK equivalent:**
    * ```powershell
        $compiler = Join-Path $env:ANDROID_NDK_HOME 'toolchains/llvm/prebuilt/windows-x86_64/bin/clang++.exe'
        & $compiler --target=aarch64-linux-android26 -g -O1 -fno-omit-frame-pointer '-fsanitize=fuzzer,address' -static-libstdc++ harness.cpp parser.cpp -o parser-fuzzer
        $resourceDirectory = & $compiler -print-resource-dir
        adb push (Join-Path $resourceDirectory 'lib/linux/libclang_rt.asan-aarch64-android.so') /data/local/tmp/
        New-Item -ItemType Directory -Path seed-corpus -Force | Out-Null
        Copy-Item known-valid-record.bin seed-corpus/seed
        ```
    {% endtab %}
    {% endtabs %}
* **Device run, same commands on Linux / Windows:** match the device ABI and API; ASan runtime locations depend on the selected NDK, so verify that the generated runtime path exists. For macOS hosts select the NDK's `darwin-x86_64` prebuilt directory instead.
    * ```text
        adb push parser-fuzzer /data/local/tmp/parser-fuzzer
        adb push seed-corpus /data/local/tmp/parser-corpus
        adb shell chmod 755 /data/local/tmp/parser-fuzzer
        adb shell "cd /data/local/tmp && LD_LIBRARY_PATH=/data/local/tmp ASAN_OPTIONS=detect_leaks=0 ./parser-fuzzer parser-corpus -runs=100 -max_len=4096 -timeout=2 -rss_limit_mb=256 -artifact_prefix=/data/local/tmp/"
        ```
* **Reproduce one artifact:** pull the emitted `crash-*`/`timeout-*` filename, keep it under a stable test name, then run that single input through the same build. A name is emitted only if a failure occurs.
    * ```text
        adb pull /data/local/tmp/REPLACE_EMITTED_ARTIFACT ./reproducer.bin
        adb push reproducer.bin /data/local/tmp/reproducer.bin
        adb shell "cd /data/local/tmp && LD_LIBRARY_PATH=/data/local/tmp ASAN_OPTIONS=detect_leaks=0 ./parser-fuzzer reproducer.bin -runs=1"
        ```
* **Confirm:** the same input produces the same sanitizer fault in the actual parser. A deliberate parser error, missing runtime/library, bad adapter ABI or harness crash before parsing is not a target memory-corruption finding. Binary-only/JNI-only targets need a compatible initialized runtime harness; this source adapter is not a universal `.so` fuzzer.
* Preserve crashing input, build/ABI, sanitizer/tombstone details, and a minimized reproducer.
* Distinguish harness errors, normal parse rejection, local denial of service, and exploitable corruption.
