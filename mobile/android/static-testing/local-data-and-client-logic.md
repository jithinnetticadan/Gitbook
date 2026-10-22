# Local Data and Client Logic

{% hint style="info" %}
Test only in-scope apps. Record package, version, source, device/API level, and original APK hash. Replace command placeholders before use.
{% endhint %}

## Local Data and Client-Side Logic

* Inspect shared preferences, SQLite, internal/external files, caches, and backups.
* Check protection of tokens, personal data, and business state; assess cross-app/backup access.
* Trace local roles/tokens/account state; verify independent server authorization.
* Review attacker-controlled SQL input and query construction.
* Flag logs, clipboard, screenshots, and keyboard behavior for [dynamic testing](../dynamic-testing/local-data-logs-and-privacy.md).

### Storage, Logging, and Screen-Protection Signals

```sh
grep -rnE 'getSharedPreferences\(|openFileOutput\(|MODE_WORLD_(READABLE|WRITEABLE)|getExternalFilesDir|getExternalStorage' <decompiled-directory>
grep -rniE 'Log\.(v|d|i|w|e)\(.*(token|password|passwd|pin|otp|ssn|auth|secret)' <decompiled-directory>
grep -rn 'FLAG_SECURE\|setFilterTouchesWhenObscured\|filterTouchesWhenObscured' <decompiled-directory>
grep -rL 'FLAG_SECURE' --include='*Activity*.java' <decompiled-directory>
```

* App-level plaintext and Android file-based encryption are different layers. Private preferences/files are normally UID-sandboxed, not world-readable. Assess actual access through a debuggable build, authorized root, backup, device state, or another demonstrated path before rating disclosure.
* `MODE_WORLD_*` is unsupported on modern Android; its presence still marks legacy insecure storage code.
* `run-as <package-name>` reads app files only for debuggable apps; it does not prove access on a release build.
* Logging: debug `Log.*` calls left in release builds expose data through Logcat, bug reports, and crash-reporting SDKs. Confirm release builds do not strip or disable them.
* `FLAG_SECURE` is per window. The last command only lists candidate Activities; check sensitive screens (PIN, OTP, payment, seed phrase) and any base Activity that sets it.
* Overlay/tapjacking defenses: look for `filterTouchesWhenObscured` on sensitive confirmation views.

## Additional Storage Formats

| Format / Surface | Static Lead | Runtime Follow-Through |
| --- | --- | --- |
| Jetpack DataStore | Preferences/Proto serializers and file locations | Identify the actual format and sensitive fields; protobuf is not encryption. |
| Room / SQLCipher | Database builder, open-helper factory, version-specific passphrase APIs | Determine whether encryption is enabled and how the key is obtained; opening plaintext in-process is not extraction of a hardware key. |
| EncryptedSharedPreferences | AndroidX Security version, key alias/provider, migration | Assess key policy, backups, failures, and plaintext lifetime; do not assume root makes the master key exportable. |
| Realm / MMKV | Configuration, file path, encryption option, key source | Use compatible tooling and trace configured protection; do not assume all versions/builds use the same defaults. |
| SQLite sidecars / deleted records | WAL, rollback journal, page residue | Preserve a consistent database/sidecar set; demonstrate relevant retained data and access rather than assuming deletion securely erases it. |
| External files / MediaStore / removable media | Shared collections, app-specific paths, URI grants | Test OS/target-specific access and uninstall residue. MediaStore does not expose every file in another app's private external directory. |
| Temporary files / exports | Location, permissions, name generation, symlink/canonical-path handling | Check race/overwrite/readability under a realistic caller; `File.createTempFile` is not inherently predictable. |
| Web storage / background jobs | Cookies, localStorage/IndexedDB, cache, WorkManager `Data` and database | Track account boundaries, logout, delayed work, retries, and logs; queued work must not reuse the wrong account's state. |

Use the [data lifecycle and acquisition workflow](../dynamic-testing/local-data-logs-and-privacy.md) for controlled before/after checks. Include removable-media residue and reinstall/restore scenarios only on disposable installations.

## Code Review Beyond Pattern Matching

Trace an untrusted source to the actual sink and relevant control. Decompiled output is approximate; resolve important branches against SMALI/native code.

| Lead | Inspect | Validate |
| --- | --- | --- |
| `Runtime.exec` / `ProcessBuilder` | Shell invocation, argument boundaries, input control | `Runtime.exec` is not itself a shell parser. Prove shell/argument injection using harmless markers rather than treating every call as command injection. |
| `Class.forName`, reflection, `DexClassLoader` | Class/code origin, storage writability, integrity/authenticity checks | Reflection is common; an attacker must control meaningful code or dispatch input. Check downloaded DEX/JAR/native updates and rollback. |
| `ObjectInputStream.readObject`, JSON, Parcelable/Bundle | Trust source, supported types, custom adapters, class loaders | Deserialization is not uniformly code execution. Assess reachable gadgets/custom behavior, type confusion, data changes, and bounded denial of service. |
| Coroutines / threads / shared mutable state | Authentication-state transitions, Mutex/transaction boundaries, cancellation | Use a bounded concurrent test to reproduce a stale check or double action; a `suspend` function alone is not a race. |
| WorkManager / delayed tasks | Stored arguments, session ownership, retry/cancellation | Reproduce logout/account switch between scheduling and execution; verify current authorization at execution. |
| R8 / DexGuard / encrypted strings | Renamed identifiers, reflection dispatch, string decryption, control flow | Plan targeted runtime observation; no obfuscation is not automatically a security defect. |
| Deprecated APIs | Target/platform behavior and replacement path | Deprecation is a review lead, not proof of exploitation on the tested version. |

**Previous:** [Configuration and Cryptography](configuration-and-cryptography.md) | **Next:** [WebView, IPC, and Dependency Checks](webview-ipc-and-dependencies.md)
