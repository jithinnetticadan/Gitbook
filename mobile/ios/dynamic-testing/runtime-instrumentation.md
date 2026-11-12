# Runtime Instrumentation

* Host `frida`, device server, and Gadget must use the **same exact Frida version**.

## Objection Session

* **On the Mac:** check the host version, then list installed/running apps. Use the resulting process name for attach and bundle identifier for spawn; start the app if it is not running.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">frida --version
  python -m pip show frida frida-tools objection
  frida-ps -Uai
  </code></pre>

{% tabs %}
{% tab title="Frida" %}
* **Mac terminal:** attach or trace the observed selector in the running process.
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">frida -U -n &#x3C;app-process-name>
  frida-trace -U -m '*[NSURLRequest *]' &#x3C;app-process-name>
  </code></pre>
* **Attach and load one of the Frida scripts below:** put the selected script in the specified host file, then trigger its target app flow.
  * ```bash
    frida -U -n '<app-process-name>' -l '<hook.js>'
    ```
{% endtab %}
{% tab title="Objection" %}
* **Mac terminal:** start the session by process name or use a bundle ID for spawn.
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">objection --name &#x3C;app-process-name> start
    objection version
    objection --help
    objection start --help
    objection --name &#x3C;bundle-id> --spawn start
    objection --serial &#x3C;device-serial> --name &#x3C;app-process-name> start
    objection --local --name &#x3C;simulator-process-name> start
    objection --name &#x3C;app-process-name> start --startup-script &#x3C;script.js>
    objection --name &#x3C;app-process-name> run 'ios info binary'
    </code></pre>
* **Objection console:** find and watch the actual class/selector used by the app.
  * ```text
    ios hooking list classes
    ios hooking list class_methods <class-name>
    ios hooking watch '-[<class-name> <selector:>]' --dump-args --dump-return --dump-backtrace
    ```
{% endtab %}
{% tab title="RMS" %}
* **Mac terminal:** start the installed RMS interface with the device's Frida server running.
  * ```bash
    frida-ps -U
    rms
    ```
* Open `http://127.0.0.1:5491/`, choose the app and use its class/method dump and hook/trace views for the observed selector. RMS uses Frida in the app process.
{% endtab %}
{% tab title="Grapefruit" %}
* **Mac terminal:** start the installed Grapefruit interface with a compatible Frida connection; current upstream requires Node.js 22.18+.
  * ```bash
    frida-ps -U
    igf
    ```
* Select the app, then inspect its Objective-C classes/methods and trace the observed selector in the runtime-hooking view.
{% endtab %}
{% endtabs %}

