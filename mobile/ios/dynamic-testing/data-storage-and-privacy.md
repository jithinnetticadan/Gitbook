# Data Storage and Privacy

* Locate containers using [Objection environment commands](runtime-instrumentation.md#classes-and-hooks) or bundle-ID metadata correlation.
* Typical path: `/var/mobile/Containers/Data/Application/<UUID>`
* Retrieve files through an approved app export/development-container workflow, or configured SSH/SFTP.&#x20;
* [Cyberduck](https://cyberduck.io/) is a transfer client.

<table><thead><tr><th width="338">Storage/Surface</th><th>Check</th></tr></thead><tbody><tr><td>Plist / <code>NSUserDefaults</code></td><td>Credentials, tokens, personal data, local roles. Plists can be XML/binary; defaults is an API.</td></tr><tr><td>SQLite / Core Data</td><td>Sensitive records, permissions, query inputs. Core Data is a framework, not synonymous with SQLite.</td></tr><tr><td>Keychain</td><td>Accessibility, access groups, authentication controls; separate from ordinary container files.</td></tr><tr><td>Cookies/credentials/cache/logs</td><td>Sensitive values and retention.</td></tr><tr><td>Pasteboard/memory/snapshots/keyboard</td><td>Exposure outside the intended interaction.</td></tr></tbody></table>

## File and Database Inspection

* **Physical device with configured SSH:** copy the known container path to the host before offline inspection.
  * ```bash
    scp -r '<ssh-user>@<device-ip>:<resolved-data-container>/Library/Preferences' './device-preferences'
    scp -r '<ssh-user>@<device-ip>:<resolved-data-container>/Library/Application Support/<database-directory>' './device-databases'
    ```
* Paths with spaces require quoting supported by the installed SCP/SFTP implementation; transfer a consistent database/sidecar set.

* **macOS Simulator:** resolve the data container, inspect files, and query a copied database.
  * ```bash
    xcrun simctl get_app_container booted '<bundle-id>' data
    xcrun simctl get_app_container booted '<bundle-id>' app
    find '<resolved-data-container>/Library' -type f
    plutil -p '<resolved-data-container>/Library/Preferences/<bundle-id>.plist'
    sqlite3 -readonly '<database-copy.db>' '.tables'
    sqlite3 -readonly '<database-copy.db>' 'SELECT * FROM <known-table> LIMIT 10;'
    ```
* **Compare storage across login/logout/account switch:** acquire each state into its own directory, then compare the same files.
  * ```bash
    diff -ru '<before-directory>' '<after-directory>'
    ```
* **Simulator runtime state and screenshots:**
  * ```bash
    xcrun simctl terminate booted '<bundle-id>'
    xcrun simctl io booted screenshot '<screenshot.png>'
    xcrun simctl spawn booted log stream --style compact --predicate 'process == "<app-process-name>"'
    ```
* **Simulator pasteboard:**
  * ```bash
    xcrun simctl pbpaste booted
    printf '%s' '<test-marker>' | xcrun simctl pbcopy booted
    ```
* Reopen using the [Simulator launch command](client-side-testing.md#deep-links-and-url-handling). On a device, use Xcode's device console or the configured SSH file path instead of Simulator paths.

* ```
  find <application-data-root> -type d -name <known-container-uuid>
  file <path-to-file>
  sqlite3 <database-file>
  ```
* **Objection:** [file/SQLite, defaults, plist, Keychain, cookies, and pasteboard commands](runtime-instrumentation.md#clipboard-screenshots-memory-and-sqlite).

## Keychain and Cookies

* **Objection Keychain dump:** app-entitled access groups and current item accessibility/authentication policy.
* [Keychain-Dumper](https://github.com/ptoomey3/Keychain-Dumper): create `/tmp/keychain`; transfer a compatible `keychain_dumper` via SFTP.
* In device SSH: `./keychain_dumper > keychain.txt`
* SQLite: use the read-only queries under [File and Database Inspection](#file-and-database-inspection).
* BinaryCookiesReader: `pip install binarycookiesreader`.

## Legacy Tools

* [iRET](https://github.com/S3Jensen/iRET), [Cycript](https://www.cycript.org/) (inspection/injection/foreign-function calls), [QuickTime](https://support.apple.com/downloads/quicktime) (recording).
* [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump): release-specific Python/SSH setup; never hardcode credentials.
* Package sources: [Havoc](https://havoc.app/), [Shadow](https://ios.jjolano.me/), [Radare2](https://cydia.radare.org/), [Akemi](https://cydia.akemi.ai/), [opa334](https://opa334.github.io/).
* Utilities: `wget`, `ps`, `sqlite3`, `unzip`, `dpkg`, BigBoss tools.
* For Objection session syntax, see [Runtime Instrumentation](runtime-instrumentation.md).
