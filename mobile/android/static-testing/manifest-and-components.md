# Manifest and Components

## Manifest and Component Review

{% tabs %}
{% tab title="apkanalyzer" %}
* **Linux / Windows, same command:** print the manifest and package/SDK/permission fields from the APK.
  * ```bash
    apkanalyzer manifest print '<app.apk>'
    apkanalyzer manifest application-id '<app.apk>'
    apkanalyzer manifest min-sdk '<app.apk>'
    apkanalyzer manifest target-sdk '<app.apk>'
    apkanalyzer manifest permissions '<app.apk>'
    ```
{% endtab %}

{% tab title="JADX" %}
* **Linux / Windows, same command:** open the APK and inspect the manifest and component classes.
  * ```
    jadx-gui '<app.apk>'
    ```
{% endtab %}

{% tab title="Apktool" %}
* **Linux / Windows, same command:** decode the manifest and resources, including XML referenced by the manifest.
  * ```
    apktool d '<app.apk>' -o '<decoded-directory>'
    ```
* Inspect `<decoded-directory>/AndroidManifest.xml` and the referenced files under `res/xml/`.
{% endtab %}

{% tab title="MobSF" %}
* Upload the acquired APK to a compatible MobSF instance; inspect the static manifest/component results and the referenced manifest attributes.
{% endtab %}

{% tab title="Grapefruit" %}
* **Host terminal:** start the installed interface with the device's Frida server running.
  * ```
    frida-ps -U
    igf
    ```
