# Preflight and Setup

## Mandatory Preflight

* **Version dependency:** host `frida`, device `frida-server`, and injected Gadget must use the **same exact Frida version**.
* `frida-tools` and Objection have independent version numbers; do not use them to select the server version.
* Recheck version compatibility after package upgrades.

* [ ] Device is connected, unlocked, and trusts the testing Mac; confirm the selected device.
* [ ] Choose a runtime path: jailbreak/server, Gadget-patched/signed app, or Frida injection into an authorized debuggable development build.
* [ ] iOS 16+ development-signed builds: enable **Settings > Privacy & Security > Developer Mode**, restart, and confirm.
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
* **Debuggable non-jailbroken path:** compatible Xcode/device support, Developer Disk Image/services, and matching cached Gadget; follow [Frida iOS setup](https://frida.re/docs/ios/#without-jailbreak).
* Developer Mode is for development workflows, not an App Store/TestFlight prerequisite. [Apple setup](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device).
* References: [Xcode documentation](https://developer.apple.com/documentation/xcode), [downloads](https://developer.apple.com/download/all/?q=Xcode).

## Jailbroken Test Device

* Use hardware/iOS-compatible jailbreaks.
* Cydia/Sileo: package managers; install only trusted OpenSSH and Frida packages (`https://build.frida.re` ).
* Match server and host `frida` library versions **exactly**; use supported architecture/platform builds.
* SSH: `root` / `alpine` default.
* Utilities: OpenSSH/SFTP, Filza, `apt-get`/`dpkg`
* Non-jailbroken device: use the patched/signed workflow in [App Patching and Signing](signing-and-app-patching.md)
* <pre class="language-bash" data-line-numbers><code class="lang-bash">ssh root@&#x3C;device-ip>
  </code></pre>
* **Attach/spawn:** [Frida and Objection connection commands](runtime-instrumentation.md#objection-session).

### Verify Client and Server Versions

* **Prerequisite:** configured SSH access to the test device.
* Run these checks on the Mac:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">frida --version
    pip3 show frida frida-tools objection
    ssh &#x3C;ssh-user>@&#x3C;device-ip> "frida-server --version"
    </code></pre>
* Client and server version outputs must match exactly; use the same host environment for Frida/Objection.
* If `frida-server` is not in the device's `PATH`, use its installed package path; rootless/rootful locations vary.
* Confirm the server service is running. After replacing it, restart via the package's supported service workflow.
