# Traffic Analysis and TLS

## Proxy Setup

1. Bind Burp to a reachable lab host IP/port; firewall "All interfaces" listeners.
2. Set the iPhone Wi-Fi proxy to that address. `127.0.0.1` on the phone is **not the proxy host**.
3. Open `http://burp`; install the CA under VPN & Device Management.
4. Enable trust: General > About > Certificate Trust Settings (labels vary).
5. Test API authentication, authorization, inputs, sensitive data, and server behavior.
6. Remove the CA after testing; renaming its file does not change encoding/trust.
7. Follow the current [PortSwigger iOS proxy setup](https://portswigger.net/burp/documentation/desktop/mobile/config-ios-device)

## Pinning Checks

* Objection command: `ios sslpinning disable`.
* [SSL Kill Switch 2](https://github.com/nabla-c0d3/ssl-kill-switch2) / [3](https://github.com/NyaMisty/ssl-kill-switch3/releases): compatible jailbroken devices only.
* AppSync alters code-signing behavior; it does **not** replace CA trust configuration.
* For Objection session syntax and startup hooks, see [Runtime Instrumentation](runtime-instrumentation.md).
