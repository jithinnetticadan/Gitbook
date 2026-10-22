# Manifest and Components

{% hint style="info" %}
Test only in-scope apps. Record package, version, source, device/API level, and original APK hash. Replace command placeholders before use.
{% endhint %}

## Manifest and Component Review

Inspect `AndroidManifest.xml` in JADX and Apktool:

* `minSdkVersion`, target SDK, permissions, application settings, activities, services, receivers, and providers.
* `android:exported`, component permissions, intent filters, deep links, and sensitive-action authorization. Intent filters are **not authentication**.
* Debug, backup, cleartext, and `android:networkSecurityConfig` settings. Check production behavior.
* Content provider authorities, exported status, path permissions, and query/update behavior.
* Dangerous permissions and whether each is necessary for app functionality.

References: [Android manifest introduction](https://developer.android.com/guide/topics/manifest/manifest-intro), [Android permissions](https://developer.android.com/reference/android/Manifest.permission), and [Android security overview](https://source.android.com/docs/security/overview/app-security).

Example settings:

```xml
<!-- AndroidManifest.xml: example application attributes -->
<application
	android:allowBackup="false"
	android:debuggable="false"
	android:networkSecurityConfig="@xml/network_security_config" />
```

```xml
<!-- res/xml/network_security_config.xml: example domain policy -->
<network-security-config>
	<domain-config cleartextTrafficPermitted="false">
		<domain includeSubdomains="true">example.com</domain>
	</domain-config>
</network-security-config>
```

Snippets are illustrative, not complete manifests. Also inspect backup/data-extraction rules and OS behavior.

### Exported Components, Backup, and Debug Triage

Check the manifest of the **release APK**, not a debug build or source tree:

```sh
grep -n 'android:exported="true"' <decoded-directory>/AndroidManifest.xml
grep -nE 'android:(allowBackup|dataExtractionRules|fullBackupContent|debuggable|usesCleartextTraffic|networkSecurityConfig)' <decoded-directory>/AndroidManifest.xml
```

* Export defaults depend on component type and target/platform version. Activities, services, and receivers historically derive defaults from intent filters; providers have different defaults (notably target API 16 versus 17+). Apps targeting API 31+ must explicitly set `android:exported` on activities, services, and receivers with intent filters. Inspect the installed package rather than treating one rule as universal.
* For each exported hit, check for `android:permission` (providers: `readPermission`/`writePermission`/`grantUriPermissions`) and for authorization in code. Multi-line `grep -B` pipelines are unreliable; review each hit.
* `android:allowBackup` defaults to `true` when unset. Open the files named by `android:dataExtractionRules` (Android 12+) and `android:fullBackupContent` (Android 11 and earlier) under `res/xml/`; excludes can limit exposure.
* `adb backup` data extraction is restricted for apps targeting API 31+ unless debuggable; confirm behavior on the test device.
* `android:debuggable="true"` in a release build allows JDWP attach. On a non-rooted device, `adb shell run-as <package-name> id` succeeding also indicates a debuggable app.

Exploit exported components at runtime: [Component Testing](../dynamic-testing/component-testing.md).

## Permissions, Tasks, and Special Access

Compare the merged release manifest with actual code use and runtime grants. A declaration is an attack-surface lead, not proof of unauthorized access.

| Surface | Review | Validate |
| --- | --- | --- |
| Custom permissions | `<permission>` ownership, `protectionLevel`, caller checks, and signature trust | A normal/dangerous permission does not restrict access to the publisher's apps. Verify which installed package defines it and what permissions the test caller actually holds. |
| Signature permissions / signing | Signing certificate, production versus known test key, key rotation | Signing identity is the boundary; sharing a known private test key can undermine it. Do not infer private-key compromise from certificate visibility. |
| Permission requests | SMS, contacts, location, microphone, camera, all-files access, package visibility | Link each request to a feature and consent; test denied/revoked/one-time grants and minimization. Compare disclosures with observed use. |
| Runtime receivers | `registerReceiver`, export flags, sender permissions, sensitive extras | Manifest-only enumeration misses dynamically registered receivers. Restrictions vary with target SDK and broadcast type. |
| Task configuration | `taskAffinity`, `launchMode`, `allowTaskReparenting`, recents behavior | Test foreground/task transitions on the affected OS; unusual values alone do not establish task hijacking. |
| Accessibility / notifications / autofill | Service declaration, required binding permission, configuration metadata | These are user-enabled capabilities. Review actual data access, caller boundaries, consent, and sensitive-field treatment. |
| VPN / device administration | `VpnService`, `DeviceAdminReceiver`, policy declarations | Distinguish granted device/profile ownership from ordinary app access; do not exercise wipe/lock operations on user data. |
| Overlays / foreground services | `SYSTEM_ALERT_WINDOW`, declared service types, background work | Test required consent, sensitive actions under obscured input, and background collection versus declared purpose. |
| USB / MIDI / cross-profile intents | Device filters, exported handlers, profile policy | Assess physical-device/cross-profile prerequisites and input validation; declaration alone does not bypass prompts. |
| Shared UID / legacy platform choices | `sharedUserId`, low target SDK, obsolete permissions | Record signing/install/OS constraints and migration needs; do not assume ordinary apps can join another UID. |
| Native loading / storage | `extractNativeLibs`, `directBootAware`, device-protected storage | Trace extraction/load paths and data available before user unlock. These flags are not vulnerabilities by themselves. |

Check `targetSdkVersion` separately from `minSdkVersion`: target level can preserve compatibility behavior, while minimum level defines supported installation versions. A high target does not prove the app implements every security control.

**Previous:** [App Architecture](app-architecture.md) | **Next:** [Secrets and Cloud](secrets-and-cloud.md)
