# iOS Dynamic Testing

{% hint style="info" %}
Use an authorized test device, test build, and test account. Jailbreaking, app patching, traffic interception, and runtime instrumentation affect device/app integrity. Isolate the lab and restore it after testing.
{% endhint %}

## Lab Setup and Provisioning

Xcode on macOS supports device development and signing. Add an Apple ID in Xcode and create a development team/profile as permitted. Free developer accounts can support limited sideloading; course notes cite a seven-day profile lifetime, but limits and expiration periods change, so check current Apple requirements. Install and trust the test profile on the device through its device-management settings.

Simulator and physical devices may differ in architecture and behavior. Intel-host simulators commonly use x86_64, while Apple Silicon simulators can use ARM64; ARM64 Simulator and iOS device binaries still target different platforms. Validate device-specific or architecture-sensitive findings on representative physical hardware. Xcode includes an iOS Simulator; a jailbreak is not required for all runtime debugging of your own development builds.

A provisioning profile associates signing certificates, device identifiers, and app identifiers for testing. Retrieve an embedded profile from an app bundle or Xcode's built products where appropriate. Limited profiles may expire; verify profile and device authorization before testing.

For the source's Xcode workflow, create a minimal development app, select the team and a connected test device, and build/install it. In Products, reveal the built `.app` in Finder and inspect its package contents for `embedded.mobileprovision`. This is the correct filename, not `embedded.mobileprovisioning`. Its allowed App ID, entitlements, and devices must match the app being signed; a profile from any arbitrary app is not sufficient. See [Xcode documentation](https://developer.apple.com/documentation/xcode) and [Xcode downloads](https://developer.apple.com/download/all/?q=Xcode).

List signing identities and sign an authorized app using the selected workflow:

```sh
security find-identity -v -p codesigning
applesign -L
applesign -i <signing-identity> -m <embedded.mobileprovision> <app.ipa>
```

