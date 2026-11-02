# Configuration and Sensitive Data

## Configuration and Sensitive Data

* **macOS terminal, extracted app:** plist, entitlements, provisioning profile, and readable resource secrets.
	* ```bash
		plutil -p '<Application.app>/Info.plist'
		codesign -d --entitlements :- '<Application.app>'
		security cms -D -i '<Application.app>/embedded.mobileprovision'
		grep -RniE 'password|api[_-]?key|secret|token|https?://' '<Application.app>' --include='*.json' --include='*.xml' --include='*.js' --include='*.txt'
		strings '<app-binary>' | grep -iE 'https?://|password|api[_-]?key|secret|token'
		```
* **ATS and privacy descriptions:** inspect the printed plist for `NSAppTransportSecurity`, exception domains, and permission usage strings. Distribution builds may omit an embedded provisioning profile.
* **Data protection and backup APIs:** inspect binary selectors/strings, then exercise the corresponding file operation at runtime.
	* ```bash
		strings '<app-binary>' | grep -E 'NSFileProtection|NSURLIsExcludedFromBackupKey|kSecAttrAccessible|kSecAttrAccessGroup|kSecAttrSynchronizable'
		```

* [ ] Search `Info.plist`, entitlements, URL schemes, JSON/resources, and strings.
* [ ] Find endpoints, test settings, credentials, tokens, keys, and sensitive data.
* [ ] Trace value use/impact; public identifiers are not automatically secrets.
* [ ] Review plist/`NSUserDefaults`, SQLite/Core Data, Keychain, logs, caches, and backups.
* [ ] Confirm storage behavior during [dynamic testing](../dynamic-testing/data-storage-and-privacy.md).
