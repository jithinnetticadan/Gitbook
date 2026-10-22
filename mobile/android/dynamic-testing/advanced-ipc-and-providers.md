# Advanced IPC and Content Providers

{% hint style="info" %}
* Start with [Component Testing](component-testing.md).
* **Prerequisites:** minimally privileged companion app, owned test records, and explicit mutation/fuzzing authorization.
* Record caller UID, permissions, signer, grants, OS/target SDK, and account state.
* ADB shell results alone do not establish ordinary-app access.
{% endhint %}

## Intent, Result, and Binder Boundaries

| Surface                                | Controlled Test                                                                                                                 | Required Evidence                                                                                                                                       |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Intent redirection                     | Trace nested Intent/`intent:` input through an exported forwarding component; vary destination/action/data/grants one at a time | The intermediary uses its own authority to reach a protected component/action without the intended authorization.                                       |
| Activity results                       | Start the observed flow for a result from the companion app, including logged-out and cancellation paths                        | Sensitive result extras or URI grants returned before the required check. An activity launch alone is insufficient.                                     |
| Mutable PendingIntent                  | Obtain the token through a real sharing path; test which unspecified fields a recipient can fill                                | Actual unintended operation under the creator's identity. Mutability may be necessary; an empty/implicit base Intent is especially important to review. |
| PendingIntent replay / reuse           | Repeat an owned token after the operation, logout, or privilege change                                                          | Security-sensitive repeated action where one-shot or stateful authorization was required. Missing `FLAG_ONE_SHOT` is not universally wrong.             |
| Bound service / AIDL / Messenger       | Bind through a companion app and call known methods with owned records                                                          | Per-method caller/role/object authorization, not merely permission to bind. Check callbacks and returned Binder handles.                                |
| Binder identity handling               | Trace permission checks, `clearCallingIdentity`, asynchronous handoff, and restoration                                          | Checks are made against the intended external caller, not a substituted service identity.                                                               |
| Implicit / sticky / ordered broadcasts | Observe intended recipients, permissions/package targeting, result data, and registration flags                                 | Demonstrate actual unintended reception/injection. Sticky persistence and ordered priority vary with platform restrictions.                             |
| Task transitions                       | Compare launcher, recents, reparenting, and `singleTask` flows                                                                  | A proven unintended task/UI transition on the specific device; assess platform advisories separately.                                                   |

* Check parser handling with bounded inputs: missing extras, incorrect types, or short invalid URIs.
* Agree on size/attempt limits; do not flood Binder or persistent components.
* Reproduce crashes and establish impact; a crash alone does not prove code execution.

## Provider Operation Matrix

* Map each authority's documented/code-discovered URI routes, operations, permissions, accounts, and data owners.
* Compare an unauthorized caller with an authorized control.

| Surface                             | Review / Test                                                               | Interpretation                                                                                                                       |
| ----------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `query`, `update`, `delete`         | Selection construction, bound arguments, permitted rows                     | Parameterized values do not automatically protect SQL identifiers or raw fragments; mutate only disposable records.                  |
| Projection / sorting / grouping     | Allowed columns, expressions, order/limit handling                          | Test access to a known forbidden test column or route; avoid dumping schema/data unnecessarily.                                      |
| `openFile` / typed assets           | URI decoding, canonical containment, modes, symlinks/races                  | Use harmless files and verify the resolved path remains inside the intended root. Prefix checks must respect path boundaries.        |
| FileProvider                        | Configured roots, exact shared URI, read/write/prefix/persistable grants    | `grantUriPermissions=true` enables granting; it does not grant arbitrary callers every URI. Prove the actual grant scope/lifetime.   |
| Route variants / undocumented paths | URI matcher, encoded segments, trailing separators, alternate operations    | Confirm authorization is enforced consistently after normalization; do not infer that every alternate URI exists.                    |
| Family apps / shared UID            | Signing/install prerequisites, provider permissions, actual caller identity | One app's compromise is a prerequisite, not proof that all installed apps share access.                                              |
| `notifyChange` / ContentObserver    | Notification URI contents, permissions, registration and delivery           | Notifications are not unrestricted broadcasts; verify that the unauthorized observer can register and receive sensitive information. |
| Malformed requests                  | Bounded invalid selection, URI, offsets, types                              | Capture rejection/crash and recovery; avoid repeated denial of service.                                                              |

* Test URI grant revocation, recipient changes, and logout independently.
* A non-exported provider may intentionally serve a narrowly granted URI; this alone is not an export-control failure.

## Dirty Stream: Untrusted Provider Metadata

* Test the shared-file consumer even when its own provider is correctly configured.

1. Locate a reachable import/share/file-picker flow that reads a remote provider's display name, `_data`, size, MIME, or URI segment.
2. Trace whether the consumer uses that untrusted metadata as a local destination path rather than generating its own safe name.
3. Use an authorized companion provider serving a harmless marker with controlled metadata. Test normalization and containment with an owner-agreed disposable destination; do not overwrite live settings, credentials, or libraries.
4. Capture the received URI/metadata, resolved destination, write result, and required user interaction. Prove an unintended file write separately from any claimed code execution or token theft.
5. Verify remediation: safe generated names or strict filename handling, canonical directory containment, and resistance to overwrite/race paths.

* **Dirty Stream is not CVE-2024-0044:** that CVE concerns platform `run-as`/installer metadata, with different prerequisites and patches.

* Reference: [Microsoft Dirty Stream research](https://www.microsoft.com/en-us/security/blog/2024/05/01/dirty-stream-attack-discovering-and-mitigating-a-common-vulnerability-pattern-in-android-apps/).
* Reference: [Android untrusted provider filenames](https://developer.android.com/privacy-and-security/risks/untrustworthy-contentprovider-provided-filename).
* Reference: [Android intent redirection](https://developer.android.com/privacy-and-security/risks/intent-redirection).
