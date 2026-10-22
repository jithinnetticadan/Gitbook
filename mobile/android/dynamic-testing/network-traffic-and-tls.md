# Network Traffic and TLS

{% hint style="info" %}
Use an authorized test device and test accounts. Preserve originals; protect dumps and restore the lab afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Before testing, confirm the device can reach the proxy and the app accepts the CA. Check pinning separately. For Frida-based bypasses, complete the [Mandatory Preflight](preflight-and-frida-setup.md#mandatory-preflight).
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

For `android sslpinning disable`, see [Objection and Runtime Instrumentation](objection-and-runtime-instrumentation.md).

## Establish Network Visibility

Record the original proxy settings before changing them. The proxy address must be reachable from the device; device loopback is not the host. Android Emulator commonly reaches the host through `10.0.2.2`; physical devices usually use the host's lab IP.

```sh
adb shell settings get global http_proxy
adb shell settings put global http_proxy <proxy-ip>:8080
adb shell am start -a android.intent.action.VIEW -d 'https://example.com'
```

Verify the browser's HTTPS request in Burp, then trigger a specific app action and correlate its timestamp/domain. Browser success does not establish the app's CA policy. Some stacks ignore the global proxy. Restore the original setting and remove the test CA afterward; if there was no proxy, `adb shell settings put global http_proxy :0` commonly clears this override. Also restore any Wi-Fi-specific proxy configuration.

System CA installation is device/version-specific: Android Verified Boot, dynamic partitions, SELinux, systemless root, and newer trust-store layouts affect the procedure. Do not assume remounting `/system` is possible. Installing a system CA does not bypass pinning; prefer an approved test trust configuration when available.

## Diagnose Before Bypassing

These are hypotheses to test, not vulnerability verdicts. Trust and pinning failures can themselves appear as TLS handshake failures.

| Observation                           | Discriminating Check                                                                                          | Next Step / Success Evidence                                                                 |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| No traffic leaves the device          | Is the action actually making a request? Check offline/cache behavior, DNS, connectivity, and app logs.       | Use an authorized network capture if needed; identify destination and protocol.              |
| Traffic leaves but bypasses Burp      | Check proxy support, VPN routing, raw sockets, and QUIC/HTTP/3.                                               | Configure a supported test route/client; demonstrate the action's request reaches the proxy. |
| TLS negotiation fails                 | Compare client/proxy/upstream logs for protocol, cipher, SNI, or mutual-TLS requirements.                     | Resolve the identified failure; do not assume pinning.                                       |
| Certificate trust fails               | Check chain, hostname, validity dates, device clock, app trust anchors, and user-CA policy.                   | Establish the intended CA trust for the specific stack.                                      |
| Trusted chain rejected by a pin check | Confirm the executing pin implementation, domain, and certificate/public-key mismatch.                        | Instrument only that validation path for testing; verify decrypted requests/responses.       |
| TLS succeeds but the operation fails  | Inspect response body, authentication, integrity verdicts, request signing, and application-layer encryption. | Diagnose application rejection separately; HTTP status alone is insufficient.                |
| Only some domains are visible         | Map each domain to its SDK, WebView, or HTTP client and domain-specific configuration.                        | Test each relevant stack independently; document remaining visibility gaps.                  |

Packet capture requires suitable device privileges or an authorized lab gateway/capture facility. Tools such as `tcpdump` are not present on every device. Capture only scoped traffic; packet visibility alone does not decrypt TLS.

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

**Confirm:** repeat the same action before/after the change, retain the matching request/response, and distinguish test-induced acceptance from the original validation behavior. A successful hook message alone proves nothing about interception or impact. Burp or [mitmproxy](https://mitmproxy.org/) can support this workflow.

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

Transparent interception requires a compatible proxy/listener and controlled device/gateway routing, including return traffic and DNS. Device NAT rules require suitable root/kernel tooling and may not cover IPv6/UDP; do not apply a generic `iptables` redirect without a rollback plan. TrustKit, custom pinning, and native clients still need the concrete verifier and a confirmed hook hit.
