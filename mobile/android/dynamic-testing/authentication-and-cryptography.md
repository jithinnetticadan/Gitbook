# Authentication, Authorization, and Cryptography

{% hint style="info" %}
Use disposable accounts and owned records. Agree on rate-limit/lockout budgets before testing. Record the normal flow first; obtain network visibility through [Network Traffic and TLS](network-traffic-and-tls.md) when assessing API controls.
{% endhint %}

## Authentication and Session Matrix

Capture a successful control request, then vary one condition at a time. Distinguish access tokens, refresh tokens, cookies, local session flags, and cached responses. Keep secrets out of shared reports and shell history.

| Test | Controlled Action | Verify |
| --- | --- | --- |
| Logout | Capture an authenticated request, log out normally, then replay it and separately attempt refresh. | Protected data/action is denied according to the session policy; record any allowed access-token lifetime/revocation delay. |
| Expiry | Reuse the test token after its intended expiry; assess refresh separately. | Server-enforced expiry and rotation, not merely a UI timer or decoded JWT claim. |
| Password reset | Use a token for its intended account, then try one reuse and a different owned account/session. | Expiry, one-time use, account binding, and required session invalidation. Some reset links intentionally work in a new browser session. |
| Password change / session revocation | Change the test password or revoke a session; repeat a protected action from a second test session. | Behavior matches documented policy, including refresh-token invalidation. |
| OTP / MFA | Try wrong, expired, previously used, and wrong-account challenges within the agreed attempt budget. | Challenge/account/transaction binding, server-side limits, and no protected action with only a pre-MFA session. |
| Account switching | Switch A to B, restart, refresh, and follow a sensitive link. | B cannot inherit A's cookies, cached data, object permissions, or refresh context. |
| Recovery / fallback | Exercise approved alternate MFA, biometric fallback, and recovery paths. | A weaker path does not bypass the intended authentication requirement. |

An HTTP `200` may carry an error or public/cached content. Verify protected data or a harmless authorized test action to establish replay impact. Missing `429` alone does not prove missing rate limits: delays, challenge invalidation, lockouts, and body-level errors may enforce them. Do not perform uncontrolled OTP guessing.

### OAuth, Identity Tokens, and Passkeys

| Flow | Test | Expected Boundary |
| --- | --- | --- |
| Native OAuth | External browser/Custom Tabs, exact redirect registration, PKCE `S256`, state and issuer/session binding | Verify the authorization server rejects an incorrect verifier/redirect and prevents code replay; absence of a visible parameter alone is not an account-takeover proof. |
| Callback handler | Competing custom-scheme handler, verified App Links, duplicate/missing parameters, account context | A captured code may still be unusable without its PKCE verifier; demonstrate the protected result under controlled accounts. |
| Google Sign-In / other OIDC | Backend ID-token signature, trusted issuer, audience, expiry and nonce when required; minimal scopes | A decoded token or client-supplied email is not authenticated identity. ID tokens and API access tokens have different intended uses. |
| JWT access tokens | Allowed algorithms, signature/key selection, issuer/audience, expiry, token type | Test approved malformed/tampered tokens against a harmless endpoint; a parser accepting `alg:none` is not a flaw unless the verifier accepts it as authenticated. |
| Credential Manager / passkeys | Registration/assertion challenge, RP ID, expected Android/web origin, signature, user verification policy, credential/account binding | Verify challenge freshness and wrong-account/wrong-origin rejection on the server. Availability depends on OS/provider/library versions, not only Android 14+. |
| Session fixation / remember-me | Supplied session values in links, rotation at login/privilege change, long-lived token revocation | Verify that a known pre-auth session cannot become someone else's authenticated session; persistence and lack of device binding need policy/context. |
| Reinstall / restore / silent login | Disposable reinstall and supported restore with known test credentials | Identify whether backup, account services, browser SSO, or device identifiers restore access; distinguish expected SSO from unauthorized session resurrection. |

