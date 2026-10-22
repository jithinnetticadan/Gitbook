# Binary Analysis

{% hint style="info" %}
Record version, source, architecture, and original/extracted artifact hashes. Use authorized copies only; App Store binaries may be FairPlay-encrypted. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Verify architecture and encryption state first. Run `otool` on macOS. See [Preflight, Tools, and IPA](preflight-tools-and-ipa.md#mandatory-preflight).
{% endhint %}

## App and Binary Review

* Find the executable via `Info.plist`; inspect linked frameworks.
* Objective-C/Swift metadata differ; missing class-dump output does not prove absent functionality.
* Source: `.h` declarations; `.m` Objective-C implementations.
* Layers: hardware/firmware and software; user data is separate from OS data. Jailbreak changes inspection capabilities.

### Binary Protections

Run on macOS; interpret indicators in context:

```sh
otool -hv <app-binary> | grep PIE
otool -I -v <app-binary> | grep stack_chk
otool -I -v <app-binary> | grep objc_release
otool -arch all -Vl <app-binary> | grep -A5 LC_ENCRYPT
otool -l <app-binary> | grep -A4 LC_ENCRYPTION_INFO
```

| Check      | Indicator                               | Limitation                                                    |
| ---------- | --------------------------------------- | ------------------------------------------------------------- |
| PIE        | Supports address randomization.         | Not proof of overall binary security.                         |
| Canaries   | `stack_chk_guard`, `stack_chk_fail`.    | Checks some stack corruption at return; not all code.         |
| ARC        | `_objc_release`.                        | Reference-lifetime management, not complete memory safety.    |
| Encryption | `cryptid=1` encrypted; `0` unencrypted. | Development/decrypted copies need not be App Store-encrypted. |

* Missing symbols may reflect optimization or language/runtime differences.
* Windows: use a macOS host or suitable Mach-O parser.

### Sensitive and Risky API Indicators

Search symbols, then inspect call sites/data flow:

```sh
otool -Iv <app-binary> | grep -w '_CC_MD5'
otool -Iv <app-binary> | grep -w '_CC_SHA1'
otool -Iv <app-binary> | grep -w '_random'
otool -Iv <app-binary> | grep -w '_srand'
otool -Iv <app-binary> | grep -w '_rand'
otool -Iv <app-binary> | grep -w '_malloc'
otool -Iv <app-binary> | grep -E '_(gets|memcpy|strncpy|strlen|vsnprintf|sscanf|strtok|alloca|sprintf|printf|vsprintf)'
```

* Source/text search: `grep -R -E '_CC_MD5|_CC_SHA1|_rand|_malloc' <analysis-directory>`.
* Review hash purpose and security-sensitive randomness; unused/system-linked matches may be false positives.
* `malloc`/`memcpy`/`strlen`/`printf` are not inherently vulnerabilities. Check bounds, sizes, format strings, and allocation failures.
* Validate MobSF API findings. Parse Mach-O symbols/strings; text grep does not analyze binary code.

Disassemble with:

```sh
otool -tV <app-binary>
```

For class metadata, see [Decryption and Class Information](../dynamic-testing/decryption-and-class-information.md).
