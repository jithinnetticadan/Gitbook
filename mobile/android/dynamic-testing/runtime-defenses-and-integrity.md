# Runtime Defenses and Integrity

## Locate the Check That Actually Runs

* Compare the same operation across three states: original environment, instrumentation without hooks, and one observational hook.
* Record warning/exit timing and relevant logs before attributing the behavior to anti-Frida checks.

<table><thead><tr><th width="110">Signal Family</th><th>Likely Observation Points</th><th>Interpretation</th></tr></thead><tbody><tr><td>Root</td><td><code>File.exists</code>, package queries, <code>Runtime.exec</code> / <code>ProcessBuilder</code>, properties, native <code>access</code> / <code>stat</code> / <code>open</code></td><td>Observe the exact path/package/command and caller. A <code>su</code> filename is only one possible check.</td></tr><tr><td>Emulator</td><td><code>Build.MODEL</code>, <code>FINGERPRINT</code>, <code>HARDWARE</code>, sensors, telephony, filesystem, native system queries</td><td>Confirm the actual decision; a missing IMEI may reflect permissions or a Wi-Fi-only device.</td></tr><tr><td>Debugger</td><td><code>Debug.isDebuggerConnected</code>, <code>TracerPid</code>, JDWP/native tracing checks</td><td>Check timing and platform restrictions; an ordinary crash is not proof of debugger detection.</td></tr><tr><td>Instrumentation</td><td>Process/thread names, open ports, loaded libraries, <code>/proc/self/maps</code>, memory strings</td><td>Renaming one file changes only one indicator; Gadget is not inherently undetectable.</td></tr><tr><td>Anti-hooking / RASP</td><td>Function prologues, executable-memory checksums, call-stack/timing checks, native watchdogs</td><td>Broad hooks can trigger checks or break normal operation; identify the responsible path first.</td></tr><tr><td>Integrity / attestation</td><td>Local signing digest, APK/code checks, Play Integrity requests and backend verdict handling</td><td>Distinguish local decisions from a backend-enforced trust boundary.</td></tr></tbody></table>

## Observe a Root-Check Input

