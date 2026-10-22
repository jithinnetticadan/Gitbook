# Preflight and Tools

{% hint style="info" %}
Test only in-scope apps. Record package, version, source, device/API level, and original APK hash. Replace command placeholders before use.
{% endhint %}

## Mandatory Preflight

* [ ] Java JDK is compatible with the selected JADX/Apktool releases; required tools are available in `PATH`.
* [ ] Preserve/hash the original APK and collect all required splits/resources/native libraries.
* [ ] Record package, app version, min/target SDK, and test-device Android/API level.
* [ ] Verify MobSF/other tool requirements for the selected release; manually validate automated findings.
* [ ] Before runtime checks or repackaging, follow [Dynamic Testing prerequisites](../dynamic-testing/preflight-and-frida-setup.md#mandatory-preflight).

## Lab Tools and Setup

* [JADX](https://github.com/skylot/jadx) / JADX-GUI - decompile DEX and inspect resources.
* [Apktool](https://apktool.org/) - decode resources and SMALI; compare its output with JADX.
* [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - automated analysis. Use release-specific setup instructions; the course's `setup.bat` / `run.bat` and `setup.sh` / `run.sh` are historical examples.
* [dex2jar](https://github.com/pxb1988/dex2jar) and [JD-GUI](https://github.com/java-decompiler/jd-gui) - alternate DEX-to-JAR workflow.
* [APKLeaks](https://github.com/dwisiswant0/apkleaks) - search APKs for exposed strings and configuration.
* Android Studio and Android SDK Platform Tools - device/package management and artifact acquisition.
* `keytool`, `jarsigner`, `zipalign`, and Android SDK signing tools - inspect or prepare test artifacts when repackaging is authorized.
* Legacy/optional: [Androwarn](https://github.com/maaaaz/androwarn), Andrubis, ApkAnalyser, [QARK](https://github.com/linkedin/qark), [Santoku](https://santoku-linux.com/), [PimpMyKali](https://github.com/Dewalt-arch/pimpmykali). Verify maintenance and compatibility.

Use current maintainer instructions; package availability varies by OS/release.

### Optional Tools by Purpose

| Purpose | Options | Prerequisite / Limitation |
| --- | --- | --- |
| Native review | Ghidra, radare2, NDK/LLVM tools | Match ABI/build; use supported Java/runtime requirements for the selected tool release. |
| Protector fingerprinting | [APKiD](https://github.com/rednaga/APKiD) | Install its supported Python/YARA dependencies; fingerprints are leads, not an authoritative inventory of library versions. |
| Alternate decompilation | GDA, Bytecode Viewer, APK Studio | Verify current platform/runtime support and compare output against SMALI; no decompiler guarantees original source recovery. |
| Secret scanning | TruffleHog filesystem mode, Gitleaks directory mode, APKLeaks | Use current CLI help and scan extracted artifacts; avoid remote credential verification without permission. Regex matches need manual authority/impact review. |
| Re-signing | [Uber APK Signer](https://github.com/patrickfav/uber-apk-signer) | Requires a compatible Java runtime; choose/record a test key. It does not possess production keys or bypass update-signature checks. |
| Runtime UI helpers | RMS, House, Inspeckage | RMS/House releases have their own Frida/container dependencies. Inspeckage is Xposed-based, not just a Frida wrapper; review maintenance and device compatibility. |
| Virtual labs | Android Emulator, Genymotion, Corellium, Waydroid | Check host/guest/ABI support and licensing. Waydroid uses a Linux container environment, not a native Windows emulator. Hardware-backed assurance needs evidence from the relevant hardware. |
| Proxy helpers | Burp, compatible Android proxy/CA utilities | An iOS-only Burp Mobile Assistant workflow is not an Android setup. Verify platform support; a preconfigured emulator does not ensure the app trusts its CA. |
| Historical scanners | AndroBugs, QARK and older suites | Label legacy/unmaintained output; do not downgrade the lab or treat scanner silence as coverage. |

For every optional tool record version, source, required privileges, artifact compatibility, and validation method. Use a tool because it answers a test question, not to mark every tool-name row as a mandatory installation.

### Windows

* Install a compatible Java **JDK**, Android Studio, JADX, and Apktool.
* Get [SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) directly or through Android Studio's SDK Manager.
* Extract to a tools directory; add it to `PATH`. Do not copy into `C:\Windows`.
* Follow [Apktool installation](https://apktool.org/docs/install/) and JADX release instructions.

### Kali Linux

Install available packages:

```sh
sudo apt-get update
sudo apt-get install adb apktool default-jdk jadx
java --version
jadx-gui
```

* Install Android Studio separately.
* PimpMyKali is optional; it does not guarantee every tool is installed.
* MobSF: use dependencies/setup for the selected release, not another release's `requirements.txt`.

### macOS

Install [Homebrew](https://brew.sh/) after reviewing its installer, then:

```sh
brew install jadx apktool android-platform-tools
jadx-gui
apktool --version
adb version
```

Install Android Studio separately. Platform tools also include `fastboot`.

**Next:** [Acquire and Decompile](acquire-and-decompile.md)
