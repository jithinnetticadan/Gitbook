# WebView, IPC, and Dependency Checks

## WebView

{% tabs %}
{% tab title="Linux" %}
* ```bash
  grep -rnE 'addJavascriptInterface|addWebMessageListener|postWebMessage|setJavaScriptEnabled\(true\)' '<decompiled-directory>'
  grep -rnE 'setAllowFileAccess|setAllowUniversalAccessFromFileURLs|setAllowFileAccessFromFileURLs' '<decompiled-directory>'
  grep -rnE 'loadUrl\(|loadData\(|loadDataWithBaseURL\(|evaluateJavascript\(|shouldOverrideUrlLoading|shouldInterceptRequest|onReceivedSslError|setMixedContentMode|onPermissionRequest|onShowFileChooser|setWebContentsDebuggingEnabled' '<decompiled-directory>'
  ```
{% endtab %}

{% tab title="Windows" %}
* ```powershell
  $patterns = @(
    'addJavascriptInterface|addWebMessageListener|postWebMessage|setJavaScriptEnabled\(true\)',
    'setAllowFileAccess|setAllowUniversalAccessFromFileURLs|setAllowFileAccessFromFileURLs',
    'loadUrl\(|loadData\(|loadDataWithBaseURL\(|evaluateJavascript\(|shouldOverrideUrlLoading|shouldInterceptRequest|onReceivedSslError|setMixedContentMode|onPermissionRequest|onShowFileChooser|setWebContentsDebuggingEnabled'
  )
  Get-ChildItem -LiteralPath '<decompiled-directory>' -Recurse -File -Include *.java,*.kt,*.js |
    Select-String -Pattern $patterns
  ```
{% endtab %}
{% endtabs %}

