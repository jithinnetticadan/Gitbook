# iOS Dynamic Testing

{% hint style="info" %}
Use authorized devices/builds and test accounts. Isolate the lab, protect evidence, and restore it afterward. Replace command placeholders before use.
{% endhint %}

## Mandatory Preflight

{% hint style="warning" %}
Use the **same exact Frida version** for the host `frida` library, device `frida-server`, and any injected Frida Gadget. `frida-tools` and Objection have separate version numbers; do not match the server to those numbers. Recheck after package upgrades.
{% endhint %}

* [ ] Device is connected, unlocked, and trusts the testing Mac; confirm the selected device.
* [ ] Choose one runtime path: compatible jailbreak with running server **or** an authorized Gadget-patched/signed build.
* [ ] Server supports the device; Gadget matches the app architecture and device/Simulator platform.
* [ ] Verify exact versions; `frida-ps -Uai` confirms the physical-device connection.
* [ ] Non-jailbroken build: suitable unencrypted executable, valid signing identity/private key, matching profile/device/entitlements, successful install.
* [ ] Traffic testing: reachable Mac proxy, installed CA profile, full certificate trust enabled; pinning checked separately.

## Lab Setup and Provisioning

1. On macOS/Xcode, add your Apple ID and select a permitted development team.
2. Build/install a minimal app on the test device; trust the developer/profile in device-management settings.
3. Products > reveal `.app` in Finder > package contents > `embedded.mobileprovision`.
4. Verify the profile's App ID, entitlements, allowed devices, and expiry match the target.

* Free accounts support limited sideloading; notes cite seven-day profiles. Check current Apple limits.
* Intel Simulator: commonly x86_64; Apple Silicon Simulator: ARM64. Simulator/device ARM64 binaries still target different platforms.
* Validate hardware-sensitive findings on a physical device. Your own development builds need not be jailbroken for debugging.
* Profile filename: `embedded.mobileprovision`, not `embedded.mobileprovisioning`. An arbitrary app's profile may not fit.

