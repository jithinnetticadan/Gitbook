# URL Handling

{% hint style="info" %}
* Record version, source, architecture, and original/extracted artifact hashes.
* Use authorized copies and replace command placeholders; App Store binaries may be FairPlay-encrypted.
{% endhint %}

## URL Handling and Inter-App Requests

* [ ] Validate caller, scheme, host, path, parameters, and authorization.
* [ ] Review custom schemes, universal links, and inter-app requests.

* Inspect handlers:

* `application:didFinishLaunchingWithOptions:` and `application:willFinishLaunchingWithOptions:`.
* `application:openURL:options:` and scene-based URL handling.
* `openURL:options:completionHandler:` call sites.

* **Input:** extracted app bundle for the following search.

```sh
grep -R -nE 'open.*options.*completionHandler|openURL\(|://' <Application.app>
grep -R -n 'mt-encrypted-file://' <Application.app>
rabin2 -zzq <app-binary> | grep -i openurl
```

* Test untrusted callers for sensitive actions/data disclosure; require user confirmation where appropriate.
* `sourceApplication` identifies a caller, not authorization by itself.
* `mt-encrypted-file://` is app-specific, not universal.
* Check deprecated APIs: [UIKit documentation](https://developer.apple.com/documentation/uikit).

* Validate handlers at runtime: [URL Schemes, Web Views, and Client Behavior](../dynamic-testing/client-side-testing.md).
