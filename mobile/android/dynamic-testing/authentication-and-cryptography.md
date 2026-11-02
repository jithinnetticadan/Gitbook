# Authentication, Authorization, and Cryptography

## Authentication and Session Matrix

* Capture a successful control request; vary one condition at a time.
* Distinguish access tokens, refresh tokens, cookies, local session flags, and cached responses.

<table><thead><tr><th width="117">Test</th><th>Controlled Action</th><th>Verify</th></tr></thead><tbody><tr><td>Logout</td><td>Capture an authenticated request, log out normally, then replay it and separately attempt refresh.</td><td>Protected data/action is denied according to the session policy; record any allowed access-token lifetime/revocation delay.</td></tr><tr><td>Expiry</td><td>Reuse the test token after its intended expiry; assess refresh separately.</td><td>Server-enforced expiry and rotation, not merely a UI timer or decoded JWT claim.</td></tr><tr><td>Password reset</td><td>Use a token for its intended account, then try one reuse and a different owned account/session.</td><td>Expiry, one-time use, account binding, and required session invalidation. Some reset links intentionally work in a new browser session.</td></tr><tr><td>Password change / session revocation</td><td>Change the test password or revoke a session; repeat a protected action from a second test session.</td><td>Behavior matches documented policy, including refresh-token invalidation.</td></tr><tr><td>OTP / MFA</td><td>Try wrong, expired, previously used, and wrong-account challenges within the agreed attempt budget.</td><td>Challenge/account/transaction binding, server-side limits, and no protected action with only a pre-MFA session.</td></tr><tr><td>Account switching</td><td>Switch A to B, restart, refresh, and follow a sensitive link.</td><td>B cannot inherit A's cookies, cached data, object permissions, or refresh context.</td></tr><tr><td>Recovery / fallback</td><td>Exercise approved alternate MFA, biometric fallback, and recovery paths.</td><td>A weaker path does not bypass the intended authentication requirement.</td></tr></tbody></table>

### OAuth, Identity Tokens, and Passkeys

<table><thead><tr><th width="160.9998779296875">Flow</th><th>Test</th><th>Expected Boundary</th></tr></thead><tbody><tr><td>Native OAuth</td><td>External browser/Custom Tabs, exact redirect registration, PKCE <code>S256</code>, state and issuer/session binding</td><td>Verify the authorization server rejects an incorrect verifier/redirect and prevents code replay; absence of a visible parameter alone is not an account-takeover proof.</td></tr><tr><td>Callback handler</td><td>Competing custom-scheme handler, verified App Links, duplicate/missing parameters, account context</td><td>A captured code may still be unusable without its PKCE verifier; demonstrate the protected result under controlled accounts.</td></tr><tr><td>Google Sign-In / other OIDC</td><td>Backend ID-token signature, trusted issuer, audience, expiry and nonce when required; minimal scopes</td><td>A decoded token or client-supplied email is not authenticated identity. ID tokens and API access tokens have different intended uses.</td></tr><tr><td>JWT access tokens</td><td>Allowed algorithms, signature/key selection, issuer/audience, expiry, token type</td><td>Test approved malformed/tampered tokens against a harmless endpoint; a parser accepting <code>alg:none</code> is not a flaw unless the verifier accepts it as authenticated.</td></tr><tr><td>Credential Manager / passkeys</td><td>Registration/assertion challenge, RP ID, expected Android/web origin, signature, user verification policy, credential/account binding</td><td>Verify challenge freshness and wrong-account/wrong-origin rejection on the server. Availability depends on OS/provider/library versions, not only Android 14+.</td></tr><tr><td>Session fixation / remember-me</td><td>Supplied session values in links, rotation at login/privilege change, long-lived token revocation</td><td>Verify that a known pre-auth session cannot become someone else's authenticated session; persistence and lack of device binding need policy/context.</td></tr><tr><td>Reinstall / restore / silent login</td><td>Disposable reinstall and supported restore with known test credentials</td><td>Identify whether backup, account services, browser SSO, or device identifiers restore access; distinguish expected SSO from unauthorized session resurrection.</td></tr></tbody></table>