* **Frida JavaScript hook:** save this on the host as a `.js` file and load it with the [Frida attach/spawn command](objection-and-runtime-instrumentation.md#attach-or-spawn), or paste it into the attached Frida REPL. It logs selected file probes and preserves the original results; adapt paths from observed code.
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
5. To test a port-specific check, change the server's loopback port and forward that port over ADB.

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
* **Forward management:** `adb forward --remove tcp:31337`.
* Rooted/emulated devices and patched builds may still fail independent integrity checks.

## Repackaging and Signature Checks

1. Use the [align/sign/verify sequence](app-patching.md#manual-patching) to prepare the rebuilt test artifact.
2. Compare the original, a rebuilt/re-signed control with no intended logic change, and the targeted patch. Packaging/resource/signature problems  must be separated from anti-tampering.
3. Trace the actual certificate comparison. Older code may use `GET_SIGNATURES` / `PackageInfo.signatures`; newer code uses `GET_SIGNING_CERTIFICATES` / `signingInfo`. Key rotation and multiple signers affect the comparison.
4. Confirm whether the app exits locally, hides a feature, or receives a server rejection. A UI change does not bypass backend attestation.
5. Test the actual backend integrity consumer using the matrix below; a local Boolean does not represent the backend verdict.

* Android normally rejects updates signed with unrelated keys; `adb install -r` does not bypass this check.
* Uninstalling may remove data and keys.
* Re-signing can legitimately change app identity, signature permissions, App Links, and backend integrations.

## Play Integrity: Backend Binding and Replay

* **Baseline:** identify the actual integrity token field/header and protected action. Obtain a genuine token while performing action A; keep its request, session and action identifiers together. Use the existing [JSON request replay command](authentication-and-cryptography.md#protected-api-and-refresh-requests), not a fabricated Google decode response.
* **Missing/invalid token inputs:** remove the field, then try these values independently with an otherwise valid protected request.
  * ```json
    {"integrityToken":""}
    ```
  * ```json
    {"integrityToken":"not-an-integrity-token"}
    ```
* **Binding body template:** replace names with the captured schema. Keep A's genuine token while changing only the protected order/object or amount to the B test transaction.
  * ```json
    {"orderId":"REPLACE_B_TEST_ORDER","amount":1,"integrityToken":"REPLACE_GENUINE_TOKEN_FOR_A"}
    ```

| Variant | Request mutation | Confirm |
| --- | --- | --- |
| Content binding | Change amount/object after token issuance; retain original token | Protected action succeeds although the decoded `requestHash` or classic challenge is not bound to that action. |
| Session binding | Submit A's token using B's session and B's test action | A token minted for another intended session/action is accepted contrary to the binding contract. |
| Replay | Resend the exact token/request after the first committed one-time action | A second forbidden state change commits; repeated reads or idempotent acknowledgements do not establish this. |
| Freshness | Delay submission beyond the server's allowed age; use a fresh control separately | A stale token still authorizes a freshness-sensitive operation. |
| Verdict enforcement | Use owner-configured test responses for failed/unrecognized app/device verdicts | The protected backend action proceeds despite a verdict the policy is intended to reject. |

* **Standard requests:** the backend must compare the verified `requestDetails.requestHash` with its own canonical action data. Editing a client-supplied `requestHash` field is not a valid signature forgery; test whether the server recomputes rather than trusts that echo. Google's automatic replay protection may produce cleared verdicts on repeated decoding; check how the backend handles that result.
* **Classic requests:** start separate server challenges for A/B, submit the genuine token for challenge A to B, then reuse A's consumed challenge. Validate the server-issued nonce, intended session/action, age and consumption policy.
* **Confirm the flaw:** record the committed action with the invalid/mismatched verified input. A successful Google token decode alone proves neither app authorization nor correct backend binding. Expected package/signing/version and verdict policies require backend verification or owner-configured tests; they cannot be demonstrated by editing the opaque token text.

## Framework-Specific Defense Leads

* RootBeer/library methods, installer-source checks, Build fields, sensor/telephony queries, and process maps are leads to the executing decision. `Build.MODEL` and similar values are fields, not universally available getters; verify the concrete API instead of copying a guessed hook.
* Xposed/LSPosed, Magisk/Zygisk, DenyList, and related modules alter the environment and may be detected. Check module, OS, and architecture compatibility; these are not guaranteed bypasses.
* Native code can issue direct system calls and bypass libc-level observations. Confirm the executing instruction, ABI, arguments, and build before considering lower-level instrumentation; absence of a libc hook hit is not proof that no check occurred.
* Installer package names are client-side signals, not server proof of authenticity. An installer-source change may also affect licensing, delivery, and integrity results.
* Play Integrity bypass-module/keybox claims are version-, provisioning-, revocation-, and backend-policy-dependent. Do not treat leaked attestation credentials or reported verdict strings as reliable evidence of a server bypass. Use authorized test provisioning and verify backend request/session binding.
* Runtime string decryption can expose obfuscated configuration; trace the consumer to determine whether the value is a privileged secret.
* SafetyNet Attestation was [fully shut down in January 2025](https://developer.android.com/privacy-and-security/safetynet/deprecation-timeline). Review stale integrations and fail-open behavior; do not treat old SafetyNet bypass recipes as a supported current path. Android native hook checks concern mechanisms such as ELF PLT/GOT or instruction changes; Windows `Ldrp` terminology is not an Android API.
* References: [Android app signing](https://developer.android.com/studio/publish/app-signing), [Play Integrity](https://developer.android.com/google/play/integrity/overview), [Frida troubleshooting](https://frida.re/docs/troubleshooting/).
* **Related:** [Java and Native Instrumentation](java-and-native-instrumentation.md) | [Network Traffic and TLS](network-traffic-and-tls.md).
