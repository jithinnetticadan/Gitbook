# iOS

Workflow: reconnaissance > static testing > dynamic testing > report. Use authorized apps/devices only.

## Testing Categories

* [Static Testing](static-testing/README.md)
* [Dynamic Testing](dynamic-testing/README.md)
* [References](references.md)

**Before runtime testing:** complete the [Mandatory Preflight](dynamic-testing/preflight-and-lab-setup.md#mandatory-preflight), including exact Frida client/server/Gadget version matching.

## Quick Context

* IPA bundles contain executable, metadata, resources, and property lists.
* Runtime setup: compatible jailbroken device or signed/provisioned test build.
* Xcode/macOS: Apple signing/development; free accounts have provisioning limits/expiry.
* Validate device-specific findings on representative hardware; Simulator behavior differs.
* Assess URL handling and web content in `WKWebView`/other web views.

### JailBreak Bypass

* HideJB - Cydia App

### Static Analysis Tool

* [ipaauditor](https://ipaauditor.com/)
* [ipascope](https://github.com/sudouday/ipascope)

### Lab Setup

* [Frida-Launcher](https://github.com/thecybersandeep/Frida-Launcher)
* [lautarovculic/ioscpy](https://github.com/lautarovculic/ioscpy)

{% file src="../../.gitbook/assets/Palera1n.pdf" %}
