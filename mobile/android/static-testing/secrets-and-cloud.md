# Secrets and Cloud

{% hint style="info" %}
* Test only in-scope apps; replace command placeholders before use.
* Record package, version, source, device/API level, and original APK hash.
{% endhint %}

## Secrets, Cloud Configuration, and Endpoints

* Search: `api`, `id`, `password`, `username`, `.com`, `aws`, `gcp`, `azure`, `http`, `https`, `secret`, `key`.
* Locations: `res/values/strings.xml`, code, JSON/configuration, assets, native libraries.
* Check: endpoints, credentials, tokens, Firebase URLs, bucket names, environment settings.
* Validate privilege and impact; public client IDs are not automatically secrets.

```sh
apkleaks -f <app.apk> -o <secrets-report.txt>
grep -rniE 'api[_-]?key|secret|token|password|AIza[0-9A-Za-z_-]{35}|BEGIN (RSA |EC )?PRIVATE KEY' <decompiled-directory>
strings <decoded-directory>/lib/<abi>/*.so | grep -iE 'key|secret|token'
grep -rniE 'firebaseio\.com|firebasestorage\.googleapis\.com|amazonaws\.com' <decompiled-directory>
```

* Secrets also hide in native `.so` libraries, not just Java/Kotlin code.
* `AIza...` matches are Google API keys. Many are restricted client identifiers; check what the key authorizes before rating it.
* A match is a lead until you confirm it is reachable and grants access.

* **Prerequisites:** explicit cloud-test authorization and scoped credentials.

* [cloud\_enum](https://github.com/initstring/cloud_enum) can identify candidate cloud assets.
* [firebaseEnum](https://github.com/Sambal0x/firebaseEnum) can help assess Firebase exposure.
* Use the [AWS CLI](https://aws.amazon.com/cli/) only with an authorized profile, e.g. `aws configure --profile <assessment-name>`. Never place credentials in notes or shell history.
* Firebase Realtime Database: `https://<database>.firebaseio.com/<test-path>.json` or a regional `firebasedatabase.app` endpoint.
* Use scoped, non-destructive reads; record response and access rules. URL format alone proves nothing.
* `.json` is not universal across Firebase products; `firebase.io.com` is incorrect.
* `cloud_enum` discovers AWS/Azure/GCP assets; discovery does not authorize testing.

## Product-Specific Cloud and SDK Checks

* Use a known synthetic record and a least-privileged test account.
* Compare unauthenticated access, account A's own record, and account B's record.
* Do not dump collections/buckets or send production events just to test a key.

| Product / Key                           | Check                                                                                         | Finding Boundary                                                                                                                                    |
| --------------------------------------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Firebase RTDB                           | Auth rules and path-level read/write decisions                                                | A public client configuration is expected; unauthorized private-data access is not. Validate regional endpoint format.                              |
| Firestore                               | Document/collection rules and authenticated ownership                                         | Use the Firestore API or SDK, not RTDB's `.json` pattern. Rules and privileged server credentials are different access paths.                       |
| Firebase Storage / cloud object storage | Object permissions, signed-URL scope/expiry, uploads/content type                             | Use known owned objects and reversible test files, not bulk enumeration or overwrite.                                                               |
| Remote Config                           | Values actually delivered to the client and trust in feature flags                            | Treat delivered values as client-readable; identify genuine secrets or server decisions relying on tamperable flags.                                |
| FCM                                     | Registration-token lifecycle, topic subscriptions, server send credentials, backend ownership | A registration token identifies a recipient; it does not by itself authorize sending messages. Check test-account reassignment and logout behavior. |
| AWS / Azure / GCP credentials           | Long-lived versus scoped temporary credentials, IAM scope, intended audience                  | Confirm privileges through approved identity/read-only checks; do not infer full-account compromise from a key-shaped string.                       |
| Analytics / ads / crash reporting       | Ingestion keys versus administrative APIs, PII, consent, event integrity                      | Public publisher/ingestion IDs may be intentional. Prove unauthorized data access or accepted harmful events in a test project.                     |
| Payment / social SDKs                   | Publishable keys/client IDs versus server secrets, token audience, backend confirmation       | Stripe publishable keys, OAuth client IDs, and many app IDs are not secret credentials. Verify the actual authority of any exposed secret.          |

* Inspect relevant SDK configuration: Sentry, Crashlytics, AppsFlyer, Branch, Adjust, Mixpanel, and similar services.
* Vendor presence alone is not a vulnerability.
* Collect backend URLs and test environments; keep discovered credentials out of these notes.
