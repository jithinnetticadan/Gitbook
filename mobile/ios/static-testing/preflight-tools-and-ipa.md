# Preflight, Tools, and IPA

{% hint style="info" %}
Record version, source, architecture, and original/extracted artifact hashes. Use authorized copies only; App Store binaries may be FairPlay-encrypted. Replace command placeholders before use.
{% endhint %}

## Mandatory Preflight

* [ ] Preserve/hash the original IPA; identify the executable through `Info.plist`.
* [ ] Verify binary architecture/platform and encryption state before disassembly or class extraction.
* [ ] Use a suitable authorized unencrypted copy when encryption blocks analysis; extracting ZIP contents does not decrypt code.
* [ ] Run `otool`/Apple tooling on a compatible macOS host, or use a suitable Mach-O parser.
* [ ] Before patching/signing or runtime checks, follow [Dynamic Testing prerequisites](../dynamic-testing/preflight-and-lab-setup.md#mandatory-preflight).

## Lab Tools

* [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - automated static analysis.
* `otool` and [MachOView](https://sourceforge.net/projects/machoview/) - inspect Mach-O headers, load commands, and symbols. `otool` is provided by Xcode/Apple Command Line Tools.
* [class-dump](http://stevenygard.com/projects/class-dump/) - Objective-C interfaces. Legacy `class-dump-z` is not automatically interchangeable.
* [Hopper](https://www.hopperapp.com/), [Ghidra](https://ghidra-sre.org/), and [IDA Free](https://hex-rays.com/ida-free/) - disassembly and reverse engineering.
* Flawfinder and Clang Static Analyzer can assist with authorized source code.
* [radare2](https://rada.re/n/) (`rabin2`, `r2`), [iRET](https://github.com/S3Jensen/iRET), [LIEF](https://lief-project.github.io/), `pagestuff` - additional binary tools; verify support and install requirements.
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

**Next:** [Binary Analysis](binary-analysis.md)
