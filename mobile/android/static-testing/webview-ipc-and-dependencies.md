# WebView, IPC, and Dependency Checks

## WebView

* <pre class="language-bash" data-line-numbers><code class="lang-bash">grep -rn 'addJavascriptInterface\|setJavaScriptEnabled(true)' &#x3C;decompiled-directory>
  grep -rn 'setAllowFileAccess(true)\|setAllowUniversalAccessFromFileURLs(true)\|setAllowFileAccessFromFileURLs(true)' &#x3C;decompiled-directory>
  grep -rn -A3 'onReceivedSslError' &#x3C;decompiled-directory> | grep 'proceed()'
  grep -rn 'loadUrl(\|loadData(\|evaluateJavascript(' &#x3C;decompiled-directory>
  </code></pre>
* `addJavascriptInterface`: annotation-limited exposure requires Android **and target API 17+**; legacy configurations expose more methods. Test the actual device/WebView.
* The object is available to **all frames**, without a calling-origin parameter; inspect attacker-controlled pages/iframes and exposed methods. [Bridge behavior](https://developer.android.com/privacy-and-security/risks/insecure-webview-native-bridges).
* `setAllowFileAccess` defaults to `false` for target API 30+; file-URL cross-access settings default to `false` for target API 16+ on supported platforms. Check explicit overrides and WebView version.
* `proceed()` in `onReceivedSslError` accepts invalid certificates.
* Trace what URLs reach `loadUrl` (intent extras, deep links, server data) and whether the page origin is validated.

#### WebView Boundaries Beyond JavaScript Enablement

| Lead                                                                | Static Review / Runtime Check                                                               | Qualification                                                                                                                                                        |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `evaluateJavascript`, `loadUrl("javascript:...")`, `onPageFinished` | Trace interpolation of untrusted values into executable script; use harmless markers        | Loading an attacker URL and injecting script into a trusted origin are different impacts.                                                                            |
| `shouldOverrideUrlLoading`                                          | Validate parsed scheme, host, port, path, redirects, and external-intent handling           | String prefix/substring allowlists can accept unintended hosts; test actual parser behavior.                                                                         |
| Mixed content / file access                                         | `setMixedContentMode`, file/content URL settings, local-to-remote access                    | Confirm an attacker-controlled resource is loaded and can reach sensitive data; settings alone are not a completed exploit.                                          |
| `shouldInterceptRequest` / `WebResourceResponse`                    | Resource selection, URL normalization, MIME/encoding, cache keys, synthetic response origin | Test crafted in-scope URLs and offline/restart behavior; prove persistent poisoning or unintended resource disclosure.                                               |
| Geolocation / media permission callbacks                            | Origin, requested resource, Android permission, user consent                                | A blanket grant is a lead; distinguish WebView-origin consent from OS-level permission.                                                                              |
| File chooser / capture                                              | Returned content URI, grants, MIME, source app, destination origin                          | Use a companion provider and harmless file to test upload disclosure; filesystem reach alone is not proof of cross-origin theft.                                     |
| Cookies / web storage                                               | Domain/path, Secure/HttpOnly/SameSite, logout, account isolation, separate data directories | Cookies can be shared within the app's WebView profile, not globally across unrelated apps. JavaScript cannot read HttpOnly cookies merely because a bridge exists.  |
| Bridge reflection / third-party script                              | Allowed native methods/arguments and code running in frames/page origin                     | Included scripts run in the page context; iframes may be same-origin or cross-origin. `addJavascriptInterface` is exposed to both. Check actual frame/bridge access. |
| Remote debugging                                                    | Actual enabled setting, release behavior, authorized ADB/transport access                   | Being on the same Wi-Fi alone does not normally grant Chrome inspection access.                                                                                      |
| Legacy bridge exposure                                              | Device WebView/provider version, Android/target SDK, annotated/exposed methods              | Historic pre-API-17 reflection attacks require the affected configuration; do not generalize them to modern annotated bridges.                                       |

* Establish attacker reachability with the [WebView runtime workflow](../dynamic-testing/component-testing.md#webview-runtime-checks).
* DevTools-injected JavaScript alone does not prove attacker reachability.

## Content Provider SQL Injection

* <pre class="language-bash" data-line-numbers><code class="lang-bash">grep -rn 'rawQuery(\|execSQL(' &#x3C;decompiled-directory> | grep '+'
  grep -rn -A15 'public Cursor query' &#x3C;decompiled-directory>
  </code></pre>
* Look for string concatenation of `selection`, `sortOrder`, or intent/URI data into SQL instead of `?` placeholders and `selectionArgs`.
* Exposure depends on the provider being exported or granting URI permissions. Confirm at runtime: [Component Testing](../dynamic-testing/component-testing.md).

## Path Traversal and FileProvider

* <pre class="language-bash" data-line-numbers><code class="lang-bash">grep -rn 'new File(' &#x3C;decompiled-directory> | grep -E 'getStringExtra|getIntent\(\)|getQueryParameter|getLastPathSegment'
  grep -rn 'path="\."\|path="/"\|&#x3C;root-path' &#x3C;decoded-directory>/res/xml/
  </code></pre>
* Check whether `../` sequences in filenames from intents, deep links, or URIs are rejected after canonicalization.
* Overly broad `FileProvider` paths (for example `<external-path path="."/>` or `<root-path>`) can expose more files than intended. Check `android:exported="false"` and `android:grantUriPermissions` on the provider.

## Deep Links and Intent Input

* <pre class="language-bash" data-line-numbers><code class="lang-bash">grep -n -A6 'android:scheme' &#x3C;decoded-directory>/AndroidManifest.xml
  grep -rn 'getIntent()\.getData()\|getQueryParameter(\|getStringExtra(' &#x3C;decompiled-directory>
  </code></pre>
* Treat deep-link parameters as untrusted external input from any app or link.
* Flag tokens, redirect URLs, or identifiers accepted without server-side validation (auto-login, WebView loading, authorization decisions).
* Verify App Links (`autoVerify`, `assetlinks.json`) where used; custom schemes can be claimed by other apps.

## PendingIntent Mutability

* ```bash
  grep -rnE 'PendingIntent\.get(Activity|Activities|Broadcast|Service|ForegroundService)' <decompiled-directory> | grep -v 'FLAG_IMMUTABLE'
  ```
* On Android 12+, apps targeting API 31+ must specify `FLAG_IMMUTABLE` or `FLAG_MUTABLE`. Older behavior defaults to mutable unless a supported immutable flag is set (`FLAG_IMMUTABLE`: API 23+).
* Risk is highest with mutable PendingIntents wrapping empty or implicit Intents, which another app may fill in. Check the base Intent's component, action, and extras.

## Third-Party Dependencies (SCA)

* With source: run `./gradlew dependencies` and an SCA scanner such as OWASP Dependency-Check or OSV-Scanner on build files/lockfiles.
* APK only: collect library versions from `META-INF/*.version`, `META-INF/maven/**/pom.properties`, version constants, package names, and MobSF output. Match versions against vulnerability databases.
* Record library/version evidence, advisory ID, affected configuration, and observed or unknown reachability. Distinguish a vulnerable-component/policy finding from a demonstrated exploitable path; a package-name match alone is not reliable version identification.
* Include transitive AndroidX/Jetpack, HTTP, image/media, JSON/parser, WebView-wrapper, payment, and analytics SDKs as relevant. Renaming/shading or backported fixes can invalidate a simple version match. APKiD is primarily a fingerprinting aid, not complete SCA.
* With source, obtain the resolved dependency graph and use a scanner-supported lockfile/SBOM/export rather than assuming every scanner parses every Gradle format. APK-only version evidence may remain uncertain; state that limit.

## Quick Triage

* **Prerequisites:** JADX and Apktool output; review every search result manually.

```sh
SRC=<decompiled-directory>
MANIFEST=<decoded-directory>/AndroidManifest.xml
grep -rniE 'api[_-]?key|secret|password|BEGIN (RSA |EC )?PRIVATE KEY' "$SRC"
grep -nE 'allowBackup|dataExtractionRules|fullBackupContent|debuggable|usesCleartextTraffic|networkSecurityConfig' "$MANIFEST"
grep -rnE 'Cipher\.getInstance\("(DES|RC4|AES/ECB|AES")|MessageDigest\.getInstance\("(MD5|SHA-?1)"\)' "$SRC"
grep -n 'android:exported="true"' "$MANIFEST"
grep -rn 'addJavascriptInterface\|onReceivedSslError\|checkServerTrusted' "$SRC"
grep -rniE 'firebaseio\.com|firebasestorage\.googleapis\.com|amazonaws\.com' "$SRC"
```
