# iOS Static Testing

{% hint style="info" %}
Record version, source, architecture, and original/extracted artifact hashes. Use authorized copies only; App Store binaries may be FairPlay-encrypted. Replace command placeholders before use.
{% endhint %}

Work through the pages in order. Each page is self-contained, so you can jump straight to the category you need.

| Step | Page | Use When |
| --- | --- | --- |
| 1 | [Preflight, Tools, and IPA](preflight-tools-and-ipa.md) | Setting up the lab, extracting the IPA, and checking encryption state. |
| 2 | [Binary Analysis](binary-analysis.md) | Checking PIE, canaries, ARC, encryption, risky APIs, and disassembly. |
| 3 | [URL Handling](url-handling.md) | Reviewing custom schemes, universal links, and inter-app requests. |
| 4 | [Configuration and Sensitive Data](configuration-and-sensitive-data.md) | Searching plists, entitlements, strings, and storage locations for secrets. |

After static review, continue with [iOS Dynamic Testing](../dynamic-testing/README.md).

## Further Reading

* [OWASP iOS Testing Guide](https://mobile-security.gitbook.io/mobile-security-testing-guide/ios-testing-guide/0x06a-platform-overview)
* [Apple Platform Security](https://support.apple.com/guide/security/welcome/web)
* [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
* [HackTricks iOS testing checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/ios-pentesting-checklist)
* [Basic Guide to iOS Pentesting](https://www.bugcrowd.com/resources/levelup/a-basic-guide-to-ios-testing-in-2022/)
* [DVIA-v2 iOS training app](https://github.com/prateek147/DVIA-v2)
* [iOS tool notes linked in the source](https://www.allysonomalley.com/?s=iOS+Pentesting+Tools)
