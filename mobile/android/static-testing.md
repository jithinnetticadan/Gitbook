# Android Static Testing

{% hint style="info" %}
Test only in-scope apps. Record package, version, source, device/API level, and original APK hash. Replace command placeholders before use.
{% endhint %}

## Mandatory Preflight

* [ ] Java JDK is compatible with the selected JADX/Apktool releases; required tools are available in `PATH`.
* [ ] Preserve/hash the original APK and collect all required splits/resources/native libraries.
* [ ] Record package, app version, min/target SDK, and test-device Android/API level.
* [ ] Verify MobSF/other tool requirements for the selected release; manually validate automated findings.
* [ ] Before runtime checks or repackaging, follow [Dynamic Testing prerequisites](dynamic-testing.md#mandatory-preflight).

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

## Acquire the APK

Find the installed package and pull its APK:

```sh
adb shell
pm list packages | grep <app-name-fragment>
pm path <package-name>
exit
adb pull <device-apk-path> <local-file.apk>
```

* Create a local output directory.
* Strip `package:` from each `pm path` result before pulling.
* Split APKs: collect all required splits; record the set.
* Acquisition: authorized device, supplied APK, or Play Store emulator. Testing may use a separate root-capable image.

## Android App Architecture

| Item | Key Point |
| --- | --- |
| Runtime | ART interprets/compiles DEX; older Android used Dalvik. |
| Sandbox | OS-enforced isolation and separate app UIDs, not just a VM. |
| Native code | `.so` libraries remain inside the app's OS boundary. |
| App IDs | Regular app IDs: 10000-19999; full UIDs also encode the user. |
| Cross-app access | Review activities, services, receivers, and providers. Exported does not mean vulnerable. |
| Users/profiles | Primary, secondary, guest, restricted/child where supported, and managed/work profiles separate data. BYOD isolation is not absolute. |
| Root | Does not automatically bypass SELinux or encryption. |
| Signing | Required for installation; protects integrity/signer identity, not against decompilation. |

Layers: Linux kernel > hardware abstraction > native/ART libraries > Java API framework > system/apps.

| Path | Purpose |
| --- | --- |
| `/data/app/<package>` | Installed artifacts. |
| `/data/data/<package>` | Private app data. |
| `/sdcard/Android/data/<package>` | App-specific external data. |

Paths/access vary by Android version and device.

## Decompile and Inspect

```sh
jadx-gui <app.apk>
apktool d <app.apk> -o <decoded-directory>
```

* Compare JADX code with Apktool resources/SMALI; resolve obfuscation or tool differences.
* Inspect `.so` native libraries separately.
* Optional DEX-to-JAR and string scanning:

```sh
d2j-dex2jar.sh <app.apk>
apkleaks -f <app.apk>
```

* Open the generated JAR in JD-GUI. dex2jar converts DEX to Java bytecode, not original source.
* MobSF: inspect decompiled code/SMALI; validate automated findings manually.

## Manifest and Component Review

Inspect `AndroidManifest.xml` in JADX and Apktool:

* `minSdkVersion`, target SDK, permissions, application settings, activities, services, receivers, and providers.
* `android:exported`, component permissions, intent filters, deep links, and sensitive-action authorization. Intent filters are **not authentication**.
* Debug, backup, cleartext, and `android:networkSecurityConfig` settings. Check production behavior.
* Content provider authorities, exported status, path permissions, and query/update behavior.
* Dangerous permissions and whether each is necessary for app functionality.

References: [Android manifest introduction](https://developer.android.com/guide/topics/manifest/manifest-intro), [Android permissions](https://developer.android.com/reference/android/Manifest.permission), and [Android security overview](https://source.android.com/docs/security/overview/app-security).

Example settings:

```xml
<!-- AndroidManifest.xml: example application attributes -->
<application
	android:allowBackup="false"
	android:debuggable="false"
	android:networkSecurityConfig="@xml/network_security_config" />
```

```xml
<!-- res/xml/network_security_config.xml: example domain policy -->
<network-security-config>
	<domain-config cleartextTrafficPermitted="false">
		<domain includeSubdomains="true">example.com</domain>
	</domain-config>
</network-security-config>
```

Snippets are illustrative, not complete manifests. Also inspect backup/data-extraction rules and OS behavior.

## Secrets, Cloud Configuration, and Endpoints

* Search: `api`, `id`, `password`, `username`, `.com`, `aws`, `gcp`, `azure`, `http`, `https`, `secret`, `key`.
* Locations: `res/values/strings.xml`, code, JSON/configuration, assets, native libraries.
* Check: endpoints, credentials, tokens, Firebase URLs, bucket names, environment settings.
* Validate privilege and impact; public client IDs are not automatically secrets.

Test cloud assets only with explicit authorization and scoped credentials:

* [cloud_enum](https://github.com/initstring/cloud_enum) can identify candidate cloud assets.
* [firebaseEnum](https://github.com/Sambal0x/firebaseEnum) can help assess Firebase exposure.
* Use the [AWS CLI](https://aws.amazon.com/cli/) only with an authorized profile, e.g. `aws configure --profile <assessment-name>`. Never place credentials in notes or shell history.

* Firebase Realtime Database: `https://<database>.firebaseio.com/<test-path>.json` or a regional `firebasedatabase.app` endpoint.
* Use scoped, non-destructive reads; record response and access rules. URL format alone proves nothing.
* `.json` is not universal across Firebase products; `firebase.io.com` is incorrect.
* `cloud_enum` discovers AWS/Azure/GCP assets; discovery does not authorize testing.

## Configuration and Cryptography

* Inspect certificates: `apksigner verify --verbose --print-certs <app.apk>`.
* Debug certificate/build: assess release context and impact, not just its presence.
* Review v1/v2/v3 schemes. Janus (CVE-2017-13156) depends on OS patch level and accepted scheme; v1 alone is not proof.
* Search: `grep -R -n 'SecretKeySpec' <decompiled-directory>`; also inspect `SSLSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER` and `java.util.Random`.
* `SecretKeySpec` is not inherently weak; check algorithm, key source, mode, IV/nonce, and use.
* `java.util.Random` is unsuitable for security-sensitive values; prefer secure randomness.
* Trace actual TLS/crypto behavior before reporting a string match.

## Local Data and Client-Side Logic

* Inspect shared preferences, SQLite, internal/external files, caches, and backups.
* Check protection of tokens, personal data, and business state; assess cross-app/backup access.
* Trace local roles/tokens/account state; verify independent server authorization.
* Review attacker-controlled SQL input and query construction.
* Flag logs, clipboard, screenshots, and keyboard behavior for [dynamic testing](dynamic-testing.md).

## Further Reading

* [OWASP Mobile Security Testing Guide: Android](https://mobile-security.gitbook.io/mobile-security-testing-guide/android-testing-guide/0x05b-basic-security_testing)
* [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
* [HackTricks Android checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/android-checklist)
* [Intro to Mobile Pentesting](https://www.hackthebox.com/blog/intro-to-mobile-pentesting)
* [OWASP mobile testing overview](https://mobile-security.gitbook.io/mobile-security-testing-guide/overview/0x03-overview)
* [HackTricks Android app pentesting](https://book.hacktricks.xyz/mobile-pentesting/android-app-pentesting)