* Prefer an external user-agent for native OAuth: [RFC 8252](https://www.rfc-editor.org/rfc/rfc8252).
* An embedded WebView is a design concern, not proof of credential theft.
* For passkeys, inspect the provider and [Credential Manager integration](https://developer.android.com/identity/sign-in/credential-manager); UI appearance alone does not establish account security.

### Captured-Request Replay

* **Host Bash/curl:** use the captured URL and authentication format; compare the response body and record ownership.
    * ```bash
        curl -i --proxy 'http://127.0.0.1:8080' --cacert '<burp-ca.pem>' 'https://<api-host>/<owned-record-path>' -H 'Authorization: Bearer <account-A-access-token>'
        curl -i --proxy 'http://127.0.0.1:8080' --cacert '<burp-ca.pem>' 'https://<api-host>/<account-B-record-path>' -H 'Authorization: Bearer <account-A-access-token>'
        curl -i --proxy 'http://127.0.0.1:8080' --cacert '<burp-ca.pem>' 'https://<api-host>/<owned-record-path>'
        ```
* Replay the first request again after logout/expiry with the original token. For cookie sessions, use the captured Cookie header instead of Bearer authentication.
* **Observed refresh endpoint:** substitute its actual parameter names and client-auth requirements.
    * ```bash
        curl -i 'https://<auth-host>/<token-endpoint>' --data-urlencode 'grant_type=refresh_token' --data-urlencode 'refresh_token=<test-refresh-token>' --data-urlencode 'client_id=<observed-client-id>'
        ```
* **OTP/reset/transaction body:** edit one captured JSON field in Burp Repeater or a local test body file; retain the captured method and required headers.
    * ```bash
        curl -i 'https://<api-host>/<observed-endpoint>' -H 'Authorization: Bearer <test-access-token>' -H 'Content-Type: application/json' --data-binary '@<captured-test-body.json>'
        ```

## Horizontal and Vertical Authorization

1. Create two normal test accounts, A and B, with separate owned objects. Add an authorized lower/higher-role pair when available.
2. Record A accessing A's object and B accessing B's object as controls.
3. With A's unchanged session, substitute only B's known object identifier in one request. Check the response content or reversible test-state change; stop after proving the boundary failure.
4. Repeat relevant read/write/export/list operations and tenant boundaries within scope. Do not enumerate unrelated users' identifiers.
5. Replay a higher-role operation with the lower-role session. Hiding a button, launching an internal activity, or changing a local `isAdmin` flag is not proof of server privilege escalation.

* Distinguish horizontal BOLA/IDOR from vertical function-level authorization failures.
* For local-only features, validate the protected data/action; a server is not required for a real local security issue.

## Biometrics and Auth-Bound Keystore

* **Inside Objection:** [Keystore commands](objection-and-runtime-instrumentation.md#keystore-and-device-checks). For concrete callback implementations, use the [class/method watcher](objection-and-runtime-instrumentation.md#classes-and-hooks) with the observed callback class.
* **Frida Java script:** enumerate key policy in the current app UID; Android 6+ for `KeyInfo`, Android 12+ for `getSecurityLevel()`.
  * ```javascript
    Java.perform(function () {
        const KeyStore = Java.use('java.security.KeyStore');
        const KeyInfo = Java.use('android.security.keystore.KeyInfo');
        const SecretKey = Java.use('javax.crypto.SecretKey');
        const SecretKeyFactory = Java.use('javax.crypto.SecretKeyFactory');
        const KeyFactory = Java.use('java.security.KeyFactory');
        const store = KeyStore.getInstance('AndroidKeyStore');
        store.load(null);
        const aliases = store.aliases();
        while (aliases.hasMoreElements()) {
            const alias = aliases.nextElement().toString();
            try {
                const key = store.getKey(alias, null);
                if (key === null) continue;
                const factory = SecretKey.class.isInstance(key)
                    ? SecretKeyFactory.getInstance(key.getAlgorithm(), 'AndroidKeyStore')
                    : KeyFactory.getInstance(key.getAlgorithm(), 'AndroidKeyStore');
                const info = Java.cast(factory.getKeySpec(key, KeyInfo.class), KeyInfo);
                console.log(JSON.stringify({ alias: alias, algorithm: key.getAlgorithm().toString(),
                    authRequired: info.isUserAuthenticationRequired(),
                    authSeconds: info.getUserAuthenticationValidityDurationSeconds(),
                    backing: info.getSecurityLevel ? info.getSecurityLevel() : info.isInsideSecureHardware() }));
            } catch (error) {
                console.log(alias + ': ' + error);
            }
        }
    });
    ```

1. Identify the concrete AndroidX/platform `BiometricPrompt` callback or legacy fingerprint path. Observe success, failure, cancellation, fallback, and exception handling without replacing them initially.
2. Trace whether the operation uses a `CryptoObject` containing a `Cipher`, `Signature`, or `Mac`, or a time-window-based auth-bound key. Missing `CryptoObject` alone does not prove a bypass.
3. Review the actual key generation/import policy: alias/provider, `setUserAuthenticationRequired`, allowed authenticators, per-use versus time-window authorization, and enrollment/device-lock invalidation rules.
4. Attempt the protected operation after cancellation, failed authentication, and expiry of the authentication window. Compare enrollment/device-lock changes with the key's configured invalidation policy.
5. If assessing callback manipulation, target the actual app callback and validate the subsequent decryption/signing or protected operation. A hook that merely logs/replaces the success callback body does not cause authentication success and may break the app.
6. Confirm any claimed server-side impact with the server result. For offline data, demonstrate unauthorized access to the protected local data instead.

* Establish backing with supported `KeyInfo` security-level data and, when required, key attestation; the provider name alone is insufficient.
* A UI transition or swallowed exception does not prove unauthorized use of a hardware-backed key.
* Root access does not automatically expose TEE/StrongBox keys.
* References: [Android Keystore](https://developer.android.com/privacy-and-security/keystore), [biometric authentication](https://developer.android.com/identity/sign-in/biometric-auth).
* **Caller context:** enumerate aliases/types/providers under the app's own UID; this does not expose every app's keys.
* Inspect the policies of keys actually used by the sensitive operation.
* Compare `BIOMETRIC_WEAK`, `BIOMETRIC_STRONG`, and device-credential fallback with required assurance and hardware-key authenticator constraints.
* Test enrollment invalidation under the configured auth policy.

## Trace Cryptographic Data Flow

* Trace: input > encoding/serialization > key source/derivation > algorithm/mode/IV/nonce > output > consumer/storage.
* Identify the purpose: secret protection, integrity verification, or a non-security checksum.

<table><thead><tr><th width="170">Observation Point</th><th>Record</th><th>Check</th></tr></thead><tbody><tr><td><code>SecretKeySpec</code>, KDF, or key import</td><td>Origin, derivation parameters, scope/lifetime, and caller</td><td>Trace bytes back to constants, storage, generation, or network; unchanged bytes alone do not prove hardcoding.</td></tr><tr><td><code>KeyGenerator</code>, <code>KeyPairGenerator</code>, Keystore</td><td>Provider, alias, purposes, auth policy, backing</td><td>Whether key export/use is possible under the stated attacker capability.</td></tr><tr><td><code>Cipher.getInstance</code>, <code>init</code>, <code>update</code>, <code>doFinal</code></td><td>Transformation, operation, key identity, IV/nonce, AAD, input/output</td><td>Same-key nonce reuse, integrity validation, mode misuse, and error handling in the actual flow.</td></tr><tr><td><code>SecureRandom</code> / other RNG</td><td>Generator, seeding and security-sensitive use</td><td>Repeatability is a clue, not proof of predictability; assess entropy and use.</td></tr><tr><td>Encoders / hashes</td><td>Base64/hex/compression/digest and downstream use</td><td>Encoding is not encryption; a weak digest used for a cache key is not equivalent to password hashing.</td></tr></tbody></table>

* **Template scope:** metadata for `Cipher.doFinal(byte[])` only; no key/plaintext dumps.
* **Not covered:** streaming/no-argument overloads or native crypto.
* **Run:** Frida CLI script/REPL using the [attach/spawn commands](objection-and-runtime-instrumentation.md#attach-or-spawn); custom agents need the [Java bridge setup](java-and-native-instrumentation.md#custom-agent-setup).
  * ```javascript
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
* Correlate cipher instances, `init` parameters, and consumers with synthetic test data.
* Capture the values needed to trace key provenance and compare repeated operations.
* Compare repeated operations under the **same key**, app restarts, and account changes.
* Key changes between sessions do not prove server origin.
* `getEncoded()` returning null may indicate a non-exportable key, not an analysis failure.
* Note key-access prerequisites and whether an attacker controls the messages.
* Plaintext in memory during legitimate use is not itself a cryptographic break; assess retention/exposure with [local data lifecycle testing](local-data-logs-and-privacy.md).
* **Related:** [Java and Native Instrumentation](java-and-native-instrumentation.md) | [Component Testing](component-testing.md).
