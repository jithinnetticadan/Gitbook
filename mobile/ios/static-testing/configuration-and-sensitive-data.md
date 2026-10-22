# Configuration and Sensitive Data

{% hint style="info" %}
Record version, source, architecture, and original/extracted artifact hashes. Use authorized copies only; App Store binaries may be FairPlay-encrypted. Replace command placeholders before use.
{% endhint %}

## Configuration and Sensitive Data

* [ ] Search `Info.plist`, entitlements, URL schemes, JSON/resources, and strings.
* [ ] Find endpoints, test settings, credentials, tokens, keys, and sensitive data.
* [ ] Trace value use/impact; public identifiers are not automatically secrets.
* [ ] Review plist/`NSUserDefaults`, SQLite/Core Data, Keychain, logs, caches, and backups.
* [ ] Confirm storage behavior during [dynamic testing](../dynamic-testing/data-storage-and-privacy.md).
