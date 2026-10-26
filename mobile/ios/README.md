# iOS

* **Basic runtime tests:** authorized app/accounts and [proxy setup](dynamic-testing/traffic-analysis-and-tls.md); jailbreak/Frida are not universally required.
* **Instrumentation:** complete [lab preflight](dynamic-testing/preflight-and-lab-setup.md#mandatory-preflight), including exact Frida client/server/Gadget version matching.

## Quick Context

* IPA bundles contain executable, metadata, resources, and property lists.
* Instrumentation setup: compatible jailbreak, or an authorized debuggable/Gadget-signed development build.
* Xcode/macOS: Apple signing/development; free accounts have provisioning limits/expiry.
* Validate device-specific findings on representative hardware; Simulator behavior differs.
* Assess URL handling and web content in `WKWebView`/other web views.

### JailBreak Bypass

* HideJB: legacy jailbreak-detection tweak; verify device/iOS compatibility, not a universal bypass.

### Static Analysis Tool

* [ipaauditor](https://ipaauditor.com/)
* [ipascope](https://github.com/sudouday/ipascope)

### Lab Setup

* [Frida-Launcher](https://github.com/thecybersandeep/Frida-Launcher)
* [lautarovculic/ioscpy](https://github.com/lautarovculic/ioscpy)

{% file src="../../.gitbook/assets/Palera1n.pdf" %}
