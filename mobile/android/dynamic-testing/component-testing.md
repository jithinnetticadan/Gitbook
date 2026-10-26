# Component Testing

[Setup](#adb-probes-and-caller-identity) | [Drozer](#drozer-setup) | [Activities](#activities) | [Services](#services) | [Receivers](#broadcast-receivers) | [Providers](#content-providers) | [Deep Links](#deep-links-and-verified-app-links) | [WebViews](#webview-runtime-checks)

{% hint style="info" %}
* Use an authorized test device and test accounts; replace command placeholders before use.
* Preserve originals, protect dumps, and restore the lab afterward.
{% endhint %}

{% hint style="warning" %}
* **Basic prerequisites:** installed test app, authorized ADB access, observed component names/inputs, and disposable test records.
* Root and Frida are **not required** for ordinary ADB/Drozer component tests. Complete [Mandatory Preflight](preflight-and-frida-setup.md#mandatory-preflight) only when using instrumentation or a patched build.
* Identify candidates using [Manifest and Components](../static-testing/manifest-and-components.md); confirm them against the installed build.
{% endhint %}

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

### Relationship to Advanced IPC

* **Here:** enumerate, invoke, test access/inputs; Intent and provider commands.
* **[Advanced IPC](advanced-ipc-and-providers.md):** forwarding, results, PendingIntent, Binder identity, provider query/path/grant abuse, Dirty Stream.

## Runtime Component Testing

1. **Enumerate:** names/authorities, export state, permissions, registrations, grants.
2. **Map inputs:** observed actions, extras/types, routes, methods, handlers.
3. **Baseline:** legitimate action on owned data; record local/API effects.
4. **Compare:** intended/unauthorized caller; logged out; owned accounts A/B and roles.
5. **Vary:** one input at a time; bounded values and harmless destinations.
6. **Confirm/restore:** protected data/action accessed; test state cleaned up.

* Follow [Activities](#activities), [Services](#services), [Broadcast Receivers](#broadcast-receivers), then [Content Providers](#content-providers).
* `exported=true`, successful command delivery, or a crash alone does not show an access-control failure.
* Track each discovered input, method, route, operation, and caller/grant combination: **tested / N/A / blocked**. Commands alone are not full coverage.

### ADB Probes and Caller Identity

* **Need:** SDK Platform Tools, USB debugging, authorized host.
* **Run:** `sh` blocks on host; replace placeholders; preserve shell quoting for spaces, `$`, and `&`.
* **Multiple devices:** add `-s <device-serial>` after every `adb`, including forwards.
* **Before testing:** preserve baseline logs; launches can change state.

```sh
adb version
adb devices -l
adb shell getprop ro.build.version.sdk
adb shell dumpsys package "<package-name>"
```

* **Record:** build, OS/target SDK, user/profile, component/authority, caller.
* **ADB = shell UID**, not an ordinary app; root is separate.
* **Confirm app-level access:** minimally privileged companion/Drozer agent; record permissions, signer, grants.
* Do not add root/permissions to force a denied ordinary-app test to pass.

| Boundary       | Check                                                                  | Confirm                                                                            |
| -------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Reachability   | Export state, OS restrictions, receiver registration, URI grants       | The specified caller can reach the component.                                      |
| Permission     | Manifest/runtime permission, signature permission, sender restrictions | A caller without the intended permission can still perform the relevant operation. |
| Authentication | Logged out, expired, or unauthenticated state                          | Protected local data/action is available without required authentication.          |
| Authorization  | Different owned account/role/object                                    | An authenticated but unauthorized caller crosses a specific access boundary.       |

### Drozer Setup

* **Need:** compatible [Drozer](https://github.com/WithSecureLabs/drozer) console + agent APK; follow release requirements.
* **Device:** enable agent server; verify port (`31415` by default).
* **Host:**

```sh
adb forward tcp:31415 tcp:31415
drozer console connect
```

* **Drozer console:** run all `run`/`help` commands here; check installed module help.
* Component `info -u` includes non-exported candidates; test reachability separately.

```text
run app.package.attacksurface <package-name>
run app.package.manifest <package-name>
run app.package.debuggable
help intents
```

* `app.package.debuggable`: inventory only, not proof of access.
* Runtime receivers: inspect registration code and trigger the relevant app state.

## Activities

### Enumerate and Establish the Baseline

* **Map:** full class name, permissions, filters, extras, data URIs.
* **Trace:** `onCreate` / `onNewIntent`; note activity reuse.
* **Baseline:** open normally; record account, protected action/data, preceding checks.

```text
run app.activity.info -a <package-name>
```

### Test Direct Access and Inputs

* **ADB:** bare launch, then harmless input. Types: `--es` string, `--ei` integer, `--ez` Boolean.

```sh
adb shell am start -n "<package-name>/<fully-qualified-activity-name>"
adb shell am start -W -n "<package-name>/<activity-name>" --es "<extra-name>" "<test-value>"
```

* **Drozer:** bare launch, extra, or supported data URI.

```text
run app.activity.start --component <package-name> <activity-name>
run app.activity.start --component <package-name> <activity-name> --extra string <extra-name> <test-value>
run app.activity.start --component <package-name> <activity-name> --data-uri <authorized-test-uri>
```

* **States:** logged out, expired session, owned accounts/roles A/B.
* **Inputs:** missing extra, different owned ID, short invalid value; vary one at a time.
* **Lifecycle:** fresh launch versus existing task (`onCreate` / `onNewIntent`).
* **Results/nested intents/grants:** companion app + [advanced checks](advanced-ipc-and-providers.md#intent-result-and-binder-boundaries).
* **Implicit routing:** [Deep Links](#deep-links-and-verified-app-links); explicit launch does not prove handler ownership.

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

```text
run app.service.info -a <package-name>
help app.service.send
```

### Test a Started Service

* **Baseline:** trigger normally, then repeat the same harmless input below.

```sh
adb shell am startservice -n "<package-name>/<service-name>" --es "<extra-name>" "<test-value>"
```

* **Drozer:** compare agent versus shell access.

```text
run app.service.start --component <package-name> <service-name> --extra string <extra-name> <test-value>
```

* **Vary:** missing/malformed inputs, unauthorized account/object; disposable state only.
* **Blocked delivery:** check OS background/foreground restrictions separately from authorization.
* Foreground start requires a compatible notification/lifecycle; do not switch blindly.

### Test a Bound Service

* **Messenger only:** use observed integer codes, not generic sample values. Default Bundle: `Message.getData()`.

```text
run app.service.send <package-name> <service-name> --msg <what> <arg1> <arg2> --extra string <parameter> <test-value>
```

* `--msg`: `what arg1 arg2`. `--extra`: Bundle field.
* **Object Bundle variant:** only when the handler expects `Message.obj`.

```text
run app.service.send <package-name> <service-name> --msg <what> <arg1> <arg2> --extra string <parameter> <test-value> --bundle-as-obj
```

* **No reply:** inconclusive; check state/callbacks, one-way/async behavior, rejection, protocol mismatch.
* **AIDL/Binder:** compatible companion client; baseline an owned-record method, then vary one input.
* **Check:** per-method/record authorization, callbacks, caller identity. Successful binding is insufficient.

### Expected Result

* **Pass:** only intended callers can start/bind and perform each protected operation.
* **Fail:** unauthorized work, protected response data, or a state change under the service's authority; a successful bind/start alone is insufficient.
* **Cleanup:** stop only disposable work started by the test and unbind companion clients; stopping a started service does not necessarily remove active bindings.

```sh
adb shell am stopservice -n "<package-name>/<service-name>"
```

## Broadcast Receivers

### Enumerate and Establish the Baseline

* **Map:** class, actions, data/categories, export state, sender permissions, registration lifetime.
* **Runtime:** inspect `registerReceiver` flags/permissions; keep the required feature open.
* **Baseline:** legitimate event with synthetic data; record action/outgoing broadcast.

```text
run app.broadcast.info -a <package-name>
run app.broadcast.info -a <package-name> -i
```

### Test Unauthorized Sending

* **Explicit ADB:** manifest receiver, observed action, harmless extras.

```sh
adb shell am broadcast -n "<package-name>/<receiver-name>" -a "<observed-action>" --es "<extra-name>" "<test-value>"
```

* **Explicit Drozer:** do not grant the permission being tested.

```text
run app.broadcast.send --component <package-name> <receiver-name> --action <observed-action> --extra string <extra-name> <test-value>
```

* **Implicit Drozer:** isolated lab/approved recipients only; other matching apps can receive this.

```text
run app.broadcast.send --action <intent-name> --extra string <parameter> <test-value>
```

* **Package-targeted ADB:** runtime receiver must be registered with a matching filter; class targeting may not work.

```sh
adb shell am broadcast -a "<observed-action>" -p "<package-name>" --es "<extra-name>" "<test-value>"
```

* **Vary:** missing/wrong-type extras, owned-record IDs; check authorization before side effects.
* Protected broadcasts/sender restrictions can block injection; record the restriction, do not bypass it.

### Test Unintended Reception

* **Select:** app-generated action with synthetic marker; exclude unrelated traffic.
* **Listen first**, then trigger the app's sending flow:

```text
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
* **Cleanup:** Ctrl+C stops sniff output; verify test listeners are removed, unregister companion receivers, and stop the test-agent process if a listener remains.

## Content Providers

### Enumerate and Establish the Baseline

* **Map:** authority/routes, operations, export state, read/write/path permissions, grants.
* **Trace:** URI matcher and query/file handlers; authority alone is not a valid route.
* **Baseline:** create test record/file normally; record URI/ID and authorized behavior.

```text
run app.provider.info -a <package-name>
run app.provider.finduri <package-name>
```

### Test Scoped Reads

* **ADB:** numeric test ID; adapt schema and shell quoting.

```sh
adb shell content query --uri "<content-uri>" --projection "<known-column>" --where "<id-column>=<numeric-test-record-id>"
```

* **Drozer:** scoped columns/record; compare unauthorized caller and owned accounts A/B.

```text
run app.provider.query <content-uri> --projection <known-column> --selection "<id-column>=?" --selection-args <owned-record-id>
```

* **Minimal query/columns:** owned item URI or small disposable dataset only; unfiltered collections may return all rows.

```text
run app.provider.query <content-uri>
run app.provider.columns <content-uri>
```

* **Columns:** metadata query. Check installed module availability.
* **File read:** URI serving a harmless test file, not a table/collection.

```text
run app.provider.read <content-uri>
```

* Console file output is not binary-safe; use a binary-safe export for file contents.

### Test Writes and File/Grant Boundaries

* **Writes require:** approval, disposable records, known columns/types, cleanup plan; otherwise skip.
* **Insert:** valid synthetic data; record returned URI/ID for update/delete.

```text
run app.provider.insert <content-uri> --string <column> <test-value>
run app.provider.update <content-uri> --selection "<id-column>=?" --selection-args <owned-record-id> --string <column> <replacement-value>
run app.provider.delete <content-uri> --selection "<id-column>=?" --selection-args <owned-record-id>
```

* **Types:** repeat typed flags per schema. Keep update/delete selections scoped.
* **Authorization:** test each operation, including observed `call()` methods; read access does not imply write access.
* **Files/grants:** roots, modes, recipients, lifetime, revocation, logout; harmless files only.
* Non-exported providers can serve granted URIs; `grantUriPermissions=true` is not universal access.
* **Follow-up:** [SQL/routes/files/observers](advanced-ipc-and-providers.md#provider-operation-matrix), [Dirty Stream consumers](advanced-ipc-and-providers.md#dirty-stream-untrusted-provider-metadata).

### Optional Provider Scanners

* **Need:** compatible modules, approved package, disposable data, agreed scan scope; read installed help.
* **Order below:** URI discovery, SQL-injection probes, SQL-table enumeration via candidate injection paths.
* Broad scans may expose schema or probe multiple routes without per-record limits; use manual tests when scope is narrower.

```text
run scanner.provider.finduris -a <package-name>
run scanner.provider.injection -a <package-name>
run scanner.provider.sqltables -a <package-name>
```

* **Confirm hits:** controlled inputs + [provider matrix](advanced-ipc-and-providers.md#provider-operation-matrix); scanner output alone is insufficient.

### Expected Result

* **Pass:** authorized caller, operation, record, file path, and grant scope are enforced independently.
* **Fail:** a specific unauthorized read/write, unsafe query effect, unintended file access, or excessive grant.
* An empty cursor, exception, or guessed-URI failure is inconclusive without a known valid authorized control.
* **Cleanup:** remove inserted records/staging files, restore modified test values, and revoke temporary grants without deleting unrelated data.

## Related Entry-Point Tests

### Deep Links and Verified App Links

* **Custom scheme / package-constrained:** use the app's observed route.

```sh
adb shell am start -a android.intent.action.VIEW -d "<scheme>://<host>/<path>?<parameter>=<test-value>" <package-name>
```

* **Implicit Drozer:** harmless in-scope URI; record handler/chooser.

```text
run app.activity.start --action android.intent.action.VIEW --data-uri <authorized-test-uri>
```

* **Compare:** explicit component, package-constrained, unconstrained routing.
* **Verification command:** Android 12+; older versions require manifest/resolver checks.
* **HTTPS baseline:** inspect verification, then launch.

```sh
adb shell pm get-app-links <package-name>
adb shell "am start -W -a android.intent.action.VIEW -c android.intent.category.BROWSABLE -d 'https://app.example.test/profile?id=test-record&mode=view' -p com.example.app"
```

* Replace example host/package/record; outer quotes protect URI `&` on the device shell.
* **Unconstrained variant:** also test from browser/companion; targeted launches do not prove default-handler ownership.

```sh
adb shell "am start -W -a android.intent.action.VIEW -c android.intent.category.BROWSABLE -d 'https://app.example.test/profile?id=test-record&mode=view'"
```

* **Routing:** custom schemes versus verified HTTPS; domain association, signer, defaults, redirects, competing handlers, broad paths.
* **Vary one:** scheme, host/subdomain, path, query, fragment, encoding, duplicate/missing parameters, redirect; owned IDs/destinations only.
* **States:** logged out, accounts A/B, post-logout, expired session; verify reached data/action.
* **Login/reset:** one-time codes, state/session binding, redirects, PKCE; redact live codes/history.
* **Association:** inspect `https://<authorized-host>/.well-known/assetlinks.json`.
* **Match:** relation, `android_app`, package, SHA-256 app-signing fingerprints against the installed build.
* **Certificates:** compare using `apksigner verify --print-certs`; upload signer may differ, re-signing can change verification.
* **JSON:** contains fingerprints; not itself signed with the app certificate.
* **Not proof of interception:** missing `autoVerify`, chooser, or handler priority alone.
* **Domain ownership/expiry:** passive checks only; no out-of-scope takeover/probing.

### WebView Runtime Checks

* **Need:** authorized ADB, `chrome://inspect/#devices`, app WebView debugging enabled.
* **Missing WebView:** debugging may be disabled. Instrumentation-enabled debugging is not release-build exposure.

1. **Inventory:** URL/origin, redirects/frames, `WebViewClient`, settings, cookies/session.
2. **Trace:** `loadUrl`, `loadDataWithBaseURL`, `addJavascriptInterface`, message-channel registration.
3. **Map bridge:** actual name/class, methods, origin rules, availability; do not assume `Android` or complete JS enumeration.
4. **Invoke:** harmless observed method from controlled content; prove attacker-reachable URL/navigation/injection.
5. **Check:** origin/frame validation, file/content access, navigation, sensitive URLs/logs/cookies, logout, native effects.
6. **Capture:** URL/content, navigation chain, invocation, local/API effect. DevTools execution alone is not proof of remote injection.

* Static candidates: [WebView, IPC, and Dependency Checks](../static-testing/webview-ipc-and-dependencies.md).
* References: [App Link verification](https://developer.android.com/training/app-links/verify-android-applinks), [WebView debugging](https://developer.chrome.com/docs/devtools/remote-debugging/webviews/).

## Cleanup

* For API effects, verify server-side authorization/results; intent filters and preceding screens are not access controls.
* Restore disposable state, remove test listeners/grants, and stop the Drozer agent server.
* Remove only the test forward; preserve unrelated forwards.

```sh
adb forward --remove tcp:31415
```

* Stuck or unexpected results: [Troubleshooting and Test Cleanup](validation-and-troubleshooting.md).
* References: [Android app components](https://developer.android.com/guide/components/fundamentals), [Intents and intent filters](https://developer.android.com/guide/components/intents-filters).
* Drozer argument references: [service modules](https://github.com/WithSecureLabs/drozer/blob/develop/src/drozer/modules/app/service.py), [broadcast modules](https://github.com/WithSecureLabs/drozer/blob/develop/src/drozer/modules/app/broadcast.py), [provider modules](https://github.com/WithSecureLabs/drozer/blob/develop/src/drozer/modules/app/provider.py). Installed release behavior may differ from the development branch.
