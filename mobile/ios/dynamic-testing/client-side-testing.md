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
* **Ownership/parser payloads:** deliver each value using the actual route through the commands above. Keep A's session; substitute B's known ID. Repeat logged out and reverse duplicate-parameter order.
	* ```text
		demo://records/view?id=REPLACE_B_RECORD_ID
		demo://records/view?id=REPLACE_A_RECORD_ID&id=REPLACE_B_RECORD_ID
		demo://records/view?id=
		demo://records/view?id=REPLACE_A_RECORD_ID&redirect=https%3A%2F%2Fprobe.example%2Flink-marker
		```
* **Confirm:** the route returns B's protected data/action under A or without login. A preview screen or external browser launch alone is not a bypass. For login callbacks, use [identity mutations](traffic-analysis-and-tls.md#native-identity-and-purchase-tests); for URL loading, use the WebView tests below.

## WebView Runtime Checks

* **WebView:** Safari > Develop > device > app WebView; requires an inspectable WebView. In its console, identify the loaded origin and frames before invoking the app's observed bridge.
	* ```javascript
		({ url: location.href, origin: location.origin, frames: frames.length });
		Object.keys(window.webkit?.messageHandlers ?? {});
		```
### Untrusted Navigation and URL Allowlists

* **Input:** trace the observed custom/universal-link parameter into `WKWebView.load`, `loadHTMLString`, or navigation-delegate decisions. Replace `trusted.example` with the allowed host and `probe.example` with the test host; test each destination separately.
	* ```text
		https://probe.example/webview.html
		https://trusted.example.probe.example/webview.html
		https://trusted.example@probe.example/webview.html
		https://probe.example/?next=https://trusted.example/
		http://trusted.example/
		```
* **macOS Simulator launch:** substitute the actual route/parameter; the destination is encoded as one query value.
	* ```bash
		xcrun simctl openurl booted 'demo://web?url=https%3A%2F%2Fprobe.example%2Fwebview.html'
		```
* **Redirect variant:** use an allowed-host route that redirects to the test host. Inspect the final origin and subsequent navigations, not just the first URL.
* **Confirm:** the unintended origin loads inside the app's WKWebView. Opening an external browser is a different result; demonstrate the bridge/data boundary below before claiming native impact.

### Native Bridge from Untrusted Content

* **Map:** actual handler name, body schema, native dispatch, allowed origins, `frameInfo.isMainFrame`/`securityOrigin` checks, and registration content world. Object enumeration may not reveal every handler; an isolated-world handler may not be callable from page JavaScript.
* **Host this page at the controlled URL:** replace handler/action/ID with the observed read-only or marker operation. A normal handler has no synchronous return value; inspect its callback or native/API effect.
	* ```html
		<!doctype html>
		<meta charset="utf-8">
		<pre id="result"></pre>
		<script>
		const result = document.getElementById('result');
		try {
		  window.webkit.messageHandlers['REPLACE_HANDLER'].postMessage({
		    action: 'REPLACE_ACTION', id: 'REPLACE_TEST_RECORD_ID'
		  });
		  result.textContent = 'Message submitted from ' + location.origin;
		} catch (error) { result.textContent = String(error); }
		</script>
		```
* **Frame variant:** embed `<iframe src="https://probe.example/webview.html"></iframe>` in a reachable page; verify whether the handler accepts a subframe message independently of top-level navigation policy.
* **Confirm:** untrusted origin/frame causes an unintended sensitive native operation or protected response. A displayed "submitted" marker only confirms that JavaScript sent the message, not that native code accepted it.

### Script Injection into a Trusted Page

* **HTML sink:** place the first payload in the actual rendered input. **Single-quoted script sink:** use the second only where the app inserts that input into a single-quoted `evaluateJavaScript` string.
	* ```html
		<img src=x onerror="document.documentElement.dataset.webviewProbe=location.origin">
		```
	* ```text
		';document.documentElement.dataset.webviewProbe=location.origin;//
		```
* **Result check in the WebView console:**
	* ```javascript
		document.documentElement.dataset.webviewProbe;
		```
* **Confirm:** app-supplied input executes in the trusted page's origin; your hosted page running its own script is not trusted-origin XSS.

### File Read Scope and Session Isolation

