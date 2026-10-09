# Android Dynamic Testing

{% hint style="info" %}
Use a dedicated, authorized emulator or test device and test accounts. Runtime instrumentation, traffic interception, and app modification can change device state; preserve the original artifact and restore the lab after testing.
{% endhint %}

## Device and Frida Setup

Android Studio provides emulators; rooted images can simplify runtime and filesystem testing. Root and Play Store availability depend on the specific image and OS release. Verify the selected image rather than assuming an API level or Play Store status guarantees root.

Identify architecture when selecting Frida server:

```sh
adb shell getprop ro.product.cpu.abilist
adb shell cat /proc/version
adb shell cat /proc/cpuinfo
```

Use the ABI list to select an application-compatible Frida build. Kernel information alone may not identify the app's userspace ABI.

Install Frida tools and Objection on the analysis host. Frida server must match the device architecture and Frida client version. On a rooted lab image:

```sh
pip3 install frida-tools
pip3 install objection
frida --version
objection version
objection --help
objection start --help
```

Use an isolated environment or the tool's recommended installer. Installing `frida-tools` first follows the notes; Objection also installs Frida dependencies. Record versions and check compatibility. All Objection shell examples use `objection [OPTIONS] COMMAND [ARGS]...` from the supplied current help: `--name` selects the target and `start` opens a session. See [Objection's CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py) for subcommand options not shown by top-level help.

```sh
adb root
adb push frida-server /data/local/tmp/frida-server
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
```

If `adb root` is unavailable, use the authorized root mechanism for that lab:

```sh
adb push frida-server /data/local/tmp/frida-server
adb shell "su -c 'chmod 755 /data/local/tmp/frida-server'"
adb shell "su -c '/data/local/tmp/frida-server &'"
```

List installed apps and attach:

```sh
frida-ps -Uai
frida -U -n <process-name>
objection --name <process-name> start
```

## Runtime Component Testing

Test exported activities, services, receivers, and providers for unintended access, missing authorization, unsafe input handling, and data exposure. `exported=true` means potential cross-app reachability, not a finding by itself.

```sh
adb shell am start -n <package-name>/<fully-qualified-activity-name>
adb shell am start -a android.intent.action.VIEW -d "<scheme>://<host>/<path>?<parameter>=<test-value>" <package-name>
```

With Drozer, install its agent in the lab and forward its port:

```sh
adb forward tcp:31415 tcp:31415
drozer console connect
```

Run commands inside the Drozer console:

```text
run app.package.attacksurface <package-name>
run app.package.debuggable
run app.package.manifest <package-name>
run app.activity.info -a <package-name>
run app.activity.start --component <package-name> <activity-name>
run app.activity.start --component <package-name> <activity-name> --data-uri <authorized-test-uri>
run app.activity.start --action android.intent.action.VIEW --data-uri <authorized-test-uri>
run app.provider.info -a <package-name>
run app.provider.finduri <package-name>
run scanner.provider.finduris -a <package-name>
run app.provider.columns <content-uri>
run app.provider.read <content-uri>
run app.provider.query <content-uri>
run app.provider.insert <content-uri> --string <column> <test-value>
run app.provider.update <content-uri> --selection "<column>=?" --selection-args <test-value> --string <column> <replacement-value>
run app.provider.delete <content-uri> --selection "<column>=?" --selection-args <test-value>
run scanner.provider.injection -a <package-name>
run scanner.provider.sqltables -a <package-name>
run app.service.info -a <package-name>
run app.service.send <package-name> <service-name> --msg 2354 9234 1 --extra string <parameter> <test-value> --bundle-as-obj
run app.broadcast.info -a <package-name>
run app.broadcast.send --action <intent-name> --extra string <parameter> <test-value>
```

Use non-destructive test data. Provider insert/update/delete operations mutate app data and must not be run against production records. Confirm authorization is enforced by the app and server, not assumed from a previous screen or intent filter.

