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
* **Extracted-app secret scanners:** select either tool for the same `.app` bundle used above. Inspect the matching file and consuming code to determine whether the value grants unintended access.

{% tabs %}
{% tab title="TruffleHog" %}
* **macOS Terminal:**
	* ```bash
		trufflehog filesystem '<Application.app>' --no-verification
		```
{% endtab %}
{% tab title="Gitleaks" %}
* **macOS Terminal:**
	* ```bash
		gitleaks dir -v '<Application.app>'
		```
{% endtab %}
{% tab title="MobSF" %}
* Upload the acquired IPA to a compatible MobSF instance; inspect the static findings and bundle files for the actual key/endpoint and its use.
{% endtab %}
{% endtabs %}

* **Data protection and backup APIs:** inspect binary selectors/strings, then exercise the corresponding file operation at runtime.
	* ```bash
		strings '<app-binary>' | grep -E 'NSFileProtection|NSURLIsExcludedFromBackupKey|kSecAttrAccessible|kSecAttrAccessGroup|kSecAttrSynchronizable'
		```

* [ ] Search `Info.plist`, entitlements, URL schemes, JSON/resources, and strings.
* [ ] Find endpoints, test settings, credentials, tokens, keys, and sensitive data.
* [ ] Trace value use/impact; public identifiers are not automatically secrets.
* [ ] Review plist/`NSUserDefaults`, SQLite/Core Data, Keychain, logs, caches, and backups.
* [ ] Confirm storage behavior during [dynamic testing](../dynamic-testing/data-storage-and-privacy.md).

## Search Result to Test

| Static result | Concrete runtime check | Confirm |
| --- | --- | --- |
| ATS exception / custom trust code | [Certificate variants](../dynamic-testing/traffic-analysis-and-tls.md#original-app-tls-negative-tests) | Original app accepts an invalid certificate or sends the sensitive operation over HTTP. |
| File protection selector / stored marker | [File attribute/read probe](../dynamic-testing/data-storage-and-privacy.md#file-protection-attribute-and-read-probe) | Fresh read works in a device state prohibited by the file's required protection. |
| Keychain accessibility/access control | [No-prompt item query](../dynamic-testing/data-storage-and-privacy.md#keychain-query-one-item-without-a-prompt) | The actual item or protected key operation is usable without required authentication. |
| URL scheme / WebView handler | [Route and bridge payloads](../dynamic-testing/client-side-testing.md) | External input reaches protected data/native behavior, not just a screen. |
| Embedded token/key | [API identity/ownership comparisons](../dynamic-testing/traffic-analysis-and-tls.md#captured-request-replay) | Extracted credential grants unintended protected access; public SDK identifiers may be expected. |