* **File scope:** inspect `loadFileURL:allowingReadAccessToURL:`. From an attacker-controlled local HTML page reachable through the app, request a known marker file outside the intended page directory but inside the app's sandbox. Substitute the current container UUID/path.
	* ```javascript
		const request = new XMLHttpRequest();
		request.onload = () => { document.body.textContent = request.responseText; };
		request.onerror = () => { document.body.textContent = 'read blocked'; };
		request.open('GET', 'file:///var/mobile/Containers/Data/Application/REPLACE_UUID/Documents/webview-marker.txt');
		request.send();
		```
* **Confirm:** the untrusted local page reads the known marker outside its intended read scope. An HTTPS page failing to read `file://` does not test the local page's configured read-access scope.
* **Session:** log in as A, load a protected WebView route, log out, then revisit and repeat its protected request. Switch to B and request A's known object. Inspect the actual `WKWebsiteDataStore` used; test persistent/nonpersistent stores separately where the app uses both.
* **Confirm:** protected A data or a new request authenticated as A remains available to B/post-logout. Distinguish stale displayed content from live credential reuse; HttpOnly cookies need not be JavaScript-readable to authenticate requests.

### Cookie Scope and Flags

* An authentication cookie is delivered to an unintended host/path, exposed to page JavaScript, sent over HTTP, or accepted in a cross-site action without the intended protection.
* Use Safari Web Inspector's Network/Storage views and the actual `Set-Cookie` response to record Domain, Path, Secure, HttpOnly and SameSite. A native cookie dump and `document.cookie` do not by themselves show all browser-enforced attributes.
* **WKWebView console:** substitute the real session-cookie name and compare with the outgoing authenticated request.
	* ```javascript
		({ origin: location.origin,
		   sessionCookieVisible: document.cookie.split(';').some(value =>
		     value.trim().startsWith('REPLACE_SESSION_COOKIE=')) });
		```

| Attribute | Test | Confirm |
| --- | --- | --- |
| Domain | Load a controlled sibling host beneath the configured parent domain | A sensitive cookie reaches an unintended sibling host; inspect the received Cookie header. |
| Path | Request an actual route outside the intended path | Cookie is attached outside the required scope. Cookie Path is not a security boundary against other JavaScript on the same origin. |
| Secure | Load matching HTTP host/path through the actual app route | Cookie is transmitted over cleartext; distinguish ATS blocking or HTTPS upgrade from a transmitted request. |
| HttpOnly | Run the console probe on the matching host/path | Sensitive session cookie is page-JavaScript-readable despite the required HttpOnly policy; native app access is a separate capability. |
| SameSite | Submit the actual test action as a cross-site POST | Cookie is sent and the protected action commits without required CSRF protection; different-origin is not always different-site. |

* **Cross-site form PoC:** serve from a different site, substitute the actual endpoint/field, and verify the resulting action rather than only the page response. Lax cookies on top-level GET and `None; Secure` with separate CSRF defenses can be legitimate.
	* ```html
		<form method="post" action="https://trusted.example/REPLACE_TEST_ACTION">
		  <input name="REPLACE_FIELD" value="cookie-probe">
		  <button type="submit">Submit test action</button>
		</form>
		```

### WKWebView Data-Store Separation

* Surfaces intended to isolate accounts/private browsing reuse A's website data or authenticated identity. Ordinary WKWebViews deliberately sharing a data store may legitimately share cookies; unrelated apps do not all use one global WebView store.
* Set these markers in A's WKWebView, then read at the same origin in B's supposedly isolated surface/private view. Repeat an actual protected request for A's known record.
	* ```javascript
		localStorage.setItem('webview-profile-probe', 'account-A');
		document.cookie = 'webview_profile_probe=account-A; Path=/; Secure; SameSite=Lax';
		```
	* ```javascript
		({ origin: location.origin, localMarker: localStorage.getItem('webview-profile-probe'),
		   cookieMarker: document.cookie.includes('webview_profile_probe=account-A') });
		```
* **Map:** the `WKWebsiteDataStore` assigned before WebView creation: shared default, a reused nonpersistent instance, a distinct nonpersistent instance, or an identifier-based store on supported versions. A distinct `WKProcessPool` alone does not establish cookie-store isolation. Check normal restart behavior and the app's actual cookie/cache deletion completion, not a hook-created store.
* **Confirm:** B/private surface can authenticate as A or retrieve A's private content contrary to the intended isolation. Marker sharing only establishes shared storage; keep the [logout/session checks](#file-read-scope-and-session-isolation) as the separate credential-lifecycle test.

