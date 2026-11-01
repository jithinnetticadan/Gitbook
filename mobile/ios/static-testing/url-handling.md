# URL Handling

## URL Handling and Inter-App Requests

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
- Validate handlers at runtime: [URL Schemes, Web Views, and Client Behavior](../dynamic-testing/client-side-testing.md).
