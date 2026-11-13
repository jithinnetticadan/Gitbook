# Data Storage and Privacy

* Locate containers using [Objection environment commands](runtime-instrumentation.md#classes-and-hooks) or bundle-ID metadata correlation.
* Typical path: `/var/mobile/Containers/Data/Application/<UUID>`
* Retrieve files through an approved app export/development-container workflow, or configured SSH/SFTP.&#x20;
* [Cyberduck](https://cyberduck.io/) is a transfer client.

<table><thead><tr><th width="338">Storage/Surface</th><th>Check</th></tr></thead><tbody><tr><td>Plist / <code>NSUserDefaults</code></td><td>Credentials, tokens, personal data, local roles. Plists can be XML/binary; defaults is an API.</td></tr><tr><td>SQLite / Core Data</td><td>Sensitive records, permissions, query inputs. Core Data is a framework, not synonymous with SQLite.</td></tr><tr><td>Keychain</td><td>Accessibility, access groups, authentication controls; separate from ordinary container files.</td></tr><tr><td>Cookies/credentials/cache/logs</td><td>Sensitive values and retention.</td></tr><tr><td>Pasteboard/memory/snapshots/keyboard</td><td>Exposure outside the intended interaction.</td></tr></tbody></table>

## File and Database Inspection

{% tabs %}
{% tab title="worse_finder" %}
### Non-Jailbroken Container Access with worse_finder

* [worse_finder](https://github.com/melvinsh/worse_finder) uses the [worse_query](https://github.com/forcequitOS/worse_query) container-manager sandbox escape to browse and export app and App Group containers without a jailbreak. The project reports support for iOS 26 and 27; verify the exact device build against current project information. Some paths can remain inaccessible because of data protection or other restrictions.
* **Build prerequisites:** macOS, Xcode 27, a physical device, and a signing team/profile that permits an App Group entitlement. In the project's Xcode target, select the team, add an App Group under Signing & Capabilities, and set the same group in `worse_finder/worse_finder.entitlements`. The default bundle identifier is a placeholder; use one provisioned for the team. A signer/profile that strips or cannot provision the App Group will not work.
* **macOS Terminal:** after configuring signing, build into the shown output directory and install using the selected device UDID.
  * ```bash
    git clone https://github.com/melvinsh/worse_finder.git
    cd worse_finder
    xcrun devicectl list devices
    xcodebuild -project worse_finder.xcodeproj -target worse_finder -configuration Debug -sdk iphoneos -allowProvisioningUpdates SYMROOT=./build build
    xcrun devicectl device install app --device '<device-udid>' build/Debug-iphoneos/worse_finder.app
    ```
* Open worse_finder on the device, select the target app, inspect its data container and App Groups, and export the relevant container as ZIP. Exports are written to worse_finder's Documents for sharing through Files or AirDrop. The built-in web server is an alternative on port `8080`; it uses plain HTTP, including for its generated passphrase.
* Inspect exported preferences, databases and caches using the commands below. Compare login/logout/account states and whether the recovered test credentials still work. Container access does not imply access to other apps' Keychain items or bypass every locked-file protection; distinguish this OS-level escape from exposure to an ordinary sandboxed app.
{% endtab %}

{% tab title="SSH / SFTP" %}
* **Physical device with configured SSH:** copy the known container path to the host before offline inspection.
  * ```bash
    scp -r '<ssh-user>@<device-ip>:<resolved-data-container>/Library/Preferences' './device-preferences'
    scp -r '<ssh-user>@<device-ip>:<resolved-data-container>/Library/Application Support/<database-directory>' './device-databases'
    ```
* Paths with spaces require quoting supported by the installed SCP/SFTP implementation; transfer a consistent database/sidecar set.
{% endtab %}

{% tab title="Simulator" %}
* **macOS Simulator:** resolve the data container, inspect files, and query a copied database.
  * ```bash
    xcrun simctl get_app_container booted '<bundle-id>' data
    xcrun simctl get_app_container booted '<bundle-id>' app
    find '<resolved-data-container>/Library' -type f
    plutil -p '<resolved-data-container>/Library/Preferences/<bundle-id>.plist'
    sqlite3 -readonly '<database-copy.db>' '.tables'
    sqlite3 -readonly '<database-copy.db>' 'SELECT * FROM <known-table> LIMIT 10;'
    ```
{% endtab %}

{% tab title="Objection" %}
* **Mac terminal:** attach to the running app with a working Frida connection.
  * ```bash
    frida-ps -Uai
    objection --name '<app-process-name>' start
    ```
* **Objection console:** obtain the app's container paths and inspect/download the target file or query its database.
  * ```text
    env
    filesystem cat <path-to-file>
    filesystem download <path-to-file>
    sqlite connect <database-file>
    ios nsuserdefaults get
    ```
* These commands run in the attached app's context; the app's entitlements and file-access state determine which items it can read.
{% endtab %}

{% tab title="Grapefruit" %}
* **Mac terminal:** start the installed Grapefruit interface with a compatible Frida connection; its current upstream release requires Node.js 22.18+.
  * ```bash
    frida-ps -Uai
    igf
    ```
* Select the app in the local UI, open its filesystem browser or SQLite inspector, then navigate to the observed preferences/database path and inspect the relevant test value. The app process and its available access determine the results.
{% endtab %}
{% endtabs %}

* **Compare storage across login/logout/account switch:** acquire each state into its own directory, then compare the same files.
  * ```bash
    diff -ru '<before-directory>' '<after-directory>'
    ```
* **Simulator process restart:** terminate and relaunch the target, then navigate to the sensitive screen with the test marker.
  * ```bash
    xcrun simctl terminate booted '<bundle-id>'
    xcrun simctl launch booted '<bundle-id>'
    ```
* **Simulator screenshot:** with that screen visible, capture and inspect the resulting image for the marker.
  * ```bash
    xcrun simctl io booted screenshot '<screenshot.png>'
    ```
* **Simulator logs:** run this in another host terminal while triggering the target feature; stop the stream with Ctrl+C.
  * ```bash
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

{% tabs %}
{% tab title="Objection" %}
* **Mac terminal:** attach to the running app with a working Frida connection.
  * ```bash
    frida-ps -Uai
    objection --name '<app-process-name>' start
    ```
* **Objection console:** inspect Keychain items accessible under the app's entitlements and the current device state.
  * ```text
    ios keychain dump
    ```
{% endtab %}
{% tab title="Grapefruit" %}
* **Mac terminal:** start the installed interface with the device's Frida server running.
  * ```bash
    frida-ps -Uai
    igf
    ```
* Select the app, then open its Keychain view and inspect the relevant item's access group, accessibility attributes and data under the current app/device context.
{% endtab %}
{% tab title="Keychain-Dumper" %}
* **Jailbroken device SSH:** transfer a compatible [Keychain-Dumper](https://github.com/ptoomey3/Keychain-Dumper) binary via SFTP and use its required entitlements; create the output directory before running.
  * ```bash
    mkdir -p /tmp/keychain
    ./keychain_dumper > keychain.txt
    ```
* The dumper's entitlements and device configuration determine its access; this is not the same caller context as the app.
{% endtab %}
{% endtabs %}

* Inspect the relevant item's accessibility/authentication policy, then use the [no-prompt query](#keychain-query-one-item-without-a-prompt) to test whether the actual item is usable in the relevant state.
* SQLite: use the read-only queries under [File and Database Inspection](#file-and-database-inspection).
* BinaryCookiesReader: `pip install binarycookiesreader`.

### File Protection: Attribute and Read Probe

* **Physical device, app context:** use the [Frida script-loading workflow](runtime-instrumentation.md#objection-session) in the process owning the file. Set the current container path for a known marker file; run the probe unlocked, then while locked where the app can execute. A suspended process producing no output is not a denied file read.
  * ```javascript
    function probeFileProtection() {
      ObjC.schedule(ObjC.mainQueue, function () {
        const path = '/var/mobile/Containers/Data/Application/REPLACE_UUID/Documents/protection-marker.txt';
        const manager = ObjC.classes.NSFileManager.defaultManager();
        const attributes = manager.attributesOfItemAtPath_error_(path, ptr(0));
        const protection = attributes === null ? 'attributes unavailable'
          : String(attributes.objectForKey_('NSFileProtectionKey'));
        const data = ObjC.classes.NSData.dataWithContentsOfFile_(path);
        console.log(JSON.stringify({ protection: protection,
          readable: data !== null, bytes: data === null ? 0 : Number(data.length()) }));
      });
    }
    probeFileProtection();
    ```
* In the Frida CLI REPL call `probeFileProtection()` after each state transition. Reopen the file on every probe; a descriptor retained before locking tests a different behavior.

| Observed class | Comparison | Expected behavior to check |
| --- | --- | --- |
| `NSFileProtectionComplete` | Unlocked versus locked, after protection keys become unavailable | New opens fail while locked. |
| `NSFileProtectionCompleteUnlessOpen` | Retained descriptor versus fresh open after lock | Existing open file may remain usable; that is not equivalent to a fresh read being allowed. |
| `NSFileProtectionCompleteUntilFirstUserAuthentication` | Reboot-before-first-unlock versus lock-after-first-unlock | Access after the first unlock can remain available while locked. |
| `NSFileProtectionNone` | Same marker, sensitive file and app requirement | No app-file protection class; device/storage encryption is a separate layer. |

* **Confirm:** the actual sensitive file's protection is weaker than its required availability and a fresh app-context read succeeds in that prohibited state. An attribute string alone or a privileged SSH/root read does not prove an ordinary app can read another app's files. Simulator/VM results do not establish physical-device key protection.

### Keychain: Query One Item Without a Prompt

* **Find selectors:** use the existing Keychain inspection commands to obtain the exact class/service/account/access group. This generic-password probe runs as the app and must match its actual item. Change the class/query for internet-password or key items; include the observed access group or synchronizable selector where required. Save the block as a host `.js` file and load it into the target process using the [Frida script-loading command](runtime-instrumentation.md#objection-session); call `probeKeychain()` in that same Frida REPL after each state transition.
  * ```javascript
    function probeKeychain() {
      ObjC.schedule(ObjC.mainQueue, function () {
        const constant = name => {
          const address = Module.findGlobalExportByName(name);
          if (address === null) throw new Error('Missing Security constant: ' + name);
          return new ObjC.Object(address.readPointer());
        };
        const query = ObjC.classes.NSMutableDictionary.dictionary();
        query.setObject_forKey_(constant('kSecClassGenericPassword'), constant('kSecClass'));
        query.setObject_forKey_('REPLACE_SERVICE', constant('kSecAttrService'));
        query.setObject_forKey_('REPLACE_ACCOUNT', constant('kSecAttrAccount'));
        query.setObject_forKey_(ObjC.classes.NSNumber.numberWithBool_(true), constant('kSecReturnData'));
        query.setObject_forKey_(constant('kSecUseAuthenticationUIFail'), constant('kSecUseAuthenticationUI'));
        const copy = new NativeFunction(Module.findGlobalExportByName('SecItemCopyMatching'),
          'int', ['pointer', 'pointer']);
        const release = new NativeFunction(Module.findGlobalExportByName('CFRelease'), 'void', ['pointer']);
        const output = Memory.alloc(Process.pointerSize);
        output.writePointer(ptr(0));
        const status = copy(query.handle, output);
        console.log('SecItemCopyMatching status=' + status + '; dataReturned=' + !output.readPointer().isNull());
        if (!output.readPointer().isNull()) release(output.readPointer());
      });
    }
    probeKeychain();
    ```
* **States:** establish the exact item is readable unlocked; rerun `probeKeychain()` while locked, after logout, and after the app's authentication window expires. After reboot, test before first unlock only with a process that can actually execute in that state; otherwise mark that case untested.
* **Interpret:** `0` = success; `-25300` = no matching item; `-25308` = interaction not allowed; `-25293` = authentication failed. A wrong service/access group producing "not found" is not evidence that lock protection works.
* **Authentication:** for an item intended to require fresh user presence, a successful no-prompt query after cancellation/expiry is a lead. Check any intentionally reusable `LAContext`/authentication window and perform the actual protected operation. A background refresh token intentionally readable after first unlock has a different requirement.
* **Nonexportable keys:** query/use the key reference and actual signing/decryption operation; failing to export raw key bytes is expected and does not prove auth-bound use works.
* **Lifecycle:** after logout/account switch, use retained credentials through the [API replay tests](traffic-analysis-and-tls.md#captured-request-replay). A stale item proves retention, not that the backend still accepts it.

### Pasteboard, Snapshots, and Account Residue

* Put a unique marker into a sensitive field, exercise copy/share/background, then use the existing pasteboard/screenshot/log commands. Read clipboard data from a separate test app as well as from the target; distinguish permission prompts and permitted user actions from unsolicited exposure.
* Open a sensitive screen, background the app and inspect its app-switcher preview; compare the preview with a deliberate screenshot, which is a different surface. Repeat after logout and account switch.
* Query a known A record in copied preferences/databases after switching to B and reopening the app. Confirm B can actually display/use A's data, or that retained credentials authorize a fresh A request, rather than reporting every leftover cache byte as live access.

## Legacy Tools

* [iRET](https://github.com/S3Jensen/iRET), [Cycript](https://www.cycript.org/) (inspection/injection/foreign-function calls), [QuickTime](https://support.apple.com/downloads/quicktime) (recording).
* [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump): release-specific Python/SSH setup; never hardcode credentials.
* Package sources: [Havoc](https://havoc.app/), [Shadow](https://ios.jjolano.me/), [opa334](https://opa334.github.io/). Legacy Radare2 and Akemi repositories are unavailable.
* Utilities: `wget`, `ps`, `sqlite3`, `unzip`, `dpkg`, BigBoss tools.
* For Objection session syntax, see [Runtime Instrumentation](runtime-instrumentation.md).
