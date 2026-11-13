# Component Testing

* Root and Frida are **not required** for ordinary ADB/Drozer component tests. Use [Device and Frida Setup](../setup.md#device-and-frida-setup) when instrumenting or patching an app.

## Components, Intents, and Provider URIs

* **Activity:** screen/action; launch with an Intent.
* **Service:** started work or bound interface; not automatically a separate thread/process.
* **Receiver:** handles broadcasts; manifest or runtime registration.
* **Provider:** data/files via `content://` and `ContentResolver`.
* **Intent:** action, URI, extras, flags, destination; a message, not a fifth component.
* **Explicit:** names a component. **Implicit:** matches action/data/category. Filters are not authorization.
* **Dispatch:** activity launch, service start/bind, and broadcast use distinct APIs.
* **Bound service:** Intent selects service; Binder/AIDL/Messenger defines subsequent calls.
* **Shared URI:** Intent carries URI/grants; `ContentResolver` accesses the provider.
* Deep links and WebViews are related surfaces, not additional component types.

## Runtime Component Testing

1. **Enumerate:** names/authorities, export state, permissions, registrations, grants.
2. **Map inputs:** observed actions, extras/types, routes, methods, handlers.
3. **Baseline:** legitimate action on owned data; record local/API effects.
4. **Compare:** intended/unauthorized caller; logged out; owned accounts A/B and roles.
5. **Vary:** one input at a time; bounded values and harmless destinations.
6. **Confirm:** protected data/action accessed.

### ADB Probes and Caller Identity

* **Need:** SDK Platform Tools, USB debugging, authorized host.
* **Run:** `sh` blocks on host; preserve shell quoting for spaces, `$`, and `&`.
* **Multiple devices:** add `-s <device-serial>` after every `adb`, including forwards.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb version
  adb devices -l
  adb shell getprop ro.build.version.release
  adb shell getprop ro.build.version.sdk
  adb shell dumpsys package "&#x3C;package-name>"
  </code></pre>
* Use the listed device serial for `-s`; use the OS/API output and installed package's target SDK to select the applicable component/permission behavior below.
* **Record:** build, OS/target SDK, user/profile, component/authority, caller.
* **ADB = shell UID**, not an ordinary app; root is separate.
* **Confirm app-level access:** minimally privileged companion/Drozer agent; record permissions, signer, grants.

<table><thead><tr><th width="137">Boundary</th><th>Check</th><th>Confirm</th></tr></thead><tbody><tr><td>Reachability</td><td>Export state, OS restrictions, receiver registration, URI grants</td><td>The specified caller can reach the component.</td></tr><tr><td>Permission</td><td>Manifest/runtime permission, signature permission, sender restrictions</td><td>A caller without the intended permission can still perform the relevant operation.</td></tr><tr><td>Authentication</td><td>Logged out, expired, or unauthenticated state</td><td>Protected local data/action is available without required authentication.</td></tr><tr><td>Authorization</td><td>Different owned account/role/object</td><td>An authenticated but unauthorized caller crosses a specific access boundary.</td></tr></tbody></table>

### Drozer Setup

* **Need:** compatible [Drozer](https://github.com/ReversecLabs/drozer/) console + agent APK; follow release requirements.
* **Device:** enable agent server; verify port (`31415` by default).
* **Host:**
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">adb forward tcp:31415 tcp:31415
    drozer console connect
    </code></pre>
* **Drozer console:** run all `run`/`help` commands here.
* Component `info -u` includes non-exported candidates.
  * <pre data-line-numbers><code>run app.package.attacksurface &#x3C;package-name>
    run app.package.manifest &#x3C;package-name>
    run app.package.debuggable
    help intents
    </code></pre>

## Activities

### Enumerate and Establish the Baseline

* **Map:** full class name, permissions, filters, extras, data URIs.
* **Trace:** `onCreate` / `onNewIntent`; note activity reuse.

{% tabs %}
{% tab title="ADB" %}
- **Linux Bash / Windows PowerShell:** inspect the installed package's activities, filters, permissions and enabled/exported state.
  * ```
    adb shell dumpsys package "<package-name>"
    ```
{% endtab %}

{% tab title="Drozer" %}
* **Drozer console:**
* <pre data-line-numbers><code>run app.activity.info -a &#x3C;package-name>
  </code></pre>
{% endtab %}

{% tab title="Grapefruit" %}
* **Host terminal:** start the installed interface with the device's Frida server running.
  * ```
    frida-ps -U
    igf
    ```
* Select the app, then use its manifest/component browser to inspect activities, filters and permissions. Its Intent builder can launch the observed component with the actual extras; this runs through instrumentation, not an ordinary independent caller.
{% endtab %}

{% tab title="AndroidSpect" %}
* Open the AndroidSpect app on the rooted device and start its server. Select the target app in its browser dashboard, then open **Components** and filter for exported activities. The displayed server address and password are provided by the app.
* **Emulator, host terminal:** forward the dashboard port and open `https://localhost:8008/`.
  * ```
    adb forward tcp:8008 tcp:8008
    ```
{% endtab %}

{% tab title="Inspeckage" %}
* With a compatible Xposed environment and Inspeckage enabled, select the target in its interface and inspect the activities and their export/permission details. Use its activity action for an in-process launch; use an external caller below when testing exported access.
{% endtab %}
{% endtabs %}

* Use the ADB or Drozer launch below to assess external-caller access; a launch originating inside the instrumented app does not establish that an unprivileged app can reach the same component.

### Test Direct Access and Inputs

{% tabs %}
{% tab title="ADB" %}
* **ADB:** bare launch, extra input. Types: `--es` string, `--ei` integer, `--ez` Boolean.
  * ```bash
    adb shell am start -n "<package-name>/<fully-qualified-activity-name>"
    adb shell am start -W -n "<package-name>/<activity-name>" --es "<extra-name>" "<test-value>"
    ```
{% endtab %}

{% tab title="Drozer" %}
* **Drozer:** bare launch, extra, or supported data URI.
  * <pre data-line-numbers><code>run app.activity.start --component &#x3C;package-name> &#x3C;activity-name>
    run app.activity.start --component &#x3C;package-name> &#x3C;activity-name> --extra string &#x3C;extra-name> &#x3C;test-value>
    run app.activity.start --component &#x3C;package-name> &#x3C;activity-name> --data-uri &#x3C;authorized-test-uri>
    </code></pre>
{% endtab %}
{% endtabs %}

* **States:** logged out, expired session, owned accounts/roles A/B.
* **Inputs:** missing extra, different owned ID, short invalid value; vary one at a time.
* **Lifecycle:** fresh launch versus existing task (`onCreate` / `onNewIntent`).
* **Results/nested intents/grants:** companion app + [advanced checks](advanced-ipc-and-providers.md#intent-result-and-binder-boundaries).
* **Implicit routing:** [Deep Links](component-testing.md#deep-links-and-url-handling); explicit launch does not prove handler ownership.

### Expected Result

* **Pass:** reject unauthorized callers/operations or enforce the required authentication and object/role checks.
* **Fail:** unauthorized access to a specific protected record/action; a screen opening alone is insufficient.
* **Blockers:** permission denial, wrong class name, disabled component, or task state; identify the cause rather than treating every failed launch as secure handling.

## Services

### Enumerate and Identify the Protocol

* **Map:** export state, permission, lifecycle; started / bound / both.
* **Started:** `onStartCommand` inputs. **Bound:** `onBind` and returned interface.
* **Messenger:** `Handler.handleMessage`; accepted `what`, `arg1`, `arg2`, Bundle fields/types.
* **AIDL/Binder:** methods, types, callbacks, caller checks; not interchangeable with Messenger.
* <pre data-line-numbers><code>run app.service.info -a &#x3C;package-name>
  help app.service.send
  </code></pre>

### Test a Started Service

* Trigger the legitimate action first, then repeat the same harmless input with one of these callers.

{% tabs %}
{% tab title="ADB" %}
- **Shell caller:**
  * ```bash
    adb shell am startservice -n "<package-name>/<service-name>" --es "<extra-name>" "<test-value>"
    ```
{% endtab %}

{% tab title="Drozer" %}
* **Drozer:** compare agent versus shell access.
  * ```bash
    run app.service.start --component <package-name> <service-name> --extra string <extra-name> <test-value>    
    ```
{% endtab %}
{% endtabs %}

* **Vary:** missing/malformed inputs, unauthorized account/object; disposable state only.
* **Blocked delivery:** check OS background/foreground restrictions separately from authorization.
* Foreground start requires a compatible notification/lifecycle; do not switch blindly.

### Test a Bound Service

* **Messenger only:** use observed integer codes, not generic sample values. Default Bundle: `Message.getData()`.
* ```bash
  run app.service.send <package-name> <service-name> --msg <what> <arg1> <arg2> --extra string <parameter> <test-value>
  ```
* `--msg`: `what arg1 arg2`. `--extra`: Bundle field.
* **Object Bundle variant:** only when the handler expects `Message.obj`.
* ```bash
  run app.service.send <package-name> <service-name> --msg <what> <arg1> <arg2> --extra string <parameter> <test-value> --bundle-as-obj
  ```
* **No reply:** inconclusive; check state/callbacks, one-way/async behavior, rejection, protocol mismatch.
* **AIDL/Binder:** compatible companion client; baseline an owned-record method, then vary one input.
* **Check:** per-method/record authorization, callbacks, caller identity. Successful binding is insufficient.

### Expected Result

* **Pass:** only intended callers can start/bind and perform each protected operation.
* **Fail:** unauthorized work, protected response data, or a state change under the service's authority; a successful bind/start alone is insufficient.
* **Stop a started service:** active client bindings may keep a bound service alive.
  * ```bash
    adb shell am stopservice -n "<package-name>/<service-name>"
    ```

## Broadcast Receivers

### Enumerate and Establish the Baseline

* **Map:** class, actions, data/categories, export state, sender permissions, registration lifetime.
* **Runtime:** inspect `registerReceiver` flags/permissions; keep the required feature open.
* **Baseline:** legitimate event with synthetic data; record action/outgoing broadcast.
* <pre data-line-numbers><code>run app.broadcast.info -a &#x3C;package-name>
  run app.broadcast.info -a &#x3C;package-name> -i
  </code></pre>

### Test Unauthorized Sending

{% tabs %}
{% tab title="ADB" %}
* **Explicit ADB:** manifest receiver, observed action, harmless extras.
  * ```bash
    adb shell am broadcast -n "<package-name>/<receiver-name>" -a "<observed-action>" --es "<extra-name>" "<test-value>"
    ```
* **Package-targeted ADB:** runtime receiver must be registered with a matching filter; class targeting may not work.
  * ```bash
    adb shell am broadcast -a "<observed-action>" -p "<package-name>" --es "<extra-name>" "<test-value>"
    ```
{% endtab %}

{% tab title="Drozer" %}
* **Explicit Drozer:** do not grant the permission being tested.
  * ```bash
    run app.broadcast.send --component <package-name> <receiver-name> --action <observed-action> --extra string <extra-name> <test-value>
    ```
* **Implicit Drozer:** isolated lab/approved recipients only; other matching apps can receive this.
  * ```bash
    run app.broadcast.send --action <intent-name> --extra string <parameter> <test-value>
    ```
{% endtab %}
{% endtabs %}

* **Vary:** missing/wrong-type extras, owned-record IDs; check authorization before side effects.
* Protected broadcasts/sender restrictions can block injection; record the restriction, do not bypass it.

### Test Unintended Reception

* **Select:** app-generated action with synthetic marker; exclude unrelated traffic.
* **Listen first**, then trigger the app's sending flow:
  * ```bash
    run app.broadcast.sniff --action <observed-action>
    ```
* **Need:** matching data/categories and OS-compatible receiver registration.
* **Incompatible helper:** companion receiver with matching filters and explicit export/permission settings.
* **Record:** receiver permissions; explicit / package / permission-restricted / implicit / ordered / sticky delivery.
* **No output:** verify registration, timing, filters, and actual sending before concluding.

### Expected Result

* **Pass (sending):** unauthorized senders cannot trigger protected actions, even when they know the action string.
* **Pass (reception):** sensitive payloads reach only intended/permitted recipients.
* **Fail:** a protected side effect from an unauthorized sender, or sensitive test data received by an unintended caller.
* ADB's `Broadcast completed` message does not prove the intended receiver ran or that authorization failed.
* Ctrl+C stops sniff output; the helper receiver can remain registered until its process exits.

## Content Providers

### Enumerate and Establish the Baseline

* **Map:** authority/routes, operations, export state, read/write/path permissions, grants.
* **Trace:** URI matcher and query/file handlers; authority alone is not a valid route.
* **Baseline:** create test record/file normally; record URI/ID and authorized behavior.
* <pre data-line-numbers><code>run app.provider.info -a &#x3C;package-name>
  run app.provider.finduri &#x3C;package-name>
  </code></pre>

### Test Scoped Reads

{% tabs %}
{% tab title="ADB" %}
* **ADB:** numeric test ID; adapt schema and shell quoting.
  * ```bash
    adb shell content query --uri "<content-uri>" --projection "<known-column>" --where "<id-column>=<numeric-test-record-id>"
    ```
{% endtab %}

{% tab title="Drozer" %}
* **Drozer:** scoped columns/record; compare unauthorized caller and owned accounts A/B.
  * ```bash
    run app.provider.query <content-uri> --projection <known-column> --selection "<id-column>=?" --selection-args <owned-record-id>
    ```
{% endtab %}
{% endtabs %}

\* \*\*Caller:\*\* the ADB query uses the shell UID; Drozer uses the agent's UID. Compare permissions and URI grants before interpreting different results.

* **Minimal query/columns:** owned item URI or small disposable dataset only; unfiltered collections may return all rows.
  * <pre data-line-numbers><code>run app.provider.query &#x3C;content-uri>
    run app.provider.columns &#x3C;content-uri>
    </code></pre>
* **Columns:** metadata query. Check installed module availability.
* **File read:** URI serving a harmless test file, not a table/collection.
  * ```bash
    run app.provider.read <content-uri>
    ```

### Test Writes and File/Grant Boundaries

* **Write inputs:** known columns/types and the test record's URI/ID.
* **Insert:** valid synthetic data; record returned URI/ID for update/delete.
  * <pre data-line-numbers><code>run app.provider.insert &#x3C;content-uri> --string &#x3C;column> &#x3C;test-value>
    run app.provider.update &#x3C;content-uri> --selection "&#x3C;id-column>=?" --selection-args &#x3C;owned-record-id> --string &#x3C;column> &#x3C;replacement-value>
    run app.provider.delete &#x3C;content-uri> --selection "&#x3C;id-column>=?" --selection-args &#x3C;owned-record-id>
    </code></pre>
* **Types:** repeat typed flags per schema. Keep update/delete selections scoped.
* **Authorization:** test each operation, including observed `call()` methods; read access does not imply write access.
* **Files/grants:** roots, modes, recipients, lifetime, revocation, logout; harmless files only.
* Non-exported providers can serve granted URIs; `grantUriPermissions=true` is not universal access.
* **Follow-up:** [SQL/routes/files/observers](advanced-ipc-and-providers.md#provider-operation-matrix), [Dirty Stream consumers](advanced-ipc-and-providers.md#dirty-stream-untrusted-provider-metadata).

### Optional Provider Scanners

* **Need:** compatible modules, approved package, disposable data, agreed scan scope.
* **Order below:** URI discovery, SQL-injection probes, SQL-table enumeration via candidate injection paths.
* Broad scans may expose schema or probe multiple routes without per-record limits.
* ```bash
  run scanner.provider.finduris -a <package-name>
  run scanner.provider.injection -a <package-name>
  run scanner.provider.sqltables -a <package-name>
  ```
* **Confirm hits:** controlled inputs + [provider matrix](advanced-ipc-and-providers.md#provider-operation-matrix); scanner output alone is insufficient.

### Expected Result

* **Pass:** authorized caller, operation, record, file path, and grant scope are enforced independently.
* **Fail:** a specific unauthorized read/write, unsafe query effect, unintended file access, or excessive grant.
* An empty cursor, exception, or guessed-URI failure is inconclusive without a known valid authorized control.

## Related Entry-Point Tests

### Deep Links and URL Handling

* **Custom scheme / package-constrained:** use the app's observed route.
  * ```bash
    adb shell am start -a android.intent.action.VIEW -d "<scheme>://<host>/<path>?<parameter>=<test-value>" <package-name>
    ```
* **Implicit Drozer:** harmless in-scope URI; record handler/chooser.
  * ```bash
    run app.activity.start --action android.intent.action.VIEW --data-uri <authorized-test-uri>
    ```
* **Compare:** explicit component, package-constrained, unconstrained routing.
* **Verification command:** Android 12+; older versions require manifest/resolver checks.
* **HTTPS baseline:** inspect verification, then launch.
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">adb shell pm get-app-links &#x3C;package-name>
    adb shell "am start -W -a android.intent.action.VIEW -c android.intent.category.BROWSABLE -d 'https://app.example.test/profile?id=test-record&#x26;mode=view' -p com.example.app"
    </code></pre>
* **Unconstrained variant:** also test from browser/companion.
  * ```bash
    adb shell "am start -W -a android.intent.action.VIEW -c android.intent.category.BROWSABLE -d 'https://app.example.test/profile?id=test-record&mode=view'"
    ```
* **Routing:** custom schemes versus verified HTTPS; domain association, signer, defaults, redirects, competing handlers, broad paths.
* **Vary one:** scheme, host/subdomain, path, query, fragment, encoding, duplicate/missing parameters, redirect; owned IDs/destinations only.
* **States:** logged out, accounts A/B, post-logout, expired session; verify reached data/action.
* **Login/reset:** one-time codes, state/session binding, redirects, PKCE.
* **Concrete route mutations:** replace the scheme/host/path/field with the actual route; deliver through the launch templates above. With A logged in, use B's known record; repeat logged out. For duplicate IDs, reverse their order too.
  * ```
    demo://records/view?id=REPLACE_B_RECORD_ID
    demo://records/view?id=REPLACE_A_RECORD_ID&id=REPLACE_B_RECORD_ID
    demo://records/view?id=
    demo://records/view?id=REPLACE_A_RECORD_ID&redirect=https%3A%2F%2Fprobe.example%2Flink-marker
    ```
* **Confirm:** protected B content/action is available under A or logged out, or an unintended redirect receives a sensitive callback. A screen opening or parser accepting duplicate parameters is not itself an authorization failure. For link-to-WebView routing, use the [WebView payloads](component-testing.md#untrusted-navigation-and-url-allowlists).
* **Association:** inspect `https://<authorized-host>/.well-known/assetlinks.json`.
* **Match:** relation, `android_app`, package, SHA-256 app-signing fingerprints against the installed build.
* **Certificates:** compare using `apksigner verify --print-certs`; upload signer may differ, re-signing can change verification.
* **JSON:** contains fingerprints; not itself signed with the app certificate.
* **Not proof of interception:** missing `autoVerify`, chooser, or handler priority alone.
* **Domain ownership/expiry:** passive checks only; no out-of-scope takeover/probing.

### WebView Runtime Checks

* **Need:** authorized ADB, `chrome://inspect/#devices`, app WebView debugging enabled.
* **Missing WebView:** debugging may be disabled. Instrumentation-enabled debugging is not release-build exposure.

#### Untrusted Navigation and URL Allowlists

* **Find the input:** trace the observed deep-link/Intent extra to `loadUrl` or `loadDataWithBaseURL`; record the allowed host and actual parameter name. Set the destination to a page you control, then try these host/parser variants. Replace `trusted.example` with the real allowed host and `probe.example` with your test host.
  * ```
    https://probe.example/webview.html
    https://trusted.example.probe.example/webview.html
    https://trusted.example@probe.example/webview.html
    https://probe.example/?next=https://trusted.example/
    http://trusted.example/
    ```
* **Launch template (Linux Bash / Windows PowerShell, unchanged):** encode the entire destination as the observed query parameter value. This example route must be replaced with the app's route; a guessed route opening nothing is not a negative result.
  * ```
    adb shell "am start -W -a android.intent.action.VIEW -d 'demo://web?url=https%3A%2F%2Fprobe.example%2Fwebview.html' -p com.example.app"
    ```
* **Redirect variant:** use an allowed-host route that actually redirects to the test page. Compare the initial URL and final `location.origin`; test navigation after the initial load too.
* **Confirm:** the unintended origin loads inside the app's WebView, not only an external browser. Establish the additional bridge/session/file access below; arbitrary external navigation alone does not establish account takeover.

#### Native Bridge from Untrusted Content

* **Identify:** in JADX, map the `addJavascriptInterface` object name to its `@JavascriptInterface` methods and argument types. Use the actual method, not an assumed `Android` object. For `WebMessageListener`/ports, use the app's registered channel and message schema instead.
* **Host this page at the controlled URL above:** replace the bridge/method and string argument with a known read-only or marker operation. Methods with other argument counts/types require that actual signature.
  * ```html
    <!doctype html>
    <meta charset="utf-8">
    <pre id="result"></pre>
    <script>
    const result = document.getElementById('result');
    try {
      const value = window['REPLACE_BRIDGE']['REPLACE_METHOD']('webview-probe');
      result.textContent = location.origin + '\n' + String(value);
    } catch (error) { result.textContent = String(error); }
    </script>
    ```
* **Frame variant:** embed the test page as `<iframe src="https://probe.example/webview.html"></iframe>` in a page reachable through the app. A JavaScript interface is exposed to frames too; verify the method runs from the frame, not just the top-level page.
* **Confirm:** untrusted content invokes an unintended sensitive native operation, receives a protected value, or crosses account boundaries. A bridge that only performs its intended public action is not automatically vulnerable. DevTools invocation alone proves method behavior, not attacker reachability.

#### Script Injection into a Trusted Page

* **HTML sink:** supply the marker below through the actual rendered search/name/message parameter. **JavaScript string sink:** use the second payload only where the value is interpolated into a single-quoted JavaScript string; adapt the delimiter to the observed code.
  * ```html
    <img src=x onerror="document.documentElement.dataset.webviewProbe=location.origin">
    ```
  * ```
    ';document.documentElement.dataset.webviewProbe=location.origin;//
    ```
* **Check the page after the app processes the input:**
  * ```javascript
    document.documentElement.dataset.webviewProbe;
    ```
* **Confirm:** the marker contains the trusted page's origin after externally supplied input executes. Merely loading your own page and running its own script is not trusted-origin XSS.

#### File Access, Mixed Content, and Session Isolation

* **Local-page file-read probe:** from an attacker-reachable `file://` page, run the following against a known marker file in the app's readable storage; use the resolved path, not another app's sandbox. A hosted HTTPS page and a local file page exercise different access settings.
  * ```javascript
    const request = new XMLHttpRequest();
    request.onload = () => { document.body.textContent = request.responseText; };
    request.onerror = () => { document.body.textContent = 'read blocked'; };
    request.open('GET', 'file:///data/user/0/com.example.app/files/webview-marker.txt');
    request.send();
    ```
* **Confirm file exposure:** the controlled page displays the known marker from outside its intended read boundary. A permissive setting, failed fetch, or file loaded directly by the app does not demonstrate cross-file access.
* **Mixed content:** add `<script src="http://probe.example/webview-marker.js"></script>` to a reachable HTTPS page; serve `document.documentElement.dataset.mixedProbe='loaded';` from that HTTP URL. Confirm execution and whether the resource's content can be influenced in the tested network model.
* **Session test:** log in as A, open a protected WebView route, log out, then revisit that route and repeat its protected request. Log in as B and revisit A's known record. Separate stale rendered content from a new response authorized with retained A credentials.
* **Debugging:** inspect the unmodified release build first. Debugging enabled only by your hook is an analysis aid, not proof the release exposes remote inspection.

#### Cookie Scope and Flags

* An authentication cookie is exposed to unintended hosts/paths, readable by page JavaScript when it should be HttpOnly, sent over HTTP, or usable in an unintended cross-site action.
* In the inspected WebView, record the real authentication cookie's `Set-Cookie` attributes and stored Domain/Path/Secure/HttpOnly/SameSite values from the Network and Application panels. `document.cookie` and native `CookieManager.getCookie()` are not complete attribute inventories.
* **WebView console:** replace the actual session-cookie name; compare with the cookie seen on the protected request. An HttpOnly cookie can authenticate that request while remaining absent from this JavaScript view.
  * ```javascript
    ({ origin: location.origin,
       sessionCookieVisible: document.cookie.split(';').some(value =>
         value.trim().startsWith('REPLACE_SESSION_COOKIE=')) });
    ```

<table><thead><tr><th width="98">Attribute</th><th width="280">Test</th><th>Confirm</th></tr></thead><tbody><tr><td>Domain</td><td>Open a controlled sibling host beneath the configured parent domain; inspect its received Cookie header</td><td>A sensitive cookie reaches a sibling origin outside the intended trust boundary. Host-only cookies should not be sent there.</td></tr><tr><td>Path</td><td>Request an actual sibling route outside the intended cookie path; inspect the outgoing Cookie header</td><td>Cookie is sent outside its configured/intended scope. Path is routing scope, not isolation from hostile JavaScript elsewhere on the same origin.</td></tr><tr><td>Secure</td><td>Open the matching <code>http://</code> host/path, if HTTP is reachable, and inspect the request</td><td>Authentication cookie is transmitted over cleartext; a missing flag alone does not establish a reachable transmission.</td></tr><tr><td>HttpOnly</td><td>Run the console probe in the cookie's matching host/path</td><td>Actual authentication cookie is JavaScript-readable where the policy requires HttpOnly; native privileged cookie access does not prove a page-JavaScript bypass.</td></tr><tr><td>SameSite</td><td>Submit a cross-site POST from a controlled different-site page to the real reversible test action</td><td>Cookie is attached and the action succeeds without the intended CSRF check. Different origins can still be same-site; top-level GET with Lax cookies can be expected.</td></tr></tbody></table>

* **Cross-site POST PoC:** replace the endpoint and form fields with the actual test action; serve from a different site, not just another port/subdomain. Check both request Cookie and the committed test-state change; `SameSite=None; Secure` may be intentional when independent CSRF protection exists.
  * ```html
    <form method="post" action="https://trusted.example/REPLACE_TEST_ACTION">
      <input name="REPLACE_FIELD" value="cookie-probe">
      <button type="submit">Submit test action</button>
    </form>
    ```

#### WebView Profile and Account Boundaries

* WebViews intended to have separate identities reuse another account's cookies, DOM storage or authenticated state. Shared storage between ordinary WebViews in one app profile is not automatically a flaw, and it is not global sharing across unrelated apps.
* In A's WebView at the target origin, set profile markers; then open that same origin in the supposedly isolated browser/profile/account-B surface and inspect them using the second command. Also repeat a protected request for A's known object.
  * ```javascript
    localStorage.setItem('webview-profile-probe', 'account-A');
    document.cookie = 'webview_profile_probe=account-A; Path=/; Secure; SameSite=Lax';
    ```
  * ```javascript
    ({ origin: location.origin, localMarker: localStorage.getItem('webview-profile-probe'),
       cookieMarker: document.cookie.includes('webview_profile_probe=account-A') });
    ```
* **Check the implementation:** map process/profile ownership, `WebView.setDataDirectorySuffix` where used (API 28+, process-wide and set before WebView initialization), and cookie/DOM-storage lifecycle. It is not a per-WebView account-switch API. Repeat the app's normal restart/logout transition without changing its storage configuration through a hook.
* **Confirm:** a surface intended to be isolated can use A's actual credentials or read A's private data. Marker crossover identifies a shared store; it does not alone establish unauthorized access. Existing logout/API checks remain in [File Access, Mixed Content, and Session Isolation](component-testing.md#file-access-mixed-content-and-session-isolation).

#### Third-Party Script in a Trusted Page

* An attacker-controlled external JavaScript dependency executes with the trusted page's origin and can use its readable data/native bridge. A classic `<script src>` executes in the including document's context, not in an isolated frame belonging to the script host.
* Serve this as the actual external dependency through a demonstrated controllable asset or owner-provided fixture; keep the top-level trusted page URL unchanged. It sets only a marker. Then use the existing [bridge test](component-testing.md#native-bridge-from-untrusted-content) for the observed native operation from this script context.
  * ```javascript
    document.documentElement.dataset.thirdPartyProbe = JSON.stringify({
      page: location.href, executionOrigin: location.origin,
      readableSessionCookie: document.cookie.split(';').some(value =>
        value.trim().startsWith('REPLACE_SESSION_COOKIE='))
    });
    ```
* **Confirm:** changing the real dependency causes script execution in the trusted origin and an unintended protected read/native effect. A normal included script or one injected only through DevTools proves the execution model, not an attacker-controlled dependency. HttpOnly cookies remain unreadable but may still authenticate requests initiated by that script.

#### Resource Interception and Cache Boundaries

* **Map the actual rule:** locate `shouldInterceptRequest`/`WebResourceResponse`, its accepted host/path, and the file/cache key it selects. For a route mapping `/assets/<name>` to local files, test these path suffixes; substitute a real marker outside the intended asset root but readable by the app.
  * ```
    /assets/../files/webview-marker.txt
    /assets/%2e%2e%2ffiles%2fwebview-marker.txt
    /assets/..%252ffiles%252fwebview-marker.txt
    /assets/webview-marker.txt?path=../files/webview-marker.txt
    ```
* **Read probe in the actual page context:** replace the URL with the mapped route. Inspect the final response and marker; if CORS prevents JavaScript reading, also distinguish that browser restriction from what the native interceptor actually returned.
  * ```javascript
    fetch('https://trusted.example/assets/REPLACE_CANDIDATE_PATH', { cache: 'no-store' })
      .then(response => response.text())
      .then(text => { document.body.textContent = 'marker=' + text.includes('webview-probe'); })
      .catch(error => { document.body.textContent = String(error); });
    ```
* **Cache test:** load a private A response containing `cache-probe-A`; switch to B, reopen the same app route and compare online, offline and process-restart behavior. Change the observed query/account selector independently. Use the existing [network transition commands](business-logic-and-backend.md#request-signing-and-replay).
* **Confirm:** the mapped URL discloses an unintended file, or B receives A's private response due to a shared/misnormalized cache key. For poisoning, inject a marker through the actual attacker-controlled content source, then show that a later trusted load reuses it; rewriting traffic with your own proxy alone does not establish attacker control.

#### Geolocation, Camera, and Microphone Grants

* **Host on the controlled HTTPS origin:** load it through the real navigation entry point; tap each button. Compare the trusted origin, an untrusted top-level origin and an iframe delegated with `allow="geolocation; camera; microphone"`. Test app OS permissions granted and denied separately.
  * ```html
    <!doctype html>
    <meta charset="utf-8">
    <button onclick="locate()">Location</button>
    <button onclick="capture({video:true})">Camera</button>
    <button onclick="capture({audio:true})">Microphone</button>
    <pre id="result"></pre>
    <script>
    const show = value => { document.getElementById('result').textContent = String(value); };
    function locate() {
      navigator.geolocation.getCurrentPosition(
        value => show('location granted; accuracy=' + value.coords.accuracy),
        error => show(error.message));
    }
    async function capture(constraints) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        show('granted: ' + stream.getTracks().map(track => track.kind).join(','));
        stream.getTracks().forEach(track => track.stop());
      } catch (error) { show(error); }
    }
    </script>
    ```
* **Confirm:** an unintended origin/frame receives the actual location/stream because native `onPermissionRequest` or geolocation callbacks grant it without the required origin-level decision. OS permission alone is not per-origin consent; a rejected promise/unsupported API does not prove the native callback validates origins.

#### File Chooser Destination and Grants

* **Hosted-page probe:** use a known `file-chooser-probe` marker file. Compare ordinary selection, Cancel, a page navigation while the chooser is open, and the app's capture/provider variant.
  * ```html
    <!doctype html>
    <meta charset="utf-8">
    <input id="pick" type="file">
    <pre id="result"></pre>
    <script>
    document.getElementById('pick').addEventListener('change', async event => {
      const file = event.target.files[0];
      if (!file) return;
      const text = await file.text();
      document.getElementById('result').textContent = location.origin +
        '; name=' + file.name + '; marker=' + text.includes('file-chooser-probe');
    });
    </script>
    ```
* For a custom result/provider flow, use the [companion file provider](advanced-ipc-and-providers.md#dirty-stream-untrusted-provider-metadata) with its normal filename and marker changed to `file-chooser-probe`; return only the observed MIME/URI contract. Trace `onShowFileChooser` result routing and URI grants.
* **Confirm:** a page receives a file not selected/authorized for it, or a stale chooser callback delivers the marker to the wrong origin after navigation. A page reading the file deliberately selected for that page is expected.
* Static candidates: [WebView, IPC, and Dependency Checks](../static-testing/webview-ipc-and-dependencies.md).
* References: [App Link verification](https://developer.android.com/training/app-links/verify-android-applinks), [WebView debugging](https://developer.chrome.com/docs/devtools/remote-debugging/webviews/).

## References

* [Android app components](https://developer.android.com/guide/components/fundamentals), [Intents and intent filters](https://developer.android.com/guide/components/intents-filters).
* Drozer: [service modules](https://github.com/ReversecLabs/drozer/blob/develop/src/drozer/modules/app/service.py), [broadcast modules](https://github.com/ReversecLabs/drozer/blob/develop/src/drozer/modules/app/broadcast.py), [provider modules](https://github.com/ReversecLabs/drozer/blob/develop/src/drozer/modules/app/provider.py)
