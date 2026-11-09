# Setup and Tools

## Host Tools

* macOS + Xcode/Command Line Tools for Apple binary tools; full Xcode for development/signing and the source-built VM workflow.
* [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - automated static analysis.
* `otool` and [MachOView](https://sourceforge.net/projects/machoview/) - inspect Mach-O headers, load commands, and symbols. `otool` is provided by Xcode/Apple Command Line Tools.
* [class-dump](http://stevenygard.com/projects/class-dump/) - Objective-C interfaces. Legacy `class-dump-z` is not automatically interchangeable.
* [Hopper](https://www.hopperapp.com/), [Ghidra](https://github.com/NationalSecurityAgency/ghidra/), and [IDA Free](https://hex-rays.com/ida-free) - disassembly and reverse engineering.
* Flawfinder and Clang Static Analyzer can assist with authorized source code.
* [radare2](https://rada.re/n/) (`rabin2`, `r2`), [iRET](https://github.com/S3Jensen/iRET), [LIEF](https://lief.re/), `pagestuff` - additional binary tools; verify support and install requirements.
* [AnyTrans](https://www.imobie.com/anytrans/download.htm), iMazing - authorized artifact management; acquisition restrictions apply.
* **Signing/development dependencies:** macOS and Xcode; follow current installation/license requirements.
* Host helpers <sup><sub>(Optional)<sub></sup>: [Frida-Launcher](https://github.com/thecybersandeep/Frida-Launcher), [ioscpy](https://github.com/lautarovculic/ioscpy), and [Cyberduck](https://cyberduck.io/) for SFTP. Verify support for the selected device and connection.

## App Preparation

* **Extract the IPA and identify the executable, on macOS:**
  * ```bash
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
* Intel Simulator: commonly x86\_64; Apple Silicon Simulator: ARM64. Simulator/device ARM64 binaries still target different platforms.
* Validate hardware-sensitive findings on a physical device. Your own development builds need not be jailbroken for debugging.
* Profile filename: `embedded.mobileprovision`, not `embedded.mobileprovisioning`. An arbitrary app's profile may not fit.
* **Debuggable non-jailbroken path:** compatible Xcode/device support, Developer Disk Image/services, and matching cached Gadget; follow [Frida iOS setup](https://frida.re/docs/ios/#without-jailbreak).
* Developer Mode is for development workflows, not an App Store/TestFlight prerequisite. [Apple setup](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device).
* References: [Xcode documentation](https://developer.apple.com/documentation/xcode), [downloads](https://developer.apple.com/download/all/?q=Xcode).

## Jailbroken Physical Test Device

* Select a jailbreak matching the device/iOS version.
* **SSH connection choices, on the Mac** <sup><sub>(Alternatives; select the device's account/port)<sub></sup>:
  * ```bash
    ssh root@<device-ip>
    ssh mobile@<device-ip>
    ssh -p <ssh-port> <ssh-user>@<device-ip>
    ```
* Initial password in the source lab: `alpine`; account/port depend on the bootstrap.
* Non-jailbroken device: use [App Patching and Signing](dynamic-testing/signing-and-app-patching.md).

## Virtual Jailbroken iPhone on Apple Silicon

* Runs ARM iOS apps in a virtual iPhone, not an Xcode Simulator.
* **Requirements:** physical Apple Silicon Mac (M1+), macOS 15+, approximately 100 GB free, full Xcode, Homebrew, and Python 3.10+.
* **Sileo/TrollStore environment:** use the pinned revision below. Current releases use Launchpad/Irisin instead; do not mix the two workflows.

### 1. Enter macOS Recovery and Configure the Host

* Shut down the Mac using Apple menu > Shut Down.
* Press and hold the power button until **Loading startup options** appears.
* Select **Options > Continue**. Select the startup volume/admin account and authenticate if prompted.
* In Recovery, open **Utilities > Terminal**.
* **Full-SIP-disable path, in Recovery Terminal:**
  * ```bash
    csrutil disable
    csrutil allow-research-guests enable
    reboot
    ```
* **After logging back into macOS, open Terminal:**
  * ```bash
    sudo nvram boot-args="amfi_get_out_of_my_way=1 -v"
    sudo shutdown -r now
    ```
* **Partial-SIP path** <sup><sub>(Alternative to full SIP disable)<sub></sup>: in Recovery Terminal:
  * ```bash
    csrutil enable --without debug
    csrutil allow-research-guests enable
    reboot
    ```
* For partial SIP, use the AMFI helper in step 3; omit the `nvram` command above.

### 2. Install Host Tools

* Install full **Xcode** from the App Store and launch it once to complete component installation.
* **Select Xcode and finish first-run setup, in macOS Terminal:**
  * ```bash
    sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
    sudo xcodebuild -license accept
    sudo xcodebuild -runFirstLaunch
    xcodebuild -version
    ```
* **Install Homebrew if absent, as the normal macOS user:**
  * ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
    ```
* **Install dependencies:**
  * ```bash
    brew install python@3.12 ideviceinstaller wget gnu-tar openssl@3 ldid-procursus sshpass keystone autoconf automake pkg-config libtool cmake
    export PATH="$(brew --prefix python@3.12)/libexec/bin:$PATH"
    python3 --version
    ```
* `make setup_tools` also installs/builds the remaining dependencies and creates the project's Python environment. Run Homebrew and `make` as the normal user, not from a root shell.

### 3. Build the iOS 26.1 VM with Sileo and TrollStore

* **Clone the source and select the revision containing the Makefile targets:**
  * ```bash
    git clone https://github.com/Lakr233/vphone-cli.git
    cd vphone-cli
    git checkout 30fcc05ca57a727033b4cf2cfd41ba4c0a4c96ab
    git submodule update --init --recursive
    ```
* **Partial-SIP helper** <sup><sub>(Alternative path; required only with partial SIP)<sub></sup>: from this directory, install the tools and start the AMFI helper before setup/boot.
  * ```bash
    make setup_tools
    xcrun python3 -m pip install amfidont
    make amfidont_allow_vphone
    ```
* **Create the jailbroken iOS 26.1 VM:**
  * ```bash
    make setup_machine JB=1 IPHONE_VERSION=26.1 IPHONE_BUILD=23B85
    ```
* Setup builds the VM, downloads/prepares firmware, enters virtual DFU, restores/installs patched firmware, and performs the first boot. No physical-iPhone recovery-button sequence is needed.
*   **Other setup variants** <sup><sub>(Alternatives; select one instead of the command above)<sub></sup>:

    | Variant                     | Command                                                                                 |
    | --------------------------- | --------------------------------------------------------------------------------------- |
    | Jailbreak, default firmware | `make setup_machine JB=1`                                                               |
    | Regular                     | `make setup_machine`                                                                    |
    | Development                 | `make setup_machine DEV=1`                                                              |
    | Local firmware pair         | `make setup_machine JB=1 IPHONE_SOURCE="<iPhone.ipsw>" CLOUDOS_SOURCE="<cloudOS.ipsw>"` |

### 4. Boot and Finish Device Setup

* **Subsequent boots, from the same `vphone-cli` directory:**
  * ```bash
    make boot
    ```
* **Partial-SIP path** <sup><sub>(Alternative path; required only with partial SIP)<sub></sup>: after a host restart, run `make amfidont_allow_vphone` before `make boot`.
* Complete the iOS setup screens. Open **Sileo** and **TrollStore** from the Home Screen.
* **Inspect the jailbreak setup log** <sup><sub>(Optional; troubleshooting)<sub></sup>: in the VM console:
  * ```bash
    cat /var/log/vphone_jb_setup.log
    ```

### Current Upstream <sup><sub>(Alternative)<sub></sup>

* **Separate from the pinned Sileo VM:** install Launchpad and its matching `VPhone.bundle`. Distributed bundles need no Xcode/Homebrew at runtime.
* Enter macOS Recovery as in step 1 and use the partial-SIP commands. Launchpad handles VM allowlisting; standalone CLI prints the required command during preflight.
* **Create with a supported local firmware pair and roothide bootstrap:**
  * ```bash
    vphone-cli host preflight
    vphone-cli vm create ios-lab \
      --iphone-source "<iPhone17,3_Restore.ipsw>" \
      --cloudos-source "<cloudOS.ipsw>" \
      --bootstrap roothide
    vphone-cli vm launch ios-lab
    ```
* **Resource overrides** <sup><sub>(Optional)<sub></sup>: `--cpu 8 --memory 8192 --disk-size 64`. **Network choices** <sup><sub>(Alternatives)<sub></sup>: `--network nat` or `--network bridged`. CFW installation requires root privileges.
* **Existing VM without packages:** Apps > Install Bootstrap > roothide; in Irisin, install `owngoal-bootstrap-vphone` using **Bootstrap Install**.
* This bootstrap uses Irisin, not Sileo/TrollStore.
* **List / stop:**
  * ```bash
    vphone-cli vm list
    vphone-cli vm stop ios-lab
    ```

### Virtual Device SSH and Frida Connectivity <a href="#virtual-device-ssh-and-frida-connectivity" id="virtual-device-ssh-and-frida-connectivity"></a>

* **Pinned Sileo VM:** install OpenSSH in Sileo and reboot the VM.
* **Mac Terminal 1:** keep the SSH forwarder running:
  * ```bash
    iproxy 2222 22
    ```
* **Mac Terminal 2:** connect to the forwarded port:
  * ```bash
    ssh -p 2222 mobile@127.0.0.1
    ```
* **Initial password:** `alpine`. **Direct guest-IP connection** <sup><sub>(Alternative to localhost forwarding)<sub></sup>: `ssh mobile@<vm-ip>`; guest port 22, forwarded host port 2222.
* **After completing Frida installation below, verify from the Mac** <sup><sub>(Alternative transports; select one of the<sub></sup> <sup><sub> </sup><sup><sub>`frida-ps`<sub></sup> <sup><sub> </sup><sup><sub>commands)<sub></sup>:
  * ```bash
    frida-ls-devices
    frida-ps -Uai
    frida-ps -D <device-id> -ai
    frida-ps -H <forwarded-host>:<frida-port> -ai
    ```
* `-U`: USB; `-D`: selected device; `-H`: separately configured Frida network endpoint. SSH port 2222 is not a Frida endpoint.
* **VM proxy:** Settings > Ethernet > Ethernet > Configure Proxy > Manual; server = guest-reachable Mac IP, port = Burp listener port. Complete [CA installation/trust](dynamic-testing/traffic-analysis-and-tls.md#proxy-setup).
* **Next:** [keychain/storage](dynamic-testing/data-storage-and-privacy.md), [runtime/memory](dynamic-testing/runtime-instrumentation.md).
* **Physical-device validation:** hardware-backed Keychain/SEP, biometrics, NFC/camera, attestation, and Apple services are not fully represented by the VM.

## Sileo Repositories and Device Utilities <a href="#sileo-repositories-and-device-utilities" id="sileo-repositories-and-device-utilities"></a>

* **Physical jailbroken device / Sileo-based VM:** Sileo > Sources > + > add URL > refresh.
* Packages must match iOS, architecture, and bootstrap layout (rootful/rootless/roothide).

| Source URL                    | Packages / Purpose                                                               |
| ----------------------------- | -------------------------------------------------------------------------------- |
| `https://build.frida.re/`     | Official Frida server.                                                           |
| `https://ellekit.space/`      | ElleKit tweak injection.                                                         |
| `https://ios.jjolano.me/`     | Shadow.                                                                          |
| `https://repo.misty.moe/apt/` | NyaMisty packages / SSL Kill Switch 3.                                           |
| `https://opa334.github.io/`   | Choicy and opa334 utilities.                                                     |
| `https://havoc.app/`          | General packages; commonly preconfigured.                                        |
| `https://apt.procurs.us/`     | Procursus Unix packages; preserve the bootstrap's configured suite/architecture. |

* **Historical sources, not verified as usable:** BigBoss (`http://apt.thebigboss.org/repofiles/cydia/`, HTTP 403); Radare (`https://cydia.radare.org/`, certificate mismatch); Akemi (`https://cydia.akemi.ai/`, timeout; legacy AppSync Unified).
* **Install through Sileo search:**
  * Access/files: OpenSSH, Filza, NewTerm or NewTerm 3 Beta, wget, `ps`, `sqlite3`, `unzip`.
  * Debugging/binaries: LLDB, odcctools.
  * Tweaks: ElleKit, Choicy, Shadow, SSL Kill Switch 3.
  * AFC filesystem access: Apple File Conduit "2".
* **Package inventory / refresh, in the guest shell:**
  * ```bash
    dpkg -l
    sudo apt-get update
    ```
* **Legacy Burp Mobile Assistant source:** `http://<mac-ip>:8080`, served by a compatible local Burp installation. The installation guide has been retired; use the [current iOS proxy/CA setup](https://portswigger.net/burp/documentation/desktop/mobile/config-ios-device) for traffic interception.

## Host Frida and Objection <a href="#host-frida-and-objection" id="host-frida-and-objection"></a>

* Host `frida`, server, and Gadget must use the **same exact Frida version**; `frida-tools` and Objection have independent version numbers.
* **Create and activate the host environment, on the Mac:**
  * ```bash
    python3 -m venv .venv-ios
    source .venv-ios/bin/activate
    ```
* **Pinned iOS 26.1 Sileo VM:**
  * ```bash
    python -m pip install "frida==17.9.0" "frida-tools==14.8.0" "objection==1.12.4"
    python -m pip check
    ```
* **Current-version tools** <sup><sub>(Alternative to the pinned install)<sub></sup>:
  * ```bash
    python -m pip install frida-tools objection
    frida --version
    python -m pip show frida frida-tools objection
    objection --help
    objection start --help
    ```
* Install the same exact server version through Sileo or Frida releases. Server architecture/bootstrap must match the guest/device.
* **Matching 17.9.0 server, in the VM's SSH session:**
  * ```bash
    sudo -i
    cd /tmp
    wget https://github.com/frida/frida/releases/download/17.9.0/frida_17.9.0_iphoneos-arm64.deb
    dpkg -i frida_17.9.0_iphoneos-arm64.deb
    frida-server --version
    ```
* **Manual server startup** <sup><sub>(Alternative to the package service; only if no server is running)<sub></sup>:
  * ```bash
    frida-server -D
    ```
* **Frida 17+ memory dumper** <sup><sub>(Optional)<sub></sup>: in the Mac's activated environment:
  * ```bash
    python -m pip install fridump3
    python -m pip check
    fridump3 --help
    frida --version
    ```
* [Memory-dump commands](dynamic-testing/runtime-instrumentation.md#optional-fridump3-memory-capture).

### Verify Client and Server Versions

* **Prerequisite:** configured SSH access to the selected guest/device.
* On the Mac:
  * ```bash
    frida --version
    python -m pip show frida frida-tools objection
    ssh <ssh-user>@<device-ip> "frida-server --version"
    ```
* **Localhost SSH forwarding** <sup><sub>(Alternative to direct device IP)<sub></sup>: for the historical VM, replace the last command with `ssh -p 2222 mobile@127.0.0.1 "frida-server --version"`.
* Client/server versions must match **exactly**; use the installed server path if absent from `PATH`.
* List apps with the [selected transport](setup.md#virtual-device-ssh-and-frida-connectivity), then [attach with Frida/Objection](dynamic-testing/runtime-instrumentation.md#objection-session).

## References

* [vphone-cli repository](https://github.com/Lakr233/vphone-cli)
* [Pinned Sileo/TrollStore revision and Makefile instructions](https://github.com/Lakr233/vphone-cli/tree/30fcc05ca57a727033b4cf2cfd41ba4c0a4c96ab)
* [Virtual iPhone build and host setup](https://mrbypass.medium.com/mastering-vphone-cli-part-1-building-a-jailbroken-ios-26-1-virtual-iphone-on-apple-silicon-06ed5a4b13d2)
* [Sileo, SSH, Frida, and proxy configuration](https://mrbypass.medium.com/mastering-vphone-cli-part-2-configuring-the-jailbroken-ios-26-1-b10d964a9103)
* [Current release: Quick Start](https://lakr233.github.io/vphone-cli/get-started/quick-start.html), [Host Setup](https://lakr233.github.io/vphone-cli/get-started/host-setup.html), [firmware compatibility](https://lakr233.github.io/vphone-cli/firmware/compatibility.html), [CLI workflow](https://lakr233.github.io/vphone-cli/machines/create-and-run.html), [package environment](https://lakr233.github.io/vphone-cli/machines/package-environment.html).
* [Frida server releases](https://github.com/frida/frida/releases)
* [fridump3.1](https://github.com/Xenorf/fridump3.1)
