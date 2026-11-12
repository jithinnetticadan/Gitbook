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

#### Native OAuth and Passkey Mutations

* **OAuth callback:** deliver the callback through the [deep-link launch template](component-testing.md#deep-links-and-url-handling), using the observed scheme/host/path. Start a fresh login for each case; test wrong, omitted, duplicate and other-session `state` separately.
    * ```text
        demo://oauth/callback?code=REPLACE_UNUSED_CODE&state=wrong-state
        demo://oauth/callback?code=REPLACE_UNUSED_CODE
        demo://oauth/callback?code=REPLACE_UNUSED_CODE&state=REPLACE_CURRENT_STATE&state=wrong-state
        ```
* **PKCE token exchange:** use an unused code bound to a known challenge. First send a different valid-length verifier; next obtain a fresh code and omit `code_verifier`; finally use the correct verifier as a control with another fresh code. Retain the real client authentication where required.

{% tabs %}
{% tab title="Linux" %}
* ```bash
    curl -i 'https://auth.example/token' --data-urlencode 'grant_type=authorization_code' --data-urlencode 'client_id=REPLACE_CLIENT_ID' --data-urlencode 'redirect_uri=REPLACE_REGISTERED_CALLBACK' --data-urlencode 'code=REPLACE_UNUSED_CODE' --data-urlencode 'code_verifier=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    ```
{% endtab %}
{% tab title="Windows" %}
* ```powershell
    curl.exe -i 'https://auth.example/token' --data-urlencode 'grant_type=authorization_code' --data-urlencode 'client_id=REPLACE_CLIENT_ID' --data-urlencode 'redirect_uri=REPLACE_REGISTERED_CALLBACK' --data-urlencode 'code=REPLACE_UNUSED_CODE' --data-urlencode 'code_verifier=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    ```
{% endtab %}
{% endtabs %}
* **Code replay/binding:** redeem the same code twice; separately use a different registered callback or another client ID in the exchange. A used/expired code rejection does not establish that PKCE or redirect binding was validated.
* **Confirm:** wrong verifier is rejected at the authorization server; wrong state is rejected by the client without creating/switching a session. A returned token or completed app login under the wrong binding is the meaningful failure. Full PKCE flow: [OAuth guide](../../../web/vulnerabilities/oauth-2.0.md#authorization-code-flow-with-pkce).
* **ID/access tokens:** change `sub`, `aud`, `iss` or expiry without re-signing and submit at the actual backend token-consumer endpoint; then test a genuine token from another test client/account. Use [JWT payloads](../../../web/vulnerabilities/jwt-attacks.md). Tampered-token rejection establishes signature enforcement, not every claim check; wrong-audience/issuer tests need genuinely signed tokens with those values.
* **Passkey assertion:** keep the captured `id`, `rawId`, `response.clientDataJSON`, `response.authenticatorData`, `response.signature` and `response.userHandle` together initially. Submit it twice; submit it after challenge expiry; and submit A's assertion to B's active login transaction. Start a fresh challenge for each independent case.
* **Passkey field isolation:** swap only `id`/`rawId` with B's known credential ID, then separately change the claimed account/user handle. Confirm the authenticated account from the response, not the user-selected account label. Challenge/origin/RP-hash/user-verification changes covered by the signature require a test authenticator that signs that variant; editing signed bytes alone only tests signature rejection.

#### Protected API and Refresh Requests

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

{% tabs %}
{% tab title="Frida" %}
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
{% endtab %}
{% tab title="Objection" %}
* **Host terminal:** attach to the app with a working Frida connection.
    * ```text
        frida-ps -Uai
        objection --name '<process-name>' start
        ```
* **Objection console:** list and inspect the app's key aliases/policies and watch their use.
    * ```text
        android keystore list
        android keystore detail
        android keystore watch
        ```
* For the actual biometric callback, use the [class/method watcher](objection-and-runtime-instrumentation.md#classes-and-hooks) with the observed callback class.
{% endtab %}
{% tab title="Grapefruit" %}
* **Host terminal:** start the installed interface with the device's Frida server running.
    * ```text
        frida-ps -Uai
        igf
        ```
* Select the app, open its Android Keystore view, and inspect the relevant alias, key attributes and authentication policy.
{% endtab %}
{% endtabs %}

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

* **Template scope:** observe `Cipher.init` overloads, Keystore alias retrieval and `doFinal(byte[])`. Logs key fingerprints/aliases, not raw keys or plaintext. **Not covered:** streaming/no-argument `doFinal`, native crypto, or complete AAD tracing.
* **Run:** Frida CLI script/REPL using the [attach/spawn commands](objection-and-runtime-instrumentation.md#attach-or-spawn); custom agents need the [Java bridge setup](java-and-native-instrumentation.md#custom-agent-setup).
  * ```javascript
    Java.perform(function () {
        const Cipher = Java.use('javax.crypto.Cipher');
        const Key = Java.use('java.security.Key');
        const KeyStore = Java.use('java.security.KeyStore');
        const System = Java.use('java.lang.System');
        const Digest = Java.use('java.security.MessageDigest');
        const aliases = new Map();
        const hex = bytes => bytes === null ? null : Array.from(bytes,
            value => ('0' + (value & 255).toString(16)).slice(-2)).join('');
        const keyLookup = KeyStore.getKey.overload('java.lang.String', '[C');
        keyLookup.implementation = function (alias, password) {
            const key = keyLookup.call(this, alias, password);
            if (key !== null) aliases.set(String(System.identityHashCode(key)), String(alias));
            return key;
        };
        for (const initialize of Cipher.init.overloads) {
            initialize.implementation = function () {
                const args = Array.from(arguments);
                const result = initialize.call(this, ...args);
                try {
                    let keyTag = 'certificate/other';
                    if (args[1] !== null && Key.class.isInstance(args[1])) {
                        const key = Java.cast(args[1], Key);
                        const encoded = key.getEncoded();
                        keyTag = encoded === null
                            ? 'alias:' + (aliases.get(String(System.identityHashCode(key))) || 'unresolved')
                            : 'sha256:' + hex(Digest.getInstance('SHA-256').digest(encoded));
                    }
                    console.log(JSON.stringify({ event: 'init', cipher: System.identityHashCode(this),
                        algorithm: String(this.getAlgorithm()), operation: args[0],
                        key: keyTag, iv: hex(this.getIV()) }));
                } catch (error) { console.log('Crypto metadata unavailable: ' + error); }
                return result;
            };
        }
        const doFinal = Cipher.doFinal.overload('[B');
        doFinal.implementation = function (input) {
            const output = doFinal.call(this, input);
            console.log('cipher=' + System.identityHashCode(this) + ' ' + this.getAlgorithm() +
                ' inputBytes=' + (input === null ? 0 : input.length) +
                ' outputBytes=' + (output === null ? 0 : output.length));
            return output;
        };
    });
    ```
* **Nonce/IV reuse:** perform two different marker encryptions, then repeat after restart/account switch. Compare `operation=1` (encryption), algorithm, key tag and IV. Same-key/same-nonce reuse in GCM/CTR is a flaw; repeated decryptions (`operation=2`) naturally reuse the stored nonce. For CBC, test IV unpredictability as well as repetition.
* **Unresolved alias:** attach before key retrieval or trace the actual key-generation/import path. An unresolved/nonexportable tag does not establish that two operations use the same key; equal aliases across different installs/accounts also need key-lifecycle confirmation.
* **Integrity mutation (Node.js REPL, Windows / Linux):** copy the actual Base64 ciphertext field, change one ciphertext byte while retaining length/encoding, then put the result back in the same captured request or local test record. If the field contains a version/IV/tag envelope, select a byte in the ciphertext portion rather than blindly editing its header.
    * ```javascript
        const ciphertext = Buffer.from('REPLACE_BASE64_CIPHERTEXT', 'base64');
        const offset = 0;
        ciphertext[offset] ^= 1;
        console.log(ciphertext.toString('base64'));
        ```
* **Confirm integrity failure:** altered data is accepted as authentic and changes a protected value/action. A parse error, rejected authentication tag, or app crash is not accepted tampering. For an oracle, compare valid padding, invalid padding and valid-padding/invalid-content variants and demonstrate a repeatable observable distinction; one generic error is insufficient.
* Correlate cipher instances, `init` parameters, and consumers with synthetic test data.
* Capture the values needed to trace key provenance and compare repeated operations.
* Compare repeated operations under the **same key**, app restarts, and account changes.
* Key changes between sessions do not prove server origin.
* `getEncoded()` returning null may indicate a non-exportable key, not an analysis failure.
* Note key-access prerequisites and whether an attacker controls the messages.
* Plaintext in memory during legitimate use is not itself a cryptographic break; assess retention/exposure with [local data lifecycle testing](local-data-logs-and-privacy.md).

### Password-Derived Keys

* **Frida Java script:** observe `SecretKeyFactory.generateSecret(KeySpec)` when the input is `PBEKeySpec`. Trigger the actual encrypted-record/login flow; native KDFs and other spec types require their own observed implementation.
    * ```javascript
        Java.perform(function () {
            const Factory = Java.use('javax.crypto.SecretKeyFactory');
            const Spec = Java.use('javax.crypto.spec.PBEKeySpec');
            const Digest = Java.use('java.security.MessageDigest');
            const hex = bytes => bytes === null ? null : Array.from(bytes,
                value => (value & 255).toString(16).padStart(2, '0')).join('');
            const generate = Factory.generateSecret.overload('java.security.spec.KeySpec');
            generate.implementation = function (input) {
                let record = null;
                if (input !== null && Spec.class.isInstance(input)) {
                    const spec = Java.cast(input, Spec);
                    record = { algorithm: String(this.getAlgorithm()), salt: hex(spec.getSalt()),
                        iterations: spec.getIterationCount(), keyBits: spec.getKeyLength() };
                }
                const key = generate.call(this, input);
                if (record !== null) {
                    const encoded = key.getEncoded();
                    record.keyHash = encoded === null ? null : hex(Digest.getInstance('SHA-256').digest(encoded));
                    console.log(JSON.stringify(record));
                }
                return key;
            };
        });
        ```
* **Comparison:** create two independent records/accounts with the same test password; compare salt, iterations, PRF in the algorithm name, key length and key fingerprint. Change the password and repeat; compare the fingerprint with the key used by the cipher hook above. A null salt/zero count may identify a password-only spec, so trace the provider's final derivation rather than assuming those are the complete parameters.
* **Flaws to establish:** one fixed salt across independently stored password records; inadequate work factor for an exposed offline-verification target; or a key derived only from public device identifiers/constants. Trace the identifier/constant into the actual KDF input; do not infer it from repeated output alone.
* **Confirm offline exposure:** obtain the actual test record/envelope through the documented storage path and reproduce its derivation/decryption with the known test password and observed parameters. This connects the weak parameters to protected data; a KDF API hit alone is not a demonstrated cryptographic failure.
* **Related:** [Java and Native Instrumentation](java-and-native-instrumentation.md) | [Component Testing](component-testing.md).
