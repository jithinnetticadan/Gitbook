# Traffic Analysis and TLS

{% hint style="info" %}
Use authorized devices/builds and test accounts. Isolate the lab, protect evidence, and restore it afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Before testing, confirm the Mac proxy is reachable, the CA profile is installed, and full certificate trust is enabled. Check pinning separately.
{% endhint %}

## Traffic Analysis and TLS

1. Bind Burp to a reachable Mac lab IP/port; firewall "All interfaces" listeners.
2. Set the iPhone Wi-Fi proxy to that address. `127.0.0.1` on the phone is **not the Mac**.
3. Open `http://burp`; install the CA under VPN & Device Management.
4. Enable trust: General > About > Certificate Trust Settings (labels vary).
5. Test API authentication, authorization, inputs, sensitive data, and server behavior.
6. Remove the CA after testing; renaming its file does not change encoding/trust.

Confirm a test HTTPS request reaches Burp before investigating pinning. CA profile installation and enabling full trust are separate steps; an app may still reject the proxy certificate.

[Mobile Assistant guide](https://portswigger.net/burp/documentation/desktop/tools/mobile-assistant/installing): verify the historical package-source example `http://<mac-ip>:8080` before use.

### Pinning Tests

* Objection command: `ios sslpinning disable`.
* [SSL Kill Switch 2](https://github.com/nabla-c0d3/ssl-kill-switch2) / [3](https://github.com/NyaMisty/ssl-kill-switch3/releases): compatible jailbroken devices only.
* Burp Mobile Assistant and app-specific instrumentation.
* AppSync alters code-signing behavior; it does **not** replace CA trust configuration.

Bypass is a test technique, not a vulnerability by itself. Report actual validation behavior/impact.

For Objection session syntax and startup hooks, see [Runtime Instrumentation](runtime-instrumentation.md).
