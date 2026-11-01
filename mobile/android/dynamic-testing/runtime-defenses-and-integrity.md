# Runtime Defenses and Integrity

## Locate the Check That Actually Runs

* Compare the same operation across three states: original environment, instrumentation without hooks, and one observational hook.
* Record warning/exit timing and relevant logs before attributing the behavior to anti-Frida checks.

<table><thead><tr><th width="110">Signal Family</th><th>Likely Observation Points</th><th>Interpretation</th></tr></thead><tbody><tr><td>Root</td><td><code>File.exists</code>, package queries, <code>Runtime.exec</code> / <code>ProcessBuilder</code>, properties, native <code>access</code> / <code>stat</code> / <code>open</code></td><td>Observe the exact path/package/command and caller. A <code>su</code> filename is only one possible check.</td></tr><tr><td>Emulator</td><td><code>Build.MODEL</code>, <code>FINGERPRINT</code>, <code>HARDWARE</code>, sensors, telephony, filesystem, native system queries</td><td>Confirm the actual decision; a missing IMEI may reflect permissions or a Wi-Fi-only device.</td></tr><tr><td>Debugger</td><td><code>Debug.isDebuggerConnected</code>, <code>TracerPid</code>, JDWP/native tracing checks</td><td>Check timing and platform restrictions; an ordinary crash is not proof of debugger detection.</td></tr><tr><td>Instrumentation</td><td>Process/thread names, open ports, loaded libraries, <code>/proc/self/maps</code>, memory strings</td><td>Renaming one file changes only one indicator; Gadget is not inherently undetectable.</td></tr><tr><td>Anti-hooking / RASP</td><td>Function prologues, executable-memory checksums, call-stack/timing checks, native watchdogs</td><td>Broad hooks can trigger checks or break normal operation; identify the responsible path first.</td></tr><tr><td>Integrity / attestation</td><td>Local signing digest, APK/code checks, Play Integrity requests and backend verdict handling</td><td>Distinguish local decisions from a backend-enforced trust boundary.</td></tr></tbody></table>

## Observe a Root-Check Input

* Template behavior: log selected file probes and preserve original results; adapt paths from observed code.
  * ```javascript
    Java.perform(function () {
        const File = Java.use('java.io.File');
        const exists = File.exists.overload();
        const watchedPaths = new Set(['/system/bin/su', '/system/xbin/su', '/sbin/su']);
        exists.implementation = function () {
            const result = exists.call(this);
            const path = this.getAbsolutePath().toString();
            if (watchedPaths.has(path)) {
                console.log('File.exists: ' + path + ' -> ' + result);
            }
            return result;
        };
    });
    ```
* Correlate the probe and caller with the block; change only the identified decision/input when needed.
* Re-run the same protected operation.
* Preserve correct return types and unrelated-call behavior for command/property/package checks.
* Globally falsifying file access or command execution can invalidate the run.
* Native checks may require the [JNI workflow](java-and-native-instrumentation.md#native--jni-workflow).

## Isolate Instrumentation Detection

1. Confirm version/ABI/process access and that the uninstrumented app works in the same environment.
2. Compare server not running, server running without attachment, attachment with no hooks, and one observational hook. Each comparison changes one variable.
3. Capture the exit reason/stack and identify checks in Java/native code. Account for watchdog timing and server-side rejection.
4. Test a narrowly identified signal only. Failure after renaming a server does not prove behavioral detection: other signatures, root checks, and compatibility failures remain possible.
5. If a new port is needed for a controlled experiment, keep it loopback-bound and forward it over authorized ADB. Do not expose an unauthenticated Frida server on all network interfaces.

* **Prerequisites:** stop the existing lab server and check its `--help` before this optional nondefault-port test.
* Run the server in one terminal; run forwarding/client commands in another.
  * ```bash
    adb shell "su -c '/data/local/tmp/frida-server -l 127.0.0.1:31337'"
    ```
* ```bash
  adb forward tcp:31337 tcp:31337
  frida-ps -H 127.0.0.1:31337
  frida -H 127.0.0.1:31337 -n <process-name>
  ```
* Stop the temporary server and remove forwarding with `adb forward --remove tcp:31337` afterward.
* Rooted/emulated devices and patched builds may still fail independent integrity checks.

## Repackaging and Signature Checks

1. Preserve the original APK/splits and signing certificate details. Use the established [align/sign/verify sequence](app-patching.md#manual-patching) for a disposable test artifact.
2. Compare the original, a rebuilt/re-signed control with no intended logic change, and the targeted patch. Packaging/resource/signature problems  must be separated from anti-tampering.
3. Trace the actual certificate comparison. Older code may use `GET_SIGNATURES` / `PackageInfo.signatures`; newer code uses `GET_SIGNING_CERTIFICATES` / `signingInfo`. Key rotation and multiple signers affect the comparison.
4. Confirm whether the app exits locally, hides a feature, or receives a server rejection. A UI change does not bypass backend attestation.
5. For Play Integrity, assess server verification, expected app identity, freshness/replay controls, and binding to the intended request/session. Standard and classic request flows differ; evaluate the implemented flow, not just a client Boolean.

* Android normally rejects updates signed with unrelated keys; `adb install -r` does not bypass this check.
* Use a disposable device/profile or an approved uninstall/reinstall; protect test data first.
* Uninstalling may remove data and keys.
* Re-signing can legitimately change app identity, signature permissions, App Links, and backend integrations.

## Framework-Specific Defense Leads

* RootBeer/library methods, installer-source checks, Build fields, sensor/telephony queries, and process maps are leads to the executing decision. `Build.MODEL` and similar values are fields, not universally available getters; verify the concrete API instead of copying a guessed hook.
* Xposed/LSPosed, Magisk/Zygisk, DenyList, and related modules alter the environment and may be detected. They are optional lab approaches, not guaranteed bypasses. Check maintenance and OS/architecture compatibility; snapshot before changes and avoid unreviewed modules on personal devices.
* Native code can issue direct system calls and bypass libc-level observations. Confirm the executing instruction, ABI, arguments, and build before considering lower-level instrumentation; absence of a libc hook hit is not proof that no check occurred.
* Installer package names are client-side signals, not server proof of authenticity. An installer-source change may also affect licensing, delivery, and integrity results.
* Play Integrity bypass-module/keybox claims are version-, provisioning-, revocation-, and backend-policy-dependent. Do not treat leaked attestation credentials or reported verdict strings as reliable evidence of a server bypass. Use authorized test provisioning and verify backend request/session binding.
* Runtime string decryption can expose obfuscated configuration, but observing a decrypted string does not prove it is a privileged secret. Trace its consumer and redact captured values.
* SafetyNet Attestation was [fully shut down in January 2025](https://developer.android.com/privacy-and-security/safetynet/deprecation-timeline). Review stale integrations and fail-open behavior; do not treat old SafetyNet bypass recipes as a supported current path. Android native hook checks concern mechanisms such as ELF PLT/GOT or instruction changes; Windows `Ldrp` terminology is not an Android API.
* References: [Android app signing](https://developer.android.com/studio/publish/app-signing), [Play Integrity](https://developer.android.com/google/play/integrity/overview), [Frida troubleshooting](https://frida.re/docs/troubleshooting/).
* **Related:** [Java and Native Instrumentation](java-and-native-instrumentation.md) | [Network Traffic and TLS](network-traffic-and-tls.md).
