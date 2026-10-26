# Advanced IPC and Content Providers

[Intents / Binder](#intent-result-and-binder-boundaries) | [Providers](#provider-operation-matrix) | [Dirty Stream](#dirty-stream-untrusted-provider-metadata)

{% hint style="info" %}
* Start with [Component Testing](component-testing.md).
* **Prerequisites:** minimally privileged companion app, owned test records, and explicit mutation/fuzzing authorization.
* Record caller UID, permissions, signer, grants, OS/target SDK, and account state.
* ADB shell results alone do not establish ordinary-app access.
{% endhint %}

## Scope and Entry Criteria

* **Basic commands:** [Component Testing](component-testing.md) for Intent delivery, Messenger, provider reads/CRUD/scanners.
* **Here:** forwarding, results, delegated authority, Binder identity, provider query/path/grant boundaries.
* **Start with:** reachable operation, authorized baseline, observed protocol/URI, disposable records.
* **Client:** compatible companion app when CLI cannot express the interaction.
* **Track:** confirmed / rejected under tested conditions / blocked / untested.

## Intent, Result, and Binder Boundaries

| Surface | Test | Confirm |
| --- | --- | --- |
| Intent redirection | Nested Intent/`intent:` through exported forwarder; vary destination/action/data/grants | Protected operation reached using intermediary authority |
| Activity results | Companion launches for result; logged-out/cancel paths | Sensitive extras/grants returned before authorization |
| Mutable PendingIntent | Obtain shared token; fill unspecified fields, especially empty/implicit base Intent | Unintended operation as creator; mutability alone is not a flaw |
| PendingIntent replay / reuse | Repeat owned token after use, logout, privilege change | Unauthorized repeat action; missing `FLAG_ONE_SHOT` alone is not a flaw |
| Bound service / AIDL / Messenger | Known methods, owned records, callbacks, returned Binder handles | Per-method caller/role/object checks; binding alone is insufficient |
| Binder identity handling | Checks, `clearCallingIdentity`, async handoff, restoration | Authorization uses intended external caller, not substituted service identity |
| Implicit / sticky / ordered broadcasts | Recipients, permissions/package, results, registration flags | Unintended reception/injection under actual platform restrictions |
| Task transitions | Launcher, recents, reparenting, `singleTask` | Unintended task/UI transition; assess platform advisories separately |

* **Malformed inputs:** missing extras, wrong types, short invalid URIs; agree size/attempt limits.
* **No flooding:** reproduce bounded failures; a crash alone is not code execution.

## Provider Operation Matrix

* Map each authority's documented/code-discovered URI routes, operations, permissions, accounts, and data owners.
* Compare an unauthorized caller with an authorized control.

| Surface | Test | Confirm / Caveat |
| --- | --- | --- |
| `query`, `update`, `delete` | Selection, bound arguments, permitted rows | Parameters do not protect raw SQL/identifiers; disposable mutations only |
| Projection / sorting / grouping | Columns, expressions, order/limit | Forbidden test column/route accessible; avoid unnecessary dumps |
| `openFile` / typed assets | Decoding, canonical paths, modes, symlinks/races | Harmless file stays inside root; prefix checks respect path boundaries |
| FileProvider | Roots, URI, read/write/prefix/persistable grants | Actual grant scope/lifetime; `grantUriPermissions=true` is not blanket access |
| Route variants / undocumented paths | Matcher, encoded segments, trailing separators, alternate operations | Consistent authorization after normalization; establish valid routes first |
| Family apps / shared UID | Signing/install prerequisites, permissions, caller UID | Demonstrate access; one compromised app does not imply universal access |
| `notifyChange` / ContentObserver | URI contents, permissions, registration/delivery | Unauthorized observer receives sensitive data; not an unrestricted broadcast |
| Malformed requests | Bounded invalid selection, URI, offsets, types | Rejection/crash and recovery; no repeated DoS |

* Test URI grant revocation, recipient changes, and logout independently.
* A non-exported provider may intentionally serve a narrowly granted URI; this alone is not an export-control failure.

## Dirty Stream: Untrusted Provider Metadata

* Test the shared-file consumer even when its own provider is correctly configured.

1. **Find consumer:** reachable import/share/picker; reads display name, `_data`, size, MIME, or URI segment.
2. **Trace destination:** remote metadata used as a local path versus safe generated name.
3. **Test:** companion provider + harmless marker + controlled metadata; agreed disposable destination only.
4. **Capture:** URI/metadata, resolved path, write result, user interaction; prove unintended write separately from execution/token theft.
5. **Verify fix:** safe names, canonical containment, overwrite/race resistance.

* Never overwrite live settings, credentials, or libraries.

* **Dirty Stream is not CVE-2024-0044:** that CVE concerns platform `run-as`/installer metadata, with different prerequisites and patches.

* Reference: [Microsoft Dirty Stream research](https://www.microsoft.com/en-us/security/blog/2024/05/01/dirty-stream-attack-discovering-and-mitigating-a-common-vulnerability-pattern-in-android-apps/).
* Reference: [Android untrusted provider filenames](https://developer.android.com/privacy-and-security/risks/untrustworthy-contentprovider-provided-filename).
* Reference: [Android intent redirection](https://developer.android.com/privacy-and-security/risks/intent-redirection).
