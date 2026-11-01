# Signing and App Patching

{% hint style="warning" %}
* **Version dependency:** Gadget must match the host's **exact Frida version**.
* **Signing prerequisites:** valid signing identity, matching profile, and suitable unencrypted executable.
{% endhint %}

## Signing

* **Dependencies:** install Node.js/npm first; Homebrew is one macOS option.
* Verify `node --version` and `npm --version`.
* Install [applesign](https://github.com/nowsecure/node-applesign): `npm install -g applesign`
* Check `applesign --help` for release-specific inputs/options.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">security find-identity -v -p codesigning
  applesign -L
  applesign -i &#x3C;signing-identity> -m &#x3C;embedded.mobileprovision> &#x3C;app.ipa>
  </code></pre>

## Non-Jailbroken App Patching

* Embed Gadget and re-sign a suitable IPA:
  * ```bash
    objection patchipa --help
    objection patchipa --source <app.ipa> --codesign-signature <signing-identity> --provision-file <embedded.mobileprovision> --gadget-version <frida-version>
    ```
* Pin Gadget to the host `frida --version` output; confirm `--gadget-version` in installed help. Automatic latest-Gadget selection can mismatch an older client.
* Requires compatible signing assets and a suitable unencrypted executable; not every Store IPA works.
* **Development signing:** enable Developer Mode on iOS 16+; confirm the profile permits the device and required entitlements.
* **Non-jailbroken hooks:** launch with a compatible debugger before Gadget loads to permit `Interceptor` hooks. Gadget's `code_signing: "required"` mode can run without that relaxation, but disables `Interceptor`; Objection hooks may be unavailable. [Gadget requirements](https://frida.re/docs/gadget/).
* `--codesign-signature` (`-c`), `--provision-file` (`-P`): check help and [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py).
* `security find-identity` lists identities; it does not create profiles or determine expiry.
