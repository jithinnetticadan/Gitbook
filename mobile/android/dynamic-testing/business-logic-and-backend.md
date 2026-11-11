# Business Logic and Backend Trust

## Establish the Authority

* Identify the decision-maker: local state, platform service, backend, or payment provider.
* Capture an authorized control; change one client-controlled input and verify the actual entitlement/data/action.
* UI changes alone do not prove server impact.
* Assess local/offline protections against their own security requirements.

<table><thead><tr><th width="173">Decision / Input</th><th width="293.0001220703125">Test</th><th>Confirm</th></tr></thead><tbody><tr><td>Premium/admin/feature flags</td><td>Change an observed local gate in a disposable build/session; repeat the protected operation</td><td>Whether enforcement exists at the actual resource boundary, not just the screen.</td></tr><tr><td>Price / quantity / currency</td><td>Modify a sandbox checkout request for an owned item</td><td>Server derives authoritative price/discount and validates range, currency, quantity, and ownership.</td></tr><tr><td>Purchase receipts / tokens</td><td>Replay an owned sandbox purchase, substitute product/account, and test pending/canceled/refunded states</td><td>Backend validates purchase with the store/provider and binds product, package, user, state, and uniqueness before granting entitlement.</td></tr><tr><td>Billing callbacks / test products</td><td>Alter only a lab callback or use supported license-tester flows</td><td>A callback or signature Boolean is not proof of settlement. Legacy <code>android.test.*</code> SKUs are not a universal modern Billing test method.</td></tr><tr><td>Trials / reinstall / device IDs</td><td>Compare approved reinstall/reset scenarios and a second test identity</td><td>Policy is enforced at the intended account/resource boundary; device IDs alone are not reliable proof of a unique person.</td></tr><tr><td>Device clock / expiry</td><td>Change time on a disposable device and repeat a scoped expiry-sensitive action</td><td>Distinguish app clock checks, server time, cached grace periods, and unrelated TLS/date failures.</td></tr><tr><td>Offline mode</td><td>Disconnect at defined points, act on synthetic data, then reconnect</td><td>Offline permission, expiry/grace policy, replay, and server reconciliation preserve the intended invariant.</td></tr><tr><td>Save files / in-app balances / scores</td><td>Change only a test save/record or sandbox submission</td><td>Verify server validation and cross-user impact; editing one's offline game state is not automatically a security vulnerability.</td></tr><tr><td>License Verification Library</td><td>Trace LVL result handling and cached licensing policy</td><td>Treat a legacy client gate separately from server entitlement; confirm whether this flow is still deployed.</td></tr><tr><td>Referral / ad / achievement events</td><td>Use provider sandbox/test mode and owned identities</td><td>Uniqueness, replay resistance, eligibility, and server verification; avoid billing or telemetry contamination.</td></tr><tr><td>Sync races / duplicate action</td><td>Send a small agreed concurrent/retry set against test state</td><td>Atomic updates, idempotency, and ownership prevent duplicate credit/debit or stale-state authorization.</td></tr><tr><td>Force-update / kill switch</td><td>Test a supported old client/request against the approved environment</td><td>Determine whether the policy is a local usability gate or a server-enforced security requirement.</td></tr></tbody></table>

