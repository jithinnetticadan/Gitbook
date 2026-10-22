# Runtime Defenses and Integrity

{% hint style="warning" %}
Assess only an authorized lab copy. Record the [baseline](methodology-and-baseline.md) before changing checks. A blocked emulator or instrumented app is a test constraint, not automatically a vulnerability.
{% endhint %}

## Locate the Check That Actually Runs

Compare the same operation on the original environment, with an instrumentation connection but no hooks, and with one observational hook. Record when the warning/exit occurs and collect relevant logs before assuming anti-Frida behavior.

| Signal Family           | Likely Observation Points                                                                                        | Interpretation                                                                                 |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Root                    | `File.exists`, package queries, `Runtime.exec` / `ProcessBuilder`, properties, native `access` / `stat` / `open` | Observe the exact path/package/command and caller. A `su` filename is only one possible check. |
| Emulator                | `Build.MODEL`, `FINGERPRINT`, `HARDWARE`, sensors, telephony, filesystem, native system queries                  | Confirm the actual decision; a missing IMEI may reflect permissions or a Wi-Fi-only device.    |
| Debugger                | `Debug.isDebuggerConnected`, `TracerPid`, JDWP/native tracing checks                                             | Check timing and platform restrictions; an ordinary crash is not proof of debugger detection.  |
| Instrumentation         | Process/thread names, open ports, loaded libraries, `/proc/self/maps`, memory strings                            | Renaming one file changes only one indicator; Gadget is not inherently undetectable.           |
| Anti-hooking / RASP     | Function prologues, executable-memory checksums, call-stack/timing checks, native watchdogs                      | Broad hooks can trigger checks or break normal operation; identify the responsible path first. |
| Integrity / attestation | Local signing digest, APK/code checks, Play Integrity requests and backend verdict handling                      | Distinguish local decisions from a backend-enforced trust boundary.                            |

## Observe a Root-Check Input

After [Frida setup](preflight-and-frida-setup.md), this Java template logs only selected file probes and preserves their original results. Adapt paths from observed code; it is not comprehensive root detection or a bypass:

```javascript
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

**Next:** correlate the probe and its caller with the block, then change only the identified decision/input if needed for the test. Re-run the same protected operation. For command/property/package checks, preserve correct return types and normal behavior for unrelated calls; globally falsifying file access or command execution can invalidate the run. Native checks may need the [JNI workflow](java-and-native-instrumentation.md#native--jni-workflow).

## Isolate Instrumentation Detection

1. Confirm version/ABI/process access and that the uninstrumented app works in the same environment.
2. Compare server not running, server running without attachment, attachment with no hooks, and one observational hook. Each comparison changes one variable.
3. Capture the exit reason/stack and identify checks in Java/native code. Account for watchdog timing and server-side rejection.
4. Test a narrowly identified signal only. Failure after renaming a server does not prove behavioral detection: other signatures, root checks, and compatibility failures remain possible.
5. If a new port is needed for a controlled experiment, keep it loopback-bound and forward it over authorized ADB. Do not expose an unauthenticated Frida server on all network interfaces.

Optional nondefault-port example, after stopping the existing lab server and checking its `--help`. Run the server in one terminal and the forwarding/client commands in another:

```sh
adb shell "su -c '/data/local/tmp/frida-server -l 127.0.0.1:31337'"
```

```sh
adb forward tcp:31337 tcp:31337
frida-ps -H 127.0.0.1:31337
frida -H 127.0.0.1:31337 -n <process-name>
```

This tests a port-specific hypothesis, not a general evasion method. Stop the temporary server and remove that forwarding with `adb forward --remove tcp:31337` afterward. Rooted/emulated devices and patched builds may still fail independent integrity checks.

## Repackaging and Signature Checks

1. Preserve the original APK/splits and signing certificate details. Use the established [align/sign/verify sequence](app-patching.md#manual-patching) for a disposable test artifact.
2. Compare the original, a rebuilt/re-signed control with no intended logic change, and the targeted patch. Packaging/resource/signature problems must be separated from anti-tampering.
3. Trace the actual certificate comparison. Older code may use `GET_SIGNATURES` / `PackageInfo.signatures`; newer code uses `GET_SIGNING_CERTIFICATES` / `signingInfo`. Key rotation and multiple signers affect the comparison.
4. Confirm whether the app exits locally, hides a feature, or receives a server rejection. A UI change does not bypass backend attestation.
5. For Play Integrity, assess server verification, expected app identity, freshness/replay controls, and binding to the intended request/session. Standard and classic request flows differ; evaluate the implemented flow, not just a client Boolean.

Android normally rejects an update signed with an unrelated key. `adb install -r` is not a bypass for that check. Use a disposable device/profile or an approved uninstall/reinstall after protecting test data; uninstalling can remove data and keys. Production app identity, signature permissions, App Links, and backend integrations can legitimately change after re-signing.

## Stop Criteria

Time-box bypass work against the test objective. Stop and document the blocked coverage when the next step exceeds authorization, risks data/device availability, or has little value compared with other tests. Obtain an owner-provided test build/environment or continue scoped API/static testing where possible. Do not change the production build or attestation policy without approval.

Commercial RASP may require specialist analysis. Report the environment, attempted checks, evidence, and remaining uncertainty, not an unproven claim that a defense is unbreakable or absent.

## Framework-Specific Defense Leads

* RootBeer/library methods, installer-source checks, Build fields, sensor/telephony queries, and process maps are leads to the executing decision. `Build.MODEL` and similar values are fields, not universally available getters; verify the concrete API instead of copying a guessed hook.
* Xposed/LSPosed, Magisk/Zygisk, DenyList, and related modules alter the environment and may be detected. They are optional lab approaches, not guaranteed bypasses. Check maintenance and OS/architecture compatibility; snapshot before changes and avoid unreviewed modules on personal devices.
* Native code can issue direct system calls and bypass libc-level observations. Confirm the executing instruction, ABI, arguments, and build before considering lower-level instrumentation; absence of a libc hook hit is not proof that no check occurred.
* Installer package names are client-side signals, not server proof of authenticity. An installer-source change may also affect licensing, delivery, and integrity results.
* Play Integrity bypass-module/keybox claims are version-, provisioning-, revocation-, and backend-policy-dependent. Do not treat leaked attestation credentials or reported verdict strings as reliable evidence of a server bypass. Use authorized test provisioning and verify backend request/session binding.
* Runtime string decryption can expose obfuscated configuration, but observing a decrypted string does not prove it is a privileged secret. Trace its consumer and redact captured values.
* SafetyNet Attestation was [fully shut down in January 2025](https://developer.android.com/privacy-and-security/safetynet/deprecation-timeline). Review stale integrations and fail-open behavior; do not treat old SafetyNet bypass recipes as a supported current path. Android native hook checks concern mechanisms such as ELF PLT/GOT or instruction changes; Windows `Ldrp` terminology is not an Android API.

References: [Android app signing](https://developer.android.com/studio/publish/app-signing), [Play Integrity](https://developer.android.com/google/play/integrity/overview), [Frida troubleshooting](https://frida.re/docs/troubleshooting/).

**Related:** [Java and Native Instrumentation](java-and-native-instrumentation.md) | [Network Traffic and TLS](network-traffic-and-tls.md)
