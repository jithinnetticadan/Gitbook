# URL Schemes, Web Views, and Client Behavior

{% hint style="info" %}
* Use authorized devices/builds and test accounts; replace command placeholders before use.
* Isolate the lab, protect evidence, and restore it afterward.
{% endhint %}

{% hint style="warning" %}
* **Prerequisites:** authorized installed app, test accounts/links, and approved capture tools. [Frida preflight](preflight-and-lab-setup.md#mandatory-preflight) applies only to instrumentation.
* Identify candidate handlers using [URL Handling](../static-testing/url-handling.md).
{% endhint %}

## URL Schemes, Web Views, and Client Behavior

* [ ] Custom/universal links: valid, malformed, unauthorized inputs; validate caller and parameters.
* [ ] WebViews: URL allowlists, JavaScript bridges, navigation, script injection/XSS. Native screens are not web pages.
* [ ] Business logic: alter test-only local state/replay requests; verify server authorization.
* [ ] Logs: Xcode Devices and Simulators or approved console.
* [ ] Pasteboard/keyboard: use non-sensitive test data.
* [ ] 3uTools: optional third-party inspection; consider privacy/provenance, not a replacement for Xcode.
* [ ] [MobSF](https://mobsf.github.io/docs/#/): dynamic iOS support depends on release/device setup.
