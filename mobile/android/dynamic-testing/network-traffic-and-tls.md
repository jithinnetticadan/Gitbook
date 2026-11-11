# Network Traffic and TLS

## Proxy Setup

1. Bind Burp to the device-reachable lab IP/port.
2. Set the device proxy and install the CA: [Android Burp guide](https://portswigger.net/support/configuring-an-android-device-to-work-with-burp).
3. Use DER where required; `.cer` renaming does not change encoding/trust. User-CA acceptance depends on OS/app policy.
4. Test API authentication, authorization, sensitive data, and server-side behavior.
5. If pinning blocks testing, use the [Objection pinning startup variant](objection-and-runtime-instrumentation.md#attach-or-spawn), a reviewed Frida script, or a patched test build.

* Trusted CA and pinning are separate checks.
* Android 7+ apps targeting API 24+ do not trust user-installed CAs by default. Use an authorized test trust configuration/device setup; installing the CA alone may not allow interception.
* Alternatives: [Proxyman](https://proxyman.io/), HTTP Canary (including Flutter attempts); verify platform/TLS compatibility.
* Setup: [MobSF Dynamic Analyzer](https://mobsf.github.io/docs/#/dynamic_analyzer), [Frida Android](https://frida.re/docs/android/).
* Optional/legacy: [CuckooDroid](https://github.com/idanr1986/cuckoo-droid) sandboxing, [BlueStacks](https://www.bluestacks.com/) emulator, [RMS](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), [Ghost](https://github.com/EntySec/Ghost). Verify maintenance/root behavior.
* [Objection session and startup commands](objection-and-runtime-instrumentation.md#attach-or-spawn).
* For flutter apps,  [FlutterTap](https://github.com/script-or-script/FlutterTap)

## Establish Network Visibility

* Use a device-reachable host address.
* Android Emulator commonly uses `10.0.2.2`; physical devices usually use the host's lab IP.
* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">adb shell settings get global http_proxy
  adb shell settings put global http_proxy &#x3C;proxy-ip>:8080
  adb shell am start -a android.intent.action.VIEW -d 'https://example.com'
  </code></pre>
* Verify browser HTTPS in Burp; trigger an app action and correlate its timestamp/domain.
* Browser success does not establish the app's CA policy; some stacks also ignore the global proxy.
* If no proxy existed, `adb shell settings put global http_proxy :0` commonly clears the global override.
* **System-CA dependencies:** device/version, Android Verified Boot, dynamic partitions, SELinux, systemless root, and trust-store layout.

## Diagnose Before Bypassing

<table><thead><tr><th width="145.0001220703125">Observation</th><th>Discriminating Check</th><th>Next Step / Success Evidence</th></tr></thead><tbody><tr><td>No traffic leaves the device</td><td>Is the action actually making a request? Check offline/cache behavior, DNS, connectivity, and app logs.</td><td>Use an authorized network capture if needed; identify destination and protocol.</td></tr><tr><td>Traffic leaves but bypasses Burp</td><td>Check proxy support, VPN routing, raw sockets, and QUIC/HTTP/3.</td><td>Configure a supported test route/client; demonstrate the action's request reaches the proxy.</td></tr><tr><td>TLS negotiation fails</td><td>Compare client/proxy/upstream logs for protocol, cipher, SNI, or mutual-TLS requirements.</td><td>Resolve the identified failure; do not assume pinning.</td></tr><tr><td>Certificate trust fails</td><td>Check chain, hostname, validity dates, device clock, app trust anchors, and user-CA policy.</td><td>Establish the intended CA trust for the specific stack.</td></tr><tr><td>Trusted chain rejected by a pin check</td><td>Confirm the executing pin implementation, domain, and certificate/public-key mismatch.</td><td>Instrument only that validation path for testing; verify decrypted requests/responses.</td></tr><tr><td>TLS succeeds but the operation fails</td><td>Inspect response body, authentication, integrity verdicts, request signing, and application-layer encryption.</td><td>Diagnose application rejection separately; HTTP status alone is insufficient.</td></tr><tr><td>Only some domains are visible</td><td>Map each domain to its SDK, WebView, or HTTP client and domain-specific configuration.</td><td>Test each relevant stack independently; document remaining visibility gaps.</td></tr></tbody></table>

## Match the Validation Implementation

### Client Certificate Validation Matrix

* Use the original release app without `sslpinning disable`, trust-manager replacement or SSL-error hooks. Trigger the same uncached request in each case and observe whether the app receives a response; a server-only `openssl` scan does not test the app's verifier.

| Presented certificate | Isolate this check | Meaningful failure |
| --- | --- | --- |
| Proxy certificate from a CA absent from app/device trust | Keep the request host correct; verify the app is not a debug/user-CA-trusting configuration | App completes the sensitive request through an untrusted chain. |
| Trusted lab chain, SAN for a different hostname | Trust the lab CA through the intended test configuration; keep the app's requested hostname unchanged | App accepts a certificate whose SAN does not match that hostname. |
| Trusted lab chain with expired/not-yet-valid leaf | Keep hostname valid and device time correct | App accepts the invalid validity period. |
| Valid trusted chain but different public key | Keep hostname, validity and chain valid; use only for a documented pinned endpoint | App accepts a key outside the active intended pin set. |

* Use a lab proxy/endpoint that can present each certificate; changing only the HTTP `Host` header does not change TLS hostname validation. If pinning rejects a test before hostname/date verification, that result does not independently prove those lower-level checks.
* **WebView:** navigate to the invalid-certificate endpoint through the real app route and observe `onReceivedSslError`; continuing with no user decision through `proceed()` confirms that path. Do not enable a bypass hook before testing the original behavior.
* **HTTP fallback:** cause that same HTTPS operation to fail validation and check whether it retries over `http://` with the original authentication/body. A public HTTP redirect alone is not sensitive cleartext fallback.

#### Generate and Present Test Certificates

* **Shared Android/iOS lab, PowerShell 7 + OpenSSL 3 on Windows/Linux/macOS:** run in a new working directory. Replace `lab-api.example.test` with the hostname the app will actually request before generating the files. The recipe creates a valid control and wrong-host/expired/future leaves under the same CA/key, isolating one validation property at a time.
  * ```powershell
    New-Item -ItemType Directory -Path tls-lab -ErrorAction Stop | Out-Null
    Set-Location tls-lab
    New-Item -ItemType Directory -Path lab-issued | Out-Null
    [IO.File]::WriteAllText((Join-Path $PWD 'lab-index.txt'), '', [Text.Encoding]::ASCII)
    [IO.File]::WriteAllText((Join-Path $PWD 'lab-serial.txt'), "1000`n", [Text.Encoding]::ASCII)
    $configuration = @(
      '[ca]', 'default_ca=lab', '[lab]', 'database=./lab-index.txt',
      'new_certs_dir=./lab-issued', 'serial=./lab-serial.txt', 'certificate=./lab-ca.crt',
      'private_key=./lab-ca.key', 'default_md=sha256', 'default_days=7',
      'policy=lab_policy', 'unique_subject=no', 'x509_extensions=lab_leaf',
      '[lab_policy]', 'commonName=supplied', '[lab_leaf]',
      'basicConstraints=critical,CA:FALSE', 'keyUsage=critical,digitalSignature,keyEncipherment',
      'extendedKeyUsage=serverAuth', 'subjectAltName=DNS:lab-api.example.test'
    ) -join "`n"
    [IO.File]::WriteAllText((Join-Path $PWD 'lab-ca.cnf'), $configuration, [Text.Encoding]::ASCII)
    [IO.File]::WriteAllText((Join-Path $PWD 'lab-wrong.cnf'),
      $configuration.Replace('DNS:lab-api.example.test', 'DNS:wrong-host.example.test'), [Text.Encoding]::ASCII)
    openssl req -x509 -newkey rsa:2048 -noenc -keyout lab-ca.key -out lab-ca.crt -days 30 -subj '/CN=Mobile TLS Lab CA' -addext 'basicConstraints=critical,CA:TRUE' -addext 'keyUsage=critical,keyCertSign,cRLSign'
    openssl req -new -newkey rsa:2048 -noenc -keyout lab-server.key -out lab-server.csr -subj '/CN=lab-api.example.test'
    openssl ca -batch -config lab-ca.cnf -in lab-server.csr -out valid.crt -notext
    openssl ca -batch -config lab-wrong.cnf -in lab-server.csr -out wrong-host.crt -notext
    $now = [DateTimeOffset]::UtcNow
    $pastStart = $now.AddDays(-3).ToString('yyMMddHHmmssZ')
    $pastEnd = $now.AddDays(-1).ToString('yyMMddHHmmssZ')
    $futureStart = $now.AddDays(1).ToString('yyMMddHHmmssZ')
    $futureEnd = $now.AddDays(3).ToString('yyMMddHHmmssZ')
    openssl ca -batch -config lab-ca.cnf -in lab-server.csr -out expired.crt -startdate $pastStart -enddate $pastEnd -notext
    openssl ca -batch -config lab-ca.cnf -in lab-server.csr -out future.crt -startdate $futureStart -enddate $futureEnd -notext
    ```
* **Verify the fixtures (same PowerShell session):** only `valid.crt` should pass for the requested hostname/current time; the other three should fail for hostname or validity, not chain signature.
  * ```powershell
    foreach ($leaf in @('valid.crt', 'wrong-host.crt', 'expired.crt', 'future.crt')) {
      openssl verify -CAfile lab-ca.crt -verify_hostname lab-api.example.test $leaf
    }
    ```
* **Serve one certificate (unchanged in Bash / PowerShell):** use another terminal in `tls-lab`; replace `valid.crt` with one variant per run. `-www` provides a TLS/HTTP control, not a replica of the production API.
  * ```text
    openssl s_server -accept 8443 -cert valid.crt -key lab-server.key -www
    ```
* **Connect the actual app:** point its real configurable URL/WebView input to `https://lab-api.example.test:8443`, and resolve that name to the device-reachable lab host through test DNS. If the app has a fixed host/port, use matching lab DNS/routing/proxy forwarding; DNS alone does not remap port 443 to 8443. A browser-only connection tests the browser, not the app.
* **Trust comparison:** first leave `lab-ca.crt` untrusted. For hostname/date isolation, install/allow that CA through the intended test trust path and verify `valid.crt` works before testing the other leaves. Android user-CA policy and iOS full trust still apply. Keep hostname, app request and device time unchanged; do not install the leaves as independent trust anchors.
* **Observe:** correlate the app's TLS result with the listener handshake/request. An application JSON error after a completed handshake differs from certificate rejection. A pin mismatch may block every lab leaf; it does not independently establish that hostname/date validation was exercised.

<table><thead><tr><th width="122.9998779296875">Implementation</th><th>Identify and Test</th><th>Common Limitation</th></tr></thead><tbody><tr><td>Java/Kotlin with OkHttp</td><td>Locate the actual <code>CertificatePinner</code> class and executing overload; correlate its host argument with the failing domain.</td><td>Versions, obfuscation, shaded packages, and independent SDK clients change hook targets.</td></tr><tr><td>Custom trust manager / Conscrypt</td><td>Inspect the concrete <code>checkServerTrusted</code> implementation and observed call stack.</td><td>An interface hook or generic Conscrypt script is not a universal bypass.</td></tr><tr><td>Network Security Config</td><td>Resolve the manifest's configuration resource, matching domain, trust anchors, and <code>&#x3C;pin-set></code>.</td><td>Configuration presence does not prove every networking stack honors it.</td></tr><tr><td>WebView</td><td>Identify the actual <code>WebViewClient</code> and SSL error path separately.</td><td>Test-only <code>SslErrorHandler.proceed()</code> changes validation, not other app traffic; never treat it as remediation.</td></tr><tr><td>Flutter</td><td>Identify the actual Dart HTTP package/adapter, Cronet client, or platform channel.</td><td><code>libflutter.so</code> does not prove all requests use its native TLS; offsets vary by build/ABI.</td></tr><tr><td>React Native</td><td>Trace JS calls into the executing platform client or custom module.</td><td>OkHttp is common, not guaranteed; Hermes/architecture changes affect analysis.</td></tr><tr><td>Cordova / Ionic</td><td>Separate WebView XHR/fetch from native HTTP plugins such as advanced-http.</td><td>Hooking WebView validation does not necessarily affect a native plugin.</td></tr><tr><td>Unity</td><td>Identify UnityWebRequest, managed HTTP, or a plugin and Mono versus IL2CPP.</td><td>Do not assume OkHttp; managed assembly/IL2CPP tooling must match the build.</td></tr><tr><td>Xamarin / .NET MAUI</td><td>Identify the managed certificate callback and selected native/managed HTTP handler.</td><td>AOT and framework versions affect visibility and hook selection.</td></tr><tr><td>Native TLS / Cronet</td><td>Locate the loaded library and verification path; inspect UDP/QUIC when applicable.</td><td>Java hooks may miss it; use build-specific native analysis, not copied offsets.</td></tr></tbody></table>

## Protocol and Endpoint Checks

* **Burp Repeater:** Proxy > HTTP history > observed request > Send to Repeater; change one method/header/body field and compare the actual response.
* **Host OpenSSL/curl:** server TLS, HTTP fallback, and method behavior. Set the endpoint to the observed route, not a guessed privileged API.
  * ```bash
    openssl s_client -connect '<api-host>:443' -servername '<api-host>' -verify_hostname '<api-host>' -verify_return_error </dev/null
    curl -i 'http://<api-host>/<observed-path>'
    curl -i -X OPTIONS 'https://<api-host>/<observed-path>'
    ```
* **App/API authentication and account comparisons:** [request replay commands](authentication-and-cryptography.md#captured-request-replay).
* **gRPC with supplied descriptors:** `grpcurl` must be installed; this does not require server reflection.
  * ```bash
    grpcurl -import-path '<proto-directory>' -proto '<service.proto>' -H 'authorization: Bearer <test-access-token>' -d '{"id":"<test-record-id>"}' '<api-host>:443' '<package.Service/Method>'
    ```

<table><thead><tr><th width="176">Surface</th><th>Scoped Test</th><th>Evidence / Limitation</th></tr></thead><tbody><tr><td>TLS versions / cipher suites</td><td>Assess an approved endpoint with a current TLS scanner and compare the app's negotiated connection</td><td>Server support for an old protocol is not proof the app can be downgraded; capture the actual requirement and negotiation.</td></tr><tr><td>Cleartext / fallback</td><td>Cause a controlled TLS trust/connectivity failure, then observe whether the same sensitive action retries over HTTP</td><td>Observe whether the same operation retries over HTTP after TLS failure.</td></tr><tr><td>HTTPS and HTTP routes</td><td>Check known endpoints and redirects with synthetic data</td><td>Confirm whether HTTP serves the observed operation or only redirects.</td></tr><tr><td>Hostname / SAN / SNI / Host</td><td>Check certificate hostname validation and in-scope virtual-host routing</td><td>Wildcards or an SNI/Host difference alone are not vulnerabilities; establish unintended access or a concrete trust failure.</td></tr><tr><td>HTTP methods</td><td>Compare allowed methods on a known owned test resource</td><td>Verify per-method authorization; do not issue destructive verbs against production data.</td></tr><tr><td>WebSockets</td><td>TLS, handshake authentication, browser Origin handling where applicable, per-message ownership, logout/reconnect</td><td>Authorization at upgrade does not guarantee message-level checks. Cross-site WebSocket hijacking requires a viable browser/credential context.</td></tr><tr><td>gRPC / HTTP/2 / protobuf</td><td>Recover authorized <code>.proto</code> descriptors or obtain them from the owner; use a compatible decoder/client</td><td>Test metadata auth, per-RPC authorization, streaming limits, cancellation, and errors. Reflection is unnecessary when compatible descriptors are supplied.</td></tr><tr><td>Local HTTP/WebSocket listeners</td><td>Binding address, authentication, origin/CSRF defenses, URI endpoints</td><td>Loopback is not an authentication mechanism; test access from a minimally privileged local app/browser as applicable.</td></tr><tr><td>DoH / QUIC / VPN routing</td><td>Identify the actual resolver/transport and approved capture point</td><td>Encrypted DNS or bypassing a proxy is not a vulnerability. Use owner-supported routing/transport controls; forced plain DNS changes the test.</td></tr><tr><td>WebRTC / signaling / TURN</td><td>Session authorization, peer/room binding, TURN credentials/expiry, ICE exposure</td><td>Assess actual privacy/access impact; a visible private IP or reachable relay alone does not establish abuse.</td></tr><tr><td>Analytics / telemetry</td><td>Compare consent states and fields actually sent to each recipient</td><td>Distinguish documented necessary processing from excess PII, secrets, cross-account mixing, or unapproved recipients.</td></tr></tbody></table>

* For TrustKit, custom pinning, and native clients, identify the actual verifier and confirm the hook fires.
