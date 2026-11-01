# Data Storage and Privacy

* Locate containers with `env` or bundle-ID metadata correlation.
* Typical path: `/var/mobile/Containers/Data/Application/<UUID>`
* Retrieve files through an approved app export/development-container workflow, or configured SSH/SFTP.&#x20;
* [Cyberduck](https://cyberduck.io/) is a transfer client.

<table><thead><tr><th width="338">Storage/Surface</th><th>Check</th></tr></thead><tbody><tr><td>Plist / <code>NSUserDefaults</code></td><td>Credentials, tokens, personal data, local roles. Plists can be XML/binary; defaults is an API.</td></tr><tr><td>SQLite / Core Data</td><td>Sensitive records, permissions, query inputs. Core Data is a framework, not synonymous with SQLite.</td></tr><tr><td>Keychain</td><td>Accessibility, access groups, authentication controls; separate from ordinary container files.</td></tr><tr><td>Cookies/credentials/cache/logs</td><td>Sensitive values and retention.</td></tr><tr><td>Pasteboard/memory/snapshots/keyboard</td><td>Exposure outside the intended interaction.</td></tr></tbody></table>

### File and Database Inspection

* ```
  find <application-data-root> -type d -name <known-container-uuid>
  file <path-to-file>
  sqlite3 <database-file>
  ```
* **Objection console:**
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">env
    filesystem cat &#x3C;path-to-file>
    filesystem download &#x3C;path-to-file>
    sqlite connect &#x3C;database-file>
    ios nsuserdefaults get
    ios nsurlcredentialstorage dump
    ios plist cat Info.plist
    ios plist cat &#x3C;app-bundle-path>/Info.plist
    ios keychain dump
    ios cookies get
    ios pasteboard monitor
    </code></pre>

### Keychain and Cookies

* **Objection Keychain dump:** app-entitled access groups and current item accessibility/authentication policy.
* [Keychain-Dumper](https://github.com/ptoomey3/Keychain-Dumper): create `/tmp/keychain`; transfer a compatible `keychain_dumper` via SFTP.
* In device SSH: `./keychain_dumper > keychain.txt`
* SQLite: install `sqlite3` if needed; use `.tables`&#x20;
* BinaryCookiesReader: `pip install binarycookiesreader`.

### Legacy Tools

* [iRET](https://github.com/S3Jensen/iRET), [Cycript](https://www.cycript.org/) (inspection/injection/foreign-function calls), [QuickTime](https://support.apple.com/downloads/quicktime) (recording).
* [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump): release-specific Python/SSH setup; never hardcode credentials.
* Package sources: [Havoc](https://havoc.app/), [Shadow](https://ios.jjolano.me/), [Radare2](https://cydia.radare.org/), [Akemi](https://cydia.akemi.ai/), [opa334](https://opa334.github.io/).
* Utilities: `wget`, `ps`, `sqlite3`, `unzip`, `dpkg`, BigBoss tools.
* For Objection session syntax, see [Runtime Instrumentation](runtime-instrumentation.md).
