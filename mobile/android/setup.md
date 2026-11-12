# Setup and Tools

## Host Tools

### Tool Index

* Install a Java JDK compatible with the selected JADX/Apktool releases and add command-line tools to `PATH`. Use current maintainer instructions; package availability varies by OS/release.
* **Android SDK:** [Android Studio](https://developer.android.com/studio), [Platform Tools / ADB](https://developer.android.com/tools/releases/platform-tools), [Android Emulator](https://developer.android.com/studio/run/emulator), [apkanalyzer](https://developer.android.com/tools/apkanalyzer), [AAPT2](https://developer.android.com/tools/aapt2), [apksigner](https://developer.android.com/tools/apksigner), [zipalign](https://developer.android.com/tools/zipalign), [bundletool](https://developer.android.com/tools/bundletool), and [Android NDK / LLVM](https://developer.android.com/ndk).
* **Java and decompilation:** [JDK / keytool and jarsigner](https://docs.oracle.com/en/java/javase/), [JADX / JADX-GUI](https://github.com/skylot/jadx), [Apktool](https://apktool.org/), [dex2jar](https://github.com/pxb1988/dex2jar), [JD-GUI](https://github.com/java-decompiler/jd-gui), [GDA](https://github.com/charles2gan/GDA-android-reversing-Tool), [APK Studio](https://github.com/vaibhavpandeyvpz/apkstudio), and [Bytecode Viewer](https://github.com/Konloch/bytecode-viewer).
* **Protector fingerprinting:** [APKiD](https://github.com/rednaga/APKiD) uses Python/YARA dependencies.
* **Runtime, IPC and device inspection:** [Frida, frida-tools and Gadget](https://frida.re/docs/), [Objection](https://github.com/sensepost/objection), [Drozer](https://github.com/ReversecLabs/drozer/), [RMS](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), [House](https://github.com/nccgroup/house), [Inspeckage](https://github.com/ac-pm/Inspeckage), [AndroidSpect](https://github.com/thecybersandeep/androidspect), [fridump3](https://github.com/rootbsd/fridump3/), [Android Keystore Audit scripts](https://github.com/ReversecLabs/android-keystore-audit/tree/master/frida-scripts), and [Frida CodeShare](https://codeshare.frida.re/). Drozer needs a compatible console and device agent; Frida server/Gadget must match the host Frida version.
* **Traffic and APIs:** [Burp Suite](https://portswigger.net/burp), [mitmproxy](https://mitmproxy.org/), [Proxyman](https://proxyman.io/), [curl](https://curl.se/), [OpenSSL](https://www.openssl.org/), [grpcurl](https://github.com/fullstorydev/grpcurl), [Chrome WebView inspection](https://developer.chrome.com/docs/devtools/remote-debugging/webviews/), [FlutterTap](https://github.com/script-or-script/FlutterTap), and [reFlutter](https://github.com/ptswarm/reFlutter).
* **Secrets, cloud and dependencies:** [APKLeaks](https://github.com/dwisiswant0/apkleaks), [OSV-Scanner](https://github.com/google/osv-scanner), [OWASP Dependency-Check](https://jeremylong.github.io/DependencyCheck/), [Trivy](https://trivy.dev/), [cloud\_enum](https://github.com/initstring/cloud_enum), [firebaseEnum](https://github.com/Sambal0x/firebaseEnum), [AWS CLI](https://aws.amazon.com/cli/), [TruffleHog](https://github.com/trufflesecurity/trufflehog), and [Gitleaks](https://github.com/gitleaks/gitleaks).
* **Native and framework recovery:** [Ghidra](https://github.com/NationalSecurityAgency/ghidra), [radare2 / rabin2](https://github.com/radareorg/radare2), [GNU binutils / readelf and strings](https://www.gnu.org/software/binutils/), [LLVM / libFuzzer](https://llvm.org/docs/LibFuzzer.html), [hermes-dec](https://github.com/P1sec/hermes-dec), [Il2CppDumper](https://github.com/Perfare/Il2CppDumper), and [pyxamstore](https://github.com/jakev/pyxamstore).
* **Data, signing and utilities:** [SQLite CLI](https://www.sqlite.org/cli.html), [DB Browser for SQLite](https://sqlitebrowser.org/), [Android Backup Extractor](https://github.com/nelenkov/android-backup-extractor), [Uber APK Signer](https://github.com/patrickfav/uber-apk-signer), [Node.js](https://nodejs.org/), [Python](https://www.python.org/), [PowerShell](https://learn.microsoft.com/powershell/), [GNU grep](https://www.gnu.org/software/grep/), and [Info-ZIP](https://infozip.sourceforge.net/) (`unzip`). Standard shell utilities such as `diff`, `tar`, `mkdir`, and `cp` depend on the host shell.
* **Automated and optional tools:** [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF), [adbauditor](https://adbauditor.com/), [MobSuite](https://mobsuite.app/#features), [thorfinn](https://github.com/PhonePe/thorfinn), [AndroHunter](https://github.com/ynsmroztas/AndroHunter), [MobiSuite-Mobile](https://github.com/nileshkale12/MobiSuite-Mobile), [QARK](https://github.com/linkedin/qark), [Androwarn](https://github.com/maaaaz/androwarn), [AndroBugs](https://github.com/AndroBugs/AndroBugs_Framework), [CuckooDroid](https://github.com/idanr1986/cuckoo-droid), [Ghost](https://github.com/EntySec/Ghost), [Santoku](https://github.com/santoku/Santoku-Linux), [PimpMyKali](https://github.com/Dewalt-arch/pimpmykali), and [Frida-Launcher](https://github.com/thecybersandeep/Frida-Launcher).
* **Virtual labs:** [Genymotion](https://www.genymotion.com/), [Corellium](https://www.corellium.com/), [Waydroid](https://waydro.id/), and [BlueStacks](https://www.bluestacks.com/). Waydroid uses a Linux container.
* **Scanning/signing:** use TruffleHog filesystem mode and Gitleaks directory mode for extracted artifacts; trace matches to their consumers. Uber APK Signer needs a compatible Java runtime and test key.

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
* **Server:** device ABI. **Gadget:** target app ABI, which may differ on a 64-bit device.
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
