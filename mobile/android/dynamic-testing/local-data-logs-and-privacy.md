# Local Data, Logs, and Privacy

* Inspect preferences, SQLite, internal/external files, caches, and backups.
* Use Android Studio Device File Explorer or Objection `env` for accessible paths.
* Inspect test copies with [DB Browser for SQLite](https://sqlitebrowser.org/) or the CLI:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">sqlite3 &#x3C;database-copy.db>
    .tables
    SELECT * FROM &#x3C;test_table> LIMIT 10;
    </code></pre>

- [ ] `.tables` is a SQLite CLI command, not SQL.
- [ ] Use approved test keyboards/clipboard observers; OS restrictions apply.
- [ ] Check the following storage and privacy surfaces:
- [ ] Sensitive logs, clipboard (`android clipboard monitor`), keyboard data, screenshots/`FLAG_SECURE`.
- [ ] Backup exposure using an OS-supported workflow.
- [ ] Local role/state tampering; verify server authorization.
- [ ] SQL injection using non-destructive test records.
- [ ] Biometrics: success/failure callbacks and exception handling; verify key/server protections independently.
- [ ] Biometric scripts: [Keystore Audit](https://github.com/FSecureLABS/android-keystore-audit/tree/master/frida-scripts).
- [ ] Targeted examples: [callback bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass.js), [exception bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass-via-exception-handling.js).
- [ ] UI bypass does not prove hardware-key/server bypass; validate the operation with the [biometric and auth-bound Keystore workflow](authentication-and-cryptography.md#biometrics-and-auth-bound-keystore).

## Logs

* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb logcat -c
  adb logcat | grep '&#x3C;search-term>'
  adb shell pidof &#x3C;package-name>
  adb logcat --pid=&#x3C;pid-from-previous-command>
  </code></pre>
* Refresh PID after app restart; avoid brittle `ps | awk | grep` filters.
* Windows: use `findstr` or Android Studio Logcat.

## Follow Sensitive Data Through Its Lifecycle

* Track each token/identifier through creation, network, memory, storage, logs, backup, clipboard, notifications, keyboard, and screens.

<table><thead><tr><th width="124">Transition</th><th>Inspect</th><th>Confirm</th></tr></thead><tbody><tr><td>Before / after login</td><td>Preferences, databases, files, caches, WebView cookies</td><td>Which values appear, who can read them, and what they authorize.</td></tr><tr><td>Background / resume</td><td>Recent-task snapshot, notifications, clipboard, background sync</td><td>Sensitive data is not exposed outside the intended session/display context.</td></tr><tr><td>Process restart / reboot</td><td>Persisted files, device-/credential-protected storage</td><td>What survives, when it becomes available, and whether access requires device/app authentication.</td></tr><tr><td>Logout / token expiry</td><td>Files, cookies, memory references, queued jobs</td><td>Local cleanup and server revocation are separate; test retained credentials according to <a href="authentication-and-cryptography.md#authentication-and-session-matrix">session policy</a>.</td></tr><tr><td>Account A to B</td><td>Cache keys, database rows, cookies, pending work</td><td>B cannot access A's data or inherit A's session.</td></tr><tr><td>Backup / restore</td><td>Included paths, restored secrets/state, key availability</td><td>Restored data does not unexpectedly restore authorization or expose another user's data.</td></tr></tbody></table>

* Record access prerequisites: ordinary app, authorized ADB, debuggable `run-as`, root, physical access, or approved backup account.
* App-level plaintext may coexist with Android file-based encryption; assess device state, sandbox access, and app protection separately.
* For memory remnants, establish realistic access and lifetime; a string match alone is insufficient.

## Acquire Consistent Storage Evidence

1. Resolve the correct user/profile and paths using `env`, package details, or Device File Explorer. `/data/data` is commonly an alias for user 0; do not assume that user for every installation.
2. Prefer an app-supported SQLite snapshot/backup or quiesce the app before copying. A live database copied without its matching `-wal` and `-shm` files can be incomplete/inconsistent.
3. Use Device File Explorer, `adb pull` with appropriate device access, or a binary-safe export. Standard `adbd` cannot read private app data merely because `su` is installed. `run-as` generally requires a debuggable app; its failure does not prove all storage is protected.

* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb root
  adb shell am force-stop &#x3C;package-name>
  adb pull /data/user/0/&#x3C;package-name>/databases ./test-databases
  adb pull /data/user/0/&#x3C;package-name>/shared_prefs ./test-shared-prefs
  </code></pre>
* Copy the relevant database directory with its WAL/SHM sidecars intact.
* For production images using `su`, use a controlled root-assisted export.

## Screenshots, Clipboard, and Input Surfaces

* Test sensitive screens unmodified before disabling `FLAG_SECURE`.
* Check ordinary screenshots, recent-task previews, and permitted screen capture; compare instrumented runs separately.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">adb shell screencap -p /sdcard/lab-screen.png
  adb pull /sdcard/lab-screen.png .
  </code></pre>
* Check actual window flags and confirm the intended screen rendered.
* Clipboard artifacts: system-managed paths such as `/data/system_ce/<user-id>/`; locations/access vary.

## Backup and Restore Validation

* `allowBackup` and backup rules identify candidates.
* Record Android/target SDK/OEM, transport, account access, device unlock/consent, and actual backup mechanism.

<table><thead><tr><th width="161">Mechanism</th><th>Validation</th></tr></thead><tbody><tr><td>Auto Backup / cloud</td><td>Inspect applicable <code>fullBackupContent</code> or <code>dataExtractionRules</code>, inclusion/exclusion rules, transport/encryption, and a supported test backup/restore.</td></tr><tr><td>Device-to-device transfer</td><td>Test separately from cloud backup; supported rules and OEM behavior can differ.</td></tr><tr><td>Legacy ADB backup</td><td>Check <code>adb help</code>, OS support, app eligibility, user confirmation, and whether actual data was captured. An empty/header-only archive is not successful extraction.</td></tr><tr><td>App export / custom backup</td><td>Test export access, format/encryption, secrets included, import validation, and account binding.</td></tr></tbody></table>

* Inspect compatible `.ab` archives with [Android Backup Extractor](https://github.com/nelenkov/android-backup-extractor).
* **Extractor dependencies:** Java and the legitimate password for encrypted archives; decryption is not password-free.
* Verify restored data, authentication requirements, and credential usability.
* Non-exportable Keystore keys may not transfer.
* Reference: [Android backup behavior and rules](https://developer.android.com/identity/data/autobackup).
* Continue with [Platform and Version-Specific Tests](platform-and-version-specific-tests.md) for permission revocation, SMS/autofill, notifications, MediaProjection, special-access services, and cross-profile behavior.
