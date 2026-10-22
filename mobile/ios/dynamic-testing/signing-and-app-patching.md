# Signing and App Patching

{% hint style="info" %}
* Use authorized devices/builds and test accounts; replace command placeholders before use.
* Isolate the lab, protect evidence, and restore it afterward.
{% endhint %}

{% hint style="warning" %}
* **Version dependency:** Gadget must match the host's **exact Frida version**.
* **Signing prerequisites:** valid signing identity, matching profile, and suitable unencrypted executable.
* Complete [Mandatory Preflight](preflight-and-lab-setup.md#mandatory-preflight).
{% endhint %}

## Signing and App Patching

### Signing

```sh
security find-identity -v -p codesigning
applesign -L
applesign -i <signing-identity> -m <embedded.mobileprovision> <app.ipa>
```

* **Dependencies:** install Node.js/npm first; Homebrew is one macOS option.
* Verify `node --version` and `npm --version`.
* Install [applesign](https://github.com/nowsecure/node-applesign): `npm install -g applesign` (not `appliesign`).
* Check `applesign --help` for release-specific inputs/options.

### Non-Jailbroken App Patching

* Embed Gadget and re-sign a suitable IPA:

```sh
objection patchipa --help
objection patchipa --source <app.ipa> --codesign-signature <signing-identity> --provision-file <embedded.mobileprovision> --gadget-version <frida-version>
```

* Pin Gadget to the host `frida --version` output; confirm `--gadget-version` in installed help. Automatic latest-Gadget selection can mismatch an older client.
* Requires compatible signing assets and a suitable unencrypted executable; not every Store IPA works.
* `--codesign-signature` (`-c`), `--provision-file` (`-P`): check help and [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py).
* `security find-identity` lists identities; it does not create profiles or determine expiry.
* Follow current signing requirements; preserve originals and do not redistribute modified apps.
