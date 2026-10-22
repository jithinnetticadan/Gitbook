# Component Testing

{% hint style="info" %}
Use an authorized test device and test accounts. Preserve originals; protect dumps and restore the lab afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Complete the [Mandatory Preflight](preflight-and-frida-setup.md#mandatory-preflight) first. Candidate components come from [Manifest and Components](../static-testing/manifest-and-components.md).
{% endhint %}

## Runtime Component Testing

* Check exported activities, services, receivers, and providers.
* Test authorization, input handling, and data exposure. `exported=true` alone is not a finding.

```sh
adb shell am start -n <package-name>/<fully-qualified-activity-name>
adb shell am start -a android.intent.action.VIEW -d "<scheme>://<host>/<path>?<parameter>=<test-value>" <package-name>
```

### ADB Probes and Caller Identity

Start with manifest candidates and confirm the installed package, including runtime receivers and URI grants. Use only known test actions/records; even starting a component can change state:

```sh
adb shell dumpsys package <package-name>
adb shell am start -W -n <package-name>/<activity-name> --es <extra-name> <test-value>
adb shell am startservice -n <package-name>/<service-name> --es <extra-name> <test-value>
adb shell am broadcast -n <package-name>/<receiver-name> -a <observed-action> --es <extra-name> <test-value>
adb shell content query --uri <content-uri> --projection <known-column> --where '<id-column>=<test-record-id>'
```

`startservice` does not exercise a bound-service Binder protocol; background-service restrictions may also block it. Use a small authorized companion app for binding/caller-UID tests. A provider query needs its actual URI, projection, and selection; avoid bulk retrieval or destructive writes.

| Boundary       | Check                                                                  | Required Evidence                                                                  |
| -------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Reachability   | Export state, OS restrictions, receiver registration, URI grants       | The specified caller can reach the component.                                      |
| Permission     | Manifest/runtime permission, signature permission, sender restrictions | A caller without the intended permission can still perform the relevant operation. |
| Authentication | Logged out, expired, or unauthenticated state                          | Protected local data/action is available without required authentication.          |
| Authorization  | Different owned account/role/object                                    | An authenticated but unauthorized caller crosses a specific access boundary.       |

ADB normally acts as the **shell UID**, with permissions an ordinary app may not have. Root is a different capability again. Validate ordinary-app claims with a separately installed, minimally privileged companion app, and record its permissions, signing identity, and URI grants. Drozer results also reflect its agent's permissions. An activity opening without sensitive data/action is not by itself an authentication bypass. Implicit broadcasts are not universally readable: permissions, package targeting, receiver flags, and OS behavior matter.

### Deep Links and Verified App Links

On Android 12+ where supported, inspect verification state before changing it:

```sh
adb shell pm get-app-links <package-name>
adb shell "am start -W -a android.intent.action.VIEW -c android.intent.category.BROWSABLE -d 'https://app.example.test/profile?id=test-record&mode=view' -p com.example.app"
```

Replace the example host/package/record with in-scope values. The outer command quotes preserve the URI's `&` for the device shell. Repeat **without `-p`**, and from a browser/companion app, to test real OS routing; a package-constrained launch does not establish default-handler ownership. On older Android, use manifest/package inspection and actual resolver behavior.

* Distinguish unverified custom schemes from verified HTTPS App Links. Inspect domain association, signing certificate identity, user defaults, and redirects; a re-signed test APK can change verification.
* Vary scheme, host/subdomain, path, query, fragment, encoding, duplicate/missing parameters, and redirect targets one at a time. Use harmless test destinations and owned identifiers.
* Repeat logged out, logged in as A/B, after logout, and with expired sessions. Validate the data/action reached, not merely the screen that appears.
* For login/reset callbacks, check one-time code use, state/session binding, redirect validation, and PKCE where applicable. Do not expose live codes in screenshots or shell history.

For HTTPS App Links, inspect `https://<authorized-host>/.well-known/assetlinks.json`: relation, `android_app` namespace, package name, and SHA-256 **app-signing** certificate fingerprints must match the installed app and intended trust relationship. Play app-signing and upload certificates can differ. The JSON contains fingerprints; it is not itself "signed with the app certificate." Compare using `apksigner verify --print-certs` on the assessed APK.

Test broad path patterns and competing handlers under actual OS verification/user defaults. Missing `autoVerify` or a chooser does not automatically prove token interception, and priority does not universally override modern link handling. Check trusted-domain ownership/expiry passively; do not register, take over, or probe out-of-scope domains to demonstrate the risk.

### WebView Runtime Checks

Use authorized ADB and Chrome's `chrome://inspect/#devices` when WebView debugging is enabled in the assessed app. A WebView absent from DevTools may simply have debugging disabled. Enabling it through instrumentation changes the test configuration and is not evidence that the release build exposes debugging.

1. Identify each live WebView, its actual URL/origin, redirects/frames, concrete `WebViewClient`, settings, and cookie/session state.
2. Observe `loadUrl`, `loadDataWithBaseURL`, `addJavascriptInterface`, and message-channel registration as applicable. Record bridge name/class, exposed methods, origin rules, and when the bridge is available; do not assume its name is `Android` or that JavaScript object enumeration finds everything.
3. Select an innocuous observed bridge method and invoke it using controlled test content. Prove how an attacker could supply that content: an allowed external URL, unsafe navigation, injected data, or another reachable source.
4. Test origin/frame validation, file/content access, unsafe navigation/redirects, sensitive URL/log/cookie exposure, and logout cleanup. Assess native bridge effects under the app's permissions.
5. Preserve the controlled URL/content, navigation chain, bridge invocation, and resulting local/API effect. DevTools console execution alone demonstrates tester capability, not a remotely reachable injection.

Static candidates: [WebView, IPC, and Dependency Checks](../static-testing/webview-ipc-and-dependencies.md). References: [App Link verification](https://developer.android.com/training/app-links/verify-android-applinks), [WebView debugging](https://developer.chrome.com/docs/devtools/remote-debugging/webviews/).

### Drozer Setup

Install a compatible host Drozer console and agent APK, open the agent, and enable its embedded server on the lab device before forwarding its port. Confirm the agent's configured port; `31415` is the usual default:

```sh
adb forward tcp:31415 tcp:31415
drozer console connect
```

Run the following commands **inside Drozer**. Check module help; availability varies by release.

### Packages and Activities

```
run app.package.attacksurface <package-name>
run app.package.debuggable
run app.package.manifest <package-name>
run app.activity.info -a <package-name>
run app.activity.start --component <package-name> <activity-name>
run app.activity.start --component <package-name> <activity-name> --data-uri <authorized-test-uri>
run app.activity.start --action android.intent.action.VIEW --data-uri <authorized-test-uri>
```

### Content Providers

```
run app.provider.info -a <package-name>
run app.provider.finduri <package-name>
run scanner.provider.finduris -a <package-name>
run app.provider.columns <content-uri>
run app.provider.read <content-uri>
run app.provider.query <content-uri>
run app.provider.insert <content-uri> --string <column> <test-value>
run app.provider.update <content-uri> --selection "<column>=?" --selection-args <test-value> --string <column> <replacement-value>
run app.provider.delete <content-uri> --selection "<column>=?" --selection-args <test-value>
run scanner.provider.injection -a <package-name>
run scanner.provider.sqltables -a <package-name>
```

### Services and Broadcasts

```
run app.service.info -a <package-name>
run app.service.send <package-name> <service-name> --msg 2354 9234 1 --extra string <parameter> <test-value> --bundle-as-obj
run app.broadcast.info -a <package-name>
run app.broadcast.send --action <intent-name> --extra string <parameter> <test-value>
```

* [Drozer](https://github.com/WithSecureLabs/drozer): interactive assessment, not just an automatic scanner.
* `app.package.debuggable` lists debuggable packages.
* `app.provider.columns` / `app.provider.read`: source-era examples; may require specific releases/extensions.
* Repeat `--string` / `--extra` for additional fields/parameters.
* Insert/update/delete mutate data: use disposable test records only.
* Verify local authorization and, for claimed API impact, server authorization; intent filters/prior screens are not access controls.
* Stop the agent server and remove the test forward with `adb forward --remove tcp:31415` when finished.
