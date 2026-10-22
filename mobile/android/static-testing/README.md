# Android Static Testing

{% hint style="info" %}
Test only in-scope apps. Record package, version, source, device/API level, and original APK hash. Replace command placeholders before use.
{% endhint %}

Work through the pages in order. Each page is self-contained, so you can jump straight to the category you need.

| Step | Page | Use When |
| --- | --- | --- |
| 1 | [Preflight and Tools](preflight-and-tools.md) | Setting up the lab; installing JADX, Apktool, MobSF, and platform tools. |
| 2 | [Acquire and Decompile](acquire-and-decompile.md) | Pulling the APK and reading its code and resources. |
| 3 | [App Architecture](app-architecture.md) | Understanding sandbox, UIDs, paths, and signing before judging findings. |
| 4 | [Manifest and Components](manifest-and-components.md) | Reviewing permissions, exported components, backup, debug, and cleartext settings. |
| 5 | [Secrets and Cloud](secrets-and-cloud.md) | Searching for credentials, endpoints, Firebase, and cloud assets. |
| 6 | [Configuration and Cryptography](configuration-and-cryptography.md) | Reviewing signing, TLS validation, and cryptographic use. |
| 7 | [Local Data and Client Logic](local-data-and-client-logic.md) | Reviewing storage, logging, screen protection, client-side authorization, and SQL input. |
| 8 | [WebView, IPC, and Dependency Checks](webview-ipc-and-dependencies.md) | Reviewing WebView, provider SQLi, path traversal, deep links, PendingIntent, dependencies, and quick triage. |

After static review, continue with [Android Dynamic Testing](../dynamic-testing/README.md).

## Further Reading

* [OWASP Mobile Security Testing Guide: Android](https://mobile-security.gitbook.io/mobile-security-testing-guide/android-testing-guide/0x05b-basic-security_testing)
* [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
* [HackTricks Android checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/android-checklist)
* [Intro to Mobile Pentesting](https://www.hackthebox.com/blog/intro-to-mobile-pentesting)
* [OWASP mobile testing overview](https://mobile-security.gitbook.io/mobile-security-testing-guide/overview/0x03-overview)
* [HackTricks Android app pentesting](https://book.hacktricks.xyz/mobile-pentesting/android-app-pentesting)
* Vidhan Thakur, "Android Static Application Security Testing" (PDF; included on the [Android page](../README.md))
