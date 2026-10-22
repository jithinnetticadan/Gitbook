# URL Schemes, Web Views, and Client Behavior

{% hint style="info" %}
Use authorized devices/builds and test accounts. Isolate the lab, protect evidence, and restore it afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Complete the [Mandatory Preflight](preflight-and-lab-setup.md#mandatory-preflight) first. Candidate handlers come from [URL Handling](../static-testing/url-handling.md).
{% endhint %}

## URL Schemes, Web Views, and Client Behavior

* [ ] Custom/universal links: valid, malformed, unauthorized inputs; validate caller and parameters.
* [ ] WebViews: URL allowlists, JavaScript bridges, navigation, script injection/XSS. Native screens are not web pages.
* [ ] Business logic: alter test-only local state/replay requests; verify server authorization.
* [ ] Logs: Xcode Devices and Simulators or approved console.
* [ ] Pasteboard/keyboard: use non-sensitive test data.

* 3uTools: optional third-party inspection; consider privacy/provenance, not a replacement for Xcode.
* [MobSF](https://mobsf.github.io/docs/#/): dynamic iOS support depends on release/device setup.

**Previous:** [Data Storage and Privacy](data-storage-and-privacy.md) | **Next:** [Decryption and Class Information](decryption-and-class-information.md)
