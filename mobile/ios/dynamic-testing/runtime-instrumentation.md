# Runtime Instrumentation

* Host `frida`, device server, and Gadget must use the **same exact Frida version**.

## Objection Session

* <pre class="language-bash" data-line-numbers><code class="lang-bash">frida-ps -Uai
  frida -U -n &#x3C;app-process-name>
  frida-trace -U -m '*[NSURLRequest *]' &#x3C;app-process-name>
  objection --name &#x3C;app-process-name> start
  </code></pre>
* Objective-C selectors: `-` instance method, `+` class method.
* Find identifiers: `frida-ps -Uai | grep '<app-name-fragment>'`.
* Attach by process name; spawn by bundle ID. Gadget may expose a different target name.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">objection version
  objection --help
  objection start --help
  objection --name &#x3C;bundle-id> --spawn start
  objection --serial &#x3C;device-serial> --name &#x3C;app-process-name> start
  objection --local --name &#x3C;simulator-process-name> start
  objection --name &#x3C;app-process-name> start --startup-script &#x3C;script.js>
  objection --name &#x3C;app-process-name> run 'ios info binary'
  </code></pre>

<table><thead><tr><th width="153.0001220703125">Option/Mode</th><th>Use</th></tr></thead><tbody><tr><td>Global flags</td><td><code>--name</code>, <code>--serial</code>, <code>--local</code>, <code>--spawn</code>, <code>--no-pause</code> go <strong>before</strong> <code>start</code>/<code>run</code>.</td></tr><tr><td>Startup flags</td><td>Go <strong>after</strong> <code>start</code>; verify <code>objection start --help</code>.</td></tr><tr><td><code>--local</code></td><td>iOS Simulator, not a physical device; compatible instrumentation required.</td></tr><tr><td><code>--no-pause</code></td><td>Immediate resume; omit for early hooks needing a paused spawn.</td></tr><tr><td><code>run</code></td><td>One-shot; do not assume hooks survive exit. Use <code>start</code> for monitoring.</td></tr></tbody></table>

## Classes and Hooks

* <pre class="language-text" data-line-numbers><code class="lang-text">env
  ios hooking list classes
  ios hooking list class_methods &#x3C;class-name>
  ios hooking watch &#x3C;class-name>
  ios hooking watch '-[&#x3C;class-name> &#x3C;selector:>]' --dump-args --dump-return --dump-backtrace
  ios sslpinning disable
  ios jailbreak disable
  </code></pre>
* Use `+` for class methods. `--dump-args` may fail on non-object arguments; inspect types first.
* **Frida 17+:** current CLI tools supply the ObjC bridge; custom agents need bundled `frida-objc-bridge`. See [bridge setup](https://frida.re/docs/bridges/).

## Clipboard, Screenshots, Memory, and SQLite

* <pre class="language-text" data-line-numbers><code class="lang-text">ios pasteboard monitor
  ios nsuserdefaults get
  ios nsurlcredentialstorage dump
  ios plist cat Info.plist
  ios plist cat &#x3C;app-bundle-path>/Info.plist
  ios keychain dump
  ios monitor crypto
  ios info binary
  ios cookies get
  memory dump all &#x3C;output-file>.dmp
  </code></pre>
* **Files and SQLite, inside Objection:**
  * ```text
    filesystem cat <path-to-file>
    filesystem download <path-to-file>
    sqlite connect <database-file>
    ```
* `ios monitor crypto` monitors supported CommonCrypto calls, not all cryptography. [Command registry](https://github.com/sensepost/objection/blob/master/objection/console/commands.py).
* Detection Bypass: Hestia, Shadow, Objection.
* Alternatives: [RMS](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), [Grapefruit](https://github.com/ChiChou/grapefruit).

### Startup Hooks

* <pre class="language-bash" data-line-numbers><code class="lang-bash">objection --name &#x3C;app-process-name> start --startup-command 'ios jailbreak disable'
  objection --name &#x3C;app-process-name> start --startup-command 'ios sslpinning disable'
  </code></pre>

## r2frida

* **Host dependencies:** radare2 and a compatible r2frida plugin; radare2 alone does not install the plugin.
* Follow the plugin's current installation instructions and command syntax.
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">r2 frida://spawn/usb//&#x3C;bundle-id>
    :i?
    :ic~&#x3C;class-or-string>
    :dtf &#x3C;function-address>
    </code></pre>
* [r2frida usage](https://github.com/nowsecure/r2frida#usage)
* Run the first line on the host, then `:` commands inside r2. Use `:dc` to resume a paused spawn; verify plugin syntax and active-process addresses.
* r2frida embeds its own Frida core.
* Inspect dumps with `strings <dump-file>`