References: [Xcode documentation](https://developer.apple.com/documentation/xcode), [downloads](https://developer.apple.com/download/all/?q=Xcode).

### Signing

```sh
security find-identity -v -p codesigning
applesign -L
applesign -i <signing-identity> -m <embedded.mobileprovision> <app.ipa>
```

Install [applesign](https://github.com/nowsecure/node-applesign): `npm install -g applesign` (not `appliesign`). Check `applesign --help` for release-specific input/options.

### Non-Jailbroken App Patching

Embed Gadget and re-sign a suitable IPA:

```sh
objection patchipa --help
objection patchipa --source <app.ipa> --codesign-signature <signing-identity> --provision-file <embedded.mobileprovision> --gadget-version <frida-version>
```

* Pin Gadget to the host `frida --version` output; confirm `--gadget-version` in installed help. Automatic latest-Gadget selection can mismatch an older client.
* Requires compatible signing assets and a suitable unencrypted executable; not every Store IPA works.
* `--codesign-signature` (`-c`), `--provision-file` (`-P`): check help and [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py).
* `security find-identity` lists identities; it does not create profiles or determine expiry.
* Follow current signing requirements; preserve originals and do not redistribute modified apps.

## Jailbroken Test Device

* Use hardware/iOS-compatible jailbreaks; checkra1n (`checkra.in`) and palera1n are not universal.
* Cydia/Sileo: package managers; install only trusted OpenSSH and Frida packages (`https://build.frida.re` in the notes).
* Match server and host `frida` library versions **exactly**; use supported architecture/platform builds.
* SSH: change historical `root` / `alpine` defaults; isolate/restrict access and remove it afterward.
* Utilities: OpenSSH/SFTP, Filza, `apt-get`/`dpkg`; availability varies.
* Non-jailbroken device: use the patched/signed workflow above; app restrictions apply.

```sh
ssh root@<device-ip>
frida-ps -Uai
objection --name <app-process-name> start
```

### Verify Client and Server Versions

Run on the Mac, using the device SSH access configured for the lab:

```sh
frida --version
pip3 show frida frida-tools objection
ssh <ssh-user>@<device-ip> "frida-server --version"
frida-ps -Uai
```

* Client and server version outputs must match exactly; use the same host environment for Frida/Objection.
* If `frida-server` is not in the device's `PATH`, use its installed package path; rootless/rootful locations vary.
* Confirm the server service is running. After replacing it, restart via the package's supported service workflow.
* Objection installation/upgrades can change Frida dependencies; recheck before testing.

## Traffic Analysis and TLS

1. Bind Burp to a reachable Mac lab IP/port; firewall "All interfaces" listeners.
2. Set the iPhone Wi-Fi proxy to that address. `127.0.0.1` on the phone is **not the Mac**.
3. Open `http://burp`; install the CA under VPN & Device Management.
4. Enable trust: General > About > Certificate Trust Settings (labels vary).
5. Test API authentication, authorization, inputs, sensitive data, and server behavior.
6. Remove the CA after testing; renaming its file does not change encoding/trust.

Confirm a test HTTPS request reaches Burp before investigating pinning. CA profile installation and enabling full trust are separate steps; an app may still reject the proxy certificate.

[Mobile Assistant guide](https://portswigger.net/burp/documentation/desktop/tools/mobile-assistant/installing): verify the historical package-source example `http://<mac-ip>:8080` before use.

### Pinning Tests

* Objection command: `ios sslpinning disable`.
* [SSL Kill Switch 2](https://github.com/nabla-c0d3/ssl-kill-switch2) / [3](https://github.com/NyaMisty/ssl-kill-switch3/releases): compatible jailbroken devices only.
* Burp Mobile Assistant and app-specific instrumentation.
* AppSync alters code-signing behavior; it does **not** replace CA trust configuration.

Bypass is a test technique, not a vulnerability by itself. Report actual validation behavior/impact.

## Runtime Analysis and Instrumentation

### Frida and Objection Connection

```sh
frida-ps -Uai
frida -U -n <app-process-name>
frida-trace -U -m '*[NSURLRequest *]' <app-process-name>
objection --name <app-process-name> start
```

* Objective-C selectors: `-` instance method, `+` class method.
* Find identifiers: `frida-ps -Uai | grep '<app-name-fragment>'`.
* Attach by process name; spawn by bundle ID. Gadget may expose a different target name.
* Current Objection: `--name` selects the target; `start` opens a session.

```sh
objection version
objection --help
objection start --help
objection --name <bundle-id> --spawn start
objection --serial <device-serial> --name <app-process-name> start
objection --local --name <simulator-process-name> start
objection --name <app-process-name> start --startup-script <script.js>
objection --name <app-process-name> run 'ios info binary'
```

| Option/Mode | Use |
| --- | --- |
| Global flags | `--name`, `--serial`, `--local`, `--spawn`, `--no-pause` go **before** `start`/`run`. |
| Startup flags | Go **after** `start`; verify `objection start --help`. |
| `--local` | iOS Simulator, not a physical device; compatible instrumentation required. |
| `--no-pause` | Immediate resume; omit for early hooks needing a paused spawn. |
| `run` | One-shot; do not assume hooks survive exit. Use `start` for monitoring. |

Use long flags: global `-s` means spawn. Interactive commands below run **inside Objection**, not the host shell.

### Classes, Hooks, and Local Checks

```text
env
ios hooking list classes
ios hooking list class_methods
ios hooking watch class <class-name>
ios hooking watch method <method-name> --dump-args --dump-return --dump-backtrace
ios sslpinning disable
ios jailbreak disable
```

### Storage, Privacy, and Memory

```text
ios pasteboard monitor
ios nsuserdefaults get
ios nsurlcredentialstorage dump
ios plist cat Info.plist
ios keychain dump
ios monitor crypt
ios info binary
ios cookies get
memory dump all <output-file>.dmp
```

* Interactive syntax varies: use in-session help; top-level `--help` does not define it.
* Detection testing: Hestia, Shadow, Objection; verify device/app compatibility.
* Alternatives: [RMS](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), [Grapefruit](https://github.com/ChiChou/grapefruit).
* Install in an isolated environment: `pip3 install frida-tools`, `pip3 install objection` (also installs Frida dependencies).

### Startup Hooks

```sh
objection --name <app-process-name> start --startup-command 'ios jailbreak disable'
objection --name <app-process-name> start --startup-command 'ios sslpinning disable'
```

Check `--startup-command`/`--startup-script` in `objection start --help` and the [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py). Instrumenting a detection return value does not establish server-side privilege bypass.

### r2frida

```text
r2 frida://spawn//usb//<bundle-id>
:i?
:ic~<class-or-string>
:dtf <function-address>
```

Verify plugin syntax; addresses apply to the active process. Inspect dumps with `strings <dump-file>`; protect/delete them afterward.

## Data Storage and Privacy

* Locate containers with `env` or bundle-ID metadata correlation, not `find -name <bundle-id>`.
* Typical path: `/var/mobile/Containers/Data/Application/<UUID>`; layout/access vary.
* Retrieve authorized files through SSH/SFTP or [Cyberduck](https://cyberduck.io/).

| Storage/Surface | Check |
| --- | --- |
| Plist / `NSUserDefaults` | Credentials, tokens, personal data, local roles. Plists can be XML/binary; defaults is an API. |
| SQLite / Core Data | Sensitive records, permissions, query inputs. Core Data is a framework, not synonymous with SQLite. |
| Keychain | Accessibility, access groups, authentication controls; separate from ordinary container files. |
| Cookies/credentials/cache/logs | Sensitive values and retention. |
| Pasteboard/memory/snapshots/keyboard | Exposure outside the intended interaction. |

### File and Database Inspection

```sh
find <application-data-root> -type d -name <known-container-uuid>
file <path-to-file>
sqlite3 <database-file>
```

```text
env
file cat <path-to-file>
file download <path-to-file>
sqlite connect <database-file>
ios nsuserdefaults get
ios nsurlcredentialstorage dump
ios plist cat Info.plist
ios keychain dump
ios cookies get
ios pasteboard monitor
```

### Keychain and Cookies

* [Keychain-Dumper](https://github.com/ptoomey3/Keychain-Dumper): create `/tmp/keychain`; transfer a compatible `keychain_dumper` via SFTP.
* In device SSH: `./keychain_dumper > keychain.txt`. Privileges/entitlements required; avoid collecting unrelated apps' data.
* SQLite: install `sqlite3` if needed; use `.tables` and limited read-only queries.
* BinaryCookiesReader: `pip install binarycookiesreader`; verify package provenance/version.
* Protect database/keychain/cookie/memory dumps; remove tools and output afterward.

### Optional and Legacy Tools

* [iRET](https://github.com/S3Jensen/iRET), [Cycript](https://www.cycript.org/) (inspection/injection/foreign-function calls), [QuickTime](https://support.apple.com/downloads/quicktime) (recording).
* [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump): release-specific Python/SSH setup; never hardcode credentials.
* Package sources: [Havoc](https://havoc.app/), [Shadow](https://ios.jjolano.me/), [Radare2](https://cydia.radare.org/), [Akemi](https://cydia.akemi.ai/), [opa334](https://opa334.github.io/).
* Utilities: `wget`, `ps`, `sqlite3`, `unzip`, `dpkg`, BigBoss tools.
* Verify provenance, maintenance, and jailbreak/iOS compatibility.

## URL Schemes, Web Views, and Client Behavior

* [ ] Custom/universal links: valid, malformed, unauthorized inputs; validate caller and parameters.
* [ ] WebViews: URL allowlists, JavaScript bridges, navigation, script injection/XSS. Native screens are not web pages.
* [ ] Business logic: alter test-only local state/replay requests; verify server authorization.
* [ ] Logs: Xcode Devices and Simulators or approved console.
* [ ] Pasteboard/keyboard: use non-sensitive test data.

* 3uTools: optional third-party inspection; consider privacy/provenance, not a replacement for Xcode.
* [MobSF](https://mobsf.github.io/docs/#/): dynamic iOS support depends on release/device setup.

## Decryption and Class Information

* FairPlay-encrypted app: use an authorized analysis copy only; do not redistribute decrypted/modified apps.
* Tools: [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump), [Clutch](https://github.com/KJCracks/Clutch), [bfinject](https://github.com/BishopFox/bfinject).
* Configure release-specific Python dependencies and secure SSH; example: `python dump.py <bundle-id>`. Never commit SSH passwords.
* Extract the app, identify its executable, and dump compatible Objective-C metadata:

```sh
class-dump <app-binary>
```

Alternatives: Objection class/method listing; Hopper, Ghidra, or IDA Free for binary analysis.

## Further Reading

* [Frida iOS documentation](https://frida.re/docs/ios/)
* [Objection](https://github.com/sensepost/objection)
* [Apple Platform Security](https://support.apple.com/guide/security/welcome/web)
* [HackTricks iOS testing checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/ios-pentesting-checklist)