# Android Checklist Coverage

Documentation cross-reference for the supplied **Android_Pentest_Master_Checklist.xlsx**, reviewed on **2026-10-22**: **373 unique checks in 20 categories**. The original workbook is embedded on the [Android page](README.md).

This maps checklist topics to test workflows, prerequisites, and applicability/correction notes. It is **not a completed assessment**, a guarantee that every Android attack is represented, or evidence that an app passes these checks. Workbook status/severity columns are source data, not verified findings; the workbook has not been edited.

## Coverage Map

Each range is inclusive and uses the workbook's original IDs. Related/duplicate entries share a workflow rather than repeating commands. Tool rows are optional tooling choices; platform and legacy rows require applicability checks.

| Checklist IDs | Count | Category | Documentation |
| --- | --- | --- | --- |
| AND-01-001 through AND-01-027 | 27 | Reconnaissance | [Acquisition, public/historical sources, delivered features](static-testing/acquire-and-decompile.md), [manifest](static-testing/manifest-and-components.md), [secrets/cloud](static-testing/secrets-and-cloud.md), [dependencies](static-testing/webview-ipc-and-dependencies.md), [signing](static-testing/configuration-and-cryptography.md). |
| AND-02-001 through AND-02-024 | 24 | APK structure / manifest | [Permissions, tasks, export defaults](static-testing/manifest-and-components.md), [signing/trust](static-testing/configuration-and-cryptography.md), [URI grants](dynamic-testing/advanced-ipc-and-providers.md), [backup](dynamic-testing/local-data-logs-and-privacy.md), [patching](dynamic-testing/app-patching.md). |
| AND-03-001 through AND-03-025 | 25 | Static code review | [Code sources/sinks and concurrency](static-testing/local-data-and-client-logic.md), [crypto/TLS](static-testing/configuration-and-cryptography.md), [WebView/SQL/IPC](static-testing/webview-ipc-and-dependencies.md), [native review](dynamic-testing/java-and-native-instrumentation.md), [secrets](static-testing/secrets-and-cloud.md). |
| AND-04-001 through AND-04-025 | 25 | Local storage | [Storage formats](static-testing/local-data-and-client-logic.md), [lifecycle/acquisition/privacy/backup](dynamic-testing/local-data-logs-and-privacy.md), [Keystore and crypto use](dynamic-testing/authentication-and-cryptography.md), [FCM limits](static-testing/secrets-and-cloud.md). |
| AND-05-001 through AND-05-029 | 29 | IPC | [Components, App Links, callers](dynamic-testing/component-testing.md), [intents/results/Binder/grants/providers](dynamic-testing/advanced-ipc-and-providers.md), [task/platform applicability](dynamic-testing/platform-and-version-specific-tests.md). |
| AND-06-001 through AND-06-028 | 28 | Runtime instrumentation | [Preflight](dynamic-testing/preflight-and-frida-setup.md), [Objection](dynamic-testing/objection-and-runtime-instrumentation.md), [Java/native hooks](dynamic-testing/java-and-native-instrumentation.md), [defenses](dynamic-testing/runtime-defenses-and-integrity.md), [Gadget](dynamic-testing/app-patching.md), [Keystore/biometrics](dynamic-testing/authentication-and-cryptography.md). |
| AND-07-001 through AND-07-024 | 24 | Network | [Proxy/TLS/pinning, protocols and framework-specific stacks](dynamic-testing/network-traffic-and-tls.md), [trust configuration](static-testing/configuration-and-cryptography.md). |
| AND-08-001 through AND-08-022 | 22 | WebView | [Static boundary checks](static-testing/webview-ipc-and-dependencies.md), [runtime origin/bridge validation](dynamic-testing/component-testing.md), [browser-based OAuth](dynamic-testing/authentication-and-cryptography.md). |
| AND-09-001 through AND-09-020 | 20 | Authentication / sessions | [Session, OAuth/OIDC/JWT/passkey and biometric tests](dynamic-testing/authentication-and-cryptography.md), [privacy/lifecycle](dynamic-testing/local-data-logs-and-privacy.md), [SMS/autofill](dynamic-testing/platform-and-version-specific-tests.md). |
| AND-10-001 through AND-10-010 | 10 | Cryptography | [Algorithms, derivation, authentication and providers](static-testing/configuration-and-cryptography.md), [runtime provenance/Keystore](dynamic-testing/authentication-and-cryptography.md). |
| AND-11-001 through AND-11-015 | 15 | Platform / permissions | [Declarations and privileges](static-testing/manifest-and-components.md), [consent, special access, hardware and profile tests](dynamic-testing/platform-and-version-specific-tests.md). |
| AND-12-001 through AND-12-010 | 10 | Deep Links / App Links | [Verification, fingerprints, routing, domains and input](dynamic-testing/component-testing.md), [forwarding/IPC](dynamic-testing/advanced-ipc-and-providers.md), [OAuth binding](dynamic-testing/authentication-and-cryptography.md). |
| AND-13-001 through AND-13-015 | 15 | Libraries / SDKs | [Cloud/service authority and keys](static-testing/secrets-and-cloud.md), [SCA](static-testing/webview-ipc-and-dependencies.md), [telemetry/WebRTC](dynamic-testing/network-traffic-and-tls.md), [Billing/provider verification](dynamic-testing/business-logic-and-backend.md). |
| AND-14-001 through AND-14-014 | 14 | Anti-reversing / tampering | [Actual checks, tooling limits, attestation and shutdowns](dynamic-testing/runtime-defenses-and-integrity.md), [dynamic loading](static-testing/local-data-and-client-logic.md), [native hooks](dynamic-testing/java-and-native-instrumentation.md). |
| AND-15-001 through AND-15-010 | 10 | Native / JNI | [JNI boundaries, hardening, memory safety and bounded fuzzing](dynamic-testing/java-and-native-instrumentation.md), [dynamic loading](static-testing/local-data-and-client-logic.md). |
| AND-16-001 through AND-16-010 | 10 | Providers, deeper tests | [Operation matrix, grants, URI variants, observers and Dirty Stream](dynamic-testing/advanced-ipc-and-providers.md). |
| AND-17-001 through AND-17-013 | 13 | Business logic | [Entitlements, Billing, prices, trials, clock/offline state, rewards and sync races](dynamic-testing/business-logic-and-backend.md). |
| AND-18-001 through AND-18-022 | 22 | Emerging / niche | [Version/hardware applicability, permissions and primary research](dynamic-testing/platform-and-version-specific-tests.md), [framework recovery](static-testing/acquire-and-decompile.md), [biometrics/passkeys](dynamic-testing/authentication-and-cryptography.md). |
| AND-19-001 through AND-19-015 | 15 | Tools / lab | [Tools and compatibility](static-testing/preflight-and-tools.md), [lab selection](dynamic-testing/methodology-and-baseline.md), [Frida preflight](dynamic-testing/preflight-and-frida-setup.md), [Drozer](dynamic-testing/component-testing.md), [Objection](dynamic-testing/objection-and-runtime-instrumentation.md). |
| AND-20-001 through AND-20-015 | 15 | Mobile backend | [Request signing, replay, mobile variants and abuse controls](dynamic-testing/business-logic-and-backend.md), [JWT/OAuth](dynamic-testing/authentication-and-cryptography.md), [network](dynamic-testing/network-traffic-and-tls.md). |
| **Total** | **373** | **Documentation coverage, not test results** | Use [validation and reporting](dynamic-testing/validation-and-troubleshooting.md) for actual findings. |

