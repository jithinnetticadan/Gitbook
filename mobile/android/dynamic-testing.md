# Android Dynamic Testing

{% hint style="info" %}
Use an authorized test device and test accounts. Preserve originals; protect dumps and restore the lab afterward. Replace command placeholders before use.
{% endhint %}

## Mandatory Preflight

{% hint style="warning" %}
Use the **same exact Frida version** for the host `frida` library, device `frida-server`, and any injected Frida Gadget. `frida-tools` and Objection have separate version numbers; do not match the server to those numbers. Recheck after package upgrades.
{% endhint %}

* [ ] `adb devices -l` shows the intended device as authorized, not `offline`/`unauthorized`.
* [ ] Server build matches the device ABI; Gadget matches the target app's ABI, including 32-bit apps on 64-bit devices.
* [ ] Choose one runtime path: root-accessible, running Frida server **or** a patched app that loads Gadget.
* [ ] Check exact versions before attaching; `frida-ps -Uai` confirms the server/Gadget connection.
* [ ] Patching: include required APK splits/libraries, align, sign, verify, and install the test build successfully.
* [ ] Traffic testing: device can reach the proxy, app accepts the CA, and pinning is checked separately.

## Device and Frida Setup

* Use a compatible Android Studio emulator or test device.
* Verify root availability; API level/Play Store status alone is insufficient.

Identify architecture when selecting Frida server:

```sh
adb shell getprop ro.product.cpu.abilist
adb shell cat /proc/version
adb shell cat /proc/cpuinfo
```

Select Frida by app-compatible ABI; kernel information alone is insufficient.

Install client tools in an isolated environment:

```sh
pip3 install frida-tools
pip3 install objection
frida --version
objection version
objection --help
objection start --help
```

* Match the host `frida` library and device server **exactly**; record version and ABI.
* Objection installs Frida dependencies and can change the installed version; recheck after installation/upgrades.
* Current CLI: `objection [OPTIONS] COMMAND [ARGS]...`; `--name` selects, `start` opens a session.
* Subcommand options: check installed help and [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py).

### Start Frida Server

Root-capable ADB image (`adb root` is not supported on ordinary production builds):

```sh
adb root
adb push frida-server /data/local/tmp/frida-server
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
```

Alternative: authorized `su` access:

```sh
adb push frida-server /data/local/tmp/frida-server
adb shell "su -c 'chmod 755 /data/local/tmp/frida-server'"
adb shell "su -c '/data/local/tmp/frida-server &'"
```

### Verify Client and Server Versions

Run after transferring and making the server executable:

```sh
adb devices -l
frida --version
pip3 show frida frida-tools objection
adb shell /data/local/tmp/frida-server --version
```

* `frida --version` and `frida-server --version` must match exactly.
* Use the same host environment for Frida and Objection.
* If mismatched: replace/pin the client or server, restart the server, then retry `frida-ps -Uai`.

List installed apps and attach:

```sh
frida-ps -Uai
frida -U -n <process-name>
objection --name <process-name> start
```

## Runtime Component Testing

* Check exported activities, services, receivers, and providers.
* Test authorization, input handling, and data exposure. `exported=true` alone is not a finding.

```sh
adb shell am start -n <package-name>/<fully-qualified-activity-name>
adb shell am start -a android.intent.action.VIEW -d "<scheme>://<host>/<path>?<parameter>=<test-value>" <package-name>
```

### Drozer Setup

Install the agent and forward its port:

```sh
adb forward tcp:31415 tcp:31415
drozer console connect
```

Run the following commands **inside Drozer**. Check module help; availability varies by release.

### Packages and Activities

```text
run app.package.attacksurface <package-name>
run app.package.debuggable
run app.package.manifest <package-name>
run app.activity.info -a <package-name>
run app.activity.start --component <package-name> <activity-name>
run app.activity.start --component <package-name> <activity-name> --data-uri <authorized-test-uri>
run app.activity.start --action android.intent.action.VIEW --data-uri <authorized-test-uri>
```

