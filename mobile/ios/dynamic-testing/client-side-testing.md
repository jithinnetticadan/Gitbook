# Deep Links and WebViews

## Deep Links and URL Handling

* **macOS/Xcode Simulator:** choose a booted simulator; install the matching Simulator build, not a physical-device IPA.
	* ```bash
		xcrun simctl list devices booted
		xcrun simctl install booted '<Simulator.app>'
		xcrun simctl launch booted '<bundle-id>'
		xcrun simctl openurl booted '<scheme>://<host>/<path>?id=<test-record-id>'
		xcrun simctl openurl booted 'https://<associated-domain>/<path>?id=<test-record-id>'
		```
* **Link input variants:** repeat each route logged out and as accounts A/B; compare normal, missing, and duplicate parameters.
	* ```bash
		xcrun simctl openurl booted '<scheme>://<host>/<path>'
		xcrun simctl openurl booted '<scheme>://<host>/<path>?id=<record-A>&id=<record-B>'
		```
* **Physical device:** deliver the same URL through Safari or a companion app; verify Universal Links from a tappable link, not only typed browser navigation.
## WebView Runtime Checks

* **WebView:** Safari > Develop > device > app WebView; requires an inspectable WebView. In its console, identify the loaded origin and frames before invoking the app's observed bridge.
	* ```javascript
		({ url: location.href, origin: location.origin, frames: frames.length });
		Object.keys(window.webkit?.messageHandlers ?? {});
		```
* **Observed WKScriptMessageHandler:** replace both handler and payload with the app's actual protocol; object enumeration may not discover every handler.
	* ```javascript
		window.webkit.messageHandlers['<observed-handler>'].postMessage({ action: '<observed-action>', id: '<test-record-id>' });
		```
## Permissions and Client Behavior

* **Simulator permissions:** these operate on the selected app's TCC grant, not its server session.
	* ```bash
		xcrun simctl privacy booted grant photos '<bundle-id>'
		xcrun simctl privacy booted revoke photos '<bundle-id>'
		xcrun simctl privacy booted reset all '<bundle-id>'
		```
* **API/business logic:** [captured-request replay](traffic-analysis-and-tls.md#captured-request-replay); **pasteboard/crypto/Keychain:** [runtime commands](runtime-instrumentation.md#clipboard-screenshots-memory-and-sqlite).

* [ ] Custom/universal links: valid, malformed, unauthorized inputs; validate caller and parameters.
* [ ] WebViews: URL allowlists, JavaScript bridges, navigation, script injection/XSS. Native screens are not web pages.
* [ ] Business logic: alter test-only local state/replay requests; verify server authorization.
* [ ] Logs: Xcode Devices and Simulators or approved console.
* [ ] Pasteboard/keyboard: use non-sensitive test data.
* [ ] 3uTools: optional third-party inspection; consider privacy/provenance, not a replacement for Xcode.
* [ ] [MobSF](https://mobsf.github.io/docs/#/): dynamic iOS support depends on release/device setup.
