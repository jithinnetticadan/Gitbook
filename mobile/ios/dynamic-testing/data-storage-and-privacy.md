# Data Storage and Privacy

{% hint style="info" %}
* Use authorized devices/builds and test accounts; replace command placeholders before use.
* Isolate the lab, protect evidence, and restore it afterward.
{% endhint %}

{% hint style="warning" %}
* **Prerequisites:** an authorized container/export path; SSH requires a compatible jailbreak or separately provided service. [Frida preflight](preflight-and-lab-setup.md#mandatory-preflight) applies to Objection/hooks.
* Identify storage locations using [Configuration and Sensitive Data](../static-testing/configuration-and-sensitive-data.md).
{% endhint %}

## Data Storage and Privacy

* Locate containers with `env` or bundle-ID metadata correlation, not `find -name <bundle-id>`.
* Typical path: `/var/mobile/Containers/Data/Application/<UUID>`; layout/access vary.
* Retrieve files through an approved app export/development-container workflow, or configured SSH/SFTP. [Cyberduck](https://cyberduck.io/) is a transfer client, not a sandbox bypass.

| Storage/Surface                      | Check                                                                                               |
| ------------------------------------ | --------------------------------------------------------------------------------------------------- |
| Plist / `NSUserDefaults`             | Credentials, tokens, personal data, local roles. Plists can be XML/binary; defaults is an API.      |
| SQLite / Core Data                   | Sensitive records, permissions, query inputs. Core Data is a framework, not synonymous with SQLite. |
| Keychain                             | Accessibility, access groups, authentication controls; separate from ordinary container files.      |
| Cookies/credentials/cache/logs       | Sensitive values and retention.                                                                     |
| Pasteboard/memory/snapshots/keyboard | Exposure outside the intended interaction.                                                          |

### File and Database Inspection

* **Shell:** run against accessible test copies, or within the approved device SSH session.

```sh
find <application-data-root> -type d -name <known-container-uuid>
file <path-to-file>
sqlite3 <database-file>
```

* **Objection console:** registered commands use `filesystem`, not `file`.

```text
env
filesystem cat <path-to-file>
filesystem download <path-to-file>
sqlite connect <database-file>
ios nsuserdefaults get
ios nsurlcredentialstorage dump
ios plist cat Info.plist
ios plist cat <app-bundle-path>/Info.plist
ios keychain dump
ios cookies get
ios pasteboard monitor
```

* `Info.plist` alone requires the current directory to be the app bundle; use `env` to resolve the bundle path for the explicit variant.

### Keychain and Cookies

* **Objection Keychain dump:** app-entitled access groups and current item accessibility/authentication policy, not unrestricted device-wide access.
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

* For Objection session syntax, see [Runtime Instrumentation](runtime-instrumentation.md).
