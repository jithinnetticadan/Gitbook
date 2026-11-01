# Preflight and Setup

## Mandatory Preflight

* [ ] Identify the executable through `Info.plist`.
* [ ] Verify binary architecture/platform and encryption state before disassembly or class extraction.
* [ ] Use a suitable authorized unencrypted copy when encryption blocks analysis; extracting ZIP contents does not decrypt code.
* [ ] Run `otool`/Apple tooling on a compatible macOS host, or use a suitable Mach-O parser.
* [ ] For patching/signing or instrumentation, follow [lab prerequisites](../dynamic-testing/preflight-and-lab-setup.md#mandatory-preflight). Basic URL/proxy tests do not require Frida or jailbreak.

## Lab Tools

* [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - automated static analysis.
* `otool` and [MachOView](https://sourceforge.net/projects/machoview/) - inspect Mach-O headers, load commands, and symbols. `otool` is provided by Xcode/Apple Command Line Tools.
* [class-dump](http://stevenygard.com/projects/class-dump/) - Objective-C interfaces. Legacy `class-dump-z` is not automatically interchangeable.
* [Hopper](https://www.hopperapp.com/), [Ghidra](https://ghidra-sre.org/), and [IDA Free](https://hex-rays.com/ida-free/) - disassembly and reverse engineering.
* Flawfinder and Clang Static Analyzer can assist with authorized source code.
* [radare2](https://rada.re/n/) (`rabin2`, `r2`), [iRET](https://github.com/S3Jensen/iRET), [LIEF](https://lief-project.github.io/), `pagestuff` - additional binary tools; verify support and install requirements.
* [Historical Veracode iRET](https://www.veracode.com/sites/default/files/Resources/Tools/iRETTool.zip) - distributions may differ or be unmaintained.
* [AnyTrans](https://www.imobie.com/anytrans/download.htm), iMazing - authorized artifact management; acquisition restrictions apply.
* **Signing/development dependencies:** macOS and Xcode; follow current installation/license requirements.

## Extract IPA

* ```bash
  unzip <app.ipa> -d <extracted-directory>
  ```

<table><thead><tr><th width="254">Location</th><th>Inspect</th></tr></thead><tbody><tr><td><code>Payload/&#x3C;Application>.app/</code></td><td>Executable, resources, property lists.</td></tr><tr><td><code>Payload/&#x3C;Application>.app/Info.plist</code></td><td>Bundle ID, executable name, URL types, permission descriptions.</td></tr><tr><td><code>iTunesMetadata.plist</code></td><td>Distribution metadata, if present.</td></tr><tr><td>Profile/signature files</td><td>Signing and provisioning metadata, if included.</td></tr></tbody></table>
