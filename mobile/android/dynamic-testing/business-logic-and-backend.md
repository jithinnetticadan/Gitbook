# Business Logic and Backend Trust

{% hint style="warning" %}
* **Prerequisites:** test tenants/accounts, sandbox payments, synthetic balances, and reversible records.
* Agree on concurrency and rate-limit budgets.
* Do not generate real ad traffic, rewards, purchases, referrals, or production charges.
{% endhint %}

## Establish the Authority

* Identify the decision-maker: local state, platform service, backend, or payment provider.
* Capture an authorized control; change one client-controlled input and verify the actual entitlement/data/action.
* UI changes alone do not prove server impact.
* Assess local/offline protections against their own security requirements.

| Decision / Input                      | Test                                                                                                    | Confirm                                                                                                                                  |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Premium/admin/feature flags           | Change an observed local gate in a disposable build/session; repeat the protected operation             | Whether enforcement exists at the actual resource boundary, not just the screen.                                                         |
| Price / quantity / currency           | Modify a sandbox checkout request for an owned item                                                     | Server derives authoritative price/discount and validates range, currency, quantity, and ownership.                                      |
| Purchase receipts / tokens            | Replay an owned sandbox purchase, substitute product/account, and test pending/canceled/refunded states | Backend validates purchase with the store/provider and binds product, package, user, state, and uniqueness before granting entitlement.  |
| Billing callbacks / test products     | Alter only a lab callback or use supported license-tester flows                                         | A callback or signature Boolean is not proof of settlement. Legacy `android.test.*` SKUs are not a universal modern Billing test method. |
| Trials / reinstall / device IDs       | Compare approved reinstall/reset scenarios and a second test identity                                   | Policy is enforced at the intended account/resource boundary; device IDs alone are not reliable proof of a unique person.                |
| Device clock / expiry                 | Change time on a disposable device and repeat a scoped expiry-sensitive action                          | Distinguish app clock checks, server time, cached grace periods, and unrelated TLS/date failures.                                        |
| Offline mode                          | Disconnect at defined points, act on synthetic data, then reconnect                                     | Offline permission, expiry/grace policy, replay, and server reconciliation preserve the intended invariant.                              |
| Save files / in-app balances / scores | Change only a test save/record or sandbox submission                                                    | Verify server validation and cross-user impact; editing one's offline game state is not automatically a security vulnerability.          |
| License Verification Library          | Trace LVL result handling and cached licensing policy                                                   | Treat a legacy client gate separately from server entitlement; confirm whether this flow is still deployed.                              |
| Referral / ad / achievement events    | Use provider sandbox/test mode and owned identities                                                     | Uniqueness, replay resistance, eligibility, and server verification; avoid billing or telemetry contamination.                           |
| Sync races / duplicate action         | Send a small agreed concurrent/retry set against test state                                             | Atomic updates, idempotency, and ownership prevent duplicate credit/debit or stale-state authorization.                                  |
| Force-update / kill switch            | Test a supported old client/request against the approved environment                                    | Determine whether the policy is a local usability gate or a server-enforced security requirement.                                        |

* Google Play references: [secure Billing integration](https://developer.android.com/google/play/billing/security), supported [Billing tests](https://developer.android.com/google/play/billing/test).
* No visible app-side verification call does not prove missing backend verification; obtain backend evidence where needed.

## Request Signing and Replay

1. Identify the actual request signature header/body and trace its producer through Java, managed code, platform service, or JNI. Failure to find a Java key does not by itself prove native storage.
2. Establish key origin and scope: public app-wide embedded secret, per-install key, authenticated server provisioning, or non-exportable signing key. Observe only test data and redact key material.
3. Determine what is signed: method, path, canonical query/body, account/session, timestamp/nonce, and action. Test one harmless field mismatch or replay at a time.
4. Confirm backend verification and binding. A strong MAC over attacker-chosen fields may still leave an authorization gap; a client-wide extractable secret cannot reliably attest genuine app execution.
5. Assess freshness/idempotency for the operation. Repeating a read request or lacking an explicit nonce is not automatically a replay vulnerability; demonstrate an unintended accepted state change.

* Trace implementation with [Java/native instrumentation](java-and-native-instrumentation.md) and [crypto provenance](authentication-and-cryptography.md#trace-cryptographic-data-flow).
* Plaintext at `Cipher.doFinal` does not automatically reveal the key or bypass server request verification.

## Mobile Backend Variants

| Variant                                 | Scoped Comparison                                                                                   | Avoid Overclaiming                                                                                                                             |
| --------------------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Mobile User-Agent / app version headers | Replay a known request with an alternate test header                                                | Header-based routing is not authentication; reaching a public route alone is not a bypass.                                                     |
| Legacy API versions                     | Compare known supported `/v1`/`/v2` or owner-documented versions                                    | Confirm equivalent authorization and validation; do not assume every guessed version is in scope.                                              |
| Device fingerprints / abuse controls    | Vary one test install/device identifier within agreed limits                                        | Verify whether account/session/transaction controls compensate; do not infer a missing control from the absence of `429`.                      |
| IP / locale / location policy           | Use explicitly approved locations/test routes and synthetic signals                                 | Determine whether the requirement is regulatory, fraud-related, or presentation only; do not bypass legal restrictions without explicit scope. |
| Rate-limit dimensions                   | Compare small approved tests across account, token, device, and source                              | One global dimension is not automatically wrong. Do not use distributed proxies or uncontrolled guessing.                                      |
| JWT / OAuth / magic links               | Verify signature, audience, redirect, PKCE, expiry, account/action binding                          | Use [authentication tests](authentication-and-cryptography.md); native-app "origin" is not a universal server-authentication mechanism.        |
| Pinning versus mTLS                     | Identify server-authentication pinning, client certificates, and application credentials separately | Pinning is normally client-side. It does not imply mTLS, and the lack of client certificates is not itself a flaw.                             |

* Record requests/responses, identity/role, and test state before/after.
* State signing/instrumentation prerequisites and the demonstrated server/local boundary.
* Troubleshooting: [Troubleshooting and Test Cleanup](validation-and-troubleshooting.md).
