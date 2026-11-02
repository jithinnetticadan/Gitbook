# Advanced IPC and Content Providers

## Scope and Entry Criteria

* **Basic commands:** [Component Testing](component-testing.md) for Intent delivery, Messenger, provider reads/CRUD/scanners.
* **Here:** forwarding, results, delegated authority, Binder identity, provider query/path/grant boundaries.
* **Start with:** reachable operation, authorized baseline, observed protocol/URI, disposable records.
* **Client:** compatible companion app when CLI cannot express the interaction.
* **Track:** confirmed / rejected under tested conditions / blocked / untested.

## Intent, Result, and Binder Boundaries

* **Companion Activity, Kotlin:** send a nested explicit Intent using the forwarding component and extra name found in the target code. Place this in the companion Activity's `onCreate` after `super.onCreate(...)`.
	* ```kotlin
		val destination = android.content.Intent().setComponent(
				android.content.ComponentName("<target-package>", "<destination-activity>"))
		val forwarded = android.content.Intent().setComponent(
				android.content.ComponentName("<target-package>", "<forwarding-activity>"))
				.putExtra("<observed-nested-intent-extra>", destination)
		startActivity(forwarded)
		```
* **Host terminal, existing companion project:** build/install, then start its exported test Activity. Compare direct access using the [activity launch templates](component-testing.md#test-direct-access-and-inputs).
	* ```bash
		./gradlew installDebug
		adb shell am start -n '<companion-package>/<test-activity>'
		```
* **Activity results, AndroidX companion Activity property:** register before the Activity is started; launch the observed flow from `onCreate` or a test button.
	* ```kotlin
		private val resultProbe = registerForActivityResult(
				androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult()
		) { result ->
				android.util.Log.i("IPCProbe", "code=${result.resultCode}; uri=${result.data?.data}; keys=${result.data?.extras?.keySet()}")
		}
		```
* **Invoke from the Activity:**
	* ```kotlin
		resultProbe.launch(android.content.Intent().setComponent(
				android.content.ComponentName("<target-package>", "<result-activity>")))
		```
* **Bound interfaces:** use the target's generated AIDL/client interface or the [Messenger command variants](component-testing.md#test-a-bound-service); ADB cannot encode arbitrary Binder transactions.

<table><thead><tr><th width="172">Surface</th><th width="274">Test</th><th>Confirm</th></tr></thead><tbody><tr><td>Intent redirection</td><td>Nested Intent/<code>intent:</code> through exported forwarder; vary destination/action/data/grants</td><td>Protected operation reached using intermediary authority</td></tr><tr><td>Activity results</td><td>Companion launches for result; logged-out/cancel paths</td><td>Sensitive extras/grants returned before authorization</td></tr><tr><td>Mutable PendingIntent</td><td>Obtain shared token; fill unspecified fields, especially empty/implicit base Intent</td><td>Unintended operation as creator; mutability alone is not a flaw</td></tr><tr><td>PendingIntent replay / reuse</td><td>Repeat owned token after use, logout, privilege change</td><td>Unauthorized repeat action; missing <code>FLAG_ONE_SHOT</code> alone is not a flaw</td></tr><tr><td>Bound service / AIDL / Messenger</td><td>Known methods, owned records, callbacks, returned Binder handles</td><td>Per-method caller/role/object checks; binding alone is insufficient</td></tr><tr><td>Binder identity handling</td><td>Checks, <code>clearCallingIdentity</code>, async handoff, restoration</td><td>Authorization uses intended external caller, not substituted service identity</td></tr><tr><td>Implicit / sticky / ordered broadcasts</td><td>Recipients, permissions/package, results, registration flags</td><td>Unintended reception/injection under actual platform restrictions</td></tr><tr><td>Task transitions</td><td>Launcher, recents, reparenting, <code>singleTask</code></td><td>Unintended task/UI transition; assess platform advisories separately</td></tr></tbody></table>

* **Malformed inputs:** missing extras, wrong types, short invalid URIs; agree size/attempt limits.
* **No flooding:** reproduce bounded failures; a crash alone is not code execution.

## Provider Operation Matrix

* **Companion Activity, Kotlin:** query one known item under the companion UID; inspect file metadata and the returned stream independently.
	* ```kotlin
		val uri = android.net.Uri.parse("<owned-item-content-uri>")
		contentResolver.query(uri, arrayOf("<known-column>"), null, null, null)?.use { cursor ->
				android.util.Log.i("IPCProbe", "rows=${cursor.count}; columns=${cursor.columnNames.joinToString()}")
		}
		```
* **Granted file URI, Kotlin:** requires a file-serving URI rather than a database route.
	* ```kotlin
		val fileUri = android.net.Uri.parse("<granted-test-file-uri>")
		contentResolver.openInputStream(fileUri)?.use { stream ->
				val marker = ByteArray(64)
				android.util.Log.i("IPCProbe", "readBytes=${stream.read(marker)}")
		}
		```
* Build and invoke through the companion commands above; compare access before the grant, after sharing, and after revocation/logout. Basic route/CRUD variants remain in [Component Testing](component-testing.md#content-providers).

* Map each authority's documented/code-discovered URI routes, operations, permissions, accounts, and data owners.
* Compare an unauthorized caller with an authorized control.

<table><thead><tr><th width="182">Surface</th><th>Test</th><th>Confirm / Caveat</th></tr></thead><tbody><tr><td><code>query</code>, <code>update</code>, <code>delete</code></td><td>Selection, bound arguments, permitted rows</td><td>Parameters do not protect raw SQL/identifiers; disposable mutations only</td></tr><tr><td>Projection / sorting / grouping</td><td>Columns, expressions, order/limit</td><td>Forbidden test column/route accessible; avoid unnecessary dumps</td></tr><tr><td><code>openFile</code> / typed assets</td><td>Decoding, canonical paths, modes, symlinks/races</td><td>Harmless file stays inside root; prefix checks respect path boundaries</td></tr><tr><td>FileProvider</td><td>Roots, URI, read/write/prefix/persistable grants</td><td>Actual grant scope/lifetime; <code>grantUriPermissions=true</code> is not blanket access</td></tr><tr><td>Route variants / undocumented paths</td><td>Matcher, encoded segments, trailing separators, alternate operations</td><td>Consistent authorization after normalization; establish valid routes first</td></tr><tr><td>Family apps / shared UID</td><td>Signing/install prerequisites, permissions, caller UID</td><td>Demonstrate access; one compromised app does not imply universal access</td></tr><tr><td><code>notifyChange</code> / ContentObserver</td><td>URI contents, permissions, registration/delivery</td><td>Unauthorized observer receives sensitive data; not an unrestricted broadcast</td></tr><tr><td>Malformed requests</td><td>Bounded invalid selection, URI, offsets, types</td><td>Rejection/crash and recovery; no repeated DoS</td></tr></tbody></table>

## Dirty Stream: Untrusted Provider Metadata

* **Trigger a discovered sharing flow, ADB:** use a URI supplied by the test provider; MIME type and target package must match the consumer.
	* ```bash
		adb shell am start -a android.intent.action.SEND -t '<observed-mime-type>' --eu android.intent.extra.STREAM '<test-provider-content-uri>' --grant-read-uri-permission -p '<consumer-package>'
		```
* The companion provider controls `OpenableColumns.DISPLAY_NAME` and `openFile()` data; vary its display-name metadata while serving the same harmless marker file. The ADB command triggers the consumer but does not implement that provider.

1. **Find consumer:** reachable import/share/picker; reads display name, `_data`, size, MIME, or URI segment.
2. **Trace destination:** remote metadata used as a local path versus safe generated name.
3. **Test:** companion provider + harmless marker + controlled metadata; agreed disposable destination only.
4. **Capture:** URI/metadata, resolved path, write result, user interaction; prove unintended write separately from execution/token theft.
5. **Verify fix:** safe names, canonical containment, overwrite/race resistance.

* **Dirty Stream is not CVE-2024-0044:** that CVE concerns platform `run-as`/installer metadata, with different prerequisites and patches.
* Reference: [Microsoft Dirty Stream research](https://www.microsoft.com/en-us/security/blog/2024/05/01/dirty-stream-attack-discovering-and-mitigating-a-common-vulnerability-pattern-in-android-apps/).
* Reference: [Android untrusted provider filenames](https://developer.android.com/privacy-and-security/risks/untrustworthy-contentprovider-provided-filename).
* Reference: [Android intent redirection](https://developer.android.com/privacy-and-security/risks/intent-redirection).
