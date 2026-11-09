# Methodology and Baseline

## Working Sequence

1. Identify the app.
2. Prepare a compatible lab.
3. Record normal behavior.
4. Observe targeted calls.
5. Make one controlled change.
6. Verify the protected operation.
7. Note limitations and untested paths.

<table><thead><tr><th width="111">Initial Pass</th><th>Deliverable</th></tr></thead><tbody><tr><td>Fingerprint</td><td>Package/version, APK/splits, ABI, target SDK, framework clues, exported components, and schemes.</td></tr><tr><td>Prepare</td><td>Compatible device and reversible lab; <a href="../setup.md#device-and-frida-setup">Frida setup</a> only when instrumenting.</td></tr><tr><td>Observe</td><td>Unmodified startup, login/logout, permissions, logs, storage changes, network behavior, and blocks.</td></tr><tr><td>Map</td><td>One complete flow from UI through local processing, IPC/WebView, API, response, storage, and background work.</td></tr><tr><td>Instrument</td><td>One observational hook that fires during a known action without changing its result.</td></tr><tr><td>Validate</td><td>One scoped test with a normal control case, changed input, actual outcome, and repeatable evidence.</td></tr></tbody></table>

## Fingerprint the Implementation

* **Host dependencies:** `unzip` and `grep`, such as in a configured WSL/Linux/macOS shell.

* ```sh
  unzip -l <app.apk> | grep -E 'libflutter|libmonodroid|libunity|libil2cpp|index\.android\.bundle|libhermes|cordova\.js|libcronet|\.so$'
  ```

* Inspect all relevant split APKs.
* No match does not prove a Java-only app; renamed assets, packing, dynamic delivery, and newer framework layouts may hide indicators.

<table><thead><tr><th width="115.9998779296875">Candidate Stack</th><th width="207">Static Clue</th><th>Confirm at Runtime / Select Layer</th></tr></thead><tbody><tr><td>Java/Kotlin</td><td>DEX classes and framework calls</td><td>Confirm ART classes and actual call path; use <code>Java.perform</code>.</td></tr><tr><td>Flutter</td><td><code>libflutter.so</code>, Dart assets</td><td>Confirm loaded modules and HTTP adapter; Dart/native code and platform channels may need different hooks.</td></tr><tr><td>React Native</td><td>JS bundle, Hermes library</td><td>Confirm native module/client calls; neither readable JS nor OkHttp is guaranteed.</td></tr><tr><td>Xamarin / .NET MAUI</td><td>Mono libraries or managed assemblies</td><td>Confirm managed/native HTTP handler and AOT mode; Java hooks alone may miss app logic.</td></tr><tr><td>Unity</td><td><code>libunity.so</code>, possibly <code>libil2cpp.so</code></td><td>Determine Mono versus IL2CPP; inspect the corresponding managed/native execution.</td></tr><tr><td>Cordova / Ionic</td><td><code>assets/www</code>, <code>cordova.js</code></td><td>Confirm the live WebView, navigation, and plugin bridge.</td></tr><tr><td>Cronet</td><td><code>org.chromium.net</code>, Cronet libraries</td><td>Confirm executing client and protocol, including possible QUIC/HTTP/3.</td></tr><tr><td>Native C/C++ / hybrid</td><td>Custom <code>.so</code> files, JNI declarations</td><td>Follow Java entry points into loaded native modules; inspect using Ghidra/radare2 and Frida.</td></tr></tbody></table>

* Framework and networking choices are independent; one app may contain multiple HTTP clients and SDKs.

## Capture the Baseline

* Split packages require `adb install-multiple` and the complete required split set, not single-APK `adb install`.
* **Connection:** [ADB device commands](component-testing.md#adb-probes-and-caller-identity); **ABI:** [device architecture commands](../setup.md#device-and-frida-setup).
* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb install &#x3C;app.apk>
  adb shell monkey -p &#x3C;package-name> -c android.intent.category.LAUNCHER 1
  adb logcat -d -v threadtime > baseline.log
  </code></pre>
* `monkey` here requests one launcher event, not a fuzzing session.
* Limit logs to the relevant PID/time window where possible.
* Check root separately with `adb shell su -c id` only on an approved rooted lab device.
* Record startup, permissions, warnings/crashes, login/logout, token refresh, storage writes, component launches, WebView behavior, and background sync/notifications.
* Record normal networking first; introduce the proxy/CA as a separate variable using [Network Traffic and TLS](network-traffic-and-tls.md).
* Compare an unmodified run, attachment with no hooks, an observational hook, then a targeted change. Reset test state between comparisons where needed.
* Emulators aid snapshots/repeatability; physical devices help validate hardware/ABI-sensitive behavior. Neither guarantees root access or a favorable Play Integrity verdict.
* Map each critical flow: action > Activity/Fragment/Compose > processing > IPC/WebView > request/response > storage > background use > logout/expiry cleanup.
* Correlate a test identifier across stages.

## Choose Tools by Task

<table><thead><tr><th width="124.0001220703125">Task</th><th width="237.0001220703125">Primary / Optional Alternative</th><th>Dependency</th></tr></thead><tbody><tr><td>Artifact review</td><td>JADX/Apktool; Androguard or MobSF</td><td><a href="../setup.md#host-tools">Host tools</a>; verify release requirements.</td></tr><tr><td>Runtime hooks</td><td>Frida; Objection</td><td>Matching host/server/Gadget versions and correct process ABI.</td></tr><tr><td>HTTP(S) inspection</td><td>Burp; mitmproxy/Proxyman</td><td>Reachable listener, correct routing, and stack-specific trust.</td></tr><tr><td>IPC</td><td>ADB <code>am</code>, <code>content</code>, <code>dumpsys</code>; Drozer</td><td>Authorized device; Drozer needs its own agent/server setup.</td></tr><tr><td>Native analysis</td><td>Ghidra; radare2</td><td>Correct ELF/ABI/build; host <code>strings</code>/<code>readelf</code> or LLVM equivalents.</td></tr><tr><td>WebView</td><td>Chrome remote debugging; targeted hooks</td><td>USB debugging and WebView debugging enabled in the assessed configuration.</td></tr><tr><td>Data/backup</td><td>File Explorer, SQLite, supported backup/restore</td><td>Appropriate app/device access and OS-specific backup mechanism.</td></tr></tbody></table>
