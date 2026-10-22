# Signing and App Patching

{% hint style="info" %}
Use authorized devices/builds and test accounts. Isolate the lab, protect evidence, and restore it afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Gadget must match the host's **exact Frida version**. You need a valid signing identity, a matching profile, and a suitable unencrypted executable. See the [Mandatory Preflight](preflight-and-lab-setup.md#mandatory-preflight).
{% endhint %}

## Signing and App Patching

### Signing

```sh
security find-identity -v -p codesigning
applesign -L
applesign -i <signing-identity> -m <embedded.mobileprovision> <app.ipa>
```

Install Node.js/npm first, then [applesign](https://github.com/nowsecure/node-applesign): `npm install -g applesign` (not `appliesign`). Homebrew is one way to install Node.js on macOS. Verify `node --version` and `npm --version`, then check `applesign --help` for release-specific input/options.

### Non-Jailbroken App Patching

Embed Gadget and re-sign a suitable IPA:

```sh
objection patchipa --help
objection patchipa --source <app.ipa> --codesign-signature <signing-identity> --provision-file <embedded.mobileprovision> --gadget-version <frida-version>
```

* Pin Gadget to the host `frida --version` output; confirm `--gadget-version` in installed help. Automatic latest-Gadget selection can mismatch an older client.
* Requires compatible signing assets and a suitable unencrypted executable; not every Store IPA works.
* `--codesign-signature` (`-c`), `--provision-file` (`-P`): check help and [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py).
* `security find-identity` lists identities; it does not create profiles or determine expiry.
* Follow current signing requirements; preserve originals and do not redistribute modified apps.
