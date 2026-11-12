# Network Traffic and TLS

## Proxy Setup

{% tabs %}
{% tab title="Burp Suite" %}
1. Bind Burp to the device-reachable lab host IP/port.
2. Set the iPhone Wi-Fi proxy to that address. `127.0.0.1` on the phone is **not the proxy host**.
3. Open `http://burp`; install the CA under VPN & Device Management.
4. Enable trust: General > About > Certificate Trust Settings (labels vary).
5. Test API authentication, authorization, inputs, sensitive data, and server behavior.
6. Confirm the app's CA trust separately from pinning.
7. Follow the current [PortSwigger iOS proxy setup](https://portswigger.net/burp/documentation/desktop/mobile/config-ios-device)
{% endtab %}
{% tab title="mitmproxy" %}
1. **Mac terminal:** start the installed proxy; use the Mac's device-reachable IP and this port in iPhone Wi-Fi proxy settings.
	 * ```bash
		 mitmproxy --listen-host 0.0.0.0 --listen-port 8080
		 ```
2. On the device, open `http://mitm.it` through the proxy and install the iOS CA profile. Enable its full trust under General > About > Certificate Trust Settings.
3. Trigger the app request and inspect the flow in mitmproxy; the app's trust/pinning implementation determines whether HTTPS content is visible.
{% endtab %}
{% tab title="Proxyman" %}
1. Start Proxyman, enable its external-device proxy listener, and set the iPhone's Wi-Fi proxy to the Mac IP/listener port displayed by Proxyman.
2. Use Proxyman's iOS certificate instructions to install its CA profile and enable full trust in Certificate Trust Settings. Enable SSL proxying for the observed host.
3. Trigger the app request and inspect it in Proxyman; the app's trust/pinning implementation determines whether HTTPS content is visible.
{% endtab %}
{% endtabs %}

## Pinning Checks

* **Objection:** [pinning command](runtime-instrumentation.md#classes-and-hooks) or [startup hook](runtime-instrumentation.md#startup-hooks).
* [SSL Kill Switch 2](https://github.com/nabla-c0d3/ssl-kill-switch2) / [3](https://github.com/NyaMisty/ssl-kill-switch3/releases): compatible jailbroken devices only.
* AppSync alters code-signing behavior; it does **not** replace CA trust configuration.
* For Objection session syntax and startup hooks, see [Runtime Instrumentation](runtime-instrumentation.md).

## Captured-Request Replay

### Original-App TLS Negative Tests

* Before enabling pinning bypass, trigger the same uncached app request through each certificate case below. Use a configured lab proxy/endpoint and the real requested hostname. Test `URLSession`, WKWebView and separate SDK clients individually where used.

| Certificate variant | Hold constant | Failure |
| --- | --- | --- |
| CA not trusted by the app/device | Correct hostname and valid dates | Sensitive app operation succeeds through the untrusted chain. |
| Trusted lab CA, wrong SAN hostname | App request hostname, chain trust and dates | Request succeeds despite hostname mismatch. |
| Trusted lab CA, expired/not-yet-valid leaf | Correct hostname and device time | Request succeeds outside certificate validity. |
| Trusted chain, unexpected public key | Correct hostname/dates; endpoint has a documented active pin | Pin policy accepts a nonmatching key. |

* For wrong-host/date tests, establish chain trust separately. A pin failure can mask another check. Changing an HTTP `Host` header alone does not change the TLS hostname being verified.
* **ATS/cleartext:** from the app's actual URL input/configuration, try the same observed route over HTTP and trigger an HTTPS trust failure. Confirm whether sensitive authentication/body data is sent in an HTTP fallback; an ATS exception or a public redirect alone is not that result.
* A successful operation only after `ios sslpinning disable` demonstrates test interception, not a vulnerability in the unmodified app.
* **Generate/present the certificates:** use the [shared TLS-lab recipe](../../android/dynamic-testing/network-traffic-and-tls.md#generate-and-present-test-certificates) on the Mac with PowerShell 7 and OpenSSL 3. It includes valid/wrong-host/expired/future leaves, fixture verification and the listener. Complete iOS CA full trust for the trusted-chain cases, then test the actual app URL rather than Safari alone.

### Protected API and Refresh Requests

* **Burp:** Proxy > HTTP history > selected request > Send to Repeater. Replay the baseline, logged-out token, and account-A token with account-B's record ID in separate tabs.
* **Host Bash/curl:** reproduce the captured method/path/headers. Replace Bearer authentication if the app uses cookies or signed requests.
	* ```bash
		curl -i --proxy 'http://127.0.0.1:8080' --cacert '<burp-ca.pem>' 'https://<api-host>/<owned-record-path>' -H 'Authorization: Bearer <account-A-access-token>'
		curl -i --proxy 'http://127.0.0.1:8080' --cacert '<burp-ca.pem>' 'https://<api-host>/<account-B-record-path>' -H 'Authorization: Bearer <account-A-access-token>'
		curl -i --proxy 'http://127.0.0.1:8080' --cacert '<burp-ca.pem>' 'https://<api-host>/<owned-record-path>'
		```
* **Replay captured JSON:** copy the actual content type, request body, and required headers from Burp; send an unchanged control before editing one field.
	* ```bash
		curl -i 'https://<api-host>/<observed-endpoint>' -H 'Authorization: Bearer <test-access-token>' -H 'Content-Type: application/json' --data-binary '@<captured-test-body.json>'
		```
* **Observed token endpoint:** replay the captured refresh grant after logout, token rotation, or session revocation; keep the actual client-authentication requirements.
	* ```bash
		curl -i 'https://<auth-host>/<token-endpoint>' --data-urlencode 'grant_type=refresh_token' --data-urlencode 'refresh_token=<test-refresh-token>' --data-urlencode 'client_id=<observed-client-id>'
		```
## Native Identity and Purchase Tests

* **OAuth callback:** use the existing [URL launch commands](client-side-testing.md#deep-links-and-url-handling) with the actual callback route. Test one callback at a time against fresh login transactions.
	* ```text
		demo://oauth/callback?code=REPLACE_UNUSED_CODE&state=wrong-state
		demo://oauth/callback?code=REPLACE_UNUSED_CODE
		demo://oauth/callback?code=REPLACE_UNUSED_CODE&state=REPLACE_CURRENT_STATE&state=wrong-state
		```
* **PKCE, macOS curl:** try a wrong verifier, an omitted verifier and the correct verifier with separate unused codes. Then replay a successfully redeemed code and change client ID/redirect independently. Preserve the observed client-authentication requirements.
	* ```bash
		curl -i 'https://auth.example/token' --data-urlencode 'grant_type=authorization_code' --data-urlencode 'client_id=REPLACE_CLIENT_ID' --data-urlencode 'redirect_uri=REPLACE_CALLBACK' --data-urlencode 'code=REPLACE_UNUSED_CODE' --data-urlencode 'code_verifier=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
		```
* **Confirm:** the client rejects wrong state; the server rejects wrong/missing verifier, wrong client/callback and code replay. A stale/used code rejection alone does not isolate those checks. [PKCE flow](../../../web/vulnerabilities/oauth-2.0.md#authorization-code-flow-with-pkce).
* **Sign in with Apple/OIDC:** send A's genuine token/code through B's app login transaction; separately test a token for another test client/audience. Change client-supplied email/account fields without changing the token. Confirm the backend account from the established session. Signature, audience, issuer, nonce and account mapping must be checked at the actual token-consumer endpoint; [JWT variants](../../../web/vulnerabilities/jwt-attacks.md).
* **Passkeys:** replay one complete authentication response, then try it after challenge expiry and against B's active challenge. Change claimed account/credential ID independently while retaining A's signed response. Wrong origin/RP hash or UV tests require a test authenticator producing valid signatures for those variants, not just edited signed bytes.
* **StoreKit:** use a genuine StoreKit sandbox transaction/receipt from A. Submit unchanged as B, substitute only the claimed product ID, replay the same transaction, then retest after refund/revocation. Use the actual backend receipt/transaction field, not a locally fabricated success callback.
	* ```json
		{"signedTransactionInfo":"REPLACE_A_SANDBOX_JWS","productId":"REPLACE_OBSERVED_PRODUCT"}
		```
* **Confirm:** B receives A's entitlement, an unrelated product is granted, or a nonrepeatable purchase is credited twice. Check the actual entitlement operation and provider state; echoed JSON or a local success screen is insufficient.

## Server TLS Check

* **TLS server check:** requires host OpenSSL; app trust/pinning is tested separately through the instrumented app.
	* ```bash
		openssl s_client -connect '<api-host>:443' -servername '<api-host>' -verify_hostname '<api-host>' -verify_return_error </dev/null
		```
