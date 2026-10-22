# Data Storage and Privacy

{% hint style="info" %}
Use authorized devices/builds and test accounts. Isolate the lab, protect evidence, and restore it afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Complete the [Mandatory Preflight](preflight-and-lab-setup.md#mandatory-preflight) first. Candidate storage locations come from [Configuration and Sensitive Data](../static-testing/configuration-and-sensitive-data.md).
{% endhint %}

## Data Storage and Privacy

* Locate containers with `env` or bundle-ID metadata correlation, not `find -name <bundle-id>`.
* Typical path: `/var/mobile/Containers/Data/Application/<UUID>`; layout/access vary.
* Retrieve authorized files through SSH/SFTP or [Cyberduck](https://cyberduck.io/).

| Storage/Surface | Check |
| --- | --- |
| Plist / `NSUserDefaults` | Credentials, tokens, personal data, local roles. Plists can be XML/binary; defaults is an API. |
| SQLite / Core Data | Sensitive records, permissions, query inputs. Core Data is a framework, not synonymous with SQLite. |
| Keychain | Accessibility, access groups, authentication controls; separate from ordinary container files. |
| Cookies/credentials/cache/logs | Sensitive values and retention. |
| Pasteboard/memory/snapshots/keyboard | Exposure outside the intended interaction. |

### File and Database Inspection

```sh
find <application-data-root> -type d -name <known-container-uuid>
file <path-to-file>
sqlite3 <database-file>
```

```text
env
file cat <path-to-file>
file download <path-to-file>
sqlite connect <database-file>
ios nsuserdefaults get
ios nsurlcredentialstorage dump
ios plist cat Info.plist
ios keychain dump
ios cookies get
ios pasteboard monitor
```

### Keychain and Cookies

* [Keychain-Dumper](https://github.com/ptoomey3/Keychain-Dumper): create `/tmp/keychain`; transfer a compatible `keychain_dumper` via SFTP.
* In device SSH: `./keychain_dumper > keychain.txt`. Privileges/entitlements required; avoid collecting unrelated apps' data.
* SQLite: install `sqlite3` if needed; use `.tables` and limited read-only queries.
* BinaryCookiesReader: `pip install binarycookiesreader`; verify package provenance/version.
* Protect database/keychain/cookie/memory dumps; remove tools and output afterward.

### Optional and Legacy Tools

* [iRET](https://github.com/S3Jensen/iRET), [Cycript](https://www.cycript.org/) (inspection/injection/foreign-function calls), [QuickTime](https://support.apple.com/downloads/quicktime) (recording).
* [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump): release-specific Python/SSH setup; never hardcode credentials.
* Package sources: [Havoc](https://havoc.app/), [Shadow](https://ios.jjolano.me/), [Radare2](https://cydia.radare.org/), [Akemi](https://cydia.akemi.ai/), [opa334](https://opa334.github.io/).
* Utilities: `wget`, `ps`, `sqlite3`, `unzip`, `dpkg`, BigBoss tools.
* Verify provenance, maintenance, and jailbreak/iOS compatibility.

For Objection session syntax, see [Runtime Instrumentation](runtime-instrumentation.md).

**Previous:** [Runtime Instrumentation](runtime-instrumentation.md) | **Next:** [URL Schemes, Web Views, and Client Behavior](client-side-testing.md)
