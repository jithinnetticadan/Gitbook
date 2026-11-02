# Deep Links and URL Handling

## Deep Links and URL Handling

* **macOS terminal:** extract registered schemes and queryable schemes from the app plist.
  * ```bash
    /usr/libexec/PlistBuddy -c 'Print :CFBundleURLTypes' '<Application.app>/Info.plist'
    /usr/libexec/PlistBuddy -c 'Print :LSApplicationQueriesSchemes' '<Application.app>/Info.plist'
    ```
* For Universal Links, read `com.apple.developer.associated-domains` using the [entitlement command](configuration-and-sensitive-data.md#configuration-and-sensitive-data).
  * ```bash
    curl -i 'https://<associated-domain>/.well-known/apple-app-site-association'
    ```
* Compare app identifiers and allowed components/paths with the installed build; registered custom schemes are not ownership verification.

* [ ] Validate caller, scheme, host, path, parameters, and authorization.
* [ ] Review custom schemes, universal links, and inter-app requests.
* [ ] Inspect handlers:
* [ ] `application:didFinishLaunchingWithOptions:` and `application:willFinishLaunchingWithOptions:`.
* [ ] `application:openURL:options:` and scene-based URL handling.
* [ ] `openURL:options:completionHandler:` call sites.
* [ ] **Input:** extracted app bundle for the following search.

- <pre class="language-bash" data-line-numbers><code class="lang-bash">grep -R -nE 'open.*options.*completionHandler|openURL\(|://' &#x3C;Application.app>
  grep -R -n 'mt-encrypted-file://' &#x3C;Application.app>
  rabin2 -zzq &#x3C;app-binary> | grep -i openurl
  </code></pre>
- Test untrusted callers for sensitive actions/data disclosure; require user confirmation where appropriate.
- `sourceApplication` identifies a caller, not authorization by itself.
- `mt-encrypted-file://` is app-specific, not universal.
- Check deprecated APIs: [UIKit documentation](https://developer.apple.com/documentation/uikit).
- Validate handlers at runtime: [Deep Links and WebViews](../dynamic-testing/client-side-testing.md).
