# Decryption and Class Information

## Decryption and Class Information

* FairPlay-encrypted app: use an authorized analysis copy only; do not redistribute decrypted/modified apps.
* Tools: [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump), [Clutch](https://github.com/KJCracks/Clutch), [bfinject](https://github.com/BishopFox/bfinject).
* Configure release-specific Python dependencies and secure SSH; example: `python dump.py <bundle-id>`. Never commit SSH passwords.
* Extract the app, identify its executable, and dump compatible Objective-C metadata:
  * ```bash
    class-dump <app-binary>
    ```
* Alternatives: Objection class/method listing; Hopper, Ghidra, or IDA Free for binary analysis.
* For encryption-dependent checks, see [Binary Analysis](../static-testing/binary-analysis.md).
