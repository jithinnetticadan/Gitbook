# Local Data, Logs, and Privacy

{% hint style="info" %}
Use an authorized test device and test accounts. Preserve originals; protect dumps and restore the lab afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Complete the [Mandatory Preflight](preflight-and-frida-setup.md#mandatory-preflight) first. Candidate storage and logic issues come from [Local Data and Client Logic](../static-testing/local-data-and-client-logic.md).
{% endhint %}

## Local Data, Logs, and Privacy Controls

* Inspect preferences, SQLite, internal/external files, caches, and backups.
* Use Android Studio Device File Explorer or Objection `env` for accessible paths.
* Inspect test copies with [DB Browser for SQLite](https://sqlitebrowser.org/) or the CLI:


```sh
sqlite3 <database-copy.db>
```

```sql
.tables
SELECT * FROM <test_table> LIMIT 10;
```

`.tables` is a SQLite CLI command, not SQL. Use approved test keyboards/clipboard observers; OS restrictions apply.

Check:

* [ ] Sensitive logs, clipboard (`android clipboard monitor`), keyboard data, screenshots/`FLAG_SECURE`.
* [ ] Backup exposure using an OS-supported workflow.
* [ ] Local role/state tampering; verify server authorization.
* [ ] SQL injection using non-destructive test records.
* [ ] Biometrics: success/failure callbacks and exception handling; verify key/server protections independently.

Biometric scripts: [Keystore Audit](https://github.com/FSecureLABS/android-keystore-audit/tree/master/frida-scripts), [callback bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass.js), [exception bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass-via-exception-handling.js). UI bypass does not prove hardware-key/server bypass. Follow the [biometric and auth-bound Keystore workflow](authentication-and-cryptography.md#biometrics-and-auth-bound-keystore) to validate the protected operation.

Legacy backup: `adb backup -apk -nosystem <package-name>`. Deprecated/unavailable on current Android; may not extract all data.

### Logs and Screenshots

```sh
adb logcat -c
adb logcat | grep '<search-term>'
adb shell pidof <package-name>
adb logcat --pid=<pid-from-previous-command>
```

* Refresh PID after app restart; avoid brittle `ps | awk | grep` filters.
* Windows: use `findstr` or Android Studio Logcat. Protect log evidence.
* Screenshot artifacts: system-managed paths such as `/data/system_ce/<user-id>/`; locations/access vary.

Save relevant baseline logs **before** `adb logcat -c`; clearing them destroys existing evidence. A filtered PID view can miss another app process or OS-generated messages, so record the capture scope.

## Follow Sensitive Data Through Its Lifecycle

Use distinguishable synthetic test records. Track each token/identifier from creation through network, memory, storage, logs, backup, clipboard, notifications, keyboard, and screen surfaces.

| Transition | Inspect | Confirm |
| --- | --- | --- |
| Before / after login | Preferences, databases, files, caches, WebView cookies | Which values appear, who can read them, and what they authorize. |
| Background / resume | Recent-task snapshot, notifications, clipboard, background sync | Sensitive data is not exposed outside the intended session/display context. |
| Process restart / reboot | Persisted files, device-/credential-protected storage | What survives, when it becomes available, and whether access requires device/app authentication. |
| Logout / token expiry | Files, cookies, memory references, queued jobs | Local cleanup and server revocation are separate; test retained credentials according to [session policy](authentication-and-cryptography.md#authentication-and-session-matrix). |
| Account A to B | Cache keys, database rows, cookies, pending work | B cannot access A's data or inherit A's session. |
| Backup / restore | Included paths, restored secrets/state, key availability | Restored data does not unexpectedly restore authorization or expose another user's data. |

Record the access capability needed: ordinary app, authorized ADB, debuggable `run-as`, root, physical access, or an approved backup account. Root-readable plaintext is not automatically cross-app exposure. App-level plaintext can coexist with Android file-based encryption; evaluate device state, sandbox access, and additional app protection separately. Memory remnants require a realistic access/lifetime analysis, not merely a string match.

## Acquire Consistent Storage Evidence

1. Resolve the correct user/profile and paths using `env`, package details, or Device File Explorer. `/data/data` is commonly an alias for user 0; do not assume that user for every installation.
2. Prefer an app-supported SQLite snapshot/backup or quiesce the app before copying. A live database copied without its matching `-wal` and `-shm` files can be incomplete/inconsistent.
3. Use Device File Explorer, `adb pull` with appropriate device access, or a binary-safe export. Standard `adbd` cannot read private app data merely because `su` is installed. `run-as` generally requires a debuggable app; its failure does not prove all storage is protected.
4. Hash acquired artifacts, retain a protected original, and inspect a separate working copy with SQLite. Record whether stopping the app changed the state you intended to measure.

Example for a **root-capable adbd lab image** and user 0, after preserving live evidence:

```sh
adb root
adb shell am force-stop <package-name>
adb pull /data/user/0/<package-name>/databases ./test-databases
adb pull /data/user/0/<package-name>/shared_prefs ./test-shared-prefs
```

Copy the whole relevant database directory so any WAL/SHM sidecars remain together. For production images using `su`, use a controlled root-assisted export instead; remove staging copies after acquisition. Do not send a binary database through text pipelines or older PowerShell redirection: byte corruption can invalidate evidence. Acquire external/scoped-storage files only with the appropriate permissions and test-user consent.

## Screenshots, Clipboard, and Input Surfaces

Test sensitive screens unmodified before disabling `FLAG_SECURE`. On the lab device, use ordinary screenshots, recent-task previews, and permitted screen capture, then compare any instrumented run separately:

```sh
adb shell screencap -p /sdcard/lab-screen.png
adb pull /sdcard/lab-screen.png .
```

Protect and remove the test image afterward. A black image alone is inconclusive: secure surfaces, capture restrictions, app state, and capture failures can look similar. Check the actual window flags and confirm the intended screen was rendered. Test clipboard retention/preview, keyboard suggestions/autofill, notifications, and overlays with approved companion tools; Android version, foreground state, and permissions affect access. For tapjacking, demonstrate a real obscured-input action under allowed overlay permissions rather than treating a missing flag as proof.

## Backup and Restore Validation

`allowBackup` and backup-rule files identify candidates, not guaranteed extraction. Record Android/target SDK/OEM, configured transport, account access, device unlock/consent, and the actual mechanism:

| Mechanism | Validation |
| --- | --- |
| Auto Backup / cloud | Inspect applicable `fullBackupContent` or `dataExtractionRules`, inclusion/exclusion rules, transport/encryption, and a supported test backup/restore. |
| Device-to-device transfer | Test separately from cloud backup; supported rules and OEM behavior can differ. |
| Legacy ADB backup | Check `adb help`, OS support, app eligibility, user confirmation, and whether actual data was captured. An empty/header-only archive is not successful extraction. |
| App export / custom backup | Test export access, format/encryption, secrets included, import validation, and account binding. |

Use the earlier legacy command only where supported. An existing compatible `.ab` archive can be inspected with [Android Backup Extractor](https://github.com/nelenkov/android-backup-extractor), which requires Java and the legitimate password for an encrypted archive; do not assume it decrypts without one.

Inventory a known synthetic marker in the backup, restore only to a disposable authorized environment, then verify its presence, authentication requirements, and any credential usability. Account for non-exportable Keystore keys that may not survive transfer; copying ciphertext alone does not establish readable disclosure. A root filesystem copy is not evidence that the platform backup mechanism includes those files. Record read/restore results and clean up test copies. Reference: [Android backup behavior and rules](https://developer.android.com/identity/data/autobackup).

For permission revocation, SMS/autofill, notifications, MediaProjection, special-access services, and cross-profile behavior, continue with [Platform and Version-Specific Tests](platform-and-version-specific-tests.md).

**Previous:** [Runtime Defenses and Integrity](runtime-defenses-and-integrity.md) | **Next:** [Platform and Version-Specific Tests](platform-and-version-specific-tests.md)
