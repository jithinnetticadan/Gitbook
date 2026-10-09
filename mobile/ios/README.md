# iOS

Use a reconnaissance, static analysis, dynamic analysis, and reporting workflow. Test only applications and devices in scope. Apps may include web content in `WKWebView` or other web views, so assess URL handling and web content where present.

## Testing Categories

* [Static Testing](static-testing.md)
* [Dynamic Testing](dynamic-testing.md)
* [References](references.md)

iOS apps are commonly distributed as `.ipa` archives. Extracted bundles contain an executable, metadata, resources, and property lists. Runtime access to protected data and process instrumentation generally requires a suitable test setup, such as a jailbroken device or correctly signed and provisioned test build.

Xcode on macOS is used for Apple development and signing workflows. Free developer accounts can support limited device testing; current provisioning restrictions and expiration periods depend on Apple account requirements. Simulator behavior may differ from physical ARM devices, so validate device-specific conclusions on representative hardware where possible.

### JailBreak Bypass

* HideJB - Cydia App

### Static Analysis Tool

* [ipaauditor](https://ipaauditor.com/)
* [ipascope](https://github.com/sudouday/ipascope)

### Lab Setup

* [Frida-Launcher](https://github.com/thecybersandeep/Frida-Launcher)
* [lautarovculic/ioscpy](https://github.com/lautarovculic/ioscpy)