### Content Providers

```text
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
```

### Services and Broadcasts

```text
run app.service.info -a <package-name>
run app.service.send <package-name> <service-name> --msg 2354 9234 1 --extra string <parameter> <test-value> --bundle-as-obj
run app.broadcast.info -a <package-name>
run app.broadcast.send --action <intent-name> --extra string <parameter> <test-value>
```

* [Drozer](https://github.com/WithSecureLabs/drozer): interactive assessment, not just an automatic scanner.
* `app.package.debuggable` lists debuggable packages.
* `app.provider.columns` / `app.provider.read`: source-era examples; may require specific releases/extensions.
* Repeat `--string` / `--extra` for additional fields/parameters.
* Insert/update/delete mutate data: use disposable test records only.
* Verify app **and server** authorization; intent filters/prior screens are not access controls.

## Runtime Instrumentation

### Objection Session

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

| Option/Mode | Use |
| --- | --- |
| `--name` | Attach by process name; spawn by package ID. Gadget may expose a different name. |
| Global options | `--name`, `--serial`, `--spawn`, `--no-pause` go **before** `start`/`run`. |
| Startup options | `--startup-command`, `--startup-script` go **after** `start`; check `objection start --help`. |
| `--no-pause` | Immediate resume; omit when early hooks need a paused spawn. |
| `run` | One-shot execution; do not assume hooks persist after exit. Use `start` for monitoring. |

Use long flags: global `-s` means spawn. Commands below run **inside Objection**; use in-session help for release-specific syntax.

### Classes and Activities

```text
env
android hooking list
android hooking search classes <keyword>
android hooking watch class <class-name> --dump-args --dump-backtrace --dump-return
android intent launch_activity <activity-name>
```

### Clipboard, Screenshots, Memory, and SQLite

```text
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

* `android heap options` / `android hooking list`: historical examples; confirm in-session help (`help android heap`).
* `FLAG_SECURE false` changes app behavior; assess original screenshot protections separately.
* `memory write` changes live data and may crash the app.
* Protect/delete memory dumps. Alternative: [Fridump](https://github.com/rootbsd/fridump).
* Review [CodeShare](https://codeshare.frida.re/) scripts before use; bypass success depends on app/version.
* Flutter: [reFlutter](https://github.com/ptswarm/reFlutter) for compatible instrumentation/traffic workflows.
* RMS: classes, arguments/returns, components, API monitoring, scripts.
* MobSF: configure a compatible dynamic-analysis environment first.

## App Patching and Repackaging

### Automated Patching

```sh
objection patchapk --help
objection patchapk --source <app.apk> --gadget-version <frida-version>
```

* Replace `<frida-version>` with the host `frida --version` output; verify `--gadget-version` in the installed patcher's help.
* Source/architecture flags belong to `patchapk`; check its help.
* `objection signapk --help`: alignment/signing with Objection's key.
* Manual workflow below uses your own test keystore.

### Manual Patching

1. Decode the APK, omitting resource decoding if appropriate: `apktool d -r <app.apk> -o <decoded-directory>`.
2. Download [Frida Gadget](https://github.com/frida/frida) matching the host's **exact Frida version** and the app ABI; decompress `.xz` and place `libfrida-gadget.so` in `lib/<abi>`.
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

* `System.loadLibrary("frida-gadget")` requires **`libfrida-gadget.so`**, not `frida-gadget.so`.
* Execute in the target process: suitable Application initialization or MainActivity/OnboardingActivity constructor.
* Check free registers and `.locals`/`.registers` before using `v0`.
* Gadget configuration/default wait behavior can pause startup.
* Without `-o`, Apktool usually writes under `dist`.
* Align before `apksigner`; legacy SHA1withRSA/SHA1 `jarsigner` is not the modern default.
* Re-signing may block updates/conflict with the original; preserve the original APK.

References: [Gadget](https://frida.re/docs/gadget/), [apksigner](https://developer.android.com/tools/apksigner), [non-root walkthrough](https://koz.io/using-frida-on-android-without-root/).

## Local Data, Logs, and Privacy Controls

* Inspect preferences, SQLite, internal/external files, caches, and backups.
* Use Android Studio Device File Explorer or Objection `env` for accessible paths.
* Inspect test copies with [DB Browser for SQLite](https://sqlitebrowser.org/) or the CLI:


```sh
sqlite3 <database-copy.db>
```

```sql
.tables
SELECT * FROM <test_table> LIMIT 10;
```

`.tables` is a SQLite CLI command, not SQL. Use approved test keyboards/clipboard observers; OS restrictions apply.

Check:

* [ ] Sensitive logs, clipboard (`android clipboard monitor`), keyboard data, screenshots/`FLAG_SECURE`.
* [ ] Backup exposure using an OS-supported workflow.
* [ ] Local role/state tampering; verify server authorization.
* [ ] SQL injection using non-destructive test records.
* [ ] Biometrics: success/failure callbacks and exception handling; verify key/server protections independently.

Biometric scripts: [Keystore Audit](https://github.com/FSecureLABS/android-keystore-audit/tree/master/frida-scripts), [callback bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass.js), [exception bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass-via-exception-handling.js). UI bypass does not prove hardware-key/server bypass.

Legacy backup: `adb backup -apk -nosystem <package-name>`. Deprecated/unavailable on current Android; may not extract all data.

### Logs and Screenshots

```sh
adb logcat -c
adb logcat | grep '<search-term>'
adb shell pidof <package-name>
adb logcat --pid=<pid-from-previous-command>
```

* Refresh PID after app restart; avoid brittle `ps | awk | grep` filters.
* Windows: use `findstr` or Android Studio Logcat. Protect log evidence.
* Screenshot artifacts: system-managed paths such as `/data/system_ce/<user-id>/`; locations/access vary.

## Network Traffic and TLS

1. Bind Burp to the lab interface; firewall any "All interfaces" listener.
2. Set the device proxy and install the CA: [Android Burp guide](https://portswigger.net/support/configuring-an-android-device-to-work-with-burp).
3. Use DER where required; `.cer` renaming does not change encoding/trust. User-CA acceptance depends on OS/app policy.
4. Test API authentication, authorization, sensitive data, and server-side behavior.
5. If pinning blocks testing, use `android sslpinning disable`, reviewed Frida scripts, or a patched test build.

* Trusted CA and pinning are separate checks; bypass is a test technique, not remediation.
* Android 7+ apps targeting API 24+ do not trust user-installed CAs by default. Use an authorized test trust configuration/device setup; installing the CA alone may not allow interception.
* Alternatives: [Proxyman](https://proxyman.io/), HTTP Canary (including Flutter attempts); verify platform/TLS compatibility.
* Setup: [MobSF Dynamic Analyzer](https://mobsf.github.io/docs/#/dynamic_analyzer), [Frida Android](https://frida.re/docs/android/).
* Optional/legacy: [CuckooDroid](https://github.com/idanr1986/cuckoo-droid) sandboxing, [BlueStacks](https://www.bluestacks.com/) emulator, [RMS](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), [Ghost](https://github.com/EntySec/Ghost). Verify maintenance/root behavior.

## Further Reading

* [Objection](https://github.com/sensepost/objection)
* [Runtime Mobile Security](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security)
* [HackTricks Android checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/android-checklist)
* [SecJuice: Introduction to Frida and Objection](https://www.secjuice.com/objection-frida-guide/)
* [Frida installation](https://frida.re/docs/installation/)
* [Frida Android testing walkthrough from the notes](https://www.varutra.com/android-pentesting-using-frida/)