[Drozer](https://github.com/WithSecureLabs/drozer) is an interactive Android assessment framework with enumeration and testing modules, not simply an automatic scanner. `app.package.debuggable` lists debuggable packages. Use module help for supported arguments. Some source-note modules, including `app.provider.columns` and `app.provider.read`, may be extension- or release-specific; do not assume they exist in a default installation. To insert two test fields or send multiple broadcast extras, repeat `--string` or `--extra` with distinct column/parameter names.

## Runtime Instrumentation

Objection provides Frida-based inspection and runtime actions:

```sh
objection --name <process-name> start
objection --name <package-name> --spawn start
objection --serial <device-serial> --name <process-name> start
objection --name <process-name> start --startup-script <script.js>
objection --name <process-name> start --startup-command 'android root disable'
objection --name <process-name> start --startup-command 'android sslpinning disable'
objection --name <process-name> run 'android root disable'
objection --name <process-name> run 'android sslpinning disable'
```

Attach with the running process name or explicitly spawn with the package identifier when supported by the lab. With Frida Gadget, select the name exposed by the Gadget setup. Global options (`--name`, `--serial`, `--spawn`, `--no-pause`) belong before `start` or `run`. Session options (`--startup-command`, `--startup-script`) belong after `start`; verify them with `objection start --help`. Use long option names to avoid confusing global `-s` (spawn) with a subcommand's short options. `--no-pause` requests immediate resume; omit it when early instrumentation requires a paused spawn.

`run` executes one Objection command without opening the interactive session. Do not assume that hooks installed by a one-shot command remain active after the process exits; use `start` for ongoing monitoring and bypass testing. Top-level help does not list interactive command syntax. Run the following commands inside the Objection prompt, not directly in the host shell, and consult in-session help for their availability and arguments.

Examples inside Objection:

```text
env
android hooking list
android hooking search classes <keyword>
android hooking watch class <class-name> --dump-args --dump-backtrace --dump-return
android intent launch_activity <activity-name>
android clipboard monitor
android ui FLAG_SECURE false
memory dump all <output-file>.dmp
memory list modules
memory list exports <module-name>
memory search 4141 --string
memory write <address> <value> --string
android heap options
sqlite connect <database-file>
```

Use `help android heap` and current tool documentation for version-specific commands. Test whether sensitive screens prevent unintended screenshots/recording with `FLAG_SECURE`. Memory dumps may contain secrets; protect and securely remove them. [Fridump](https://github.com/rootbsd/fridump) is another memory-dumping option.

`android heap options` and `android hooking list` are retained from the source as historical command notes; verify their availability in installed help. `android ui FLAG_SECURE false` deliberately alters app behavior: distinguish the unmodified app's protections from instrumented behavior. `memory write` changes live process data and may crash the test app.

Frida scripts from [Frida CodeShare](https://codeshare.frida.re/) or local scripts can be used after review. Objection includes commands such as `android root disable`; behavior depends on app and tool version. For Flutter, [reFlutter](https://github.com/ptswarm/reFlutter) may assist with instrumentation and traffic analysis. Runtime Mobile Security (RMS) supports class/method inspection, argument and return monitoring, component testing, API monitoring, and script execution. MobSF also supports dynamic analysis when its environment is configured using current documentation.

## App Patching and Repackaging

For an authorized test build, Objection can patch an APK to include Frida Gadget:

```sh
objection patchapk --help
objection patchapk --source <app.apk>
```

`patchapk` remains a current top-level command; its source/architecture options are specific to that subcommand and are not shown by `objection --help`. For Objection's APK signing workflow, inspect `objection signapk --help`; `signapk` zipaligns and signs with Objection's key, whereas the manual workflow below uses your own test keystore.

Manual workflow when automated patching is unsuitable:

1. Decode the APK, omitting resource decoding if appropriate: `apktool d -r <app.apk> -o <decoded-directory>`.
2. Download the Frida Gadget library matching the target ABI from [Frida releases](https://github.com/frida/frida), decompress the `.xz` artifact, and place it in the corresponding `lib/<abi>` directory as `libfrida-gadget.so`. `System.loadLibrary("frida-gadget")` resolves that filename; `frida-gadget.so` alone is incorrect for this load call.
3. Add the load call to an appropriate initialization path. Example SMALI:

   ```smali
   const-string v0, "frida-gadget"
   invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
   ```

4. Rebuild, sign, and align the disposable test artifact:

   ```sh
   apktool b <decoded-directory> -o <unsigned-test.apk>
   keytool -genkey -v -keystore <test.keystore> -alias <test-alias> -keyalg RSA -keysize 2048 -validity 10000
   zipalign -p 4 <unsigned-test.apk> <aligned-test.apk>
   apksigner sign --ks <test.keystore> --ks-key-alias <test-alias> <aligned-test.apk>
   apksigner verify <aligned-test.apk>
   ```

Use current Android SDK signing documentation; legacy `jarsigner` workflows may not be suitable for modern APKs. Re-signing can prevent updates or conflict with the original app. Keep the original unchanged.

The load call must execute in the target process; an Application initializer or an appropriate activity constructor such as the source's MainActivity/OnboardingActivity is a possible location. Ensure a usable register and correct `.locals`/`.registers` declaration rather than blindly inserting `v0`. Gadget configuration and its default wait behavior affect startup. Without `-o`, Apktool normally places its rebuilt APK under the decoded directory's `dist` folder. The source's SHA1withRSA/SHA1 `jarsigner` recipe is legacy and should not be used as the modern signing default. See [Frida Gadget](https://frida.re/docs/gadget/), [apksigner](https://developer.android.com/tools/apksigner), and the source's [non-root Android walkthrough](https://koz.io/using-frida-on-android-without-root/).

## Local Data, Logs, and Privacy Controls

Inspect shared preferences, databases, internal/external storage, caches, and backups using Android Studio Device File Explorer or Objection where access permits. Use Objection's SQLite commands or [DB Browser for SQLite](https://sqlitebrowser.org/) for database review.

For a local test copy, inspect tables with the SQLite command-line client:

```sh
sqlite3 <database-copy.db>
```

```sql
.tables
SELECT * FROM <test_table> LIMIT 10;
```

Replace placeholders before use; `.tables` is a SQLite CLI meta-command, not SQL. Check app-specific directories with Objection `env`; additional cache/library paths vary by app. Use an approved test keyboard or test clipboard observer when assessing third-party input/clipboard exposure, and consider Android-version restrictions.

Check:

* Sensitive values in logs. Clear and filter logs carefully; Windows users can use `findstr` instead of `grep`.
* Clipboard exposure (`android clipboard monitor`), keyboard/input behavior, app-switcher screenshots, and use of `FLAG_SECURE`.
* Backup exposure. Historical `adb backup` is deprecated or unavailable on current Android; choose a workflow supported by the OS under test.
* Client-side authorization and mutable business state; confirm server-side enforcement.
* SQL injection in runtime queries using attacker-controlled input, with non-destructive test records.
* Biometric and other local-authentication flows. Check whether success/failure callbacks and exception handling can be manipulated, and whether sensitive server actions are independently authorized. The notes include [Android Keystore Audit examples](https://github.com/FSecureLABS/android-keystore-audit/tree/master/frida-scripts); review scripts and use them only against an authorized test build.

The two specific source examples are [fingerprint callback bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass.js) and [exception-handling bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass-via-exception-handling.js). Authentication UI bypass does not automatically bypass hardware-backed key access or server authorization.

On a legacy lab device that still supports it, the corrected historical backup syntax is `adb backup -apk -nosystem <package-name>` (not one quoted argument). Do not assume that current Android permits this or that it extracts all app data.

For log review, Android Studio Logcat is an alternative to ADB. Clear old output and filter for app-specific values or process IDs:

```sh
adb logcat -c
adb logcat | grep '<search-term>'
adb shell pidof <package-name>
adb logcat --pid=<pid-from-previous-command>
```

The source's `ps | awk | grep` recipe is brittle because process-list fields vary and it can match unrelated lines. PID filtering is preferable where supported; record a new PID after restarting the app.

On Windows, use `findstr` or Android Studio's Logcat filters. Treat logs as sensitive evidence. App-generated screenshots may be stored in system-managed locations such as `/data/system_ce/<user-id>/`; exact paths vary by Android version and device access.

## Network Traffic and TLS

Configure an authorized Burp Suite listener bound to the right interface, set the emulator/device proxy, and install the CA using the current [Android Burp configuration guide](https://portswigger.net/support/configuring-an-android-device-to-work-with-burp). Certificate trust differs by Android version and app network-security configuration. Proxyman is an alternative on macOS. Inspect API authentication, authorization, sensitive data, and server-side behavior.

Export the Burp CA in DER format for the Android certificate-install workflow where required. The notes rename it to `.cer`; the extension does not change the encoding or make the app trust user CAs. Bind the listener to the lab interface; if using the notes' "All interfaces" option, restrict access with the host firewall. A trusted CA addresses trust-chain validation, whereas pinning may still reject the connection. [Proxyman](https://proxyman.io/) is another option; platform support depends on the product/version. The notes also mention HTTP Canary, including for Flutter traffic; compatibility and TLS interception are not guaranteed.

For in-scope TLS testing, Objection includes `android sslpinning disable`; Frida scripts and patched builds are alternatives. Pinning bypass is a testing technique, not a remediation. See [MobSF Dynamic Analyzer documentation](https://mobsf.github.io/docs/#/dynamic_analyzer) and [Frida Android documentation](https://frida.re/docs/android/).

Other tools in the notes include [CuckooDroid](https://github.com/idanr1986/cuckoo-droid) for sandbox analysis, [BlueStacks](https://www.bluestacks.com/) (root behavior varies by product/version), [Runtime Mobile Security](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), and [Ghost Framework](https://github.com/EntySec/Ghost). Verify maintenance and use only within an authorized lab.

## Further Reading

* [Objection](https://github.com/sensepost/objection)
* [Runtime Mobile Security](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security)
* [HackTricks Android checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/android-checklist)
* [SecJuice: Introduction to Frida and Objection](https://www.secjuice.com/objection-frida-guide/)
* [Frida installation](https://frida.re/docs/installation/)
* [Frida Android testing walkthrough from the notes](https://www.varutra.com/android-pentesting-using-frida/)