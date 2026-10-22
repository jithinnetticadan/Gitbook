# Preflight and Lab Setup

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
* Intel Simulator: commonly x86\_64; Apple Silicon Simulator: ARM64. Simulator/device ARM64 binaries still target different platforms.
* Validate hardware-sensitive findings on a physical device. Your own development builds need not be jailbroken for debugging.
* Profile filename: `embedded.mobileprovision`, not `embedded.mobileprovisioning`. An arbitrary app's profile may not fit.

References: [Xcode documentation](https://developer.apple.com/documentation/xcode), [downloads](https://developer.apple.com/download/all/?q=Xcode).

## Jailbroken Test Device

* Use hardware/iOS-compatible jailbreaks; checkra1n (`checkra.in`) and palera1n are not universal.
* Cydia/Sileo: package managers; install only trusted OpenSSH and Frida packages (`https://build.frida.re` in the notes).
* Match server and host `frida` library versions **exactly**; use supported architecture/platform builds.
* SSH: change historical `root` / `alpine` defaults; isolate/restrict access and remove it afterward.
* Utilities: OpenSSH/SFTP, Filza, `apt-get`/`dpkg`; availability varies.
* Non-jailbroken device: use the patched/signed workflow in [Signing and App Patching](signing-and-app-patching.md); app restrictions apply.

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
