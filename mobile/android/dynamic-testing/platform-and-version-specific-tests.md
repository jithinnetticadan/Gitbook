# Platform and Version-Specific Tests

## Record Applicability First

* **OS/API and patch/build identity:** run these before selecting the applicable version-specific test.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb shell getprop ro.build.version.release
  adb shell getprop ro.build.version.sdk
  adb shell getprop ro.build.version.security_patch
  adb shell getprop ro.build.fingerprint
  </code></pre>
* Record OEM/model, GPU/driver, WebView/browser version, bootloader/root state, target SDK, user/profile, and special-access grants.
* Check the current advisory and vendor-shipped fix/backport; Android version or a spoofed property alone is insufficient evidence.

## Permissions and User-Granted Capabilities

* **ADB:** inspect the actual package permissions, then vary a declared runtime permission such as camera access.
  * ```bash
    adb shell pm revoke '<package-name>' android.permission.CAMERA
    adb shell pm grant '<package-name>' android.permission.CAMERA
    adb shell cmd appops get '<package-name>'
    adb shell pm list users
    adb shell dumpsys device_policy
    adb shell dumpsys media_projection
    ```
* Package/target-SDK details: [installed package inventory](component-testing.md#adb-probes-and-caller-identity). Reopen the relevant feature after each grant/revoke and check collection, UI fallback, and background behavior.
* **Open user-controlled access settings:** choose the test service/provider in the system UI.
  * ```bash
    adb shell am start -a android.settings.ACCESSIBILITY_SETTINGS
    adb shell am start -a android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS
    adb shell am start -a android.settings.MANAGE_OVERLAY_PERMISSION -d 'package:<package-name>'
    adb shell settings get secure enabled_accessibility_services
    adb shell settings get secure enabled_notification_listeners
    ```

<table><thead><tr><th width="159">Surface</th><th>Controlled Test</th><th>Boundary / Limitation</th></tr></thead><tbody><tr><td>Runtime permissions</td><td>Deny, revoke, select approximate location, or use one-time grants where supported</td><td>Verify graceful failure and least privilege; compare declared purpose, actual collection, and disclosures.</td></tr><tr><td>Accessibility service</td><td>Enable only an approved test service with explicit user consent; inspect events/actions exposed by sensitive flows</td><td>The service's binding permission is not an ordinary silent grant to any app. Record what the user enabled and what the OS permits.</td></tr><tr><td>Notification listener</td><td>Check synthetic OTP/message previews under actual consent, device-lock, and OS restrictions</td><td>Do not assume every listener receives every sensitive notification on every Android version.</td></tr><tr><td>Autofill / keyboard</td><td>Use an approved test provider/IME; inspect field classification, origin/account association, and sensitive values</td><td>Password autofill is legitimate functionality. A user-selected provider seeing intended data is not automatically an app flaw.</td></tr><tr><td>SMS Retriever / OTP</td><td>Verify app hash/recipient flow, receiver protection, challenge/account binding, expiry and reuse</td><td>Retriever does not grant arbitrary SMS inbox access. Distinguish SMS permission, user-consent APIs, and backend OTP validation.</td></tr><tr><td>Overlay / obscured touches</td><td>Use a harmless synthetic confirmation and approved overlay app</td><td>Record required special access; distinguish overlay tapjacking from animation/task-based attacks.</td></tr><tr><td>MediaProjection / recents</td><td>With explicit capture consent, test screen/region selection, background transitions, cancellation and secure screens</td><td>User-granted capture is not itself a bypass; identify unintended data capture or violated protection. OS versions differ in consent/session rules.</td></tr><tr><td>Foreground work / standby</td><td>Inspect service type/purpose, notification, permission, collection after backgrounding or logout, and battery exemptions</td><td>Persistent work can be legitimate; correlate collection with consent and user/session state.</td></tr><tr><td>All-files / scoped storage</td><td>Grant only approved permissions and inspect actual accessible paths/MediaStore/URI grants</td><td><code>MANAGE_EXTERNAL_STORAGE</code> needs justification; it does not automatically expose all private app data.</td></tr><tr><td>VPN service</td><td>Observe an approved VPN's routing and compare TLS-protected data visibility</td><td>VPN consent permits routing, not automatic TLS decryption or bypass of app authentication.</td></tr><tr><td>Device admin / owner</td><td>Review configured policies, enrollment and app identity</td><td>Do not trigger lock/wipe or unenroll a real device. Device/profile-owner authority is distinct from legacy admin and ordinary app privileges.</td></tr><tr><td>Work/personal profiles</td><td>Test approved cross-profile links, file grants, clipboard, and chooser behavior with synthetic data</td><td>Record policies and both profiles' identities; manifest filters alone do not override enterprise policy.</td></tr><tr><td>USB / MIDI</td><td>Exercise known handlers using approved hardware and harmless inputs</td><td>Record physical access, permission prompts, device identity, and parser behavior.</td></tr><tr><td>Bluetooth / BLE / HID</td><td>Check scoped pairing, authenticated operations, application authorization, and test-device inputs</td><td>A Bluetooth-stack CVE is not an app flaw by association; radio tests must not affect nearby devices.</td></tr><tr><td>NFC</td><td>Send a controlled tag/URI to the app's declared dispatch path</td><td>Trace proximity-triggered data into links/intents and validate destination/input handling.</td></tr><tr><td>Wireless debugging</td><td>Review pairing/authentication, trusted hosts, and exposed listeners</td><td>Knowing a port is not authentication. Distinguish modern paired TLS debugging from legacy exposed ADB; do not brute-force pairing codes.</td></tr></tbody></table>

* Use [authentication and cryptography](authentication-and-cryptography.md) for biometrics/passkeys.

## Companion Recipes for Privacy and Obscured Input

### Notification Visibility

* **Companion service, Kotlin:** add this class to a separate Android test app, replace `REPLACE_TARGET_PACKAGE` with the target package, and register it in the companion manifest below. The listener observes target-app notifications; it does not create one.
  * ```kotlin
    package com.example.ipcprobe

    class ProbeNotifications : android.service.notification.NotificationListenerService() {
        override fun onNotificationPosted(item: android.service.notification.StatusBarNotification) {
            if (item.packageName != "REPLACE_TARGET_PACKAGE") return
            val extras = item.notification.extras
            val text = listOf("android.title", "android.text", "android.bigText")
                .joinToString(" ") { extras.getCharSequence(it)?.toString() ?: "" }
            android.util.Log.i("PrivacyProbe", "markerVisible=${text.contains("notification-probe")}")
        }
    }
    ```
* **Inside the companion manifest's application:** build/install using the [companion workflow](advanced-ipc-and-providers.md#intent-result-and-binder-boundaries), enable this service through the notification-listener settings command above, and filter Logcat for `PrivacyProbe`.
  * ```xml
    <service xmlns:android="http://schemas.android.com/apk/res/android"
        android:name="com.example.ipcprobe.ProbeNotifications"
        android:exported="true"
        android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE">
      <intent-filter>
        <action android:name="android.service.notification.NotificationListenerService" />
      </intent-filter>
    </service>
    ```
* **Trigger and observe:** install the companion, enable its `ProbeNotifications` service in notification-listener settings, and use the target's notification-producing feature with the marker `notification-probe`. Watch the host terminal while the event arrives:
  * ```text
    adb logcat -s PrivacyProbe:I
    ```
* `markerVisible=true` means the enabled listener received the marker; `false` means this event did not contain it in the inspected text fields. No log can mean no event or listener registration/delivery failure; verify the notification and selected listener before interpreting it.
* **Compare:** unlocked, locked, app logged out, notification replaced/removed. Separately inspect the lock-screen preview with private/public visibility settings.
* **Confirm:** content violates the intended notification/lock-screen privacy requirement. User-granted listener access to ordinary notification text is expected; modern OS redaction may suppress sensitive OTP content independently of the app.

### Obscured Touches

* **Companion manifest, outside application:** declare `android.permission.SYSTEM_ALERT_WINDOW`. Substitute the companion package into the overlay-settings command above and grant the companion permission; granting the target app permission does not enable the companion overlay.
* **Companion Activity, Android 8+ Kotlin:** position the translucent marker rectangle over the target's test confirmation button. Pixel coordinates/size must match the test device. A separate lifecycle handler should retain/remove the view as the companion's UI requires.
  * ```kotlin
    check(android.provider.Settings.canDrawOverlays(this))
    val windowManager = getSystemService(android.content.Context.WINDOW_SERVICE) as android.view.WindowManager
    val overlay = android.widget.TextView(this).apply {
        text = "overlay probe"
        setBackgroundColor(android.graphics.Color.YELLOW)
    }
    val parameters = android.view.WindowManager.LayoutParams(
        240, 100, android.view.WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
        android.view.WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
            android.view.WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
        android.graphics.PixelFormat.TRANSLUCENT
    ).apply {
        gravity = android.view.Gravity.TOP or android.view.Gravity.LEFT
        x = 100
        y = 500
        alpha = 0.5f
    }
    windowManager.addView(overlay, parameters)
    ```
* **Trigger:** build/install the companion, grant its overlay permission, and run the code from its Activity after the grant. Open the target's synthetic confirmation screen, align the overlay with its button, then tap the button and inspect the resulting operation.
* **Compare:** the same confirmation without overlay, with overlap, and with the overlay beside the button. Observe the actual operation and, where instrumented, `MotionEvent.FLAG_WINDOW_IS_OBSCURED` / `FLAG_WINDOW_IS_PARTIALLY_OBSCURED`.
* **Confirm:** a sensitive action accepts a delivered obscured touch contrary to the intended requirement. Android's untrusted-touch opacity rules or a hidden overlay can prevent delivery; a blocked tap alone does not establish that the app filters obscured events. This tests overlay input, not TapTrap/task-animation attacks.

### Autofill, SMS, and Capture Transitions

* **Companion accessibility service, separate Kotlin file:** replace the package filter with the target package. Enter `accessibility-probe` into the feature being tested; compare an ordinary field, a password/PIN field, a post-logout screen and the locked-device flow.
  * ```kotlin
    package com.example.ipcprobe

    class ProbeAccessibility : android.accessibilityservice.AccessibilityService() {
        override fun onAccessibilityEvent(event: android.view.accessibility.AccessibilityEvent) {
            if (event.packageName?.toString() != "REPLACE_TARGET_PACKAGE") return
            val eventMarker = event.text.joinToString(" ").contains("accessibility-probe")
            val treeMarker = rootInActiveWindow
                ?.findAccessibilityNodeInfosByText("accessibility-probe")?.isNotEmpty() == true
            android.util.Log.i("PrivacyProbe", "eventMarker=$eventMarker; treeMarker=$treeMarker; password=${event.isPassword}")
        }
        override fun onInterrupt() {}
    }
    ```
* **Inside application:**
  * ```xml
    <service xmlns:android="http://schemas.android.com/apk/res/android"
        android:name="com.example.ipcprobe.ProbeAccessibility"
        android:exported="true" android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
      <intent-filter><action android:name="android.accessibilityservice.AccessibilityService" /></intent-filter>
      <meta-data android:name="android.accessibilityservice" android:resource="@xml/probe_accessibility" />
    </service>
    ```
* **Companion resource `res/xml/probe_accessibility.xml`:** enable the service using the accessibility settings command already documented above.
  * ```xml
    <accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
        android:accessibilityEventTypes="typeViewTextChanged|typeWindowStateChanged|typeWindowContentChanged"
        android:accessibilityFeedbackType="feedbackGeneric"
        android:canRetrieveWindowContent="true"
        android:notificationTimeout="100" />
    ```
* **Trigger and observe:** build/install the companion with the service and resource above, enable its `ProbeAccessibility` service in Accessibility settings, then enter `accessibility-probe` into the target's test fields. Read `eventMarker`, `treeMarker` and `password` using `adb logcat -s PrivacyProbe:I` on the host. No output is inconclusive until the service is enabled and events are delivered.
* **Confirm:** clear sensitive marker text or an action appears where the app's required masking/authentication policy should prevent it. An explicitly enabled service seeing ordinary UI content is expected; report the actual sensitive field/state rather than accessibility support itself.
* **Companion keyboard, separate Kotlin file (API 26+):** observes field metadata and marker visibility; the button inserts only a test marker. It is not a full keyboard implementation.
  * ```kotlin
    package com.example.ipcprobe

    class ProbeKeyboard : android.inputmethodservice.InputMethodService() {
        override fun onStartInput(info: android.view.inputmethod.EditorInfo, restarting: Boolean) {
            super.onStartInput(info, restarting)
            if (info.packageName != "REPLACE_TARGET_PACKAGE") return
            val noLearning = info.imeOptions and android.view.inputmethod.EditorInfo.IME_FLAG_NO_PERSONALIZED_LEARNING != 0
            android.util.Log.i("PrivacyProbe", "inputType=${info.inputType}; noLearning=$noLearning")
        }
        override fun onCreateInputView(): android.view.View = android.widget.Button(this).apply {
            text = "Insert test marker"
            setOnClickListener {
                currentInputConnection?.commitText("keyboard-probe", 1)
                val visible = currentInputConnection?.getTextBeforeCursor(128, 0)?.contains("keyboard-probe")
                android.util.Log.i("PrivacyProbe", "markerVisible=$visible")
            }
        }
    }
    ```
* **Inside application:**
  * ```xml
    <service xmlns:android="http://schemas.android.com/apk/res/android"
        android:name="com.example.ipcprobe.ProbeKeyboard"
        android:exported="true" android:permission="android.permission.BIND_INPUT_METHOD">
      <intent-filter><action android:name="android.view.InputMethod" /></intent-filter>
      <meta-data android:name="android.view.im" android:resource="@xml/probe_keyboard" />
    </service>
    ```
* **Companion resource `res/xml/probe_keyboard.xml`:**
  * ```xml
    <input-method xmlns:android="http://schemas.android.com/apk/res/android"
        android:supportsSwitchingToNextInputMethod="true" />
    ```
* **Build/install:** use the existing [companion commands](advanced-ipc-and-providers.md#intent-result-and-binder-boundaries). **Activate keyboard (Linux / Windows, unchanged):**
  * ```text
    adb shell ime list -s
    adb shell ime enable com.example.ipcprobe/.ProbeKeyboard
    adb shell ime set com.example.ipcprobe/.ProbeKeyboard
    ```
* **Trigger and observe:** focus each target field and tap the companion keyboard's **Insert test marker** button. Read `inputType`, `noLearning` and `markerVisible` using `adb logcat -s PrivacyProbe:I` on the host; `markerVisible` refers only to the marker inserted by this test keyboard.
* Compare login/password/PIN/payment fields with an ordinary text field. Inspect the observed `inputType` variation and no-learning flag against the intended keyboard policy. The chosen IME receiving text the user types is normal; a plaintext/misclassified sensitive field or prohibited retained/suggested marker needs a concrete result. A missing no-learning flag alone does not demonstrate stored keyboard history.

* **Autofill:** save separate credentials for A and B in the selected test autofill provider. Open login, account switch and embedded-web login; compare the offered credential's package/domain and target field. A credential suggested/filled into a different untrusted origin or account boundary needs an actual fill/disclosure result, not just a label mismatch.
* **SMS/OTP:** request a challenge for A, then submit that code with B's challenge ID; reuse it after successful completion; repeat after expiry. For the app-side receiver use the real action/extras through [receiver probes](component-testing.md#test-unauthorized-sending). A filled textbox is not server-side OTP acceptance.
* **MediaProjection/recents:** open a marked sensitive screen, start the OS capture workflow, then background/lock/logout and revisit it. Compare live capture, recent-task preview and cancellation. Confirm which marked content is visible after the protection/session transition; keep device consent and app protection results distinct.

## Research and Legacy Vulnerability Triage

<table><thead><tr><th width="192">Research / Identifier</th><th>Applicability and Evidence</th></tr></thead><tbody><tr><td><a href="https://pixnapping.com/">Pixnapping, CVE-2025-48561</a></td><td>Rendering/pixel side-channel research, not generic GPU code execution. The researchers report particular Pixel/Samsung devices and Android 13–16 builds; their page was last updated October 2025 and discusses incomplete initial mitigation. Check newer vendor advisories and actual builds; do not extrapolate to every device or promise that an app flag fixes it.</td></tr><tr><td><a href="https://taptrap.click/">TapTrap</a></td><td>Animation-driven tapjacking differs from overlay permissions. The authors report Android 13–16 fixes in the December 2025 security update and separate browser fixes. Confirm the installed vendor/browser patch; use a harmless action if authorized testing is still applicable.</td></tr><tr><td><a href="https://rtx.meta.security/exploitation/2024/03/04/Android-run-as-forgery.html">CVE-2024-0044</a></td><td>Installer-metadata/newline injection affecting <code>run-as</code>, with ADB prerequisites in the original research. Check exact version/fix and later advisory updates. This is <strong>not Dirty Stream</strong>.</td></tr><tr><td><a href="https://rtx.meta.security/exploitation/2024/06/03/Android-Zygote-injection.html">CVE-2024-31317</a></td><td>Zygote command injection through privileged settings, not an ordinary unprivileged app's deserialization bug. Requires relevant settings-write authority; the disclosed fix is in the June 2024 bulletin. Device-specific platform testing needs explicit scope.</td></tr><tr><td>Janus, CVE-2017-13156</td><td>Verify affected OS/package verifier, patch level, and accepted signature path. A v1 signature or low app target SDK alone does not establish applicability.</td></tr><tr><td>StrandHogg / CVE-2020-0096</td><td>Distinguish manifest/task-affinity patterns from the historical platform task-hijacking vulnerability. Consult the <a href="https://source.android.com/docs/security/bulletin/2020-05-01">May 2020 Android bulletin</a> and actual task transitions; do not apply old device assumptions universally.</td></tr><tr><td>Mali/Adreno or Bluetooth advisories</td><td>Match exact hardware, driver/firmware and vendor fix; for example, a Mali CVE is not applicable merely because the app renders graphics. GPU.zip/Pixnapping side channels and GPU driver memory-corruption CVEs are different issues.</td></tr><tr><td>Dirty Stream</td><td>An app-level untrusted file-provider metadata pattern; use <a href="advanced-ipc-and-providers.md#dirty-stream-untrusted-provider-metadata">Advanced IPC and Content Providers</a>, not an OS <code>run-as</code> recipe.</td></tr><tr><td>SafetyNet Attestation</td><td>Google <a href="https://developer.android.com/privacy-and-security/safetynet/deprecation-timeline">fully shut it down in January 2025</a>. Assess migration and failure handling; do not describe it as a currently functional fallback.</td></tr></tbody></table>
