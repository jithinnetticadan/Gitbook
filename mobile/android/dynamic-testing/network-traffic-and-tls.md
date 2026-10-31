# Network Traffic and TLS

{% hint style="info" %}
* Use an authorized test device and test accounts; replace command placeholders before use.
* Preserve originals, protect dumps, and restore the lab afterward.
{% endhint %}

{% hint style="warning" %}
* **Prerequisites:** reachable proxy and CA trust accepted by the app; assess pinning separately.
* For Frida-based bypasses, complete [Mandatory Preflight](preflight-and-frida-setup.md#mandatory-preflight).
{% endhint %}

## Network Traffic and TLS

1. Bind Burp to the lab interface; firewall any "All interfaces" listener.
2. Set the device proxy and install the CA: [Android Burp guide](https://portswigger.net/support/configuring-an-android-device-to-work-with-burp).
3. Use DER where required; `.cer` renaming does not change encoding/trust. User-CA acceptance depends on OS/app policy.
4. Test API authentication, authorization, sensitive data, and server-side behavior.
5. If pinning blocks testing, use `android sslpinning disable`, reviewed Frida scripts, or a patched test build.

* Trusted CA and pinning are separate checks; bypass is a test technique, not remediation.
* Android 7+ apps targeting API 24+ do not trust user-installed CAs by default. Use an authorized test trust configuration/device setup; installing the CA alone may not allow interception.
* Alternatives: [Proxyman](https://proxyman.io/), HTTP Canary (including Flutter attempts); verify platform/TLS compatibility.
* Setup: [MobSF Dynamic Analyzer](https://mobsf.github.io/docs/#/dynamic_analyzer), [Frida Android](https://frida.re/docs/android/).
* Optional/legacy: [CuckooDroid](https://github.com/idanr1986/cuckoo-droid) sandboxing, [BlueStacks](https://www.bluestacks.com/) emulator, [RMS](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), [Ghost](https://github.com/EntySec/Ghost). Verify maintenance/root behavior.
* For `android sslpinning disable`, see [Objection and Runtime Instrumentation](objection-and-runtime-instrumentation.md).
* For flutter apps,  [FlutterTap](https://github.com/script-or-script/FlutterTap)

## Establish Network Visibility

* Use a device-reachable host address; device loopback is not the host.
* Android Emulator commonly uses `10.0.2.2`; physical devices usually use the host's lab IP.

```sh
adb shell settings get global http_proxy
adb shell settings put global http_proxy <proxy-ip>:8080
adb shell am start -a android.intent.action.VIEW -d 'https://example.com'
```

* Verify browser HTTPS in Burp; trigger an app action and correlate its timestamp/domain.
* Browser success does not establish the app's CA policy; some stacks also ignore the global proxy.
* Restore original global and Wi-Fi-specific proxy settings; remove the test CA afterward.
* If no proxy existed, `adb shell settings put global http_proxy :0` commonly clears the global override.
* **System-CA dependencies:** device/version, Android Verified Boot, dynamic partitions, SELinux, systemless root, and trust-store layout.
* Do not assume `/system` can be remounted.
* A system CA does not bypass pinning; prefer an approved test trust configuration when available.

## Diagnose Before Bypassing

* Treat the matrix as hypotheses, not vulnerability verdicts.
* Trust/pinning failures may appear as TLS handshake failures.

| Observation                           | Discriminating Check                                                                                          | Next Step / Success Evidence                                                                 |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| No traffic leaves the device          | Is the action actually making a request? Check offline/cache behavior, DNS, connectivity, and app logs.       | Use an authorized network capture if needed; identify destination and protocol.              |
| Traffic leaves but bypasses Burp      | Check proxy support, VPN routing, raw sockets, and QUIC/HTTP/3.                                               | Configure a supported test route/client; demonstrate the action's request reaches the proxy. |
| TLS negotiation fails                 | Compare client/proxy/upstream logs for protocol, cipher, SNI, or mutual-TLS requirements.                     | Resolve the identified failure; do not assume pinning.                                       |
| Certificate trust fails               | Check chain, hostname, validity dates, device clock, app trust anchors, and user-CA policy.                   | Establish the intended CA trust for the specific stack.                                      |
| Trusted chain rejected by a pin check | Confirm the executing pin implementation, domain, and certificate/public-key mismatch.                        | Instrument only that validation path for testing; verify decrypted requests/responses.       |
| TLS succeeds but the operation fails  | Inspect response body, authentication, integrity verdicts, request signing, and application-layer encryption. | Diagnose application rejection separately; HTTP status alone is insufficient.                |
| Only some domains are visible         | Map each domain to its SDK, WebView, or HTTP client and domain-specific configuration.                        | Test each relevant stack independently; document remaining visibility gaps.                  |

* **Capture prerequisites:** suitable device privileges or an authorized lab gateway/capture facility.
* Confirm tool availability; `tcpdump` is not installed on every device.
* Capture only scoped traffic; packet visibility does not decrypt TLS.

## Match the Validation Implementation

| Implementation                   | Identify and Test                                                                                                        | Common Limitation                                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| Java/Kotlin with OkHttp          | Locate the actual `CertificatePinner` class and executing overload; correlate its host argument with the failing domain. | Versions, obfuscation, shaded packages, and independent SDK clients change hook targets.                        |
| Custom trust manager / Conscrypt | Inspect the concrete `checkServerTrusted` implementation and observed call stack.                                        | An interface hook or generic Conscrypt script is not a universal bypass.                                        |
| Network Security Config          | Resolve the manifest's configuration resource, matching domain, trust anchors, and `<pin-set>`.                          | Configuration presence does not prove every networking stack honors it.                                         |
| WebView                          | Identify the actual `WebViewClient` and SSL error path separately.                                                       | Test-only `SslErrorHandler.proceed()` changes validation, not other app traffic; never treat it as remediation. |
| Flutter                          | Identify the actual Dart HTTP package/adapter, Cronet client, or platform channel.                                       | `libflutter.so` does not prove all requests use its native TLS; offsets vary by build/ABI.                      |
| React Native                     | Trace JS calls into the executing platform client or custom module.                                                      | OkHttp is common, not guaranteed; Hermes/architecture changes affect analysis.                                  |
| Cordova / Ionic                  | Separate WebView XHR/fetch from native HTTP plugins such as advanced-http.                                               | Hooking WebView validation does not necessarily affect a native plugin.                                         |
| Unity                            | Identify UnityWebRequest, managed HTTP, or a plugin and Mono versus IL2CPP.                                              | Do not assume OkHttp; managed assembly/IL2CPP tooling must match the build.                                     |
| Xamarin / .NET MAUI              | Identify the managed certificate callback and selected native/managed HTTP handler.                                      | AOT and framework versions affect visibility and hook selection.                                                |
| Native TLS / Cronet              | Locate the loaded library and verification path; inspect UDP/QUIC when applicable.                                       | Java hooks may miss it; use build-specific native analysis, not copied offsets.                                 |

* **Confirm:** repeat the same action before/after the change and retain matching requests/responses.
* Distinguish test-induced acceptance from original validation behavior; a hook message alone proves neither interception nor impact.
* Use Burp or [mitmproxy](https://mitmproxy.org/) for this workflow.

## Protocol and Endpoint Checks

| Surface                        | Scoped Test                                                                                                         | Evidence / Limitation                                                                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| TLS versions / cipher suites   | Assess an approved endpoint with a current TLS scanner and compare the app's negotiated connection                  | Server support for an old protocol is not proof the app can be downgraded; capture the actual requirement and negotiation.                     |
| Cleartext / fallback           | Cause a controlled TLS trust/connectivity failure, then observe whether the same sensitive action retries over HTTP | Restore the original trust/routing afterward; do not remove production certificates or modify production services.                             |
| HTTPS and HTTP routes          | Check known endpoints and redirects with synthetic data                                                             | Do not send real credentials over HTTP just to establish exposure. Confirm whether HTTP serves a sensitive operation or only redirects.        |
| Hostname / SAN / SNI / Host    | Check certificate hostname validation and in-scope virtual-host routing                                             | Wildcards or an SNI/Host difference alone are not vulnerabilities; establish unintended access or a concrete trust failure.                    |
| HTTP methods                   | Compare allowed methods on a known owned test resource                                                              | Verify per-method authorization; do not issue destructive verbs against production data.                                                       |
| WebSockets                     | TLS, handshake authentication, browser Origin handling where applicable, per-message ownership, logout/reconnect    | Authorization at upgrade does not guarantee message-level checks. Cross-site WebSocket hijacking requires a viable browser/credential context. |
| gRPC / HTTP/2 / protobuf       | Recover authorized `.proto` descriptors or obtain them from the owner; use a compatible decoder/client              | Test metadata auth, per-RPC authorization, streaming limits, cancellation, and errors. Do not enable production reflection solely for testing. |
| Local HTTP/WebSocket listeners | Binding address, authentication, origin/CSRF defenses, URI endpoints                                                | Loopback is not an authentication mechanism; test access from a minimally privileged local app/browser as applicable.                          |
| DoH / QUIC / VPN routing       | Identify the actual resolver/transport and approved capture point                                                   | Encrypted DNS or bypassing a proxy is not a vulnerability. Use owner-supported routing/transport controls; forced plain DNS changes the test.  |
| WebRTC / signaling / TURN      | Session authorization, peer/room binding, TURN credentials/expiry, ICE exposure                                     | Assess actual privacy/access impact; a visible private IP or reachable relay alone does not establish abuse.                                   |
| Analytics / telemetry          | Compare consent states and fields actually sent to each recipient                                                   | Distinguish documented necessary processing from excess PII, secrets, cross-account mixing, or unapproved recipients.                          |

* **Transparent interception dependencies:** compatible proxy/listener and controlled device/gateway routing, including return traffic and DNS.
* Device NAT requires suitable root/kernel tooling; rules may not cover IPv6/UDP.
* Do not apply generic `iptables` redirects without a rollback plan.
* For TrustKit, custom pinning, and native clients, identify the actual verifier and confirm the hook fires.
