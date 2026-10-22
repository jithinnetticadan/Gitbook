# WebView, IPC, and Dependency Checks

{% hint style="info" %}
Test only in-scope apps. Record package, version, source, device/API level, and original APK hash. Replace command placeholders before use.
{% endhint %}

## Code-Level Pattern Checks

Use grep hits as leads. Record code/configuration evidence, attacker capability, the relevant access path, and impact. Instrumentation or physical access may be valid prerequisites when stated explicitly. Use `<decompiled-directory>` for JADX output and `<decoded-directory>` for Apktool output.

### WebView

```sh
grep -rn 'addJavascriptInterface\|setJavaScriptEnabled(true)' <decompiled-directory>
grep -rn 'setAllowFileAccess(true)\|setAllowUniversalAccessFromFileURLs(true)\|setAllowFileAccessFromFileURLs(true)' <decompiled-directory>
grep -rn -A3 'onReceivedSslError' <decompiled-directory> | grep 'proceed()'
grep -rn 'loadUrl(\|loadData(\|evaluateJavascript(' <decompiled-directory>
```

* `addJavascriptInterface` exposes methods annotated `@JavascriptInterface` (API 17+) to JavaScript in the loaded page. Impact depends on which methods are exposed and whether attacker-controlled content can load.
* `setAllowFileAccess` defaults to `false` for apps targeting API 30+; the file-URL access settings default to `false` from API 16+. Enabling them with untrusted content is the risk.
* `proceed()` in `onReceivedSslError` accepts invalid certificates.
* Trace what URLs reach `loadUrl` (intent extras, deep links, server data) and whether the page origin is validated.

#### WebView Boundaries Beyond JavaScript Enablement

| Lead                                                                | Static Review / Runtime Check                                                               | Qualification                                                                                                                                                       |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `evaluateJavascript`, `loadUrl("javascript:...")`, `onPageFinished` | Trace interpolation of untrusted values into executable script; use harmless markers        | Loading an attacker URL and injecting script into a trusted origin are different impacts.                                                                           |
| `shouldOverrideUrlLoading`                                          | Validate parsed scheme, host, port, path, redirects, and external-intent handling           | String prefix/substring allowlists can accept unintended hosts; test actual parser behavior.                                                                        |
| Mixed content / file access                                         | `setMixedContentMode`, file/content URL settings, local-to-remote access                    | Confirm an attacker-controlled resource is loaded and can reach sensitive data; settings alone are not a completed exploit.                                         |
| `shouldInterceptRequest` / `WebResourceResponse`                    | Resource selection, URL normalization, MIME/encoding, cache keys, synthetic response origin | Test crafted in-scope URLs and offline/restart behavior; prove persistent poisoning or unintended resource disclosure.                                              |
| Geolocation / media permission callbacks                            | Origin, requested resource, Android permission, user consent                                | A blanket grant is a lead; distinguish WebView-origin consent from OS-level permission.                                                                             |
| File chooser / capture                                              | Returned content URI, grants, MIME, source app, destination origin                          | Use a companion provider and harmless file to test upload disclosure; filesystem reach alone is not proof of cross-origin theft.                                    |
| Cookies / web storage                                               | Domain/path, Secure/HttpOnly/SameSite, logout, account isolation, separate data directories | Cookies can be shared within the app's WebView profile, not globally across unrelated apps. JavaScript cannot read HttpOnly cookies merely because a bridge exists. |
| Bridge reflection / third-party script                              | Allowed native methods/arguments and code running in frames/page origin                     | A third-party script included by a page often runs with that page's privileges; an iframe has a different origin. Evaluate the actual bridge API and frame access.  |
| Remote debugging                                                    | Actual enabled setting, release behavior, authorized ADB/transport access                   | Being on the same Wi-Fi alone does not normally grant Chrome inspection access.                                                                                     |
| Legacy bridge exposure                                              | Device WebView/provider version, Android/target SDK, annotated/exposed methods              | Historic pre-API-17 reflection attacks require the affected configuration; do not generalize them to modern annotated bridges.                                      |

Use the [WebView runtime workflow](../dynamic-testing/component-testing.md#webview-runtime-checks) to establish attacker reachability; DevTools-injected JavaScript alone is not that evidence.

### Content Provider SQL Injection

```sh
grep -rn 'rawQuery(\|execSQL(' <decompiled-directory> | grep '+'
grep -rn -A15 'public Cursor query' <decompiled-directory>
```

* Look for string concatenation of `selection`, `sortOrder`, or intent/URI data into SQL instead of `?` placeholders and `selectionArgs`.
* Exposure depends on the provider being exported or granting URI permissions. Confirm at runtime: [Component Testing](../dynamic-testing/component-testing.md).

### Path Traversal and FileProvider

```sh
grep -rn 'new File(' <decompiled-directory> | grep -E 'getStringExtra|getIntent\(\)|getQueryParameter|getLastPathSegment'
grep -rn 'path="\."\|path="/"\|<root-path' <decoded-directory>/res/xml/
```

* Check whether `../` sequences in filenames from intents, deep links, or URIs are rejected after canonicalization.
* Overly broad `FileProvider` paths (for example `<external-path path="."/>` or `<root-path>`) can expose more files than intended. Check `android:exported="false"` and `android:grantUriPermissions` on the provider.

### Deep Links and Intent Input

```sh
grep -n -A6 'android:scheme' <decoded-directory>/AndroidManifest.xml
grep -rn 'getIntent()\.getData()\|getQueryParameter(\|getStringExtra(' <decompiled-directory>
```

* Treat deep-link parameters as untrusted external input from any app or link.
* Flag tokens, redirect URLs, or identifiers accepted without server-side validation (auto-login, WebView loading, authorization decisions).
* Verify App Links (`autoVerify`, `assetlinks.json`) where used; custom schemes can be claimed by other apps.

### PendingIntent Mutability

```sh
grep -rnE 'PendingIntent\.get(Activity|Activities|Broadcast|Service|ForegroundService)' <decompiled-directory> | grep -v 'FLAG_IMMUTABLE'
```

* Apps targeting API 31+ must specify `FLAG_IMMUTABLE` or `FLAG_MUTABLE`. Before that, `PendingIntent` is mutable by default.
* Risk is highest with mutable PendingIntents wrapping empty or implicit Intents, which another app may fill in. Check the base Intent's component, action, and extras.

### Third-Party Dependencies (SCA)

* With source: run `./gradlew dependencies` and an SCA scanner such as OWASP Dependency-Check or OSV-Scanner on build files/lockfiles.
* APK only: collect library versions from `META-INF/*.version`, `META-INF/maven/**/pom.properties`, version constants, package names, and MobSF output. Match versions against vulnerability databases.
* Record library/version evidence, advisory ID, affected configuration, and observed or unknown reachability. Distinguish a vulnerable-component/policy finding from a demonstrated exploitable path; a package-name match alone is not reliable version identification.
* Include transitive AndroidX/Jetpack, HTTP, image/media, JSON/parser, WebView-wrapper, payment, and analytics SDKs as relevant. Renaming/shading or backported fixes can invalidate a simple version match. APKiD is primarily a fingerprinting aid, not complete SCA.
* With source, obtain the resolved dependency graph and use a scanner-supported lockfile/SBOM/export rather than assuming every scanner parses every Gradle format. APK-only version evidence may remain uncertain; state that limit.

## Quick Triage

Run after decompiling with JADX and Apktool; review each result:

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
