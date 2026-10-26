# Methodology and Baseline

{% hint style="info" %}
* Use in-scope apps, devices, APIs, and disposable test accounts.
* Preserve original APKs/splits and record hashes.
* Capture baseline behavior before hooks or changes to trust, app code, or local state.
{% endhint %}

## Working Sequence

1. Identify the app.
2. Prepare a compatible lab.
3. Record normal behavior.
4. Observe targeted calls.
5. Make one controlled change.
6. Verify the protected operation.
7. Note limitations and untested paths.

* Static analysis identifies code, configuration, and possible paths.
* Dynamic testing establishes behavior only under tested conditions; untriggered paths remain untested, not proven safe.
* Modifying client code does not imply control of the OS, other apps, hardware-backed keys, or server.

| Initial Pass | Deliverable                                                                                                                          |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| Fingerprint  | Package/version, APK/splits, ABI, target SDK, framework clues, exported components, and schemes.                                     |
| Prepare      | Compatible device and reversible lab; [Frida preflight](preflight-and-frida-setup.md#mandatory-preflight) only when instrumenting. |
| Observe      | Unmodified startup, login/logout, permissions, logs, storage changes, network behavior, and blocks.                                  |
| Map          | One complete flow from UI through local processing, IPC/WebView, API, response, storage, and background work.                        |
| Instrument   | One observational hook that fires during a known action without changing its result.                                                 |
| Validate     | One scoped test with a normal control case, changed input, actual outcome, and repeatable evidence.                                  |

* Use this as a first-hour guide; do not rush hardware setup or safety checks to meet a time target.
* Bypass controls only for an in-scope test or assessment of the control itself.

## Fingerprint the Implementation

* **Host dependencies:** `unzip` and `grep`, such as in a configured WSL/Linux/macOS shell.

```sh
unzip -l <app.apk> | grep -E 'libflutter|libmonodroid|libunity|libil2cpp|index\.android\.bundle|libhermes|cordova\.js|libcronet|\.so$'
```

* Inspect all relevant split APKs.
* No match does not prove a Java-only app; renamed assets, packing, dynamic delivery, and newer framework layouts may hide indicators.

| Candidate Stack       | Static Clue                            | Confirm at Runtime / Select Layer                                                                         |
| --------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Java/Kotlin           | DEX classes and framework calls        | Confirm ART classes and actual call path; use `Java.perform`.                                             |
| Flutter               | `libflutter.so`, Dart assets           | Confirm loaded modules and HTTP adapter; Dart/native code and platform channels may need different hooks. |
| React Native          | JS bundle, Hermes library              | Confirm native module/client calls; neither readable JS nor OkHttp is guaranteed.                         |
| Xamarin / .NET MAUI   | Mono libraries or managed assemblies   | Confirm managed/native HTTP handler and AOT mode; Java hooks alone may miss app logic.                    |
| Unity                 | `libunity.so`, possibly `libil2cpp.so` | Determine Mono versus IL2CPP; inspect the corresponding managed/native execution.                         |
| Cordova / Ionic       | `assets/www`, `cordova.js`             | Confirm the live WebView, navigation, and plugin bridge.                                                  |
| Cronet                | `org.chromium.net`, Cronet libraries   | Confirm executing client and protocol, including possible QUIC/HTTP/3.                                    |
| Native C/C++ / hybrid | Custom `.so` files, JNI declarations   | Follow Java entry points into loaded native modules; inspect using Ghidra/radare2 and Frida.              |

* Framework and networking choices are independent; one app may contain multiple HTTP clients and SDKs.

## Record a Runtime Profile

```
App/package/version and APK/split hashes:
Device/Android patch level/ABI/target SDK:
Original or patched/debug build; signing differences:
Framework and evidence; remaining unknowns:
Networking client/protocol per domain:
Root/emulator/debug/instrumentation checks and triggering action:
CA policy, pinning implementation, integrity/attestation behavior:
Accounts/roles and approved test limits:
Tool versions and baseline evidence timestamps:
```

* Classify controls as observed, not observed in tested flows, or unknown.
* An uneventful launch does not prove a control is absent.

## Capture the Baseline

* **Prerequisite:** disposable test installation.
* Split packages require `adb install-multiple` and the complete required split set, not single-APK `adb install`.
* Preserve approved test data before uninstalling/resetting an existing app.

```sh
adb devices -l
adb shell getprop ro.product.cpu.abilist
adb install <app.apk>
adb shell monkey -p <package-name> -c android.intent.category.LAUNCHER 1
adb logcat -d -v threadtime > baseline.log
```

* `monkey` here requests one launcher event, not a fuzzing session.
* Limit logs to the relevant PID/time window where possible; protect output that may contain unrelated data.
* Save existing logs before clearing them.
* Check root separately with `adb shell su -c id` only on an approved rooted lab device.

* Record startup, permissions, warnings/crashes, login/logout, token refresh, storage writes, component launches, WebView behavior, and background sync/notifications.
* Record normal networking first; introduce the proxy/CA as a separate variable using [Network Traffic and TLS](network-traffic-and-tls.md).
* Compare an unmodified run, attachment with no hooks, an observational hook, then a targeted change. Reset test state between comparisons where needed.
* Emulators aid snapshots/repeatability; physical devices help validate hardware/ABI-sensitive behavior. Neither guarantees root access or a favorable Play Integrity verdict. Bootloader unlocking can erase data and changes integrity state.

* Map each critical flow: action > Activity/Fragment/Compose > processing > IPC/WebView > request/response > storage > background use > logout/expiry cleanup.
* Correlate a test identifier across stages; keep real secrets out of the notes.

## Choose Tools by Task

| Task               | Primary / Optional Alternative                  | Dependency                                                                                  |
| ------------------ | ----------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Artifact review    | JADX/Apktool; Androguard or MobSF               | [Static tool setup](../static-testing/preflight-and-tools.md); verify release requirements. |
| Runtime hooks      | Frida; Objection                                | Matching host/server/Gadget versions and correct process ABI.                               |
| HTTP(S) inspection | Burp; mitmproxy/Proxyman                        | Reachable listener, correct routing, and stack-specific trust.                              |
| IPC                | ADB `am`, `content`, `dumpsys`; Drozer          | Authorized device; Drozer needs its own agent/server setup.                                 |
| Native analysis    | Ghidra; radare2                                 | Correct ELF/ABI/build; host `strings`/`readelf` or LLVM equivalents.                        |
| WebView            | Chrome remote debugging; targeted hooks         | USB debugging and WebView debugging enabled in the assessed configuration.                  |
| Data/backup        | File Explorer, SQLite, supported backup/restore | Appropriate app/device access and OS-specific backup mechanism.                             |

* **Shell dependencies:** install the named utilities before using `grep`, `unzip`, or shell-redirection examples.
* PowerShell is not Bash; replace placeholders and preserve device-shell quoting.
* Run Frida JavaScript in the injected agent, not the host shell.