* `addJavascriptInterface`: annotation-limited exposure requires Android **and target API 17+**; legacy configurations expose more methods. Test the actual device/WebView.
* The object is available to **all frames**, without a calling-origin parameter; inspect attacker-controlled pages/iframes and exposed methods. [Bridge behavior](https://developer.android.com/privacy-and-security/risks/insecure-webview-native-bridges).
* **Attack path:** an attacker-controlled URL or page reaches the app's WebView and invokes an exposed native method; a source hit alone is not a flaw. Follow the [bridge test steps](../dynamic-testing/component-testing.md#native-bridge-from-untrusted-content) and confirm app reachability plus an unintended protected result or action.
* `setAllowFileAccess` defaults to `false` for target API 30+; file-URL cross-access settings default to `false` for target API 16+ on supported platforms. Check explicit overrides and WebView version.
* `proceed()` in `onReceivedSslError` accepts invalid certificates.
* **TLS-error search command:** [TLS and pinning patterns](configuration-and-cryptography.md).
* Trace what URLs reach `loadUrl` (intent extras, deep links, server data) and whether the page origin is validated. | Search hit | Run next | Confirm vulnerability | | --- | --- | --- | | URL parameter reaches `loadUrl` | [URL variants](../dynamic-testing/component-testing.md#untrusted-navigation-and-url-allowlists) | Unintended origin reaches privileged app WebView. | | Native bridge/message channel | [Controlled-page bridge PoC](../dynamic-testing/component-testing.md#native-bridge-from-untrusted-content) | Untrusted frame invokes unintended protected native operation. | | String enters HTML/script | [Injection markers](../dynamic-testing/component-testing.md#script-injection-into-a-trusted-page) | Marker executes in the trusted origin. | | File/mixed-content settings, cookies | [File/session probes](../dynamic-testing/component-testing.md#file-access-mixed-content-and-session-isolation) | Actual file read, script execution or cross-account credential use. | | `shouldInterceptRequest` / `WebResourceResponse` | [Resource/cache probes](../dynamic-testing/component-testing.md#resource-interception-and-cache-boundaries) | URL/MIME/cache mapping discloses a file or serves attacker-influenced/private content across the intended boundary. | | Geolocation / `onPermissionRequest` | [Origin/frame permission page](../dynamic-testing/component-testing.md#geolocation-camera-and-microphone-grants) | Unintended origin obtains actual location/media access, not merely an OS permission. | | `onShowFileChooser` / capture results | [Chooser callback probe](../dynamic-testing/component-testing.md#file-chooser-destination-and-grants) | Marker file is delivered to the wrong page/origin or beyond the user's grant. | | Provider query/path concatenation | [Provider payloads](../dynamic-testing/advanced-ipc-and-providers.md#provider-injection-and-file-traversal) | Argument changes query logic or reads outside the exposed root. |
* **Debugging:** test the unmodified release configuration with the [runtime inspection workflow](../dynamic-testing/component-testing.md#webview-runtime-checks). Enabling debugging through instrumentation is not release exposure; same-Wi-Fi access alone does not grant ADB inspection.

## Content Provider SQL Injection

{% tabs %}
{% tab title="Linux" %}
* ```bash
  grep -rnE 'rawQuery\(|execSQL\(' '<decompiled-directory>' | grep '+'
  grep -rn -A15 'public Cursor query' '<decompiled-directory>'
  ```
{% endtab %}

{% tab title="Windows" %}
* ```powershell
  $source = Get-ChildItem -LiteralPath '<decompiled-directory>' -Recurse -File -Include *.java,*.kt
  $source | Select-String -Pattern 'rawQuery\(|execSQL\(' | Where-Object { $_.Line -match '\+' }
  $source | Select-String -Pattern 'public Cursor query' -Context 0,15
  ```
{% endtab %}
{% endtabs %}

* Look for string concatenation of `selection`, `sortOrder`, or intent/URI data into SQL instead of `?` placeholders and `selectionArgs`.
* Exposure depends on the provider being exported or granting URI permissions. Confirm at runtime: [Component Testing](../dynamic-testing/component-testing.md).
* **Attack path:** a malicious app supplies crafted query arguments to an exposed provider; verify whether the actual query returns a protected marker row or performs an unintended operation using the [provider injection steps](../dynamic-testing/advanced-ipc-and-providers.md#provider-injection-and-file-traversal). A concatenation hit alone is not proof.

## Path Traversal and FileProvider

{% tabs %}
{% tab title="Linux" %}
* ```bash
  grep -rn 'new File(' '<decompiled-directory>' | grep -E 'getStringExtra|getIntent\(\)|getQueryParameter|getLastPathSegment'
  grep -rnE 'path="\."|path="/"|<root-path' '<decoded-directory>/res/xml/'
  ```
{% endtab %}

{% tab title="Windows" %}
* ```powershell
  Get-ChildItem -LiteralPath '<decompiled-directory>' -Recurse -File -Include *.java,*.kt |
    Select-String -Pattern 'new File\(' | Where-Object { $_.Line -match 'getStringExtra|getIntent\(\)|getQueryParameter|getLastPathSegment' }
  Get-ChildItem -LiteralPath '<decoded-directory>/res/xml' -Recurse -File -Filter '*.xml' |
    Select-String -Pattern 'path="\."|path="/"|<root-path'
  ```
{% endtab %}
{% endtabs %}

* Check whether `../` sequences in filenames from intents, deep links, or URIs are rejected after canonicalization.
* Overly broad `FileProvider` paths (for example `<external-path path="."/>` or `<root-path>`) can expose more files than intended. Check `android:exported="false"` and `android:grantUriPermissions` on the provider.
* **Attack path:** an external caller controls a URI/path that the app resolves to a file outside its shared root; place a known marker outside that root and follow the [provider file-route test](../dynamic-testing/advanced-ipc-and-providers.md#provider-injection-and-file-traversal). Confirm the caller reads that marker.

## Deep Links and URL Handling

{% tabs %}
{% tab title="Linux" %}
* ```bash
  grep -n -A6 'android:scheme' '<decoded-directory>/AndroidManifest.xml'
  grep -rnE 'getIntent\(\)\.getData\(\)|getQueryParameter\(|getStringExtra\(' '<decompiled-directory>'
  ```
{% endtab %}

{% tab title="Windows" %}
* ```powershell
  Select-String -LiteralPath '<decoded-directory>/AndroidManifest.xml' -Pattern 'android:scheme' -Context 0,6
  Get-ChildItem -LiteralPath '<decompiled-directory>' -Recurse -File -Include *.java,*.kt |
    Select-String -Pattern 'getIntent\(\)\.getData\(\)|getQueryParameter\(|getStringExtra\('
  ```
{% endtab %}
{% endtabs %}

* Treat deep-link parameters as untrusted external input from any app or link.
* Flag tokens, redirect URLs, or identifiers accepted without server-side validation (auto-login, WebView loading, authorization decisions).
* Verify App Links (`autoVerify`, `assetlinks.json`) where used; custom schemes can be claimed by other apps.
* **Attack path:** another app or link supplies a crafted route/identifier to reach a protected screen or action; exercise the real handler with logged-out and A/B test accounts using [deep-link runtime tests](../dynamic-testing/component-testing.md#deep-links-and-url-handling). Confirm protected data or an action, not merely screen navigation.

## PendingIntent Mutability

* A `PendingIntent` allows another component to perform an action later **with the creating app's authority**.
  * `FLAG_IMMUTABLE` → recipient cannot modify the Intent. **Preferred when mutation isn't required.**
  * `FLAG_MUTABLE` → recipient can supply/modify permitted Intent information.
* **Attack Flow:**
  * Bank App creates mutable `PendingIntent` → exposes/passes it via Intent/Bundle/IPC → Attacker App obtains it → calls `send()` with modified data → action executes under the Bank App's authority.
* On Android 12+, apps targeting API 31+ must specify `FLAG_IMMUTABLE` or `FLAG_MUTABLE`. Older behavior defaults to mutable unless a supported immutable flag is set (`FLAG_IMMUTABLE`: API 23+).
* Risk is highest with mutable PendingIntents wrapping empty or implicit Intents, which another app may fill in. Check the base Intent's component, action, and extras.
* **Test:** obtain the target-created token through the real result/share/IPC flow; change one fill-in field at a time, then replay that same token after use or logout. Confirm an unintended protected action or record, not merely a successful `send()`. Follow the [PendingIntent fill-in and replay steps](../dynamic-testing/advanced-ipc-and-providers.md#pendingintent-fill-in-and-replay).

{% tabs %}
{% tab title="Linux" %}
- ```bash
  grep -rnE 'PendingIntent\.get(Activity|Activities|Broadcast|Service|ForegroundService)' '<decompiled-directory>' | grep -v 'FLAG_IMMUTABLE'
  ```
{% endtab %}

{% tab title="Windows" %}
* ```powershell
  Get-ChildItem -LiteralPath '<decompiled-directory>' -Recurse -File -Include *.java,*.kt |
    Select-String -Pattern 'PendingIntent\.get(Activity|Activities|Broadcast|Service|ForegroundService)' |
    Where-Object { $_.Line -notmatch 'FLAG_IMMUTABLE' }
  ```
{% endtab %}
{% endtabs %}

## Third-Party Dependencies (SCA)

* Select a scanner based on available input: supported source manifests/lockfiles for OSV, resolved artifacts for Dependency-Check, or an SBOM for Trivy.

{% tabs %}
{% tab title="Linux" %}
- [**OSV-Scanner V2**](https://google.github.io/osv-scanner/usage/)**:** obtain the release dependency configuration and scan supported manifests/lockfiles.
  * ```bash
    ./gradlew :app:dependencies --configuration releaseRuntimeClasspath
    osv-scanner scan source -r . --format json --output-file osv-results.json
    ```
- [**OWASP Dependency-Check CLI**](https://jeremylong.org/DependencyCheck/dependency-check-cli/index.html)**:** scan resolved dependency JAR/AAR artifacts or other supported files; APK/DEX scanning alone is not a complete dependency inventory.
  * ```bash
    dependency-check.sh --project 'Android-app' --scan '<dependency-artifact-directory>' --format HTML --out './dependency-check-report'
    ```
{% endtab %}

{% tab title="Windows" %}
* **OSV-Scanner V2:** use the Windows Gradle wrapper; the scanner command is unchanged.
  * ```powershell
    .\gradlew.bat :app:dependencies --configuration releaseRuntimeClasspath
    osv-scanner scan source -r . --format json --output-file osv-results.json
    ```
* **OWASP Dependency-Check CLI:** install its supported Java runtime; database updates may require the selected release's NVD/API configuration.
  * ```powershell
    dependency-check.bat --project 'Android-app' --scan '<dependency-artifact-directory>' --format HTML --out '.\dependency-check-report'
    ```
{% endtab %}
{% endtabs %}

* Replace the Gradle module/configuration with the real flavor. Gradle console output is not itself an OSV lockfile; use a supported manifest/lockfile or SBOM and check package coverage.
* [**Trivy**](https://trivy.dev/latest/docs/target/sbom/)**:** same command on Linux and Windows; first create or obtain `app-bom.json`.
  * ```
    trivy sbom --format json --output sca-results.json app-bom.json
    ```
* An SBOM containing only APK metadata covers only identified components; it is not an exhaustive dependency graph.
* **Interpret:** compare each advisory's detected package/version with the resolved dependency graph and actual feature/configuration. Scanner findings identify affected-component candidates; use the reachability checks below to establish a testable vulnerable path.

{% tabs %}
{% tab title="Linux" %}
- ```bash
  unzip -l '<app.apk>' | grep -E 'META-INF/.*(pom.properties|\.version|MANIFEST.MF)'
  unzip -p '<app.apk>' 'META-INF/maven/*/*/pom.properties'
  ```
{% endtab %}

{% tab title="Windows" %}
* ```powershell
  $archive = [IO.Compression.ZipFile]::OpenRead((Resolve-Path '<app.apk>'))
  try {
    foreach ($entry in ($archive.Entries | Where-Object {
      $_.FullName -match '^META-INF/.*(pom\.properties|\.version|MANIFEST\.MF)$'
    })) {
      $reader = [IO.StreamReader]::new($entry.Open())
      try { [pscustomobject]@{ Entry = $entry.FullName; Text = $reader.ReadToEnd() } }
      finally { $reader.Dispose() }
    }
  } finally { $archive.Dispose() }
  ```
{% endtab %}
{% endtabs %}

* APK only: collect library versions from `META-INF/*.version`, `META-INF/maven/**/pom.properties`, version constants, package names, and MobSF output. Match versions against vulnerability databases.
* **APK-only SBOM example:** put only evidence-backed components into `app-bom.json`. This Jackson coordinate is an example of a versioned Maven component, not a claim that the target ships it; replace it with the package/version actually recovered.
  * ```json
    {
      "bomFormat": "CycloneDX",
      "specVersion": "1.5",
      "version": 1,
      "components": [{
        "type": "library",
        "group": "com.fasterxml.jackson.core",
        "name": "jackson-databind",
        "version": "2.9.8",
        "purl": "pkg:maven/com.fasterxml.jackson.core/jackson-databind@2.9.8"
      }]
    }
    ```
* **Reachability example:** for a Jackson deserialization advisory, locate the actual `ObjectMapper` configuration and `readValue` call, trace whether external input reaches it, and compare the advisory's required version/type/polymorphic configuration. A packaged old version is component exposure; an advisory-specific reproducer reaching the affected parser is stronger exploit evidence. Retain the package/version/advisory match even when runtime reachability remains unknown.
* Record library/version evidence, advisory ID, affected configuration, and observed or unknown reachability. Distinguish a vulnerable-component/policy finding from a demonstrated exploitable path; a package-name match alone is not reliable version identification.
* Include transitive AndroidX/Jetpack, HTTP, image/media, JSON/parser, WebView-wrapper, payment, and analytics SDKs as relevant. Renaming/shading or backported fixes can invalidate a simple version match. APKiD is primarily a fingerprinting aid, not complete SCA.
* With source, obtain the resolved dependency graph and use a scanner-supported lockfile/SBOM/export rather than assuming every scanner parses every Gradle format. APK-only version evidence may remain uncertain; state that limit.

## Quick Triage

* **Input:** JADX source and Apktool decoded resources. Use the resulting paths/line numbers to inspect actual call sites.

{% tabs %}
{% tab title="Linux" %}
- ```bash
  SRC='<decompiled-directory>'
  MANIFEST='<decoded-directory>/AndroidManifest.xml'
  grep -rniE 'api[_-]?key|secret|password|BEGIN (RSA |EC )?PRIVATE KEY' "$SRC"
  grep -nE 'allowBackup|dataExtractionRules|fullBackupContent|debuggable|usesCleartextTraffic|networkSecurityConfig' "$MANIFEST"
  grep -rnE 'Cipher\.getInstance\("(DES|DESede|RC4|ARCFOUR|AES/ECB|AES")|MessageDigest\.getInstance\("(MD5|SHA-?1)"\)' "$SRC"
  grep -n 'android:exported="true"' "$MANIFEST"
  grep -rn 'addJavascriptInterface\|onReceivedSslError\|checkServerTrusted' "$SRC"
  grep -rniE 'firebaseio\.com|firebasestorage\.googleapis\.com|amazonaws\.com' "$SRC"
  ```
{% endtab %}

{% tab title="Windows" %}
* ```powershell
  $source = '<decompiled-directory>'
  $manifest = Join-Path '<decoded-directory>' 'AndroidManifest.xml'
  $sourceFiles = Get-ChildItem -LiteralPath $source -Recurse -File
  Select-String -LiteralPath $sourceFiles.FullName -Pattern @(
    'api[_-]?key|secret|password|BEGIN (RSA |EC )?PRIVATE KEY',
    'Cipher\.getInstance\("(DES|DESede|RC4|ARCFOUR|AES/ECB|AES")|MessageDigest\.getInstance\("(MD5|SHA-?1)"\)',
    'addJavascriptInterface|onReceivedSslError|checkServerTrusted',
    'firebaseio\.com|firebasestorage\.googleapis\.com|amazonaws\.com'
  )
  Select-String -LiteralPath $manifest -Pattern @(
    'allowBackup|dataExtractionRules|fullBackupContent|debuggable|usesCleartextTraffic|networkSecurityConfig',
    'android:exported="true"'
  )
  ```
{% endtab %}
{% endtabs %}

\* \*\*Next:\*\* inspect matched values and consumers, then run the relevant \[secrets/cloud]\(secrets-and-cloud.md), \[component]\(../dynamic-testing/component-testing.md), \[crypto]\(../dynamic-testing/authentication-and-cryptography.md#trace-cryptographic-data-flow), or \[WebView]\(../dynamic-testing/component-testing.md#webview-runtime-checks) test. A string/flag match alone is not confirmation of the flaw.
