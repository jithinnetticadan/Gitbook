# Setup and Tools

## Host Tools

* Install a Java JDK compatible with the selected JADX/Apktool releases; add command-line tools to `PATH`.
* [JADX](https://github.com/skylot/jadx) / JADX-GUI - decompile DEX and inspect resources.
* [Apktool](https://apktool.org/) - decode resources and SMALI; compare its output with JADX.
* [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) - automated analysis. Use release-specific setup instructions; the course's `setup.bat` / `run.bat` and `setup.sh` / `run.sh` are historical examples.
* [dex2jar](https://github.com/pxb1988/dex2jar) and [JD-GUI](https://github.com/java-decompiler/jd-gui) - alternate DEX-to-JAR workflow.
* [APKLeaks](https://github.com/dwisiswant0/apkleaks) - search APKs for exposed strings and configuration.
* Android Studio and Android SDK Platform Tools - device/package management and artifact acquisition.
* `keytool`, `jarsigner`, `zipalign`, and Android SDK signing tools - inspect or prepare test artifacts when repackaging is authorized.
* Legacy/optional: [Androwarn](https://github.com/maaaaz/androwarn), Andrubis, ApkAnalyser, [QARK](https://github.com/linkedin/qark), [Santoku project repository](https://github.com/santoku/Santoku-Linux), [PimpMyKali](https://github.com/Dewalt-arch/pimpmykali). Verify maintenance and compatibility.
* Use current maintainer instructions; package availability varies by OS/release.

### Optional Tools

| Purpose                  | Options                                                          | Prerequisite / Limitation                                                                                                                                                                    |
| ------------------------ | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Native review            | Ghidra, radare2, NDK/LLVM tools                                  | Match ABI/build; use supported Java/runtime requirements for the selected tool release.                                                                                                      |
| Protector fingerprinting | [APKiD](https://github.com/rednaga/APKiD)                        | Install its supported Python/YARA dependencies; fingerprints are leads, not an authoritative inventory of library versions.                                                                  |
| Alternate decompilers    | GDA, Bytecode Viewer, APK Studio                                 | Verify current platform/runtime support and compare output against SMALI; no decompiler guarantees original source recovery.                                                                 |
| Secret scanning          | TruffleHog filesystem mode, Gitleaks directory mode, APKLeaks    | Use current CLI help and scan extracted artifacts; trace matched values to their actual consumer and privileges.                               |
| Re-signing               | [Uber APK Signer](https://github.com/patrickfav/uber-apk-signer) | Requires a compatible Java runtime; choose/record a test key. It does not possess production keys or bypass update-signature checks.                                                         |
| Runtime UI helpers       | RMS, House, Inspeckage                                           | RMS/House releases have their own Frida/container dependencies. Inspeckage is Xposed-based, not just a Frida wrapper; review maintenance and device compatibility.                           |
| Virtual labs             | Android Emulator, Genymotion, Corellium, Waydroid                | Check host/guest/ABI support and licensing. Waydroid uses a Linux container environment, not a native Windows emulator. Hardware-backed assurance needs evidence from the relevant hardware. |
| Proxy helpers            | Burp, compatible Android proxy/CA utilities                      | An iOS-only Burp Mobile Assistant workflow is not an Android setup. Verify platform support; a preconfigured emulator does not ensure the app trusts its CA.                                 |
| Historical scanners      | AndroBugs, QARK and older suites                                 | Label legacy/unmaintained output; do not downgrade the lab or treat scanner silence as coverage.                                                                                             |

### Windows

* Install a compatible Java **JDK**, Android Studio, JADX, and Apktool.
* Get [SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) directly or through Android Studio's SDK Manager.
* Extract to a tools directory; add it to `PATH`. Do not copy into `C:\Windows`.
* Follow [Apktool installation](https://apktool.org/docs/install/) and JADX release instructions.

### Kali Linux

* Install packages available for the selected distribution:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">sudo apt-get update
    sudo apt-get install adb apktool default-jdk jadx
    java --version
    jadx-gui
    </code></pre>
* Install Android Studio separately.
* PimpMyKali is optional; it does not guarantee every tool is installed.
* MobSF: use dependencies/setup for the selected release, not another release's `requirements.txt`.

### macOS

* **Prerequisite:** review and install [Homebrew](https://brew.sh/) before running:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">brew install jadx apktool android-platform-tools
    jadx-gui
    apktool --version
    </code></pre>
* Install Android Studio separately.
  * Verify ADB using the [device connection commands](dynamic-testing/component-testing.md#adb-probes-and-caller-identity).

* Optional launcher: [Frida-Launcher](https://github.com/thecybersandeep/Frida-Launcher); verify device and version support.

## App and Device Preparation

* Collect the APK, required splits/resources/native libraries; record package/version, min/target SDK, and device Android/API level.
* Connect the device or start the emulator; enable USB debugging and accept the host authorization prompt.
* **Connection and ABI:**

  * ```bash
    adb devices -l
    adb shell getprop ro.build.version.release
    adb shell getprop ro.build.version.sdk
    adb shell getprop ro.product.cpu.abilist
    ```

* With multiple devices, use `adb -s <serial> <command>`. [App acquisition/install variants](static-testing/acquire-and-decompile.md).
* **Repackaging:** include required splits/libraries, align, sign, verify, then install. [Patching commands](dynamic-testing/app-patching.md).
* **Proxy/CA:** [Network Traffic and TLS](dynamic-testing/network-traffic-and-tls.md); app CA trust and pinning are separate checks.
* Basic [ADB/component tests](dynamic-testing/component-testing.md#adb-probes-and-caller-identity) do not require Frida or root.

## Device and Frida Setup

* Use a compatible Android Studio emulator or test device.
* **Runtime path:** root-accessible Frida server or an app patched with Gadget.
* **Root / kernel details:**
* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb shell su -c id
  adb shell cat /proc/version
  adb shell cat /proc/cpuinfo
  </code></pre>
* **Server:** device ABI. **Gadget:** target app ABI, which may differ on a 64-bit device.&#x20;
* Install client tools in an isolated environment:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">pip3 install frida-tools
    pip3 install objection
    objection version
    objection --help
    objection start --help
    </code></pre>
* Match the host `frida` library and device server **exactly.**
* Gadget uses the same exact Frida version. `frida-tools` and Objection have independent version numbers.
* Objection installs Frida dependencies and can change the installed version.
* Current CLI: `objection [OPTIONS] COMMAND [ARGS]...`; `--name` selects, `start` opens a session.
* Subcommand options: check installed help and [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py).

### Start Frida Server

* Download the matching version/ABI from [Frida releases](https://github.com/frida/frida/releases), extract the `.xz`, and name the extracted binary `frida-server` for these commands.
* **Transfer the server once, then choose the root-adbd or su startup variant:**
  * ```bash
    adb push frida-server /data/local/tmp/frida-server
    ```
* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb root
  adb shell "chmod 755 /data/local/tmp/frida-server"
  adb shell "/data/local/tmp/frida-server &#x26;"
  # OR #
  adb shell "su -c 'chmod 755 /data/local/tmp/frida-server'"
  adb shell "su -c '/data/local/tmp/frida-server &#x26;'"
  </code></pre>

### Verify Client and Server Versions

* <pre class="language-bash" data-line-numbers><code class="lang-bash">frida --version
  pip3 show frida frida-tools objection
  adb shell /data/local/tmp/frida-server --version
  </code></pre>
* `frida --version` and `frida-server --version` must match exactly.
* Use the same host environment for Frida and Objection.
* **ADB connection:** [device selection and authorization commands](dynamic-testing/component-testing.md#adb-probes-and-caller-identity).
* List installed apps:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">frida-ps -Uai
    </code></pre>
* **Runtime sessions:** [Frida CLI and Objection attach/spawn variants](dynamic-testing/objection-and-runtime-instrumentation.md#attach-or-spawn).
