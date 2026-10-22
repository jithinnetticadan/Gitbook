# Traffic Analysis and TLS

{% hint style="info" %}
* Use authorized devices/builds and test accounts; replace command placeholders before use.
* Isolate the lab, protect evidence, and restore it afterward.
{% endhint %}

{% hint style="warning" %}
* **Prerequisites:** reachable Mac proxy, installed CA profile, and enabled full certificate trust.
* Check pinning separately from CA trust.
{% endhint %}

## Traffic Analysis and TLS

1. Bind Burp to a reachable Mac lab IP/port; firewall "All interfaces" listeners.
2. Set the iPhone Wi-Fi proxy to that address. `127.0.0.1` on the phone is **not the Mac**.
3. Open `http://burp`; install the CA under VPN & Device Management.
4. Enable trust: General > About > Certificate Trust Settings (labels vary).
5. Test API authentication, authorization, inputs, sensitive data, and server behavior.
6. Remove the CA after testing; renaming its file does not change encoding/trust.

* Confirm a test HTTPS request reaches Burp before investigating pinning.
* CA profile installation and enabling full trust are separate steps; apps may still reject the proxy certificate.

* Follow the [Mobile Assistant guide](https://portswigger.net/burp/documentation/desktop/tools/mobile-assistant/installing); verify the historical `http://<mac-ip>:8080` package-source example before use.

### Pinning Tests

* Objection command: `ios sslpinning disable`.
* [SSL Kill Switch 2](https://github.com/nabla-c0d3/ssl-kill-switch2) / [3](https://github.com/NyaMisty/ssl-kill-switch3/releases): compatible jailbroken devices only.
* Burp Mobile Assistant and app-specific instrumentation.
* AppSync alters code-signing behavior; it does **not** replace CA trust configuration.

* Bypass is a test technique, not itself a vulnerability; report actual validation behavior and impact.
* For Objection session syntax and startup hooks, see [Runtime Instrumentation](runtime-instrumentation.md).
