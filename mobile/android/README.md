# Android

* **Basic runtime tests:** [ADB/component prerequisites](dynamic-testing/component-testing.md#adb-probes-and-caller-identity); Frida/root are not universally required.
* **Instrumentation:** complete [Frida preflight](dynamic-testing/preflight-and-frida-setup.md#mandatory-preflight), including exact client/server/Gadget version matching.

## Quick Context

* ART (older Android: Dalvik); OS sandbox and separate app UIDs.
* Cross-app checks: activities, services, receivers, providers.
* Root aids inspection; it does not prove an app access-control flaw.
* Paths:&#x20;
  * `/data/app/<package>`
  * `/data/data/<package>`
  * `/sdcard/Android/data/<package>`
* XSS applies to web content/WebViews, not ordinary native screens. Also assess server-side request effects.

### Lab Setup

* [Frida-Launcher](https://github.com/thecybersandeep/Frida-Launcher)

## Testing Guides

{% file src="../../.gitbook/assets/Android Static Analysis.pdf" %}

{% file src="../../.gitbook/assets/Android Dynamic Analysis.pdf" %}

{% file src="../../.gitbook/assets/Android_Pentest_Master_Checklist.xlsx" %}
