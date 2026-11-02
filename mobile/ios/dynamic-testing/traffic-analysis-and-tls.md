# Network Traffic and TLS

## Proxy Setup

1. Bind Burp to the device-reachable lab host IP/port.
2. Set the iPhone Wi-Fi proxy to that address. `127.0.0.1` on the phone is **not the proxy host**.
3. Open `http://burp`; install the CA under VPN & Device Management.
4. Enable trust: General > About > Certificate Trust Settings (labels vary).
5. Test API authentication, authorization, inputs, sensitive data, and server behavior.
6. Confirm the app's CA trust separately from pinning.
7. Follow the current [PortSwigger iOS proxy setup](https://portswigger.net/burp/documentation/desktop/mobile/config-ios-device)

## Pinning Checks

* **Objection:** [pinning command](runtime-instrumentation.md#classes-and-hooks) or [startup hook](runtime-instrumentation.md#startup-hooks).
* [SSL Kill Switch 2](https://github.com/nabla-c0d3/ssl-kill-switch2) / [3](https://github.com/NyaMisty/ssl-kill-switch3/releases): compatible jailbroken devices only.
* AppSync alters code-signing behavior; it does **not** replace CA trust configuration.
* For Objection session syntax and startup hooks, see [Runtime Instrumentation](runtime-instrumentation.md).

## Captured-Request Replay

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
* **TLS server check:** requires host OpenSSL; app trust/pinning is tested separately through the instrumented app.
	* ```bash
		openssl s_client -connect '<api-host>:443' -servername '<api-host>' -verify_hostname '<api-host>' -verify_return_error </dev/null
		```
