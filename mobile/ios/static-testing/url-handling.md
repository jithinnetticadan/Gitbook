# URL Handling

{% hint style="info" %}
Record version, source, architecture, and original/extracted artifact hashes. Use authorized copies only; App Store binaries may be FairPlay-encrypted. Replace command placeholders before use.
{% endhint %}

## URL Handling and Inter-App Requests

* [ ] Validate caller, scheme, host, path, parameters, and authorization.
* [ ] Review custom schemes, universal links, and inter-app requests.

Inspect handlers:

* `application:didFinishLaunchingWithOptions:` and `application:willFinishLaunchingWithOptions:`.
* `application:openURL:options:` and scene-based URL handling.
* `openURL:options:completionHandler:` call sites.

Search an extracted app bundle:

```sh
grep -R -nE 'open.*options.*completionHandler|openURL\(|://' <Application.app>
grep -R -n 'mt-encrypted-file://' <Application.app>
rabin2 -zzq <app-binary> | grep -i openurl
```

* Test untrusted callers for sensitive actions/data disclosure; require user confirmation where appropriate.
* `sourceApplication` identifies a caller, not authorization by itself.
* `mt-encrypted-file://` is app-specific, not universal.
* Check deprecated APIs: [UIKit documentation](https://developer.apple.com/documentation/uikit).

Test these handlers at runtime: [URL Schemes, Web Views, and Client Behavior](../dynamic-testing/client-side-testing.md).

**Previous:** [Binary Analysis](binary-analysis.md) | **Next:** [Configuration and Sensitive Data](configuration-and-sensitive-data.md)
