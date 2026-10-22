# Configuration and Cryptography

{% hint style="info" %}
* Test only in-scope apps; replace command placeholders before use.
* Record package, version, source, device/API level, and original APK hash.
{% endhint %}

## Configuration and Cryptography

* Inspect certificates: `apksigner verify --verbose --print-certs <app.apk>`.
* Debug certificate/build: assess release context and impact, not just its presence.
* Review v1/v2/v3 schemes. Janus (CVE-2017-13156) depends on OS patch level and accepted scheme; v1 alone is not proof.
* Search: `grep -R -n 'SecretKeySpec' <decompiled-directory>`; also inspect `SSLSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER` and `java.util.Random`.
* `SecretKeySpec` is not inherently weak; check algorithm, key source, mode, IV/nonce, and use.
* `java.util.Random` is unsuitable for security-sensitive values; prefer secure randomness.
* Trace actual TLS/crypto behavior before reporting a string match.

### Cryptography Patterns

```sh
grep -rnE 'Cipher\.getInstance\("(DES|DESede|RC4|ARCFOUR|Blowfish|AES/ECB|AES")' <decompiled-directory>
grep -rnE 'MessageDigest\.getInstance\("(MD5|SHA-?1)"\)' <decompiled-directory>
grep -rnE 'byte\[\] *(key|iv)[A-Za-z0-9_]* *=|IvParameterSpec\(|SecretKeySpec\(' <decompiled-directory>
grep -rn 'new Random(' <decompiled-directory>
```

* Plain `Cipher.getInstance("AES")` commonly defaults to ECB on Android; ECB leaks structure and has no IV.
* MD5/SHA-1 are weak for passwords and signatures; they may be acceptable for non-security checksums.
* Hardcoded key/IV byte arrays or string-derived keys are recoverable from the APK. Prefer Android Keystore-backed keys.
* `java.util.Random` becomes a finding only when it feeds OTPs, session tokens, reset codes, or nonces; ignore UI/animation use. Use `SecureRandom` instead.

### TLS and Cleartext Patterns

```sh
grep -rn -A4 'checkServerTrusted' <decompiled-directory>
grep -rn 'ALLOW_ALL_HOSTNAME_VERIFIER\|HostnameVerifier' <decompiled-directory>
grep -rn -A3 'onReceivedSslError' <decompiled-directory> | grep 'proceed()'
grep -rn 'CertificatePinner' <decompiled-directory>
grep -rn '"http://' <decompiled-directory> | grep -v 'schemas.android.com\|w3.org'
grep -rniE 'cleartextTrafficPermitted|<pin-set' <decoded-directory>/res/xml/
```

* An empty `checkServerTrusted()`, an allow-all hostname verifier, or a WebView calling `proceed()` on SSL errors is a lead. Establish which validation is bypassed, whether that implementation is used for sensitive traffic, and the attacker/impact before reporting it.
* Missing certificate pinning is a hardening gap, not automatically a vulnerability; rate by app risk. Check `CertificatePinner`, `<pin-set>`, and custom trust managers.
* Cleartext: `android:usesCleartextTraffic`, `cleartextTrafficPermitted="true"` in `<base-config>` or `<domain-config>`, and `http://` endpoints. Cleartext is blocked by default when targeting API 28+.

## Signing and Trust Boundaries

* Inspect v1/v2/v3 verification and signer identity with `apksigner`; v4 uses a separate incremental-install signature artifact and is not a replacement for APK authenticity verification. Absence of every newer scheme is not automatically exploitable.
* APK signing certificates are normally self-signed. Do not confuse that with a weak signing key, a known private debug key, or an unsafe TLS trust anchor. A debug-looking certificate does not prove `debuggable`/backup flags are enabled.
* Review actual key algorithms/sizes, release-key custody, certificate rotation, and signature-dependent permissions/App Links. Janus needs an affected, unpatched verifier and a relevant accepted signing path.
* For Network Security Config, resolve per-domain inheritance, `includeSubdomains`, debug overrides, user/system/custom trust anchors, and pin expiry/backup pins. Custom trust anchors can be legitimate; assess provenance, intended endpoints, and actual validation. Non-platform HTTP stacks may not honor this configuration.

## Key Derivation and Cryptographic Semantics

| Candidate                          | Trace / Validate                                                                                    | Avoid This Shortcut                                                                                                                                                  |
| ---------------------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PBKDF2 / password-derived key      | PRF, work factor, random per-record salt, password entropy, key length, and attacker offline access | Use current algorithm-specific guidance and device performance budgets; one fixed iteration threshold is not valid for every KDF.                                    |
| Static salt                        | Whether passwords can share precomputation or produce equal derived values                          | Salt reuse weakens isolation but does not eliminate all KDF work.                                                                                                    |
| CBC IV / GCM or CTR nonce          | IV unpredictability where required; nonce uniqueness under the same key                             | Repeated values under different keys are not the same as same-key nonce reuse.                                                                                       |
| Device-identifier key derivation   | IMEI, Android ID, MAC, timestamps, embedded material                                                | Identifiers are not secret entropy; trace the complete derivation rather than assuming a secure KDF fixes a predictable input.                                       |
| CBC/CTR without authentication     | Authenticating wrapper/protocol, attacker ciphertext control, error differences                     | Lack of a nearby HMAC call alone does not establish a padding oracle; prove integrity failure or an observable oracle.                                               |
| Hashes and signatures              | Security purpose, collision resistance versus password guessing, MAC/signature construction         | MD5/SHA-1 collision weaknesses do not imply a practical preimage attack in every use. Fast hashes are unsuitable for password storage even when collision-resistant. |
| Custom crypto / provider selection | Algorithm construction, JCA provider/version, explicit parameters, known advisories                 | Provider names and XOR loops alone do not prove a break; separate encoding, checksums, obfuscation, and real cryptography.                                           |
| Keystore / StrongBox               | Key purposes, exportability, authentication policy, verified security level                         | Missing StrongBox is not automatically a finding; evaluate the required protection and device support.                                                               |

* Validate findings with [runtime cryptographic data-flow testing](../dynamic-testing/authentication-and-cryptography.md#trace-cryptographic-data-flow).
* Reference: [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