## Important Source Qualifications

| Workbook Example | Treatment in These Notes |
| --- | --- |
| AND-18-003 labels CVE-2024-0044 "Dirty Stream" | Corrected: platform `run-as` forgery and app-level untrusted provider filenames are different issues. |
| AND-14-013 says SafetyNet remains functional | Corrected against Google's January 2025 shutdown; assess migration/failure handling. |
| AND-01-026 / AND-02-012 / AND-18-005 equate v1 with Janus | Require an affected unpatched verifier and relevant signing path. |
| AND-04-001 calls private preferences world-readable | Corrected sandbox versus app-level plaintext versus OS encryption; state acquisition prerequisites. |
| AND-04-022 / AND-13-013 infer FCM send authority from a registration token | A recipient token is not a server sending credential. |
| AND-08-009 / AND-08-014 imply network-only debugging or global cookie sharing | Require actual debugging access; assess the app's WebView profile and origin boundaries. |
| AND-09-001 / AND-09-002 / AND-10-005 infer flaws from missing crypto objects or StrongBox | Evaluate protected operation, auth-bound key policy, assurance requirement, and hardware support. |
| AND-06-006 / AND-06-014 / AND-06-024 and related bypass rows | No universal pinning bypass, undetectable module, or guaranteed integrity verdict; validate exact build and backend result. |
| AND-11-013 / AND-18-013 equate a leaked port with wireless ADB access | Pairing/authentication and exposure are separate; no routine PIN brute force. |
| AND-13-005 / AND-19-007 / AND-19-012 use legacy products or commands | Use supported Billing tests, current Objection `--name ... start`, and platform-appropriate proxy tools. |
| AND-20-011 / AND-20-015 conflate pinning/mTLS or missing nonce/replay | Distinguish server authentication, client authentication, authorization, and operation-specific freshness. |
| AND-18 research timings, device lists and fixes | Primary-source leads with exact version/vendor applicability, not universal device findings or a promise of current exploitability. |

The original and embedded workbook were byte-identical at review (SHA-256: `279BEAEEC42365CFA5AF770BDEBECDC8EBF25BA00E54BE523984ECD73C2AB8FD`). Reconcile new workbook revisions by ID; do not silently transfer assessment results between different app/build/device contexts.