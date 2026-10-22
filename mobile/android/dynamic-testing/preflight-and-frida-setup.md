# Preflight and Frida Setup

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
