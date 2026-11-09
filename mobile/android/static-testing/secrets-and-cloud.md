# Secrets and Cloud

## Secrets, Cloud Configuration, and Endpoints

* Search: `api`, `id`, `password`, `username`, `.com`, `aws`, `gcp`, `azure`, `http`, `https`, `secret`, `key`.
* Locations: `res/values/strings.xml`, code, JSON/configuration, assets, native libraries.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">apkleaks -f &#x3C;app.apk>
  apkleaks -f &#x3C;app.apk> -o &#x3C;secrets-report.txt>
  grep -rniE 'api[_-]?key|secret|token|password|AIza[0-9A-Za-z_-]{35}|BEGIN (RSA |EC )?PRIVATE KEY' &#x3C;decompiled-directory>
  strings &#x3C;decoded-directory>/lib/&#x3C;abi>/*.so | grep -iE 'key|secret|token'
  grep -rniE 'firebaseio\.com|firebasestorage\.googleapis\.com|amazonaws\.com' &#x3C;decompiled-directory>
  </code></pre>
* Secrets also hide in native `.so` libraries, not just Java/Kotlin code.
* `AIza...` matches are Google API keys. Many are restricted client identifiers.
* [cloud\_enum](https://github.com/initstring/cloud_enum) can identify cloud assets.
* [firebaseEnum](https://github.com/Sambal0x/firebaseEnum) can help assess Firebase exposure.
* Use the [AWS CLI](https://aws.amazon.com/cli/) only with an authorized profile, e.g. `aws configure --profile <assessment-name>`.
* Firebase Realtime Database:&#x20;
  * `https://<database>.firebaseio.com/<test-path>.json`&#x20;
  * Regional `firebasedatabase.app` endpoint.
* `.json` is not universal across Firebase products.

## Product-Specific Cloud and SDK Checks

* **Host Bash/curl, observed RTDB item:** compare unauthenticated access with the corresponding Firebase test-user ID token.
  * ```bash
    curl -i 'https://<database-host>/<owned-test-path>.json'
    curl -i --get 'https://<database-host>/<owned-test-path>.json' --data-urlencode 'auth=<firebase-test-user-id-token>'
    ```
* **Firestore document:** use an actual project/database/document path; repeat with account-A's token and account-B's known document.
  * ```bash
    curl -i 'https://firestore.googleapis.com/v1/projects/<project-id>/databases/(default)/documents/<collection>/<test-document>' -H 'Authorization: Bearer <firebase-test-user-id-token>'
    ```
* **AWS credential identity:** use the configured test profile; this identifies the caller, not its complete permission set.
  * ```bash
    aws sts get-caller-identity --profile '<assessment-profile>'
    aws s3api head-object --bucket '<bucket>' --key '<owned-object-key>' --profile '<assessment-profile>'
    ```
* For app backend/SDK event APIs, use the [captured-request replay templates](../dynamic-testing/authentication-and-cryptography.md#captured-request-replay) with the actual product endpoint and test account.

### Anonymous S3 Access from Packaged Bucket Paths

* Resolve the bucket, region, prefix, and object key from app configuration or observed requests.
* **Host AWS CLI, no credentials:** list one page under the discovered prefix, then read one known test object.
  * ```bash
    aws s3api list-objects-v2 --bucket '<bucket>' --prefix '<observed-prefix>/' --max-keys 10 --no-paginate --no-sign-request --region '<region>'
    aws s3api head-object --bucket '<bucket>' --key '<owned-test-object-key>' --no-sign-request --region '<region>'
    aws s3api get-object --bucket '<bucket>' --key '<owned-test-object-key>' --no-sign-request --region '<region>' './s3-test-object'
    ```
* **Authenticated comparison:** replace `--no-sign-request` with `--profile '<assessment-profile>'`.
* Listing and object reads are separate permissions: denied listing does not rule out a readable known object. Public app assets may be intentional; confirm access to data intended to be private.
* References: [ListObjectsV2](https://docs.aws.amazon.com/cli/latest/reference/s3api/list-objects-v2.html), [GetObject](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-object.html).

<table><thead><tr><th width="160">Product / Key</th><th>Check</th><th>Finding Boundary</th></tr></thead><tbody><tr><td>Firebase RTDB</td><td>Auth rules and path-level read/write decisions</td><td>A public client configuration is expected; unauthorized private-data access is not. Validate regional endpoint format.</td></tr><tr><td>Firestore</td><td>Document/collection rules and authenticated ownership</td><td>Use the Firestore API or SDK, not RTDB's <code>.json</code> pattern. Rules and privileged server credentials are different access paths.</td></tr><tr><td>Firebase Storage / cloud object storage</td><td>Object permissions, signed-URL scope/expiry, uploads/content type</td><td>Use known owned objects and reversible test files, not bulk enumeration or overwrite.</td></tr><tr><td>Remote Config</td><td>Values actually delivered to the client and trust in feature flags</td><td>Treat delivered values as client-readable; identify genuine secrets or server decisions relying on tamperable flags.</td></tr><tr><td>FCM</td><td>Registration-token lifecycle, topic subscriptions, server send credentials, backend ownership</td><td>A registration token identifies a recipient; it does not by itself authorize sending messages. Check test-account reassignment and logout behavior.</td></tr><tr><td>AWS / Azure / GCP credentials</td><td>Long-lived versus scoped temporary credentials, IAM scope, intended audience</td><td>Confirm privileges through approved identity/read-only checks; do not infer full-account compromise from a key-shaped string.</td></tr><tr><td>Analytics / ads / crash reporting</td><td>Ingestion keys versus administrative APIs, PII, consent, event integrity</td><td>Public publisher/ingestion IDs may be intentional. Prove unauthorized data access or accepted harmful events in a test project.</td></tr><tr><td>Payment / social SDKs</td><td>Publishable keys/client IDs versus server secrets, token audience, backend confirmation</td><td>Stripe publishable keys, OAuth client IDs, and many app IDs are not secret credentials. Verify the actual authority of any exposed secret.</td></tr></tbody></table>

* Inspect relevant SDK configuration: Sentry, Crashlytics, AppsFlyer, Branch, Adjust, Mixpanel, and similar services.
