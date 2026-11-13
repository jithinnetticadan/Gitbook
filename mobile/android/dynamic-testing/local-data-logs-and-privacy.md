# Data Storage and Privacy

* Inspect preferences, SQLite, internal/external files, caches, and backups.
* Use Android Studio Device File Explorer or the [Objection environment command](objection-and-runtime-instrumentation.md#classes-and-hooks) for accessible paths.
* Inspect test copies with [DB Browser for SQLite](https://sqlitebrowser.org/) or the CLI:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">sqlite3 &#x3C;database-copy.db>
    .tables
    SELECT * FROM &#x3C;test_table> LIMIT 10;
    </code></pre>

## Focused Test Flow

1. Choose one sensitive value or action and create distinct test markers for accounts A and B. Record the normal stored value, log output, screen state, and protected-operation result.
2. Trigger the real feature that creates or consumes the value. Inspect app-owned files/databases with [File and Database Inspection](#file-and-database-inspection); inspect logs, screenshots, clipboard and keyboard surfaces in the sections below.
3. Repeat after logout, account switch, background/resume, process restart, and the relevant lock/unlock or backup/restore transition. Record whether the marker remains and which caller/access context can read or use it.
4. For a local role/state value, establish the protected operation under account A, change only that app-owned value using the actual prefs/database field, restart or retrigger the feature, then repeat the same operation. Confirm a flaw only if a protected action/data result succeeds contrary to the server's authorization policy; a changed label or enabled button alone is not sufficient.

* Backup/restore: use [Backup and Restore Validation](#backup-and-restore-validation), then open the restored app and test the known marker and authentication state.
* Provider SQL injection: use the concrete [selection-argument and file-route tests](advanced-ipc-and-providers.md#provider-injection-and-file-traversal).
* Biometric callback/key checks: follow [Biometrics and Auth-Bound Keystore](authentication-and-cryptography.md#biometrics-and-auth-bound-keystore), then perform the protected decrypt/sign/action after each failed, canceled, or expired authentication case.
* Keyboard and obscured-touch checks: use the [companion keyboard](platform-and-version-specific-tests.md) and [obscured-touch steps](platform-and-version-specific-tests.md#obscured-touches); confirm actual sensitive text exposure or an accepted protected action, not merely a missing flag.

## Logs

{% tabs %}
{% tab title="Linux" %}
* ```bash
  adb logcat -c
  adb logcat | grep '<search-term>'
  adb shell pidof '<package-name>'
  adb logcat --pid='<pid-from-previous-command>'
  ```
{% endtab %}
{% tab title="Windows" %}
* ```powershell
  adb logcat -c
  adb logcat | Select-String -SimpleMatch '<search-term>'
  adb shell pidof '<package-name>'
  adb logcat --pid='<pid-from-previous-command>'
  ```
{% endtab %}
{% endtabs %}
* Refresh PID after app restart; avoid brittle `ps | awk | grep` filters.

## Follow Sensitive Data Through Its Lifecycle

* Track each token/identifier through creation, network, memory, storage, logs, backup, clipboard, notifications, keyboard, and screens.

<table><thead><tr><th width="124">Transition</th><th>Inspect</th><th>Confirm</th></tr></thead><tbody><tr><td>Before / after login</td><td>Preferences, databases, files, caches, WebView cookies</td><td>Which values appear, who can read them, and what they authorize.</td></tr><tr><td>Background / resume</td><td>Recent-task snapshot, notifications, clipboard, background sync</td><td>Sensitive data is not exposed outside the intended session/display context.</td></tr><tr><td>Process restart / reboot</td><td>Persisted files, device-/credential-protected storage</td><td>What survives, when it becomes available, and whether access requires device/app authentication.</td></tr><tr><td>Logout / token expiry</td><td>Files, cookies, memory references, queued jobs</td><td>Local cleanup and server revocation are separate; test retained credentials according to <a href="authentication-and-cryptography.md#authentication-and-session-matrix">session policy</a>.</td></tr><tr><td>Account A to B</td><td>Cache keys, database rows, cookies, pending work</td><td>B cannot access A's data or inherit A's session.</td></tr><tr><td>Backup / restore</td><td>Included paths, restored secrets/state, key availability</td><td>Restored data does not unexpectedly restore authorization or expose another user's data.</td></tr></tbody></table>

* Record access prerequisites: ordinary app, authorized ADB, debuggable `run-as`, root, physical access, or approved backup account.
* App-level plaintext may coexist with Android file-based encryption; assess device state, sandbox access, and app protection separately.
* For memory remnants, establish realistic access and lifetime; a string match alone is insufficient.

## File and Database Inspection

{% tabs %}
{% tab title="ADB run-as" %}
* **Debuggable app:** confirm `run-as` identity and inspect one file. These ADB shell commands are the same on Linux and Windows.
  * ```bash
    adb shell run-as '<package-name>' id
    adb shell run-as '<package-name>' ls -la
    adb shell run-as '<package-name>' cat 'shared_prefs/<preferences-file>.xml'
    ```
{% endtab %}

{% tab title="ADB root" %}
* **Root-capable adbd:** run on the host; the package path below is for Android user 0.
  * ```text
    adb root
    adb shell am force-stop '<package-name>'
    adb pull '/data/user/0/<package-name>/databases' ./test-databases
    adb pull '/data/user/0/<package-name>/shared_prefs' ./test-shared-prefs
    ```
* For production images using `su`, use a root-assisted export. Keep the matching database WAL/SHM sidecars for a consistent SQLite copy.
{% endtab %}

{% tab title="Objection" %}
* **Host terminal:** attach to the running app with a working Frida connection.
  * ```text
    frida-ps -Uai
    objection --name '<process-name>' start
    ```
* **Objection console:** locate app files and inspect/download the selected preferences or database.
  * ```text
    env
    filesystem cat <path-to-file>
    filesystem download <path-to-file>
    sqlite connect <database-file>
    ```
{% endtab %}

{% tab title="Grapefruit" %}
* **Host terminal:** start the installed interface with the device's Frida server running.
  * ```text
    frida-ps -Uai
    igf
    ```
* Select the app, then use its filesystem browser or SQLite inspector to inspect the actual preferences/database path and test marker. Access is in the instrumented app's context.
{% endtab %}

{% tab title="Android Studio" %}
* Open Device Explorer for the selected device, navigate to the app's data directory and inspect/export its preferences or databases. File access depends on the device and app configuration.
{% endtab %}
{% tab title="AndroidSpect" %}
* On the rooted device, open AndroidSpect and start its server. Select the target app in the browser dashboard; use **Files**, **SharedPreferences**, or **SQLite** to inspect the relevant path and marker. The app displays the dashboard address and password.
* **Emulator, host terminal:**
  * ```text
    adb forward tcp:8008 tcp:8008
    ```
* Open `https://localhost:8008/` and select the target. AndroidSpect reads through its root context.
{% endtab %}
{% tab title="Inspeckage" %}
* In a compatible Xposed environment, select the target app in Inspeckage and use its Shared Preferences, SQLite or filesystem views/hooks while triggering the relevant app action.
{% endtab %}
{% endtabs %}

* Export a debuggable app's private directory as a binary tar stream:

{% tabs %}
{% tab title="Linux" %}
* ```bash
  adb exec-out run-as '<package-name>' tar -cf - . > app-data.tar
  ```
{% endtab %}
{% tab title="Windows" %}
* **PowerShell 7.4+:** native output redirection preserves the binary stream.
  * ```powershell
    adb exec-out run-as '<package-name>' tar -cf - . > app-data.tar
    ```
{% endtab %}
{% endtabs %}

* Extract each app state into a separate host directory and compare the same paths; close/quiesce database writers before acquisition.

{% tabs %}
{% tab title="Linux" %}
* ```bash
  mkdir -p before
  tar -xf app-data.tar -C before
  diff -ru before after
  ```
{% endtab %}
{% tab title="Windows" %}
* ```powershell
  New-Item -ItemType Directory -Path './before' -Force | Out-Null
  tar.exe -xf app-data.tar -C './before'
  $beforeRoot = (Resolve-Path './before').Path
  $afterRoot = (Resolve-Path './after').Path
  $beforeFiles = Get-ChildItem $beforeRoot -Recurse -File | ForEach-Object { [pscustomobject]@{ Path = $_.FullName.Substring($beforeRoot.Length); Hash = (Get-FileHash -LiteralPath $_.FullName).Hash } }
  $afterFiles = Get-ChildItem $afterRoot -Recurse -File | ForEach-Object { [pscustomobject]@{ Path = $_.FullName.Substring($afterRoot.Length); Hash = (Get-FileHash -LiteralPath $_.FullName).Hash } }
  Compare-Object $beforeFiles $afterFiles -Property Path, Hash
  ```
{% endtab %}
{% endtabs %}

1. Resolve the correct user/profile and paths using `env`, package details, or Device File Explorer. `/data/data` is commonly an alias for user 0; do not assume that user for every installation.
2. Prefer an app-supported SQLite snapshot/backup or quiesce the app before copying. A live database copied without its matching `-wal` and `-shm` files can be incomplete/inconsistent.
3. Use Device File Explorer, `adb pull` with appropriate device access, or a binary-safe export. Standard `adbd` cannot read private app data merely because `su` is installed. `run-as` generally requires a debuggable app; its failure does not prove all storage is protected.

## Screenshots, Clipboard, and Input Surfaces

* Test sensitive screens unmodified before disabling `FLAG_SECURE`.
* Check ordinary screenshots, recent-task previews, and permitted screen capture; compare instrumented runs separately.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb shell screencap -p /sdcard/lab-screen.png
  adb pull /sdcard/lab-screen.png .
  </code></pre>
* Check actual window flags and confirm the intended screen rendered.
* Clipboard artifacts: system-managed paths such as `/data/system_ce/<user-id>/`; locations/access vary.

## Backup and Restore Validation

* **Device with an enabled backup transport:** select the actual restore-set token from `bmgr list sets`; commands depend on OS and transport availability.
  * ```bash
    adb shell bmgr enabled
    adb shell bmgr list transports
    adb shell bmgr backupnow '<package-name>'
    adb shell bmgr list sets
    adb shell bmgr restore '<restore-set-token>' '<package-name>'
    ```
* **Legacy ADB backup, only where supported:** inspect the resulting archive for a known marker before treating extraction as successful.
  * ```bash
    adb backup -f app-backup.ab -apk -nosystem '<package-name>'
    java -jar abe.jar unpack app-backup.ab app-backup.tar
    ```
* Encrypted archives require the password using the extractor's documented input method. Reopen the app and compare the restored login/storage state.

* `allowBackup` and backup rules identify candidates.
* Record Android/target SDK/OEM, transport, account access, device unlock/consent, and actual backup mechanism.

<table><thead><tr><th width="161">Mechanism</th><th>Validation</th></tr></thead><tbody><tr><td>Auto Backup / cloud</td><td>Inspect applicable <code>fullBackupContent</code> or <code>dataExtractionRules</code>, inclusion/exclusion rules, transport/encryption, and a supported test backup/restore.</td></tr><tr><td>Device-to-device transfer</td><td>Test separately from cloud backup; supported rules and OEM behavior can differ.</td></tr><tr><td>Legacy ADB backup</td><td>Check <code>adb help</code>, OS support, app eligibility, user confirmation, and whether actual data was captured. An empty/header-only archive is not successful extraction.</td></tr><tr><td>App export / custom backup</td><td>Test export access, format/encryption, secrets included, import validation, and account binding.</td></tr></tbody></table>

* Inspect compatible `.ab` archives with [Android Backup Extractor](https://github.com/nelenkov/android-backup-extractor).
* **Extractor dependencies:** Java and the legitimate password for encrypted archives; decryption is not password-free.
* Verify restored data, authentication requirements, and credential usability.
* Non-exportable Keystore keys may not transfer.
* Reference: [Android backup behavior and rules](https://developer.android.com/identity/data/autobackup).
* Continue with [Platform and Version-Specific Tests](platform-and-version-specific-tests.md) for permission revocation, SMS/autofill, notifications, MediaProjection, special-access services, and cross-profile behavior.