* Google Play references: [secure Billing integration](https://developer.android.com/google/play/billing/security), supported [Billing tests](https://developer.android.com/google/play/billing/test).

## Request Signing and Replay

### Purchase, Receipt, and Local-Gate Recipes

* **Checkout:** in the actual sandbox request, change one observed field at a time. These are individual field substitutions, not complete requests; keep SKU, account and other fields unchanged for the price/range tests.
	* ```json
		{"unitPrice": 0.01}
		```
	* ```json
		{"quantity": -1}
		```
	* ```json
		{"currency": "REPLACE_DIFFERENT_SUPPORTED_CURRENCY"}
		```
* **Confirm:** inspect the resulting order total, entitlement and provider transaction, not just an echoed request value. Server recalculation/rejection is expected; a free/underpriced completed sandbox entitlement establishes the flaw.
* **Receipt binding:** submit A's genuine sandbox purchase token once as A, then unchanged as B; separately substitute only the product ID. Repeat the original token after first redemption and after a provider-confirmed refund/cancellation. Keep package/store/environment fields consistent unless testing them individually.
	* ```json
		{"purchaseToken":"REPLACE_A_SANDBOX_TOKEN","productId":"REPLACE_PRODUCT_ID"}
		```
* **Confirm:** B receives A's entitlement, a token for a cheaper product grants another product, or the same purchase grants a nonrepeatable entitlement twice. A token accepted while the order remains pending is meaningful only if the protected entitlement is already usable.
* **Local gate:** locate the real Boolean-returning method and signature, then use a targeted Frida return override; substitute an existing entitlement operation, not a fictional API.
	* ```javascript
		Java.perform(function () {
		    const Gate = Java.use('REPLACE_GATE_CLASS');
		    const check = Gate.REPLACE_BOOLEAN_METHOD.overload();
		    check.implementation = function () { return true; };
		});
		```
* **Confirm:** perform the protected action after the hook. An unlocked menu with a denied backend operation proves only a local UI gate was bypassed; an offline feature can still have a real local entitlement boundary.

### Signed-Request Mutation Matrix

* Use the existing [request replay template](authentication-and-cryptography.md#captured-request-replay). For each row, begin with a new valid control request and keep its signature unchanged unless the test specifically obtains a new signature.

| Mutation | Test | Confirm |
| --- | --- | --- |
| Body | Change one amount/object/account field after signing | Server accepts a changed protected action despite the mismatched body. |
| Path/query | Substitute B's known object ID after signing | Signature is not bound to the selected resource and authorization also permits the cross-account action. |
| Identity | Use A's signed request with B's session, then reverse | Unintended identity/transaction association; not merely B receiving B's data. |
| Freshness | Replay exactly, then replay beyond the accepted timestamp window | Nonrepeatable state change commits again or a stated expiry is bypassed. |
| Idempotency | Repeat with the same key; then change only the key | Compare committed operations; changing a client key must not bypass purchase/receipt uniqueness. |

* A MAC/checksum that is intentionally only corruption detection need not enforce authentication. Determine the signature's actual contract before interpreting the result.

* **Replay:** use the [captured JSON request template](authentication-and-cryptography.md#captured-request-replay) for each observed checkout, receipt, balance, or feature endpoint; edit its actual fields rather than generic guessed names.
* **Offline/network transitions, ADB:** run each state separately and repeat the same app operation.
	* ```bash
		adb shell svc wifi disable
		adb shell svc data disable
		adb shell svc wifi enable
		adb shell svc data enable
		```
* Cellular commands require a supported device/radio; emulator Ethernet or VPN routes may keep connectivity active.

1. Identify the actual request signature header/body and trace its producer through Java, managed code, platform service, or JNI. Failure to find a Java key does not by itself prove native storage.
2. Establish key origin and scope: public app-wide embedded secret, per-install key, authenticated server provisioning, or non-exportable signing key.
3. Determine what is signed: method, path, canonical query/body, account/session, timestamp/nonce, and action. Test one harmless field mismatch or replay at a time.
4. Confirm backend verification and binding. A strong MAC over attacker-chosen fields may still leave an authorization gap; a client-wide extractable secret cannot reliably attest genuine app execution.
5. Assess freshness/idempotency for the operation. Repeating a read request or lacking an explicit nonce is not automatically a replay vulnerability; demonstrate an unintended accepted state change.

* Trace implementation with [Java/native instrumentation](java-and-native-instrumentation.md) and [crypto provenance](authentication-and-cryptography.md#trace-cryptographic-data-flow).
* Plaintext at `Cipher.doFinal` does not automatically reveal the key or bypass server request verification.

## Mobile Backend Variants

<table><thead><tr><th width="153.000244140625">Variant</th><th>Scoped Comparison</th><th>Avoid Overclaiming</th></tr></thead><tbody><tr><td>Mobile User-Agent / app version headers</td><td>Replay a known request with an alternate test header</td><td>Header-based routing is not authentication; reaching a public route alone is not a bypass.</td></tr><tr><td>Legacy API versions</td><td>Compare known supported <code>/v1</code>/<code>/v2</code> or owner-documented versions</td><td>Confirm equivalent authorization and validation; do not assume every guessed version is in scope.</td></tr><tr><td>Device fingerprints / abuse controls</td><td>Vary one test install/device identifier within agreed limits</td><td>Verify whether account/session/transaction controls compensate; do not infer a missing control from the absence of <code>429</code>.</td></tr><tr><td>IP / locale / location policy</td><td>Use explicitly approved locations/test routes and synthetic signals</td><td>Determine whether the requirement is regulatory, fraud-related, or presentation only; do not bypass legal restrictions without explicit scope.</td></tr><tr><td>Rate-limit dimensions</td><td>Compare small approved tests across account, token, device, and source</td><td>One global dimension is not automatically wrong. Do not use distributed proxies or uncontrolled guessing.</td></tr><tr><td>JWT / OAuth / magic links</td><td>Verify signature, audience, redirect, PKCE, expiry, account/action binding</td><td>Use <a href="authentication-and-cryptography.md">authentication tests</a>; native-app "origin" is not a universal server-authentication mechanism.</td></tr><tr><td>Pinning versus mTLS</td><td>Identify server-authentication pinning, client certificates, and application credentials separately</td><td>Pinning is normally client-side. It does not imply mTLS, and the lack of client certificates is not itself a flaw.</td></tr></tbody></table>

* Record requests/responses, identity/role, and test state before/after.
* State signing/instrumentation prerequisites and the demonstrated server/local boundary.
* Troubleshooting: [Testing and Troubleshooting](validation-and-troubleshooting.md).
