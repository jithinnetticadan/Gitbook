# Preflight and Setup

## Mandatory Preflight

{% hint style="warning" %}
* **Version dependency:** host `frida`, device `frida-server`, and injected Gadget must use the **same exact Frida version**.
* `frida-tools` and Objection have independent version numbers; do not use them to select the server version.
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
* Identify the device architecture before selecting Frida server:
* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb shell getprop ro.product.cpu.abilist
  adb shell cat /proc/version
  adb shell cat /proc/cpuinfo
  </code></pre>
* **Server:** device ABI. **Gadget:** target app ABI, which may differ on a 64-bit device.&#x20;
* Install client tools in an isolated environment:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">pip3 install frida-tools
    pip3 install objection
    frida --version
    objection version
    objection --help
    objection start --help
    </code></pre>
* Match the host `frida` library and device server **exactly.**
* Objection installs Frida dependencies and can change the installed version.
* Current CLI: `objection [OPTIONS] COMMAND [ARGS]...`; `--name` selects, `start` opens a session.
* Subcommand options: check installed help and [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py).

### Start Frida Server

* Download the matching version/ABI from [Frida releases](https://github.com/frida/frida/releases), extract the `.xz`, and name the extracted binary `frida-server` for these commands.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb root
  adb push frida-server /data/local/tmp/frida-server
  adb shell "chmod 755 /data/local/tmp/frida-server"
  adb shell "/data/local/tmp/frida-server &#x26;"
  # OR #
  adb push frida-server /data/local/tmp/frida-server
  adb shell "su -c 'chmod 755 /data/local/tmp/frida-server'"
  adb shell "su -c '/data/local/tmp/frida-server &#x26;'"
  </code></pre>

### Verify Client and Server Versions

* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb devices -l
  frida --version
  pip3 show frida frida-tools objection
  adb shell /data/local/tmp/frida-server --version
  </code></pre>
* `frida --version` and `frida-server --version` must match exactly.
* Use the same host environment for Frida and Objection.
* List installed apps and attach:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">frida-ps -Uai
    frida -U -n &#x3C;process-name>
    objection --name &#x3C;process-name> start
    </code></pre>