* Objective-C selectors: `-` instance method, `+` class method.
* Find identifiers: `frida-ps -Uai | grep '<app-name-fragment>'`.
* Attach by process name; spawn by bundle ID. Gadget may expose a different target name.

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
* Detection Bypass: Hestia, Shadow, Objection.
* Alternatives: [RMS](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), [Grapefruit](https://github.com/ChiChou/grapefruit).

## Cryptographic Parameters and Tampering

{% tabs %}
{% tab title="Objection" %}
* **Mac terminal:** attach to the running app with a working Frida connection.
  * ```bash
    frida-ps -Uai
    objection --name '<app-process-name>' start
    ```
* **Objection console:** monitor supported CommonCrypto calls while exercising the test operation.
  * ```text
    ios monitor crypto
    ```
{% endtab %}
{% tab title="Frida" %}
* **Frida CLI:** load this script through the session workflow above. It observes one-shot `CCCrypt` and `CCKeyDerivationPBKDF`; it does not cover streaming `CCCryptor*` or CryptoKit. Key/salt fingerprints identify repeated inputs without printing raw keys/passwords.
  * ```javascript
    const hex = address => Array.from(new Uint8Array(address.readByteArray(32)),
      value => value.toString(16).padStart(2, '0')).join('');
    const digestAddress = Module.findGlobalExportByName('CC_SHA256');
    if (digestAddress === null) throw new Error('CC_SHA256 not loaded');
    const sha256 = new NativeFunction(digestAddress, 'pointer', ['pointer', 'uint', 'pointer']);
    const fingerprint = (address, length) => {
      if (address.isNull() || length === 0) return null;
      const output = Memory.alloc(32);
      sha256(address, length, output);
      return hex(output);
    };
    const crypt = Module.findGlobalExportByName('CCCrypt');
    if (crypt !== null) Interceptor.attach(crypt, {
      onEnter(args) {
        const algorithm = args[1].toInt32();
        const options = args[2].toInt32();
        this.record = { api: 'CCCrypt', operation: args[0].toInt32(), algorithm: algorithm,
          options: options, keyBytes: args[4].toUInt32(), inputBytes: args[7].toUInt32(),
          keyHash: fingerprint(args[3], args[4].toUInt32()) };
        if (algorithm === 0 && (options & 2) === 0) {
          this.record.aesCbcIv = args[5].isNull() ? 'zero IV (implicit)'
            : Array.from(new Uint8Array(args[5].readByteArray(16)),
              value => value.toString(16).padStart(2, '0')).join('');
        }
      },
      onLeave(result) {
        this.record.status = result.toInt32();
        console.log(JSON.stringify(this.record));
      }
    });
    const derive = Module.findGlobalExportByName('CCKeyDerivationPBKDF');
    if (derive !== null) Interceptor.attach(derive, {
      onEnter(args) {
        this.record = { api: 'CCKeyDerivationPBKDF', algorithm: args[0].toInt32(),
          saltBytes: args[4].toUInt32(), saltHash: fingerprint(args[3], args[4].toUInt32()),
          prf: args[5].toInt32(), rounds: args[6].toUInt32(), keyBytes: args[8].toUInt32() };
      },
      onLeave(result) {
        this.record.status = result.toInt32();
        console.log(JSON.stringify(this.record));
      }
    });
    ```
{% endtab %}
{% tab title="Grapefruit" %}
* **Mac terminal:** start the installed interface with the device's Frida server running.
  * ```bash
    frida-ps -Uai
    igf
    ```
* Select the app, open its cryptographic API monitoring view and trigger the operation. Record the observed algorithm, parameters and output associated with the actual test field.
{% endtab %}
{% endtabs %}

* Trigger two encryptions of different test markers and correlate the calls with the stored/transmitted field. Objection's monitor covers supported CommonCrypto calls; the Frida script's scope is stated in its tab.
* **Interpret:** `CCCrypt` operation `0` encrypts, `1` decrypts; algorithm `0` is AES. Options bit `2` means ECB; without it the one-shot AES API uses CBC, and a null IV means zero bytes. Compare successful encryption calls only; repeated decryption naturally reuses the saved IV. PKCS#7 padding is options bit `1`, not authentication.
* **KDF test:** create two independent records/accounts with the same test password. Compare salt hashes, PRF, rounds and output length; then repeat with a different password. Equal per-record salts indicate reuse, but iteration adequacy needs the actual algorithm, offline exposure and current password-KDF guidance. A SHA-256 key fingerprint changing does not establish a strong derivation.
* **Ciphertext mutation, Node.js REPL on macOS:** select an offset inside the ciphertext portion of the actual Base64 envelope, not its IV/version/tag header; send/store the changed field through the same flow.
  * ```javascript
    const encrypted = Buffer.from('REPLACE_BASE64_CIPHERTEXT', 'base64');
    const offset = 0;
    encrypted[offset] ^= 1;
    console.log(encrypted.toString('base64'));
    ```
* **Confirm:** the changed ciphertext is accepted as authentic and alters a protected value/action. A failed MAC/tag, padding error or rejected parser input is not accepted tampering. Correlate a hardcoded/weakly derived key with this actual consumer rather than reporting every crypto call.

## Biometric Callback and Protected Operation

* **Baseline:** trigger the feature and compare success, Cancel, failed biometrics and passcode fallback. Identify whether the app calls `evaluatePolicy` or an access-control/key operation. Policy `1` is biometrics; policy `2` permits device-owner authentication including passcode fallback.
* **Frida script:** initially observe only. Set `globalThis.forceBiometricSuccess = true` in the same Frida REPL and cancel the next prompt to test a client callback that trusts a success Boolean. No private key or authentication context is granted by this override.
  * ```javascript
    globalThis.forceBiometricSuccess = false;
    const pendingReplies = new Set();
    const evaluate = ObjC.classes.LAContext['- evaluatePolicy:localizedReason:reply:'];
    if (!evaluate) throw new Error('evaluatePolicy unavailable; inspect actual authentication path');
    Interceptor.attach(evaluate.implementation, {
      onEnter(args) {
        const policy = args[2].toInt32();
        const reply = new ObjC.Block(args[4]);
        const original = reply.implementation;
        pendingReplies.add(reply);
        reply.implementation = function (success, error) {
          console.log('policy=' + policy + '; actualSuccess=' + success +
            '; override=' + globalThis.forceBiometricSuccess);
          try {
            return original(globalThis.forceBiometricSuccess ? true : success,
              globalThis.forceBiometricSuccess ? ptr(0) : error);
          } finally { pendingReplies.delete(reply); }
        };
      }
    });
    ```
* **Confirm:** after the forced callback, perform the same protected export/read/payment/signing operation. A screen transition alone is only a UI-gate bypass. If Keychain/SEP use still requires authentication, record that enforced boundary rather than claiming hardware-key bypass.
* **Key-bound flow:** `evaluateAccessControl`/`SecKey`/Keychain ACL paths may not invoke this selector. Use the [no-prompt Keychain test](data-storage-and-privacy.md#keychain-query-one-item-without-a-prompt), inspect the actual key access-control flags, and compare the real signing/decryption result after cancellation/expiry. Repeat enrollment/fallback changes only against the item's configured policy.

## Runtime Memory Search

* Exercise the relevant login/payment flow with a unique test marker, then search the running app's memory for that marker and associated credential values.

{% tabs %}
{% tab title="Objection" %}
* **Mac terminal:** attach to the running process.
  * ```bash
    frida-ps -Uai
    objection --name '<app-process-name>' start
    ```
* **Objection console:**
  * ```text
    memory search <test-marker> --string
    memory dump all <output-file>.dmp
    ```
{% endtab %}
{% tab title="fridump3" %}
### Optional fridump3 Memory Capture

* **Prerequisite:** [host tool setup](../setup.md#host-frida-and-objection), Frida 17+, running target app.
* **USB, on the Mac:**

  * ```bash
    frida-ps -Ua
    fridump3 -u -s -o ./memory-capture "<running-process-name>"
    ```

* **Network endpoint variant:**

  * ```bash
    fridump3 -H <forwarded-host>:<frida-port> -s -o ./memory-capture "<running-process-name>"
    ```

* Use the process name, not the bundle ID. `-s` extracts strings; `-o` selects the output directory. [CLI reference](https://github.com/Xenorf/fridump3.1).
* **macOS Terminal:** search generated strings for the test value.
  * ```bash
    grep -RniF '<test-marker>' './memory-capture'
    ```
{% endtab %}
{% tab title="Grapefruit" %}
* **Mac terminal:** start the installed interface and select the running app.
  * ```bash
    frida-ps -Uai
    igf
    ```
* Use the memory scanner to search the marker in the selected process and inspect the matching region.
{% endtab %}
{% endtabs %}

* Repeat after logout or expiry; determine whether a retained credential remains usable and what access is needed to read the process.

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
