# Android Static Testing

{% hint style="info" %}
Analyze only applications in scope. Record the package, version, acquisition method, device assumptions, and a hash of the original artifact before analysis.
{% endhint %}

## Lab Tools and Setup

* [JADX](https://github.com/skylot/jadx) / JADX-GUI - decompile DEX and inspect resources.
* [Apktool](https://apktool.org/) - decode resources and SMALI; compare its output with JADX.
* [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - automated static and dynamic analysis. The course uses `setup.bat` / `run.bat` on Windows and `setup.sh` / `run.sh` on Unix; these are historical setup examples, not a guarantee of support in the current release. Follow the repository's current installation requirements.
* [dex2jar](https://github.com/pxb1988/dex2jar) and [JD-GUI](https://github.com/java-decompiler/jd-gui) - alternate DEX-to-JAR workflow.
* [APKLeaks](https://github.com/dwisiswant0/apkleaks) - search APKs for exposed strings and configuration.
* Android Studio and Android SDK Platform Tools - device/package management and artifact acquisition.
* `keytool`, `jarsigner`, `zipalign`, and Android SDK signing tools - inspect or prepare test artifacts when repackaging is authorized.
* Additional/legacy tools in the course notes: [Androwarn](https://github.com/maaaaz/androwarn), Andrubis, ApkAnalyser, [QARK](https://github.com/linkedin/qark), [Santoku](https://santoku-linux.com/), and [PimpMyKali](https://github.com/Dewalt-arch/pimpmykali). Verify maintenance, compatibility, and provenance before installing older tools.

Install Java, Android Studio / SDK Platform Tools, JADX, and Apktool using current official instructions. On Windows, make `adb` available in `PATH`; MobSF has Windows scripts in its repository. Kali package names in the course notes include `adb`, `apktool`, `default-jdk`, and `jadx`. On macOS, common Homebrew packages include `jadx`, `apktool`, and `android-platform-tools`. Tool packaging changes; prefer current maintainer documentation.

### Windows

Install a compatible Java **JDK** for the selected JADX/Apktool releases, rather than assuming any Java runtime is sufficient. Get platform tools from [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools), extract to a dedicated tools directory, and add that directory to `PATH`; copying tools into `C:\Windows` is unnecessary. Android Studio's SDK Manager is another source. Follow [Apktool installation instructions](https://apktool.org/docs/install/) and the JADX release instructions.

### Kali Linux

These commands reproduce the package-manager workflow in the notes where those packages are available:

```sh
sudo apt-get update
sudo apt-get install adb apktool default-jdk jadx
java --version
jadx-gui
```

Install Android Studio separately. PimpMyKali is an optional provisioning script, not a guarantee that every listed tool will be installed or compatible. For MobSF, use the selected release's documented dependencies and setup process rather than installing an arbitrary `requirements.txt` from another release.

### macOS

Install Homebrew using its [official instructions](https://brew.sh/), inspect the installer before running it, then install supported packages:

```sh
brew install jadx apktool android-platform-tools
jadx-gui
apktool --version
adb version
```

Install Android Studio separately. Platform tools also provide utilities such as `fastboot`.

## Acquire the APK

On an authorized device or emulator, identify the package and APK path, then pull the artifact:

```sh
adb shell
pm list packages | grep <app-name-fragment>
pm path <package-name>
exit
adb pull <device-apk-path> <local-file.apk>
```

`pm path` can return multiple paths for split APKs. Strip the `package:` prefix from each returned path before `adb pull`. Collect required splits and document the set. Create a local output directory first. The notes use a Play Store-equipped emulator for acquisition and a separate root-capable lab image for testing; an authorized device or supplied test APK is also suitable.

## Android App Architecture

Most Java/Kotlin app code runs on Android Runtime (ART); older versions used Dalvik. Apps normally run under separate Linux UIDs and in app sandboxes. Native `.so` libraries execute outside the Java VM but remain within the app's OS security boundary. Android users and work profiles provide further separation.

Apps can communicate through interfaces such as activities, services, broadcast receivers, and content providers when exposed or explicitly permitted. A component marked `exported` can be reachable by other apps, but exploitability depends on its permissions, input validation, authentication, and behavior.

Common paths include `/data/app/<package>` for installed artifacts, `/data/data/<package>` for private app data, and `/sdcard/Android/data/<package>` for app-specific external data. Paths and access vary by OS version and device configuration.

Android's broad software stack includes the Linux kernel, hardware abstraction layer, native/ART libraries, Java API framework, and system/apps layer. Regular app IDs typically occupy 10000-19999; full Linux UIDs also encode the Android user. The notes' 10000-99999 range is not the regular app-ID range. Primary, secondary, guest, restricted/child profiles where supported, and managed/work profiles can have separate app data. Personal/work separation supports BYOD data isolation, but is not an absolute guarantee against exfiltration.

ART executes DEX bytecode using interpretation and compilation; the sandbox is an OS boundary, not simply a separate VM. Root does not automatically override every SELinux or encryption restriction. APK signing establishes integrity and signer identity and is required for installation; it does **not** prevent decompilation or keep source logic secret.

## Decompile and Inspect

```sh
jadx-gui <app.apk>
apktool d <app.apk> -o <decoded-directory>
```

Compare decompiled code with decoded resources and SMALI, especially when obfuscation or tool differences are present. JADX performs DEX decompilation; use dex2jar only when a separate Java decompiler workflow is useful. Native libraries use the `.so` extension.

```sh
d2j-dex2jar.sh <app.apk>
apkleaks -f <app.apk>
```

Open the generated JAR in JD-GUI. dex2jar converts DEX to Java bytecode in a JAR, not SMALI directly into original Java source. MobSF may display decompiled code and SMALI; inspect relevant paths manually and validate automated findings.

## Manifest and Component Review

Inspect `AndroidManifest.xml` in JADX and Apktool output. Review:

* `minSdkVersion`, target SDK, permissions, application settings, activities, services, receivers, and providers.
* `android:exported`, component permissions, intent filters, deep links, and whether sensitive actions enforce authorization. Intent filters route intents; they are not authentication.
* Debug and backup settings, cleartext traffic policy, and `android:networkSecurityConfig`. Confirm production builds do not unintentionally enable debugging or permit cleartext traffic.
* Content provider authorities, exported status, path permissions, and query/update behavior.
* Dangerous permissions and whether each is necessary for app functionality.

References: [Android manifest introduction](https://developer.android.com/guide/topics/manifest/manifest-intro), [Android permissions](https://developer.android.com/reference/android/Manifest.permission), and [Android security overview](https://source.android.com/docs/security/overview/app-security).

Examples of settings to inspect, in their appropriate files:

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

These are illustrative snippets, not complete app manifests or universal remediation. Inspect backup/data-extraction rules and Android-version behavior as well as `allowBackup`.

## Secrets, Cloud Configuration, and Endpoints

Search code, resources, and assets for terms such as `api`, `id`, `password`, `username`, `.com`, `aws`, `gcp`, `azure`, `http`, `https`, `secret`, and `key`. Inspect `res/values/strings.xml`, source strings, JSON/configuration files, and native libraries. Validate whether values are live, privileged, and exploitable; a public client identifier is not automatically a secret.

Look for endpoints, credentials, tokens, Firebase URLs, storage bucket names, and environment-specific configuration. If cloud resources are identified, test only with explicit authorization and scoped credentials:

* [cloud_enum](https://github.com/initstring/cloud_enum) can identify candidate cloud assets.
* [firebaseEnum](https://github.com/Sambal0x/firebaseEnum) can help assess Firebase exposure.
* Use the [AWS CLI](https://aws.amazon.com/cli/) only with an authorized profile, e.g. `aws configure --profile <assessment-name>`. Never place credentials in notes or shell history.

When a Firebase database URL is found in the manifest or app resources, verify its access controls only with explicit authorization. A database endpoint may use a `.json` path, but the URL format alone does not establish exposure; use a non-destructive read-only check and document the response and applicable rules.

Firebase Realtime Database examples are `https://<database>.firebaseio.com/<test-path>.json` or the region-specific `firebasedatabase.app` endpoint. The source's `firebase.io.com/.json` is not a valid canonical Firebase example. This REST pattern does not apply to every Firebase product. `cloud_enum` covers AWS, Azure, and GCP asset discovery; discovery alone is not permission to test those assets.

## Configuration and Cryptography

Review signing and build configuration. A debug certificate or build setting may indicate a release-process weakness, but assess practical impact and distribution context. Identify applicable signing schemes (v1/v2/v3) and investigate known signature weaknesses relevant to supported Android versions.

Use `apksigner verify --verbose --print-certs <app.apk>` to inspect signing information. Janus (CVE-2017-13156), mentioned in the notes, concerns vulnerable Android signature-verification behavior; applicability depends on OS patch level and the accepted signing scheme, not just the presence of v1 signing.

Inspect for weak or obsolete cryptography, permissive TLS validation, and insecure randomness. Examples include searching for `SecretKeySpec`, `SSLSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER`, and `java.util.Random`. Verify data flow and actual behavior rather than reporting a string match alone; prefer secure randomness APIs for security-sensitive values.

`SecretKeySpec` is not itself deprecated or weak; inspect its algorithm, key source, mode, IV/nonce, and usage. `java.util.Random` is unsuitable for security-sensitive unpredictability, not inherently a "collision attack" finding. A source search such as `grep -R -n 'SecretKeySpec' <decompiled-directory>` is a triage step only.

## Local Data and Client-Side Logic

Identify shared preferences, SQLite databases, internal/external storage, caches, and backup mechanisms. Determine whether tokens, personal data, or sensitive business state are insufficiently protected, and whether another app or a device backup can access them.

Review client-side authorization and business logic. Locally stored roles, tokens, or account state may be alterable; confirm the server independently enforces authorization. Inspect database query construction for SQL injection involving attacker-controlled input. Note logging, clipboard, screenshots, and keyboard behavior for runtime follow-up.

## Further Reading

* [OWASP Mobile Security Testing Guide: Android](https://mobile-security.gitbook.io/mobile-security-testing-guide/android-testing-guide/0x05b-basic-security_testing)
* [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
* [HackTricks Android checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/android-checklist)
* [Intro to Mobile Pentesting](https://www.hackthebox.com/blog/intro-to-mobile-pentesting)
* [OWASP mobile testing overview](https://mobile-security.gitbook.io/mobile-security-testing-guide/overview/0x03-overview)
* [HackTricks Android app pentesting](https://book.hacktricks.xyz/mobile-pentesting/android-app-pentesting)