### Third-Party Script in a Trusted Page

* A controllable external script inherits the trusted document's execution origin, readable data and exposed WK message-handler access. The script's download hostname is not its execution origin; this differs from an isolated iframe.
* Place the marker in the actual controllable dependency or an owner-provided fixture, keeping the trusted top-level URL unchanged. Reuse the [observed message-handler PoC](#native-bridge-from-untrusted-content) from that script when checking native impact.
	* ```javascript
		document.documentElement.dataset.thirdPartyProbe = JSON.stringify({
		  page: location.href, executionOrigin: location.origin,
		  readableSessionCookie: document.cookie.split(';').some(value =>
		    value.trim().startsWith('REPLACE_SESSION_COOKIE='))
		});
		```
* **Confirm:** control of the real dependency leads to script execution in the trusted page and an unintended protected read/native operation. DevTools-only insertion or an unchanged trusted dependency is not proof of attacker control. HttpOnly still blocks direct cookie reads, not automatically authenticated requests; isolated-world handler availability must be checked separately.

### Media Permissions and File Chooser

* **Controlled HTTPS page:** test trusted/untrusted origins and subframes. For WKWebView, map media-capture/geolocation decisions to the app's delegate and OS TCC grants; support varies with OS/WebKit and capture API.
	* ```html
		<!doctype html>
		<meta charset="utf-8">
		<button onclick="capture({video:true})">Camera</button>
		<button onclick="capture({audio:true})">Microphone</button>
		<button onclick="locate()">Location</button>
		<input id="pick" type="file">
		<pre id="result"></pre>
		<script>
		const show = value => { document.getElementById('result').textContent = String(value); };
		async function capture(constraints) {
		  try {
		    const stream = await navigator.mediaDevices.getUserMedia(constraints);
		    show(location.origin + ': ' + stream.getTracks().map(track => track.kind).join(','));
		    stream.getTracks().forEach(track => track.stop());
		  } catch (error) { show(error); }
		}
		function locate() {
		  navigator.geolocation.getCurrentPosition(
		    value => show(location.origin + ': location granted; accuracy=' + value.coords.accuracy),
		    error => show(error.message));
		}
		document.getElementById('pick').addEventListener('change', async event => {
		  const file = event.target.files[0];
		  if (file) show(location.origin + ': marker=' + (await file.text()).includes('file-chooser-probe'));
		});
		</script>
		```
* **Media result:** an unintended origin/frame obtains an actual stream/location without the required per-origin decision. Repeat with app TCC access denied. A successful OS grant or a supported API by itself is not a flaw.
* **Chooser result:** select the known marker, then compare Cancel and navigation while the picker is open. Confirm a file is delivered to an unintended origin/stale completion handler; deliberately selecting a file for the requesting page is expected.
* **Custom scheme/cache:** for apps using `WKURLSchemeHandler`, trace its actual scheme-to-file mapping, then try `../`, `%2e%2e%2f` and double-encoded path segments against a known marker outside the mapped root. Switch A to B and repeat the same private route online/offline/restart; confirm an unintended file or A's private cached response reaches B. There is no universal handler for intercepting arbitrary HTTPS requests in WKWebView.

## Permissions and Client Behavior

* **Simulator permissions:** these operate on the selected app's TCC grant, not its server session.
	* ```bash
		xcrun simctl privacy booted grant photos '<bundle-id>'
		xcrun simctl privacy booted revoke photos '<bundle-id>'
		xcrun simctl privacy booted reset all '<bundle-id>'
		```
* **Related tests:** [API/session replay](traffic-analysis-and-tls.md#captured-request-replay), [crypto parameters/tampering](runtime-instrumentation.md#cryptographic-parameters-and-tampering), [biometric callback](runtime-instrumentation.md#biometric-callback-and-protected-operation), [Keychain/file protection](data-storage-and-privacy.md#keychain-and-cookies), [pasteboard/snapshots](data-storage-and-privacy.md#pasteboard-snapshots-and-account-residue).
