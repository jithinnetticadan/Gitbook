# Methodology and Baseline

{% hint style="info" %}
Use in-scope apps, devices, APIs, and disposable test accounts. Preserve the original APK/splits and record hashes. Capture behavior before installing hooks or changing trust, app code, or local state.
{% endhint %}

## Working Sequence

Identify the app > prepare the matching lab > record normal behavior > observe targeted calls > make one controlled change > verify the protected operation > document evidence and limits.

Static analysis identifies code/configuration and possible paths. Dynamic testing shows what executes under the conditions tested; a path you did not trigger remains untested, not proven safe. Client code can be modified on a tester-controlled device, but that does not imply control of the OS, other apps, hardware-backed keys, or the server.

| Initial Pass | Deliverable |
| --- | --- |
| Fingerprint | Package/version, APK/splits, ABI, target SDK, framework clues, exported components, and schemes. |
| Prepare | Compatible device and reversible test environment; complete [mandatory preflight](preflight-and-frida-setup.md#mandatory-preflight). |
| Observe | Unmodified startup, login/logout, permissions, logs, storage changes, network behavior, and blocks. |
| Map | One complete flow from UI through local processing, IPC/WebView, API, response, storage, and background work. |
| Instrument | One observational hook that fires during a known action without changing its result. |
| Validate | One scoped test with a normal control case, changed input, actual outcome, and repeatable evidence. |

This can guide the first hour; do not rush hardware setup or safety checks to meet a time target. Bypass controls only when required for an in-scope test or when assessing the control itself.

## Fingerprint the Implementation

On the host, with `unzip` and `grep` available (for example a configured WSL/Linux/macOS shell):

```sh
unzip -l <app.apk> | grep -E 'libflutter|libmonodroid|libunity|libil2cpp|index\.android\.bundle|libhermes|cordova\.js|libcronet|\.so$'
```

Inspect all relevant split APKs too. No match does not prove a Java-only app: renamed assets, packing, dynamic delivery, and newer framework layouts can hide these indicators.

| Candidate Stack | Static Clue | Confirm at Runtime / Select Layer |
| --- | --- | --- |
| Java/Kotlin | DEX classes and framework calls | Confirm ART classes and actual call path; use `Java.perform`. |
| Flutter | `libflutter.so`, Dart assets | Confirm loaded modules and HTTP adapter; Dart/native code and platform channels may need different hooks. |
| React Native | JS bundle, Hermes library | Confirm native module/client calls; neither readable JS nor OkHttp is guaranteed. |
| Xamarin / .NET MAUI | Mono libraries or managed assemblies | Confirm managed/native HTTP handler and AOT mode; Java hooks alone may miss app logic. |
| Unity | `libunity.so`, possibly `libil2cpp.so` | Determine Mono versus IL2CPP; inspect the corresponding managed/native execution. |
| Cordova / Ionic | `assets/www`, `cordova.js` | Confirm the live WebView, navigation, and plugin bridge. |
| Cronet | `org.chromium.net`, Cronet libraries | Confirm executing client and protocol, including possible QUIC/HTTP/3. |
| Native C/C++ / hybrid | Custom `.so` files, JNI declarations | Follow Java entry points into loaded native modules; inspect using Ghidra/radare2 and Frida. |

Framework and networking choices are independent. One app can contain multiple HTTP clients and SDKs.

## Record a Runtime Profile

```text
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

Mark controls as observed, not observed in tested flows, or unknown. Do not infer absence from an uneventful launch.

## Capture the Baseline

Use a disposable test installation; use `adb install-multiple` with the complete required split set instead of `adb install` for split packages. Do not uninstall/reset an existing app without preserving approved test data.

```sh
adb devices -l
adb shell getprop ro.product.cpu.abilist
adb install <app.apk>
adb shell monkey -p <package-name> -c android.intent.category.LAUNCHER 1
adb logcat -d -v threadtime > baseline.log
```

`monkey` here requests one launcher event, not a fuzzing session. Logs may contain unrelated data; limit capture to the relevant PID/time window where possible and protect the output. Save existing logs before clearing them. Check root separately with `adb shell su -c id` only on an approved rooted lab device.

* Record startup, permissions, warnings/crashes, login/logout, token refresh, storage writes, component launches, WebView behavior, and background sync/notifications.
* Record normal networking first; introduce the proxy/CA as a separate variable using [Network Traffic and TLS](network-traffic-and-tls.md).
* Compare an unmodified run, attachment with no hooks, an observational hook, then a targeted change. Reset test state between comparisons where needed.
* Emulators aid snapshots/repeatability; physical devices help validate hardware/ABI-sensitive behavior. Neither guarantees root access or a favorable Play Integrity verdict. Bootloader unlocking can erase data and changes integrity state.

For each critical flow, record: action > Activity/Fragment/Compose > processing > IPC/WebView > request/response > stored values > background use > logout/expiry cleanup. Correlate one test identifier across these stages without putting real secrets in the notes.

## Choose Tools by Task

| Task | Primary / Optional Alternative | Dependency |
| --- | --- | --- |
| Artifact review | JADX/Apktool; Androguard or MobSF | [Static tool setup](../static-testing/preflight-and-tools.md); verify release requirements. |
| Runtime hooks | Frida; Objection | Matching host/server/Gadget versions and correct process ABI. |
| HTTP(S) inspection | Burp; mitmproxy/Proxyman | Reachable listener, correct routing, and stack-specific trust. |
| IPC | ADB `am`, `content`, `dumpsys`; Drozer | Authorized device; Drozer needs its own agent/server setup. |
| Native analysis | Ghidra; radare2 | Correct ELF/ABI/build; host `strings`/`readelf` or LLVM equivalents. |
| WebView | Chrome remote debugging; targeted hooks | USB debugging and WebView debugging enabled in the assessed configuration. |
| Data/backup | File Explorer, SQLite, supported backup/restore | Appropriate app/device access and OS-specific backup mechanism. |

Host shell examples containing `grep`, `unzip`, or shell redirection assume the named utilities are installed. PowerShell is not Bash; replace placeholders and preserve device-shell quoting. Frida JavaScript runs in the injected agent, not the host shell.

**Next:** [Preflight and Frida Setup](preflight-and-frida-setup.md)