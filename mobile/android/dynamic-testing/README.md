# Android Dynamic Testing

{% hint style="info" %}
Use an authorized test device and test accounts. Preserve originals; protect dumps and restore the lab afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Before instrumentation, complete [Preflight and Frida Setup](preflight-and-frida-setup.md). Host `frida`, device `frida-server`, and any Gadget must use the **same exact Frida version**. Record an unmodified baseline before applying hooks or bypasses.
{% endhint %}

| Step | Page | Use When |
| --- | --- | --- |
| 1 | [Methodology and Baseline](methodology-and-baseline.md) | Fingerprinting frameworks, profiling runtime behavior, and mapping critical flows. |
| 2 | [Preflight and Frida Setup](preflight-and-frida-setup.md) | Preparing the device, starting Frida server, and verifying versions. |
| 3 | [Component Testing](component-testing.md) | ADB/Drozer IPC tests, caller permissions, App Links, and WebView bridges. |
| 4 | [Advanced IPC and Content Providers](advanced-ipc-and-providers.md) | Binder, intent redirection, result/grant boundaries, provider operations, and Dirty Stream. |
| 5 | [Objection and Runtime Instrumentation](objection-and-runtime-instrumentation.md) | Objection commands for classes, clipboard, memory, `FLAG_SECURE`, and SQLite. |
| 6 | [Java and Native Instrumentation](java-and-native-instrumentation.md) | Writing targeted Frida hooks; resolving overloads, classloaders, JNI, and symbols. |
| 7 | [App Patching and Repackaging](app-patching.md) | Loading Gadget into an authorized test copy when the server path is unavailable. |
| 8 | [Runtime Defenses and Integrity](runtime-defenses-and-integrity.md) | Diagnosing root/emulator/debug/Frida checks, anti-tampering, and attestation. |
| 9 | [Local Data, Logs, and Privacy](local-data-logs-and-privacy.md) | Tracking data lifecycle, acquiring SQLite evidence, testing privacy and backup/restore. |
| 10 | [Platform and Version-Specific Tests](platform-and-version-specific-tests.md) | Special access, profiles, hardware, platform research, and patch applicability. |
| 11 | [Network Traffic and TLS](network-traffic-and-tls.md) | Diagnosing routing, TLS, trust, pinning, and multiple HTTP stacks. |
| 12 | [Authentication, Authorization, and Cryptography](authentication-and-cryptography.md) | Session replay, two-account authorization, biometrics, Keystore, and crypto provenance. |
| 13 | [Business Logic and Backend Trust](business-logic-and-backend.md) | Entitlements, Billing, offline/replay behavior, request signing, and backend variants. |
| 14 | [Validation, Reporting, and Troubleshooting](validation-and-troubleshooting.md) | Confirming impact, diagnosing blocked tests, recording evidence, and cleanup. |

Review [Android Static Testing](../static-testing/README.md) first; its findings direct which dynamic checks matter. After baseline/preflight, choose the relevant category rather than applying every bypass in sequence.

## Further Reading

* [Workbook Coverage](../checklist-coverage.md): all 373 checklist IDs mapped to workflows, with source qualifications and conditional/legacy cases.
* Vidhan Thakur, *Android Dynamic Application Security Testing*, Field Guide 02 (63-page PDF), embedded on the [Android page](../README.md). Commands and conclusions here are qualified against current platform/tool behavior; older guide snippets may not run unchanged.
* [Objection](https://github.com/sensepost/objection)
* [Runtime Mobile Security](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security)
* [HackTricks Android checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/android-checklist)
* [SecJuice: Introduction to Frida and Objection](https://www.secjuice.com/objection-frida-guide/)
* [Frida installation](https://frida.re/docs/installation/)
* [Frida Android testing walkthrough from the notes](https://www.varutra.com/android-pentesting-using-frida/)
