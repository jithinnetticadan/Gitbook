# Decryption and Class Information

## Decryption and Class Information

* FairPlay-encrypted apps need a suitable decrypted executable for static code analysis.
* Tools: [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump), [Clutch](https://github.com/KJCracks/Clutch), [bfinject](https://github.com/BishopFox/bfinject).
* Configure the selected tool's Python dependencies and SSH connection; example: `python dump.py <bundle-id>`.
* Extract the app, identify its executable, and dump compatible Objective-C metadata:
  * ```bash
    class-dump <app-binary>
    ```
* Alternatives: Objection class/method listing; Hopper, Ghidra, or IDA Free for binary analysis.
* For encryption-dependent checks, see [Binary Analysis](../static-testing/binary-analysis.md).
