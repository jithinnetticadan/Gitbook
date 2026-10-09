# iOS Static Testing

{% hint style="info" %}
Analyze only application artifacts in scope. Record the app version, acquisition method, executable architecture, and hashes of the original archive and extracted app. App Store binaries may be FairPlay-encrypted; use only a legitimately obtained, authorized analysis copy.
{% endhint %}

## Lab Tools

* [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - automated static analysis.
* `otool` and [MachOView](https://sourceforge.net/projects/machoview/) - inspect Mach-O headers, load commands, and symbols.
* [class-dump](http://stevenygard.com/projects/class-dump/) - extract Objective-C interface information where supported. The source also names the legacy `class-dump-z` variant; verify compatibility rather than assuming interchangeability.
* [Hopper](https://www.hopperapp.com/), [Ghidra](https://ghidra-sre.org/), and [IDA Free](https://hex-rays.com/ida-free/) - disassembly and reverse engineering.
* Flawfinder and Clang Static Analyzer can assist with authorized source code.
* [iRET](https://github.com/S3Jensen/iRET), [LIEF](https://lief-project.github.io/), and Apple's `pagestuff` are additional binary-analysis options; check current platform support and provenance. The source also links a [historical Veracode iRET archive](https://www.veracode.com/sites/default/files/Resources/Tools/iRETTool.zip); do not assume different distributions are identical or maintained.
* [AnyTrans](https://www.imobie.com/anytrans/download.htm) or iMazing can assist with authorized device/app artifact management; availability and acquisition restrictions vary.

Xcode and macOS are used for Apple development and signing workflows. Follow current vendor installation and licensing instructions.

## Obtain and Extract an IPA

An `.ipa` is a ZIP-format archive. Preserve the original and extract a working copy:

```sh
unzip <app.ipa> -d <extracted-directory>
```

Common contents include:

* `Payload/<Application>.app/` - application bundle, executable, resources, and property lists.
* `iTunesMetadata.plist` - distribution metadata when present.
* `Payload/<Application>.app/Info.plist` - bundle identifier, executable name, URL types, permission descriptions, and other metadata.
* Provisioning and signature metadata where included.

Confirm the actual archive paths. MobSF can automate parts of the static review.

## App and Binary Review

Identify the executable from `Info.plist`, then inspect it and linked frameworks. Objective-C and Swift have different runtime metadata and decompilation characteristics. In source projects, `.h` files declare interfaces and `.m` files commonly contain Objective-C implementation. Missing class-dump output does not prove functionality is absent.

At a high level, iOS combines hardware/firmware and software layers, with user data separated from operating-system data. Use this boundary when evaluating app container access and data protection; a jailbroken test device changes the inspection capabilities available to the tester.

### Binary Protections

These checks are indicators, not standalone proof of security:

```sh
otool -hv <app-binary> | grep PIE
otool -I -v <app-binary> | grep stack_chk
otool -I -v <app-binary> | grep objc_release
otool -arch all -Vl <app-binary> | grep -A5 LC_ENCRYPT
otool -l <app-binary> | grep -A4 LC_ENCRYPTION_INFO
```

* **PIE:** Position-independent executables support address randomization.
* **Stack canaries:** Look for symbols such as `stack_chk_guard` and `stack_chk_fail` where applicable.
* **ARC:** `_objc_release` may appear in binaries using Objective-C ARC; presence alone does not establish memory safety.
* **Encryption:** Review encryption load commands and `cryptid` in context. App Store encryption state may differ from a legitimately decrypted test copy.

Stack canaries check for certain stack corruption at function return; their presence does not prove all code is protected. ARC manages Objective-C reference lifetimes, not all memory-safety problems. `cryptid=1` ordinarily indicates encryption and `cryptid=0` an unencrypted image; a development or decrypted test binary need not have App Store encryption. Missing symbols can also result from optimization or language/runtime differences.

`otool` is available on macOS; on Windows use a macOS analysis host or an appropriate Mach-O parser.

### Sensitive and Risky API Indicators

Use `otool` on macOS to search linked symbols. Inspect call sites and data flow before drawing conclusions:

```sh
otool -Iv <app-binary> | grep -w '_CC_MD5'
otool -Iv <app-binary> | grep -w '_CC_SHA1'
otool -Iv <app-binary> | grep -w '_random'
otool -Iv <app-binary> | grep -w '_srand'
otool -Iv <app-binary> | grep -w '_rand'
otool -Iv <app-binary> | grep -w '_malloc'
otool -Iv <app-binary> | grep -E '_(gets|memcpy|strncpy|strlen|vsnprintf|sscanf|strtok|alloca|sprintf|printf|vsprintf)'
```

For source or extracted text on Linux/macOS, recursively search for these symbols, e.g. `grep -R -E '_CC_MD5|_CC_SHA1|_rand|_malloc' <analysis-directory>`. Weak hashes, predictable randomness, or unsafe memory functions need contextual review and may be false positives when unused or only system-linked.

`malloc`, `memcpy`, `strlen`, and `printf` are not inherently vulnerabilities. Check bounds, attacker-controlled sizes/format strings, allocation failure handling, and actual cryptographic use. MobSF's API findings should be triaged the same way. For Mach-O binaries, inspect symbols or extract strings rather than relying on recursive text grep to parse binary code.

Disassemble with:

```sh
otool -tV <app-binary>
```

## URL Handling and Inter-App Requests

Review custom URL schemes, universal links, and app-to-app URL requests. Trace validation of the source, scheme, host, path, parameters, and authorization before an action. Inspect implementations corresponding to:

* `application:didFinishLaunchingWithOptions:` and `application:willFinishLaunchingWithOptions:`.
* `application:openURL:options:` and scene-based URL handling.
* `openURL:options:completionHandler:` call sites.

Search an extracted app bundle:

```sh
grep -R -nE 'open.*options.*completionHandler|openURL\(|://' <Application.app>
grep -R -n 'mt-encrypted-file://' <Application.app>
rabin2 -zzq <app-binary> | grep -i openurl
```

Test whether untrusted apps/links can trigger sensitive actions or disclose data. Check deprecated APIs against current [Apple UIKit documentation](https://developer.apple.com/documentation/uikit).

Review `sourceApplication` in URL options where relevant, but do not treat caller identity alone as authorization. Check whether user confirmation is appropriate for the operation. `mt-encrypted-file://` is a source-specific search example, not a universal iOS scheme. Renaming an IPA to ZIP is optional because it is already a ZIP archive; it does not decrypt its executable.

## Configuration and Sensitive Data

Inspect `Info.plist`, entitlements, URL schemes, embedded configuration, JSON/resources, and strings for endpoints, test settings, credentials, tokens, keys, and sensitive data. Validate findings and trace value use; a public app identifier is not automatically a secret.

Review property lists, `NSUserDefaults`, SQLite, Core Data, Keychain, logs, caches, and backups for likely sensitive-data paths. Confirm actual runtime behavior during dynamic testing.

## Further Reading

* [OWASP iOS Testing Guide](https://mobile-security.gitbook.io/mobile-security-testing-guide/ios-testing-guide/0x06a-platform-overview)
* [Apple Platform Security](https://support.apple.com/guide/security/welcome/web)
* [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
* [HackTricks iOS testing checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/ios-pentesting-checklist)
* [Basic Guide to iOS Pentesting](https://www.bugcrowd.com/resources/levelup/a-basic-guide-to-ios-testing-in-2022/)
* [DVIA-v2 iOS training app](https://github.com/prateek147/DVIA-v2)
* [iOS tool notes linked in the source](https://www.allysonomalley.com/?s=iOS+Pentesting+Tools)