# Setup and Tools

## Host Tools

* macOS + Xcode/Command Line Tools for Apple binary tools; full Xcode for development/signing and the source-built VM workflow.
* [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - automated static analysis.
* `otool` and [MachOView](https://sourceforge.net/projects/machoview/) - inspect Mach-O headers, load commands, and symbols. `otool` is provided by Xcode/Apple Command Line Tools.
* [class-dump](http://stevenygard.com/projects/class-dump/) - Objective-C interfaces. Legacy `class-dump-z` is not automatically interchangeable.
* [Hopper](https://www.hopperapp.com/), [Ghidra](https://ghidra-sre.org/), and [IDA Free](https://hex-rays.com/ida-free/) - disassembly and reverse engineering.
* Flawfinder and Clang Static Analyzer can assist with authorized source code.
* [radare2](https://rada.re/n/) (`rabin2`, `r2`), [iRET](https://github.com/S3Jensen/iRET), [LIEF](https://lief-project.github.io/), `pagestuff` - additional binary tools; verify support and install requirements.
* [Historical Veracode iRET](https://www.veracode.com/sites/default/files/Resources/Tools/iRETTool.zip) - distributions may differ or be unmaintained.
* [AnyTrans](https://www.imobie.com/anytrans/download.htm), iMazing - authorized artifact management; acquisition restrictions apply.
* **Signing/development dependencies:** macOS and Xcode; follow current installation/license requirements.
* Optional host helpers: [Frida-Launcher](https://github.com/thecybersandeep/Frida-Launcher), [ioscpy](https://github.com/lautarovculic/ioscpy), and [Cyberduck](https://cyberduck.io/) for SFTP. Verify support for the selected device and connection.

## App Preparation

* **Extract the IPA and identify the executable, on macOS:**

  ```bash
  unzip "<app.ipa>" -d "<extracted-directory>"
  plutil -p "<extracted-directory>/Payload/<Application>.app/Info.plist"
  /usr/libexec/PlistBuddy -c "Print :CFBundleExecutable" "<extracted-directory>/Payload/<Application>.app/Info.plist"
  file "<app-binary>"
  otool -hv "<app-binary>"
  otool -l "<app-binary>" | grep -A 5 LC_ENCRYPT
  ```

* Use `CFBundleExecutable` to resolve `<app-binary>`. ZIP extraction does not decrypt the executable; class extraction/disassembly needs an unencrypted copy when `cryptid` is nonzero.
* Device and Simulator ARM64 binaries target different platforms; inspect Mach-O platform/load commands before selecting tooling or Gadget.

<table><thead><tr><th width="254">Location</th><th>Inspect</th></tr></thead><tbody><tr><td><code>Payload/&#x3C;Application>.app/</code></td><td>Executable, resources, property lists.</td></tr><tr><td><code>Payload/&#x3C;Application>.app/Info.plist</code></td><td>Bundle ID, executable name, URL types, permission descriptions.</td></tr><tr><td><code>iTunesMetadata.plist</code></td><td>Distribution metadata, if present.</td></tr><tr><td>Profile/signature files</td><td>Signing and provisioning metadata, if included.</td></tr></tbody></table>

## Device and Provisioning Setup

* **Physical device:** connect, unlock, and trust the Mac.
* **Runtime path:** physical/virtual jailbreak + server, Gadget-patched/signed app, or debuggable development build.
* **iOS 16+ development-signed builds:** Settings > Privacy & Security > Developer Mode > restart > confirm.
* **Gadget:** match app architecture and device/Simulator platform.
* **Non-jailbroken install:** unencrypted executable, signing identity/private key, and matching provisioning profile/device/entitlements. [Patching/signing commands](dynamic-testing/signing-and-app-patching.md).
* **Proxy/CA:** [Network Traffic and TLS](dynamic-testing/traffic-analysis-and-tls.md#proxy-setup). Basic URL/proxy tests do not require Frida or jailbreak.

1. On macOS/Xcode, add your Apple ID and select a permitted development team.
2. Build/install a minimal app on the test device; trust the developer/profile in device-management settings.
3. Products > reveal `.app` in Finder > package contents > `embedded.mobileprovision`.
4. Verify the profile's App ID, entitlements, allowed devices, and expiry match the target.

* Free accounts support limited sideloading; notes cite seven-day profiles. Check current Apple limits.
* Intel Simulator: commonly x86_64; Apple Silicon Simulator: ARM64. Simulator/device ARM64 binaries still target different platforms.
* Validate hardware-sensitive findings on a physical device. Your own development builds need not be jailbroken for debugging.
* Profile filename: `embedded.mobileprovision`, not `embedded.mobileprovisioning`. An arbitrary app's profile may not fit.
* **Debuggable non-jailbroken path:** compatible Xcode/device support, Developer Disk Image/services, and matching cached Gadget; follow [Frida iOS setup](https://frida.re/docs/ios/#without-jailbreak).
* Developer Mode is for development workflows, not an App Store/TestFlight prerequisite. [Apple setup](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device).
* References: [Xcode documentation](https://developer.apple.com/documentation/xcode), [downloads](https://developer.apple.com/download/all/?q=Xcode).

## Jailbroken Physical Test Device

* Select a jailbreak matching the device/iOS version.
* Install OpenSSH through [Sileo/Cydia sources](#sileo-repositories-and-device-utilities).
* **SSH variants, on the Mac:**

  ```bash
  ssh root@<device-ip>
  ssh mobile@<device-ip>
  ssh -p <ssh-port> <ssh-user>@<device-ip>
  ```

* Initial password in the source lab: `alpine`; account/port depend on the bootstrap.
* Non-jailbroken device: use [App Patching and Signing](dynamic-testing/signing-and-app-patching.md).

## Virtual Jailbroken iPhone on Apple Silicon

[vphone-cli](https://github.com/Lakr233/vphone-cli) runs ARM iOS binaries through Apple's Virtualization.framework/PCC infrastructure; it is not an Xcode Simulator.

Sources: Akash Katare's [Part 1: build](https://mrbypass.medium.com/mastering-vphone-cli-part-1-building-a-jailbroken-ios-26-1-virtual-iphone-on-apple-silicon-06ed5a4b13d2) and [Part 2: configure](https://mrbypass.medium.com/mastering-vphone-cli-part-2-configuring-the-jailbroken-ios-26-1-b10d964a9103). **Article workflow:** Makefile + JB/Sileo. **Current upstream:** Launchpad/`VPhone.bundle` + optional Irisin bootstrap.

### Host Preparation

* **Host:** physical Apple Silicon Mac (M1+), macOS 15+, approximately 100 GB free. Nested macOS VMs are unsupported.
* **Makefile build:** full Xcode, completed first-run/license setup, Homebrew; run build commands as the normal macOS user.
* **Firmware:** supported iPhone IPSW/cloudOS pair; [compatibility list](https://lakr233.github.io/vphone-cli/firmware/compatibility.html).
* **Article host configuration, in macOS Recovery:**

  ```bash
  csrutil disable
  csrutil allow-research-guests enable
  ```

* **After restarting into macOS:**

  ```bash
  sudo nvram boot-args="amfi_get_out_of_my_way=1 -v"
  ```

* Restart again. For the partial-SIP variant, use the alternative below instead.

### Article-Compatible JB and Sileo Workflow

* **Pinned Makefile revision:** [`30fcc05`](https://github.com/Lakr233/vphone-cli/tree/30fcc05ca57a727033b4cf2cfd41ba4c0a4c96ab). Its README documents iOS 26.1 and the targets below; current `main` no longer has these targets.
* **Clone and build the JB VM:**

  ```bash
  git clone https://github.com/Lakr233/vphone-cli.git
  cd vphone-cli
  git checkout 30fcc05ca57a727033b4cf2cfd41ba4c0a4c96ab
  git submodule update --init --recursive
  make setup_machine JB=1
  ```

* **Setup variants** - choose one:

  | Variant | Command |
  | ------- | ------- |
  | Jailbreak: Sileo + TrollStore | `make setup_machine JB=1` |
  | Regular | `make setup_machine` |
  | Development | `make setup_machine DEV=1` |
  | Specific iPhone firmware | `make setup_machine JB=1 IPHONE_VERSION=26.1 IPHONE_BUILD=23B85` |

* **Subsequent boots:**

  ```bash
  make boot
  ```

* **Partial-SIP host variant:** in Recovery, run `csrutil enable --without debug` and `csrutil allow-research-guests enable`, then restart. In the source directory, install/start the AMFI helper before setup/boot:

  ```bash
  make setup_tools
  xcrun python3 -m pip install amfidont
  make amfidont_allow_vphone
  ```

* **First boot:** Sileo/TrollStore appear after JB finalization. For stalled setup, inspect `/var/log/vphone_jb_setup.log` from the guest shell.
* Continue with [Sileo packages](#sileo-repositories-and-device-utilities), SSH, and Frida below.

### Current Upstream Alternative

* Install Launchpad and its matching `VPhone.bundle`: [Quick Start](https://lakr233.github.io/vphone-cli/get-started/quick-start). Distributed bundles need no Xcode/Homebrew at runtime.
* **Host:** in Recovery, run `csrutil enable --without debug` and `csrutil allow-research-guests enable`, then restart. Launchpad handles VM allowlisting; standalone CLI prints the command during preflight. [Host Setup](https://lakr233.github.io/vphone-cli/get-started/host-setup.html).
* **Create with a supported local firmware pair and roothide bootstrap:**

  ```bash
  vphone-cli host preflight
  vphone-cli vm create ios-lab \
    --iphone-source "<iPhone17,3_Restore.ipsw>" \
    --cloudos-source "<cloudOS.ipsw>" \
    --bootstrap roothide
  vphone-cli vm launch ios-lab
  ```

* **Creation variants:** `--cpu 8 --memory 8192 --disk-size 64`; `--network nat` or `--network bridged`. CFW installation requires root privileges; see the [CLI workflow](https://lakr233.github.io/vphone-cli/machines/create-and-run.html).
* **Existing VM without packages:** Apps > Install Bootstrap > roothide; in Irisin, install `owngoal-bootstrap-vphone` using **Bootstrap Install**. [Package Environment](https://lakr233.github.io/vphone-cli/machines/package-environment.html).
* Current bootstrap uses Irisin, not the articles' Sileo/TrollStore environment.
* **List / stop:**

  ```bash
  vphone-cli vm list
  vphone-cli vm stop ios-lab
  ```

### Virtual Device SSH and Frida Connectivity

* **Makefile JB VM:** install OpenSSH in Sileo. On the Mac, keep the forwarder running in one terminal and connect from another:

  ```bash
  iproxy 2222 22
  ```

  ```bash
  ssh -p 2222 mobile@127.0.0.1
  ```

* **Initial password:** `alpine`. **Direct guest-IP variant:** `ssh mobile@<vm-ip>`; guest port 22, forwarded host port 2222.
* **Frida transport variants, on the Mac:**

  ```bash
  frida-ls-devices
  frida-ps -Uai
  frida-ps -D <device-id> -ai
  frida-ps -H <forwarded-host>:<frida-port> -ai
  ```

* `-U`: USB; `-D`: selected device; `-H`: configured Frida network endpoint. SSH port 2222 is not a Frida endpoint.
* **VM proxy:** Settings > Ethernet > Ethernet > Configure Proxy > Manual; server = guest-reachable Mac IP, port = Burp listener port. Complete [CA installation/trust](dynamic-testing/traffic-analysis-and-tls.md#proxy-setup).
* **Next:** [keychain/storage](dynamic-testing/data-storage-and-privacy.md), [runtime/memory](dynamic-testing/runtime-instrumentation.md).
* **Physical-device validation:** hardware-backed Keychain/SEP, biometrics, NFC/camera, attestation, and Apple services are not fully represented by the VM.

## Sileo Repositories and Device Utilities

* **Physical jailbroken device / Sileo-based VM:** Sileo > Sources > + > add URL > refresh.
* Packages must match iOS, architecture, and bootstrap layout (rootful/rootless/roothide).

| Source URL | Packages / Purpose |
| ---------- | ------------------ |
| `https://build.frida.re/` | Official Frida server. |
| `https://ellekit.space/` | ElleKit tweak injection. |
| `https://ios.jjolano.me/` | Shadow. |
| `https://repo.misty.moe/apt/` | NyaMisty packages / SSL Kill Switch 3. |
| `https://opa334.github.io/` | Choicy and opa334 utilities. |
| `https://havoc.app/` | General packages; default in the article's lab. |
| `https://apt.procurs.us/` | Procursus Unix packages; preserve the bootstrap's configured suite/architecture. |
| `http://apt.thebigboss.org/repofiles/cydia/` | BigBoss packages; legacy HTTP source. |
| `https://cydia.radare.org/` | radare tooling; legacy source. |
| `https://cydia.akemi.ai/` | Karen/Akemi packages, including legacy AppSync Unified. |

* **Install through Sileo search:**
  * Access/files: OpenSSH, Filza, NewTerm or NewTerm 3 Beta, wget, `ps`, `sqlite3`, `unzip`.
  * Debugging/binaries: LLDB, odcctools.
  * Tweaks: ElleKit, Choicy, Shadow, SSL Kill Switch 3.
  * AFC filesystem access: Apple File Conduit "2".
* **Package inventory / refresh, in the guest shell:**

  ```bash
  dpkg -l
  sudo apt-get update
  ```

* **Burp Mobile Assistant source:** `http://<mac-ip>:8080`; use the [PortSwigger workflow](https://portswigger.net/burp/documentation/desktop/tools/mobile-assistant/installing) for supported devices. This is the local Burp server, not a public repository.

## Host Frida and Objection

* Host `frida`, server, and Gadget must use the **same exact Frida version**; `frida-tools` and Objection have independent version numbers.
* **Current host tools, on the Mac:**

```bash
python3 -m venv .venv-ios
source .venv-ios/bin/activate
python -m pip install frida-tools objection
frida --version
python -m pip show frida frida-tools objection
objection --help
objection start --help
```

* Install the same exact server version through Sileo or [Frida releases](https://github.com/frida/frida/releases). Server architecture/bootstrap must match the guest/device.

* **Part 2's reported working versions** - alternative to the current host install:

```bash
python -m pip install "frida==17.9.0" "frida-tools==14.8.0" "objection==1.12.4"
python -m pip check
```

* **Matching 17.9.0 server, in the article's guest:**

  ```bash
  sudo -i
  cd /tmp
  wget https://github.com/frida/frida/releases/download/17.9.0/frida_17.9.0_iphoneos-arm64.deb
  dpkg -i frida_17.9.0_iphoneos-arm64.deb
  frida-server --version
  ```

* **Manual startup variant** - when the package has not already started a server service:

  ```bash
  frida-server -D
  ```

* **Optional Frida 17+ memory dumper, on the Mac:** [fridump3.1](https://github.com/Xenorf/fridump3.1).

```bash
python -m pip install fridump3
python -m pip check
fridump3 --help
frida --version
```

* [Memory-dump commands](dynamic-testing/runtime-instrumentation.md#optional-fridump3-memory-capture).

### Verify Client and Server Versions

* **Prerequisite:** configured SSH access to the selected guest/device.
* On the Mac:

  ```bash
  frida --version
  python -m pip show frida frida-tools objection
  ssh <ssh-user>@<device-ip> "frida-server --version"
  ```

* For the historical VM's localhost SSH forward, replace the last command with `ssh -p 2222 mobile@127.0.0.1 "frida-server --version"`.
* Client/server versions must match **exactly**; use the installed server path if absent from `PATH`.
* List apps with the [selected transport](#virtual-device-ssh-and-frida-connectivity), then [attach with Frida/Objection](dynamic-testing/runtime-instrumentation.md#objection-session).
