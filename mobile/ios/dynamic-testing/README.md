# iOS Dynamic Testing

{% hint style="info" %}
Use authorized devices/builds and test accounts. Isolate the lab, protect evidence, and restore it afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Always start with [Preflight and Lab Setup](preflight-and-lab-setup.md). Host `frida`, device `frida-server`, and any Gadget must use the **same exact Frida version**.
{% endhint %}

| Step | Page | Use When |
| --- | --- | --- |
| 1 | [Preflight and Lab Setup](preflight-and-lab-setup.md) | Provisioning, jailbroken-device setup, and verifying Frida versions. |
| 2 | [Signing and App Patching](signing-and-app-patching.md) | Testing on a non-jailbroken device; re-signing or patching an IPA with Gadget. |
| 3 | [Traffic Analysis and TLS](traffic-analysis-and-tls.md) | Intercepting traffic with Burp and testing certificate pinning. |
| 4 | [Runtime Instrumentation](runtime-instrumentation.md) | Hooking classes and methods with Frida, Objection, and r2frida. |
| 5 | [Data Storage and Privacy](data-storage-and-privacy.md) | Inspecting plists, databases, Keychain, cookies, and dumps. |
| 6 | [URL Schemes, Web Views, and Client Behavior](client-side-testing.md) | Testing deep links, WebViews, business logic, logs, and pasteboard. |
| 7 | [Decryption and Class Information](decryption-and-class-information.md) | Working with FairPlay-encrypted apps and extracting class metadata. |

Review [iOS Static Testing](../static-testing/README.md) first; its findings direct which dynamic checks matter.

## Further Reading

* [Frida iOS documentation](https://frida.re/docs/ios/)
* [Objection](https://github.com/sensepost/objection)
* [Apple Platform Security](https://support.apple.com/guide/security/welcome/web)
* [HackTricks iOS testing checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/ios-pentesting-checklist)