Prefer an external user-agent for native OAuth per [RFC 8252](https://www.rfc-editor.org/rfc/rfc8252). An embedded WebView is a design concern, not automatic evidence of credential theft. For passkeys, inspect the actual provider and [Credential Manager integration](https://developer.android.com/identity/sign-in/credential-manager); do not infer account security from the UI alone.

## Horizontal and Vertical Authorization

1. Create two normal test accounts, A and B, with separate owned objects. Add an authorized lower/higher-role pair when available.
2. Record A accessing A's object and B accessing B's object as controls.
3. With A's unchanged session, substitute only B's known object identifier in one request. Check the response content or reversible test-state change; stop after proving the boundary failure.
4. Repeat relevant read/write/export/list operations and tenant boundaries within scope. Do not enumerate unrelated users' identifiers.
5. Replay a higher-role operation with the lower-role session. Hiding a button, launching an internal activity, or changing a local `isAdmin` flag is not proof of server privilege escalation.

Classify horizontal BOLA/IDOR versus vertical function-level authorization. For a local-only feature, validate the local protected data/action; a server is not required for a real local security issue.

## Biometrics and Auth-Bound Keystore

Treat callback/UI state, key authorization, and server authorization as separate controls.

1. Identify the concrete AndroidX/platform `BiometricPrompt` callback or legacy fingerprint path. Observe success, failure, cancellation, fallback, and exception handling without replacing them initially.
2. Trace whether the operation uses a `CryptoObject` containing a `Cipher`, `Signature`, or `Mac`, or a time-window-based auth-bound key. Missing `CryptoObject` alone does not prove a bypass.
3. Review the actual key generation/import policy: alias/provider, `setUserAuthenticationRequired`, allowed authenticators, per-use versus time-window authorization, and enrollment/device-lock invalidation rules.
4. On a disposable setup, attempt the protected operation after cancellation, failed authentication, and expiry of the permitted authentication window. Test enrollment/device-lock changes only when explicitly approved; they can invalidate keys.
5. If assessing callback manipulation, target the actual app callback and validate the subsequent decryption/signing or protected operation. A hook that merely logs/replaces the success callback body does not cause authentication success and may break the app.
6. Confirm any claimed server-side impact with the server result. For offline data, demonstrate unauthorized access to the protected local data instead.

Use `KeyInfo` security-level information where supported and key attestation when required to establish backing, not the provider name alone. A successful UI transition or swallowed exception does not prove that a hardware-backed key was used without authorization. Root access does not automatically expose keys inside a TEE/StrongBox. See [Android Keystore](https://developer.android.com/privacy-and-security/keystore) and [biometric authentication](https://developer.android.com/identity/sign-in/biometric-auth).

Enumerate the app-accessible Keystore aliases/types/providers through its own UID context, then inspect the policy of keys actually used by the sensitive operation. Enumeration does not grant access to every app's keys. Assess `BIOMETRIC_WEAK` versus `BIOMETRIC_STRONG` and device-credential fallback against the required assurance; hardware key authorization constrains supported authenticators. Verify enrollment-invalidation behavior under the configured auth policy rather than reporting a missing explicit setter as a flaw.

## Trace Cryptographic Data Flow

Map input > encoding/serialization > key source/derivation > algorithm/mode/IV/nonce > output > consumer/storage. Determine whether the operation protects a real secret, verifies integrity, or is merely a non-security checksum.

| Observation Point | Record | Check |
| --- | --- | --- |
| `SecretKeySpec`, KDF, or key import | Origin, derivation parameters, scope/lifetime, and caller | Trace bytes back to constants, storage, generation, or network; unchanged bytes alone do not prove hardcoding. |
| `KeyGenerator`, `KeyPairGenerator`, Keystore | Provider, alias, purposes, auth policy, backing | Whether key export/use is possible under the stated attacker capability. |
| `Cipher.getInstance`, `init`, `update`, `doFinal` | Transformation, operation, key identity, IV/nonce, AAD, input/output | Same-key nonce reuse, integrity validation, mode misuse, and error handling in the actual flow. |
| `SecureRandom` / other RNG | Generator, seeding and security-sensitive use | Repeatability is a clue, not proof of predictability; assess entropy and use. |
| Encoders / hashes | Base64/hex/compression/digest and downstream use | Encoding is not encryption; a weak digest used for a cache key is not equivalent to password hashing. |

The following observational template logs metadata for only `Cipher.doFinal(byte[])`. It does not dump keys or plaintext and does not cover streaming/no-argument overloads or native crypto:

```javascript
Java.perform(function () {
    const Cipher = Java.use('javax.crypto.Cipher');
    const doFinal = Cipher.doFinal.overload('[B');
    doFinal.implementation = function (input) {
        const output = doFinal.call(this, input);
        console.log(this.getAlgorithm().toString() +
            ' inputBytes=' + (input === null ? 0 : input.length) +
            ' outputBytes=' + (output === null ? 0 : output.length));
        return output;
    };
});
```

Correlate specific cipher instances, `init` parameters, and consumers using synthetic test data. Capture additional values only when necessary and protect those artifacts. Compare repeated operations under the **same key**, app restarts, and account changes. Changing keys between sessions does not prove server origin; `getEncoded()` returning null may reflect a non-exportable key, not an analysis failure.

Report cryptographic weaknesses with the relevant key access, message control, and impact. Seeing plaintext in process memory during legitimate use alone is not a cryptographic break. Use [local data lifecycle testing](local-data-logs-and-privacy.md) to assess retention and exposure.

**Related:** [Java and Native Instrumentation](java-and-native-instrumentation.md) | [Component Testing](component-testing.md)

**Previous:** [Network Traffic and TLS](network-traffic-and-tls.md) | **Next:** [Business Logic and Backend Trust](business-logic-and-backend.md)