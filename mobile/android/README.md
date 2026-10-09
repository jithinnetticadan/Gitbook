# Android

Android testing follows reconnaissance, static analysis, dynamic analysis, and reporting. Test only applications and environments you are authorized to assess. Native screens are not automatically vulnerable to web XSS; consider WebViews and server-side effects of mobile requests where applicable.

## Testing Categories

* [Static Testing](static-testing.md)
* [Dynamic Testing](dynamic-testing.md)
* [References](references.md)

Android applications commonly run on Android Runtime (ART); older versions used Dalvik. Apps normally have separate Linux UIDs and sandboxed data. Cross-app access can occur through exposed activities, services, broadcast receivers, or content providers. Root access changes what a tester can inspect; it does not replace validation of the app's access controls.

Common paths include `/data/app/<package>` for installed artifacts, `/data/data/<package>` for private app data, and `/sdcard/Android/data/<package>` for app-specific external storage. Exact paths and access vary by Android version and device.

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
