# Platform and Version-Specific Tests

{% hint style="warning" %}
Separate application defects from device/OS vulnerabilities and explicitly granted capabilities. Use approved companion tools and disposable lab devices. Kernel/GPU exploits, pairing attacks, device-owner changes, wipe operations, and hardware testing require separate explicit scope; they are not routine app-test prerequisites.
{% endhint %}

## Record Applicability First

```sh
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell getprop ro.build.version.security_patch
adb shell getprop ro.build.fingerprint
```

Also record OEM/model, relevant GPU/driver, WebView/browser version, bootloader/root state, app target SDK, user/profile, and granted special access. Check the vendor's shipped fix/backport and current advisory; Android version or a spoofed property alone is insufficient evidence. Establish whether the entry applies before running a proof of concept.

## Permissions and User-Granted Capabilities

| Surface | Controlled Test | Boundary / Limitation |
| --- | --- | --- |
| Runtime permissions | Deny, revoke, select approximate location, or use one-time grants where supported | Verify graceful failure and least privilege; compare declared purpose, actual collection, and disclosures. |
| Accessibility service | Enable only an approved test service with explicit user consent; inspect events/actions exposed by sensitive flows | The service's binding permission is not an ordinary silent grant to any app. Record what the user enabled and what the OS permits. |
| Notification listener | Check synthetic OTP/message previews under actual consent, device-lock, and OS restrictions | Do not assume every listener receives every sensitive notification on every Android version. |
| Autofill / keyboard | Use an approved test provider/IME; inspect field classification, origin/account association, and sensitive values | Password autofill is legitimate functionality. A user-selected provider seeing intended data is not automatically an app flaw. |
| SMS Retriever / OTP | Verify app hash/recipient flow, receiver protection, challenge/account binding, expiry and reuse | Retriever does not grant arbitrary SMS inbox access. Distinguish SMS permission, user-consent APIs, and backend OTP validation. |
| Overlay / obscured touches | Use a harmless synthetic confirmation and approved overlay app | Record required special access; distinguish overlay tapjacking from animation/task-based attacks. |
| MediaProjection / recents | With explicit capture consent, test screen/region selection, background transitions, cancellation and secure screens | User-granted capture is not itself a bypass; identify unintended data capture or violated protection. OS versions differ in consent/session rules. |
| Foreground work / standby | Inspect service type/purpose, notification, permission, collection after backgrounding or logout, and battery exemptions | Persistent work can be legitimate; correlate collection with consent and user/session state. |
| All-files / scoped storage | Grant only approved permissions and inspect actual accessible paths/MediaStore/URI grants | `MANAGE_EXTERNAL_STORAGE` needs justification; it does not automatically expose all private app data. |
| VPN service | Observe an approved VPN's routing and compare TLS-protected data visibility | VPN consent permits routing, not automatic TLS decryption or bypass of app authentication. |
| Device admin / owner | Review configured policies, enrollment and app identity | Do not trigger lock/wipe or unenroll a real device. Device/profile-owner authority is distinct from legacy admin and ordinary app privileges. |
| Work/personal profiles | Test approved cross-profile links, file grants, clipboard, and chooser behavior with synthetic data | Record policies and both profiles' identities; manifest filters alone do not override enterprise policy. |
| USB / MIDI | Exercise known handlers using approved hardware and harmless inputs | Record physical access, permission prompts, device identity, and parser behavior. |
| Bluetooth / BLE / HID | Check scoped pairing, authenticated operations, application authorization, and test-device inputs | A Bluetooth-stack CVE is not an app flaw by association; radio tests must not affect nearby devices. |
| NFC | Send a controlled tag/URI to the app's declared dispatch path | Trace proximity-triggered data into links/intents and validate destination/input handling. |
| Wireless debugging | Review pairing/authentication, trusted hosts, exposure, and cleanup on the lab device | Knowing a port is not authentication. Distinguish modern paired TLS debugging from legacy exposed ADB; do not brute-force pairing codes. |

Restore grants, test providers, pairing records, profile policies, and capture/routing changes afterward. For biometric assurance and passkeys, use [authentication and cryptography](authentication-and-cryptography.md); lack of attestation or `BIOMETRIC_STRONG` needs a concrete policy/threat-model assessment.

## Research and Legacy Vulnerability Triage

These entries preserve useful research leads without treating each workbook label as a confirmed finding.

| Research / Identifier | Applicability and Evidence |
| --- | --- |
| [Pixnapping, CVE-2025-48561](https://pixnapping.com/) | Rendering/pixel side-channel research, not generic GPU code execution. The researchers report particular Pixel/Samsung devices and Android 13–16 builds; their page was last updated October 2025 and discusses incomplete initial mitigation. Check newer vendor advisories and actual builds; do not extrapolate to every device or promise that an app flag fixes it. |
| [TapTrap](https://taptrap.click/) | Animation-driven tapjacking differs from overlay permissions. The authors report Android 13–16 fixes in the December 2025 security update and separate browser fixes. Confirm the installed vendor/browser patch; use a harmless action if authorized testing is still applicable. |
| [CVE-2024-0044](https://rtx.meta.security/exploitation/2024/03/04/Android-run-as-forgery.html) | Installer-metadata/newline injection affecting `run-as`, with ADB prerequisites in the original research. Check exact version/fix and later advisory updates. This is **not Dirty Stream**. |
| [CVE-2024-31317](https://rtx.meta.security/exploitation/2024/06/03/Android-Zygote-injection.html) | Zygote command injection through privileged settings, not an ordinary unprivileged app's deserialization bug. Requires relevant settings-write authority; the disclosed fix is in the June 2024 bulletin. Device-specific platform testing needs explicit scope. |
| Janus, CVE-2017-13156 | Verify affected OS/package verifier, patch level, and accepted signature path. A v1 signature or low app target SDK alone does not establish applicability. |
| StrandHogg / CVE-2020-0096 | Distinguish manifest/task-affinity patterns from the historical platform task-hijacking vulnerability. Consult the [May 2020 Android bulletin](https://source.android.com/docs/security/bulletin/2020-05-01) and actual task transitions; do not apply old device assumptions universally. |
| Mali/Adreno or Bluetooth advisories | Match exact hardware, driver/firmware and vendor fix; for example, a Mali CVE is not applicable merely because the app renders graphics. GPU.zip/Pixnapping side channels and GPU driver memory-corruption CVEs are different issues. |
| Dirty Stream | An app-level untrusted file-provider metadata pattern; use [Advanced IPC and Content Providers](advanced-ipc-and-providers.md#dirty-stream-untrusted-provider-metadata), not an OS `run-as` recipe. |
| SafetyNet Attestation | Google [fully shut it down in January 2025](https://developer.android.com/privacy-and-security/safetynet/deprecation-timeline). Assess migration and failure handling; do not describe it as a currently functional fallback. |

For each research lead record: applicable / not applicable / unknown, primary advisory, checked date, exact prerequisites, observed evidence, fix status, and ownership (app, OS, browser, hardware, or backend). Do not copy generic severity labels, success rates, or research timings into a finding without validating the assessed environment.

**Previous:** [Local Data, Logs, and Privacy](local-data-logs-and-privacy.md) | **Next:** [Network Traffic and TLS](network-traffic-and-tls.md)