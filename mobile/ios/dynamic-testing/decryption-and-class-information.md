# Decryption and Class Information

{% hint style="info" %}
Use authorized devices/builds and test accounts. Isolate the lab, protect evidence, and restore it afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Use an authorized analysis copy only. Decryption tools need a working jailbroken-device setup: complete the [Mandatory Preflight](preflight-and-lab-setup.md#mandatory-preflight) first.
{% endhint %}

## Decryption and Class Information

* FairPlay-encrypted app: use an authorized analysis copy only; do not redistribute decrypted/modified apps.
* Tools: [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump), [Clutch](https://github.com/KJCracks/Clutch), [bfinject](https://github.com/BishopFox/bfinject).
* Configure release-specific Python dependencies and secure SSH; example: `python dump.py <bundle-id>`. Never commit SSH passwords.
* Extract the app, identify its executable, and dump compatible Objective-C metadata:

```sh
class-dump <app-binary>
```

Alternatives: Objection class/method listing; Hopper, Ghidra, or IDA Free for binary analysis.

Binary checks that depend on encryption state: [Binary Analysis](../static-testing/binary-analysis.md).

**Previous:** [URL Schemes, Web Views, and Client Behavior](client-side-testing.md)
