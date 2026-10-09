# Android

Workflow: reconnaissance > static testing > dynamic testing > report. Use authorized apps/devices only.

## Testing Categories

* [Static Testing](static-testing.md)
* [Dynamic Testing](dynamic-testing.md)
* [References](references.md)

**Before runtime testing:** complete the [Mandatory Preflight](dynamic-testing.md#mandatory-preflight), including exact Frida client/server/Gadget version matching.

## Quick Context

* ART (older Android: Dalvik); OS sandbox and separate app UIDs.
* Cross-app checks: activities, services, receivers, providers.
* Root aids inspection; it does not prove an app access-control flaw.
* Paths: `/data/app/<package>`, `/data/data/<package>`, `/sdcard/Android/data/<package>`; layout/access vary.
* XSS applies to web content/WebViews, not ordinary native screens. Also assess server-side request effects.

### Static Analysis Tool

* [adbauditor](https://adbauditor.com/)
* [apkstudio](https://github.com/vaibhavpandeyvpz/apkstudio)

### Dynamic Analysis Tool

* [thorfinn](https://github.com/PhonePe/thorfinn)

### SSLPinning Bypass

* [FlutterTap](https://github.com/script-or-script/FlutterTap)

### Lab Setup

* [Frida-Launcher](https://github.com/thecybersandeep/Frida-Launcher)

{% file src="../../.gitbook/assets/Android Static Analysis.pdf" %}

{% file src="../../.gitbook/assets/Android Dynamic Analysis.pdf" %}

{% file src="../../.gitbook/assets/Android_Pentest_Master_Checklist.xlsx" %}