* Select the app and inspect its manifest/component browser. Use [external-caller tests](../dynamic-testing/component-testing.md#runtime-component-testing) for protected operations.
{% endtab %}
{% endtabs %}

* `minSdkVersion`, target SDK, permissions, application settings, activities, services, receivers, and providers.
* `android:exported`, component permissions, intent filters, deep links, and sensitive-action authorization. Intent filters are **not authentication**.
* Debug, backup, cleartext, and `android:networkSecurityConfig` settings. Check production behavior.
* Content provider authorities, exported status, path permissions, and query/update behavior.
* Dangerous permissions and whether each is necessary for app functionality.
* References: [Android manifest introduction](https://developer.android.com/guide/topics/manifest/manifest-intro), [Android permissions](https://developer.android.com/reference/android/Manifest.permission), and [Android security overview](https://source.android.com/docs/security/overview/app-security).
* Example settings:
  * ```xml
    <!-- AndroidManifest.xml: example application attributes -->
    <application
    	android:allowBackup="false"
    	android:debuggable="false"
    	android:networkSecurityConfig="@xml/network_security_config" />
    ```
  * ```xml
    <!-- res/xml/network_security_config.xml: example domain policy -->
    <network-security-config>
    	<domain-config cleartextTrafficPermitted="false">
    		<domain includeSubdomains="true">example.com</domain>
    	</domain-config>
    </network-security-config>
    ```

### Defaults When Attributes Are Omitted

<table><thead><tr><th width="262.9998779296875">Attribute / setting</th><th>Default when omitted</th><th>Validation</th></tr></thead><tbody><tr><td><code>android:debuggable</code></td><td><code>false</code>.</td><td>Confirm the installed release build; <code>true</code> enables debugging.</td></tr><tr><td><code>android:allowBackup</code></td><td><code>true</code>. Auto Backup applies when both the app target and device are API 23+.</td><td>Check cloud backup and device transfer separately, backup rules, and the data actually included. <code>true</code> alone does not establish exposure.</td></tr><tr><td><code>android:fullBackupContent</code> / <code>android:dataExtractionRules</code></td><td>No custom rules file. Eligible Auto Backup includes most app files by default; cache, code-cache, and no-backup directories are excluded.</td><td>Resolve the XML when present; <code>fullBackupContent="false"</code> disables full backup under the legacy rules. Check the rules applicable to the device and target SDK.</td></tr><tr><td><code>android:usesCleartextTraffic</code></td><td>Target API 27 or lower: <code>true</code>; target API 28+: <code>false</code> on platforms applying the policy. Introduced in API 23.</td><td>On API 24+, a Network Security Config overrides this attribute; it is ignored for apps targeting API 38+. Check the effective domain policy and actual traffic.</td></tr><tr><td><code>android:networkSecurityConfig</code></td><td>No custom config. On API 24+, the platform base policy uses the cleartext defaults above and trusts system CAs; user-added CAs are also trusted by default for target API 23 or lower.</td><td>Inspect referenced <code>base-config</code>, <code>domain-config</code>, trust anchors, and <code>debug-overrides</code>; domain settings inherit unspecified values from the enclosing config or base config.</td></tr><tr><td><code>android:exported</code> for activities, activity aliases, services, and manifest receivers</td><td>Intent filter present: <code>true</code>; no intent filter: <code>false</code>. For target API 31+ on Android 12+, a component with an intent filter must declare the attribute or installation fails.</td><td>Inspect each component and its filters, inherited/component permissions, and installed state.</td></tr><tr><td><code>android:exported</code> for providers</td><td>On device API 16 or lower, providers behave as exported. On API 17+, default is <code>true</code> for target API 16 or lower and <code>false</code> for target API 17+.</td><td>Review read/write and path permissions and temporary URI grants; an unexported provider can still grant specific URI access.</td></tr><tr><td>Component <code>android:permission</code></td><td>Activities, services, and receivers inherit <code>&#x3C;application android:permission></code>; if neither sets one, no manifest permission protects the component. An activity alias without its own permission does not inherit the target activity's permission.</td><td>For aliases and providers, check their own permissions; for providers also check <code>readPermission</code>, <code>writePermission</code>, path permissions, and URI grants. Permission checks do not replace application authorization.</td></tr><tr><td>Provider <code>android:grantUriPermissions</code></td><td><code>false</code>; individual <code>&#x3C;grant-uri-permission></code> paths can still permit temporary grants.</td><td>Inspect grant flags, allowed paths, and actual caller access.</td></tr><tr><td>Custom <code>&#x3C;permission android:protectionLevel></code></td><td><code>normal</code>.</td><td>A requesting app is normally granted it at install; check the defining package and actual caller grants.</td></tr><tr><td><code>android:enabled</code> / <code>android:directBootAware</code></td><td>Application and component <code>enabled</code> default to <code>true</code>; component <code>directBootAware</code> defaults to <code>false</code>.</td><td>Application and component must both be enabled; also check installed state and device-protected storage.</td></tr><tr><td><code>android:allowTaskReparenting</code> / activity <code>launchMode</code> / <code>taskAffinity</code></td><td>Reparenting: <code>false</code>, inherited from application unless overridden. Launch mode: <code>standard</code>. Affinity: application affinity, normally the package name.</td><td>Check activity overrides and actual task behavior.</td></tr><tr><td><code>android:extractNativeLibs</code></td><td>Depends on <code>minSdkVersion</code> and Android Gradle Plugin version; no single fixed default.</td><td>Inspect the release APK's native libraries and installed behavior.</td></tr><tr><td><code>minSdkVersion</code> / <code>targetSdkVersion</code></td><td>Minimum defaults to API <code>1</code>; target defaults to the minimum.</td><td>Read the packaged APK's values; build tooling can populate or override source-manifest values.</td></tr></tbody></table>

* **Network policy:** domain settings can permit cleartext even when another domain denies it. Platform policy is best-effort: raw sockets and some third-party stacks may not enforce it. The example above denies cleartext only for `example.com` and its subdomains, not globally.
* **Source references:** [application attributes](https://developer.android.com/guide/topics/manifest/application-element), [provider attributes](https://developer.android.com/guide/topics/manifest/provider-element), [permission protection levels](https://developer.android.com/guide/topics/manifest/permission-element), [SDK defaults](https://developer.android.com/guide/topics/manifest/uses-sdk-element), and [network security configuration](https://developer.android.com/privacy-and-security/security-config).

### Exported Components, Backup, and Debug Triage

* **Required artifact:** manifest from the **release APK**, not a debug build or source tree.
* ```bash
  grep -n 'android:exported="true"' <decoded-directory>/AndroidManifest.xml
  grep -nE 'android:(allowBackup|dataExtractionRules|fullBackupContent|debuggable|usesCleartextTraffic|networkSecurityConfig)' <decoded-directory>/AndroidManifest.xml
  ```
* **Installed package and device API:** inspect the relevant component sections and effective flags, not only explicit `exported="true"` matches.
  * ```bash
    adb shell dumpsys package '<package-name>'
    adb shell getprop ro.build.version.sdk
    ```
* For each exported hit, check for `android:permission` (providers: `readPermission`/`writePermission`/`grantUriPermissions`) and for authorization in code. Multi-line `grep -B` pipelines are unreliable; review each hit.
* **Backup rules:** inspect `dataExtractionRules` on Android 12+ with target API 31+, or `fullBackupContent` on older devices or for target API 30 or lower. Some manufacturers permit device transfer despite `allowBackup=false`. [Backup rules](https://developer.android.com/identity/data/autobackup).
* On Android 12+, `adb backup` excludes data from apps targeting API 31+ unless debuggable; command availability and older-device behavior vary.
* `android:debuggable="true"` in a release build allows JDWP attach. Check [run-as identity and private-file access](../dynamic-testing/local-data-logs-and-privacy.md#file-and-database-inspection) on the installed build.
* Validate exported components at runtime: [Component Testing](../dynamic-testing/component-testing.md).

## Permissions, Tasks, and Special Access

* Compare the merged release manifest with code use and runtime grants.

<table><thead><tr><th width="202">Surface</th><th>Review</th><th>Validate</th></tr></thead><tbody><tr><td>Custom permissions</td><td><code>&#x3C;permission></code> ownership, <code>protectionLevel</code>, caller checks, and signature trust</td><td>A normal/dangerous permission does not restrict access to the publisher's apps. Verify which installed package defines it and what permissions the test caller actually holds.</td></tr><tr><td>Signature permissions / signing</td><td>Signing certificate, production versus known test key, key rotation</td><td>Signing identity is the boundary; sharing a known private test key can undermine it. Do not infer private-key compromise from certificate visibility.</td></tr><tr><td>Permission requests</td><td>SMS, contacts, location, microphone, camera, all-files access, package visibility</td><td>Link each request to a feature and consent; test denied/revoked/one-time grants and minimization. Compare disclosures with observed use.</td></tr><tr><td>Runtime receivers</td><td><code>registerReceiver</code>, export flags, sender permissions, sensitive extras</td><td>Manifest-only enumeration misses dynamically registered receivers. Restrictions vary with target SDK and broadcast type.</td></tr><tr><td>Task configuration</td><td><code>taskAffinity</code>, <code>launchMode</code>, <code>allowTaskReparenting</code>, recents behavior</td><td>Test foreground/task transitions on the affected OS; unusual values alone do not establish task hijacking.</td></tr><tr><td>Accessibility / notifications / autofill</td><td>Service declaration, required binding permission, configuration metadata</td><td>These are user-enabled capabilities. Review actual data access, caller boundaries, consent, and sensitive-field treatment.</td></tr><tr><td>VPN / device administration</td><td><code>VpnService</code>, <code>DeviceAdminReceiver</code>, policy declarations</td><td>Distinguish granted device/profile ownership from ordinary app access; do not exercise wipe/lock operations on user data.</td></tr><tr><td>Overlays / foreground services</td><td><code>SYSTEM_ALERT_WINDOW</code>, declared service types, background work</td><td>Test required consent, sensitive actions under obscured input, and background collection versus declared purpose.</td></tr><tr><td>USB / MIDI / cross-profile intents</td><td>Device filters, exported handlers, profile policy</td><td>Assess physical-device/cross-profile prerequisites and input validation; declaration alone does not bypass prompts.</td></tr><tr><td>Shared UID / legacy platform choices</td><td><code>sharedUserId</code>, low target SDK, obsolete permissions</td><td>Record signing/install/OS constraints and migration needs; do not assume ordinary apps can join another UID.</td></tr><tr><td>Native loading / storage</td><td><code>extractNativeLibs</code>, <code>directBootAware</code>, device-protected storage</td><td>Trace extraction/load paths and data available before user unlock. These flags are not vulnerabilities by themselves.</td></tr></tbody></table>

* `targetSdkVersion`: affects compatibility behavior; a high target does not prove every security control is implemented.
* `minSdkVersion`: defines supported installation versions; assess it separately from the target SDK.