The source misspells the npm package as `appliesign`; [applesign](https://github.com/nowsecure/node-applesign) is the tool intended (`npm install -g applesign` where appropriate for the lab). Confirm input types and options with `applesign --help` for the installed release.

### Non-Jailbroken App Patching

Objection's `patchipa` command embeds Frida Gadget in a suitable IPA and re-signs it:

```sh
objection patchipa --help
objection patchipa --source <app.ipa> --codesign-signature <signing-identity> --provision-file <embedded.mobileprovision>
```

This preserves the source's `-c` signing-identity option using its descriptive long form. The [maintainer CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py) defines `--provision-file` (`-P`); check installed help for release-specific requirements. Compatible signing assets and a suitable unencrypted executable are needed. Not every App Store IPA can be patched, re-signed, or installed by this workflow. `security find-identity` lists identities; it does not generate provisioning profiles or determine their expiration.

Use current Apple signing documentation; third-party signing tools and syntax can change. Preserve original artifacts and do not redistribute modified apps.

## Jailbroken Test Device

Use a dedicated device and a jailbreak compatible with its exact iOS/device version. Historical notes mention checkra.in, Cydia, Sileo, and the Frida repository `https://build.frida.re`; support changes frequently, so consult current maintainers. Install OpenSSH and a compatible Frida server from trusted sources.

The notes also mention palera1n. Neither it nor checkra1n is a universal jailbreak for all hardware/iOS releases. Verify Frida server/client versions and supported architecture before connecting. Cydia/Sileo are package managers, not assurance that a package is trustworthy.

Install Frida client tools and Objection on the macOS host. Connect over an isolated network. Historical notes use `root` / `alpine`; these are well-known default credentials and must never be retained. Change credentials, restrict SSH, and remove access after testing.

Common lab utilities on jailbroken devices include OpenSSH/SFTP, a file manager such as Filza, and the package manager's `apt-get`/`dpkg` tools. Availability depends on the jailbreak and package manager; install only from trusted sources. Non-jailbroken runtime instrumentation is a separate workflow: patch an authorized app to include the required Frida library, then re-sign it with a provisioning profile that permits installation on the test device. This process is more constrained and may not work for every app.

```sh
ssh root@<device-ip>
frida-ps -Uai
objection --name <app-process-name> start
```

## Traffic Analysis and TLS

Configure Burp Suite or another authorized proxy listener on the analysis host; set the device Wi-Fi proxy to the host/port. Install the CA profile and explicitly enable certificate trust in Certificate Trust Settings. Keep the CA on the test device only and remove it when done. See [Burp Suite Mobile Assistant](https://portswigger.net/burp/documentation/desktop/tools/mobile-assistant/installing).

For a physical iPhone, `127.0.0.1:8080` points to the phone, not the Mac. Use the Mac's reachable lab IP and listener port; "All interfaces" is the course option, but restrict the listener to the lab with a firewall. Open `http://burp` through the configured proxy, install the CA profile under VPN & Device Management, then enable trust under General > About > Certificate Trust Settings (labels vary by iOS release). Renaming a certificate file does not change its format or trust state. The historical Mobile Assistant package-source example is `http://<mac-ip>:8080`; verify the current installation guide before using it.

Inspect requests for authentication, authorization, input validation, sensitive data, and server-side behavior. Test pinning only in scope. Options from the notes:

* Objection command: `ios sslpinning disable`.
* [SSL Kill Switch 2](https://github.com/nabla-c0d3/ssl-kill-switch2) or [SSL Kill Switch 3](https://github.com/NyaMisty/ssl-kill-switch3/releases) on a compatible jailbroken test device.
* Burp Mobile Assistant and app-specific instrumentation.
* AppSync has historically been used on jailbroken devices to alter code-signing behavior; it is not a general certificate-trust control. Prefer explicit test-CA installation and trust configuration, and use only a compatible, isolated lab device.

Pinning bypass is a test technique; report the underlying validation behavior and impact, not the bypass itself as a vulnerability.

## Runtime Analysis and Instrumentation

List/attach to apps with Frida, or trace Objective-C methods:

```sh
frida-ps -Uai
frida -U -n <app-process-name>
frida-trace -U -m '*[NSURLRequest *]' <app-process-name>
objection --name <app-process-name> start
```

In Objective-C method selectors, `-` denotes an instance method and `+` a class method. Use `frida-ps -Uai | grep '<app-name-fragment>'` to find identifiers; attaching by process name differs from spawning by bundle ID. All Objection shell examples follow the supplied current help: `--name` selects the target and `start` opens a session. A Gadget-injected app can expose a Gadget-specific process name; select the actual target rather than assuming a bundle ID always works for attachment.

Additional connection and session examples:

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

`--local` selects a local iOS Simulator connection; it is not the USB/physical-device workflow and still requires a compatible instrumentation setup. Global options (`--name`, `--serial`, `--local`, `--spawn`, `--no-pause`) go before `start` or `run`; session options go after `start`. Use long names to avoid confusing global `-s` (spawn) with subcommand short options. `--no-pause` requests immediate resume; omit it if early instrumentation needs a paused spawn. `run` executes a single command without an interactive session; use `start` for persistent monitoring rather than assuming one-shot hooks remain active after exit.

Useful commands inside the Objection prompt (not directly in the host shell):

```text
env
ios hooking list classes
ios hooking list class_methods
ios hooking watch class <class-name>
ios hooking watch method <method-name> --dump-args --dump-return --dump-backtrace
ios sslpinning disable
ios jailbreak disable
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

Top-level `objection --help` does not define interactive command syntax. Command availability and arguments vary by release; consult in-session help/current documentation rather than inferring replacements from the top-level CLI. Hestia, Shadow, or Objection jailbreak checks can help assess detection behavior on compatible test devices. Alternative tools include [Runtime Mobile Security](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security) and [Grapefruit](https://github.com/ChiChou/grapefruit). r2frida can inspect authorized processes; consult its installed version's help for connection and command syntax.

Install Frida tools and Objection using the recommended installer or an isolated environment (`pip3 install frida-tools` and `pip3 install objection` in the source workflow). Objection installs Frida dependencies. Current startup examples are:

```sh
objection --name <app-process-name> start --startup-command 'ios jailbreak disable'
objection --name <app-process-name> start --startup-command 'ios sslpinning disable'
```

`--startup-command` and `--startup-script` are `start` options confirmed by the checked [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py), not global options listed by top-level help. Verify them against `objection start --help` for the installed build. Alternatively, identify and instrument the app's detection method, then validate the effect; a local return-value change does not establish a server-side privilege bypass.

An example r2frida session from the notes is:

```text
r2 frida://spawn//usb//<bundle-id>
:i?
:ic~<class-or-string>
:dtf <function-address>
```

Use the plugin's current help for exact syntax and interpret addresses in the active process session. After an authorized memory dump, `strings <dump-file>` can help identify readable values; protect and securely remove the dump.

## Data Storage and Privacy

App data is commonly under `/var/mobile/Containers/Data/Application/<UUID>`, but paths vary. Use Objection `env` to identify directories. On an authorized jailbroken device, SSH/SFTP or [Cyberduck](https://cyberduck.io/) can retrieve files.

Do not expect `find ... -name <bundle-id>` to locate UUID-named containers. Use runtime paths from `env` or correlate container metadata with the bundle identifier. Property lists can be XML **or binary**, and `NSUserDefaults` is a preferences API, not a separate database format. Core Data is an object persistence framework that can use SQLite, not simply a synonym for SQLite. The Keychain is separate from ordinary app-container files and should be assessed by item accessibility, access groups, and authentication controls.

Inspect:

* Property lists and `NSUserDefaults` for credentials, tokens, personal data, and mutable authorization state.
* SQLite and Core Data for sensitive records, access control, and unsafe query behavior.
* Keychain accessibility/access controls and data protection.
* Cookies, URL credentials, caches, logs, clipboard/pasteboard data, and in-memory secrets.
* App-switcher snapshots and keyboard/input behavior.

Commands and Objection operations from the notes:

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

`keychain-dumper` is another noted tool for authorized jailbroken-device tests. Transfer it securely, protect its output, and remove it after use. Treat database, keychain, memory, and cookie dumps as sensitive data.

The source's [Keychain-Dumper](https://github.com/ptoomey3/Keychain-Dumper) example creates `/tmp/keychain`, transfers a compatible `keychain_dumper` binary over SFTP, and runs `./keychain_dumper > keychain.txt` in the device SSH session. Appropriate privileges/entitlements are required and results may include data outside the target app; restrict collection to the agreed scope. SQLite may require a separately installed `sqlite3` client; use `.tables` and limited read-only test queries. For cookie-file analysis the notes name BinaryCookiesReader (`pip install binarycookiesreader`); inspect its provenance and release requirements before installing.

Additional tools listed in the notes include [iRET](https://github.com/S3Jensen/iRET), [Cycript](https://www.cycript.org/) (legacy runtime inspection, injection, and foreign-function calls), and [QuickTime Player](https://support.apple.com/downloads/quicktime) for supported device recording. [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump) may require Python dependencies and SSH access; follow its current documentation, enter credentials securely, and never hardcode them in scripts or source control. Historical jailbreak package sources include [Havoc](https://havoc.app/), [Shadow](https://ios.jjolano.me/), [Radare2](https://cydia.radare.org/), [Akemi](https://cydia.akemi.ai/), and [opa334](https://opa334.github.io/); verify legitimacy and device compatibility before use. The notes also list `wget`, `ps`, `sqlite3`, `unzip`, `dpkg`, and BigBoss utilities. Availability depends on the jailbreak; legacy tools may not support current iOS releases.

## URL Schemes, Web Views, and Client Behavior

Exercise custom URL schemes and universal links with valid, malformed, and unauthorized inputs. Confirm the app validates callers and parameters before opening resources or performing actions. For apps using web views, test URL allowlists, JavaScript bridges, navigation, and web content for script injection/XSS. Native screens are not themselves web pages.

Test business logic by changing local test data and replaying requests, then verify server-side authorization. Review logs in Xcode Devices and Simulators or an approved device console. Assess pasteboard and keyboard behavior with non-sensitive test data.

The source also names 3uTools for device/log inspection. Treat it as an optional third-party utility with privacy/provenance considerations, not a substitute for Xcode's supported logging workflow. MobSF automated dynamic analysis is another source-note option; iOS dynamic support depends on the selected MobSF release and compatible device setup. See the [MobSF documentation](https://mobsf.github.io/docs/#/).

## Decryption and Class Information

App Store binaries may use FairPlay encryption. For authorized analysis, tools from the notes include [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump), [Clutch](https://github.com/KJCracks/Clutch), and [bfinject](https://github.com/BishopFox/bfinject). Use only copies obtained and processed within authorization; do not redistribute decrypted or modified apps.

Follow the selected tool's current installation instructions for its Python dependencies and device SSH setup. A typical invocation is `python dump.py <bundle-id>` after configuring a secure device connection; do not put SSH passwords in scripts or source control.

For Objective-C class metadata, extract the bundle, identify its executable, then run `class-dump` where compatible:

```sh
class-dump <app-binary>
```

Objection can also list classes/methods. Hopper, Ghidra, and IDA Free are alternatives for binary analysis.

## Further Reading

* [Frida iOS documentation](https://frida.re/docs/ios/)
* [Objection](https://github.com/sensepost/objection)
* [Apple Platform Security](https://support.apple.com/guide/security/welcome/web)
* [HackTricks iOS testing checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/ios-pentesting-checklist)