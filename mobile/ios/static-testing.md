# iOS Static Testing

{% hint style="info" %}
Record version, source, architecture, and original/extracted artifact hashes. Use authorized copies only; App Store binaries may be FairPlay-encrypted. Replace command placeholders before use.
{% endhint %}

## Mandatory Preflight

* [ ] Preserve/hash the original IPA; identify the executable through `Info.plist`.
* [ ] Verify binary architecture/platform and encryption state before disassembly or class extraction.
* [ ] Use a suitable authorized unencrypted copy when encryption blocks analysis; extracting ZIP contents does not decrypt code.
* [ ] Run `otool`/Apple tooling on a compatible macOS host, or use a suitable Mach-O parser.
* [ ] Before patching/signing or runtime checks, follow [Dynamic Testing prerequisites](dynamic-testing.md#mandatory-preflight).

## Lab Tools

* [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - automated static analysis.
* `otool` and [MachOView](https://sourceforge.net/projects/machoview/) - inspect Mach-O headers, load commands, and symbols.
* [class-dump](http://stevenygard.com/projects/class-dump/) - Objective-C interfaces. Legacy `class-dump-z` is not automatically interchangeable.
* [Hopper](https://www.hopperapp.com/), [Ghidra](https://ghidra-sre.org/), and [IDA Free](https://hex-rays.com/ida-free/) - disassembly and reverse engineering.
* Flawfinder and Clang Static Analyzer can assist with authorized source code.
* [iRET](https://github.com/S3Jensen/iRET), [LIEF](https://lief-project.github.io/), `pagestuff` - additional binary tools; verify support.
* [Historical Veracode iRET](https://www.veracode.com/sites/default/files/Resources/Tools/iRETTool.zip) - distributions may differ or be unmaintained.
* [AnyTrans](https://www.imobie.com/anytrans/download.htm), iMazing - authorized artifact management; acquisition restrictions apply.

Use macOS/Xcode for Apple signing/development. Follow current installation/license requirements.

## Obtain and Extract an IPA

Preserve the IPA; extract a working copy (ZIP format):

```sh
unzip <app.ipa> -d <extracted-directory>
```

| Location | Inspect |
| --- | --- |
| `Payload/<Application>.app/` | Executable, resources, property lists. |
| `Payload/<Application>.app/Info.plist` | Bundle ID, executable name, URL types, permission descriptions. |
| `iTunesMetadata.plist` | Distribution metadata, if present. |
| Profile/signature files | Signing and provisioning metadata, if included. |

Confirm actual paths; use MobSF for initial triage. Renaming IPA to ZIP does not decrypt the executable.

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

| Check | Indicator | Limitation |
| --- | --- | --- |
| PIE | Supports address randomization. | Not proof of overall binary security. |
| Canaries | `stack_chk_guard`, `stack_chk_fail`. | Checks some stack corruption at return; not all code. |
| ARC | `_objc_release`. | Reference-lifetime management, not complete memory safety. |
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

## URL Handling and Inter-App Requests

* [ ] Validate caller, scheme, host, path, parameters, and authorization.
* [ ] Review custom schemes, universal links, and inter-app requests.

Inspect handlers:

* `application:didFinishLaunchingWithOptions:` and `application:willFinishLaunchingWithOptions:`.
* `application:openURL:options:` and scene-based URL handling.
* `openURL:options:completionHandler:` call sites.

Search an extracted app bundle:

```sh
grep -R -nE 'open.*options.*completionHandler|openURL\(|://' <Application.app>
grep -R -n 'mt-encrypted-file://' <Application.app>
rabin2 -zzq <app-binary> | grep -i openurl
```

* Test untrusted callers for sensitive actions/data disclosure; require user confirmation where appropriate.
* `sourceApplication` identifies a caller, not authorization by itself.
* `mt-encrypted-file://` is app-specific, not universal.
* Check deprecated APIs: [UIKit documentation](https://developer.apple.com/documentation/uikit).

## Configuration and Sensitive Data

* [ ] Search `Info.plist`, entitlements, URL schemes, JSON/resources, and strings.
* [ ] Find endpoints, test settings, credentials, tokens, keys, and sensitive data.
* [ ] Trace value use/impact; public identifiers are not automatically secrets.
* [ ] Review plist/`NSUserDefaults`, SQLite/Core Data, Keychain, logs, caches, and backups.
* [ ] Confirm storage behavior during [dynamic testing](dynamic-testing.md).

## Further Reading

* [OWASP iOS Testing Guide](https://mobile-security.gitbook.io/mobile-security-testing-guide/ios-testing-guide/0x06a-platform-overview)
* [Apple Platform Security](https://support.apple.com/guide/security/welcome/web)
* [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
* [HackTricks iOS testing checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/ios-pentesting-checklist)
* [Basic Guide to iOS Pentesting](https://www.bugcrowd.com/resources/levelup/a-basic-guide-to-ios-testing-in-2022/)
* [DVIA-v2 iOS training app](https://github.com/prateek147/DVIA-v2)
* [iOS tool notes linked in the source](https://www.allysonomalley.com/?s=iOS+Pentesting+Tools)