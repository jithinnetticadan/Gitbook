# Local Data, Logs, and Privacy

{% hint style="info" %}
* Use an authorized test device and test accounts; replace command placeholders before use.
* Preserve originals, protect dumps, and restore the lab afterward.
{% endhint %}

{% hint style="warning" %}
* **Prerequisite:** complete [Mandatory Preflight](preflight-and-frida-setup.md#mandatory-preflight).
* Identify candidates using [Local Data and Client Logic](../static-testing/local-data-and-client-logic.md).
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

* `.tables` is a SQLite CLI command, not SQL.
* Use approved test keyboards/clipboard observers; OS restrictions apply.

* Check the following storage and privacy surfaces:

* [ ] Sensitive logs, clipboard (`android clipboard monitor`), keyboard data, screenshots/`FLAG_SECURE`.
* [ ] Backup exposure using an OS-supported workflow.
* [ ] Local role/state tampering; verify server authorization.
* [ ] SQL injection using non-destructive test records.
* [ ] Biometrics: success/failure callbacks and exception handling; verify key/server protections independently.

* Biometric scripts: [Keystore Audit](https://github.com/FSecureLABS/android-keystore-audit/tree/master/frida-scripts).
* Targeted examples: [callback bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass.js), [exception bypass](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass-via-exception-handling.js).
* UI bypass does not prove hardware-key/server bypass; validate the operation with the [biometric and auth-bound Keystore workflow](authentication-and-cryptography.md#biometrics-and-auth-bound-keystore).
* **Legacy command:** `adb backup -apk -nosystem <package-name>`; deprecated/unavailable on current Android and may not extract all data.

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

* Save relevant baseline logs **before** `adb logcat -c`; clearing logs destroys existing evidence.
* Record capture scope; a PID filter may miss other app processes or OS messages.

## Follow Sensitive Data Through Its Lifecycle

* Use distinguishable synthetic test records.
* Track each token/identifier through creation, network, memory, storage, logs, backup, clipboard, notifications, keyboard, and screens.

| Transition               | Inspect                                                         | Confirm                                                                                                                                                                          |
| ------------------------ | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Before / after login     | Preferences, databases, files, caches, WebView cookies          | Which values appear, who can read them, and what they authorize.                                                                                                                 |
| Background / resume      | Recent-task snapshot, notifications, clipboard, background sync | Sensitive data is not exposed outside the intended session/display context.                                                                                                      |
| Process restart / reboot | Persisted files, device-/credential-protected storage           | What survives, when it becomes available, and whether access requires device/app authentication.                                                                                 |
| Logout / token expiry    | Files, cookies, memory references, queued jobs                  | Local cleanup and server revocation are separate; test retained credentials according to [session policy](authentication-and-cryptography.md#authentication-and-session-matrix). |
| Account A to B           | Cache keys, database rows, cookies, pending work                | B cannot access A's data or inherit A's session.                                                                                                                                 |
| Backup / restore         | Included paths, restored secrets/state, key availability        | Restored data does not unexpectedly restore authorization or expose another user's data.                                                                                         |

* Record access prerequisites: ordinary app, authorized ADB, debuggable `run-as`, root, physical access, or approved backup account.
* Root-readable plaintext is not automatically cross-app exposure.
* App-level plaintext may coexist with Android file-based encryption; assess device state, sandbox access, and app protection separately.
* For memory remnants, establish realistic access and lifetime; a string match alone is insufficient.

## Acquire Consistent Storage Evidence

1. Resolve the correct user/profile and paths using `env`, package details, or Device File Explorer. `/data/data` is commonly an alias for user 0; do not assume that user for every installation.
2. Prefer an app-supported SQLite snapshot/backup or quiesce the app before copying. A live database copied without its matching `-wal` and `-shm` files can be incomplete/inconsistent.
3. Use Device File Explorer, `adb pull` with appropriate device access, or a binary-safe export. Standard `adbd` cannot read private app data merely because `su` is installed. `run-as` generally requires a debuggable app; its failure does not prove all storage is protected.
4. Hash acquired artifacts, retain a protected original, and inspect a separate working copy with SQLite. Record whether stopping the app changed the state you intended to measure.

* **Example prerequisites:** root-capable **adbd lab image**, user 0, and preserved live evidence.

```sh
adb root
adb shell am force-stop <package-name>
adb pull /data/user/0/<package-name>/databases ./test-databases
adb pull /data/user/0/<package-name>/shared_prefs ./test-shared-prefs
```

* Copy the relevant database directory with its WAL/SHM sidecars intact.
* For production images using `su`, use a controlled root-assisted export; remove staging copies afterward.
* **Binary safety:** avoid text pipelines and older PowerShell redirection; corrupted bytes can invalidate evidence.
* External/scoped-storage acquisition requires appropriate permissions and test-user consent.

## Screenshots, Clipboard, and Input Surfaces

* Test sensitive screens unmodified before disabling `FLAG_SECURE`.
* Check ordinary screenshots, recent-task previews, and permitted screen capture; compare instrumented runs separately.

```sh
adb shell screencap -p /sdcard/lab-screen.png
adb pull /sdcard/lab-screen.png .
```

* Protect the test image and remove it afterward.
* A black image is inconclusive: secure surfaces, capture restrictions, app state, and capture failures may look similar.
* Check actual window flags and confirm the intended screen rendered.
* Use approved companion tools for clipboard retention/preview, keyboard suggestions/autofill, notifications, and overlays.
* **Access dependencies:** Android version, foreground state, and permissions.
* Prove tapjacking with an actual obscured-input action under permitted overlay access; a missing flag alone is insufficient.

## Backup and Restore Validation

* `allowBackup` and backup rules identify candidates; they do not guarantee extraction.
* Record Android/target SDK/OEM, transport, account access, device unlock/consent, and actual backup mechanism.

| Mechanism                  | Validation                                                                                                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Auto Backup / cloud        | Inspect applicable `fullBackupContent` or `dataExtractionRules`, inclusion/exclusion rules, transport/encryption, and a supported test backup/restore.             |
| Device-to-device transfer  | Test separately from cloud backup; supported rules and OEM behavior can differ.                                                                                    |
| Legacy ADB backup          | Check `adb help`, OS support, app eligibility, user confirmation, and whether actual data was captured. An empty/header-only archive is not successful extraction. |
| App export / custom backup | Test export access, format/encryption, secrets included, import validation, and account binding.                                                                   |

* Use the legacy backup command only where supported.
* Inspect compatible `.ab` archives with [Android Backup Extractor](https://github.com/nelenkov/android-backup-extractor).
* **Extractor dependencies:** Java and the legitimate password for encrypted archives; decryption is not password-free.
* Locate a synthetic marker in the backup; restore only to a disposable authorized environment.
* Verify restored data, authentication requirements, and credential usability.
* Non-exportable Keystore keys may not transfer; copied ciphertext alone does not establish readable disclosure.
* Root filesystem copies do not prove those files are included in platform backups.
* Record read/restore results and clean up test copies.
* Reference: [Android backup behavior and rules](https://developer.android.com/identity/data/autobackup).
* Continue with [Platform and Version-Specific Tests](platform-and-version-specific-tests.md) for permission revocation, SMS/autofill, notifications, MediaProjection, special-access services, and cross-profile behavior.
