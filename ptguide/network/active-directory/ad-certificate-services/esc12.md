# ESC12

{% hint style="info" %}
Steal CA private key from Yubico YubiHSM
{% endhint %}

## Why It Works

* Some organizations store the CA's private key on a hardware security module - specifically a **Yubico YubiHSM2** - for extra protection, using a Key Storage Provider (KSP) to hand off signing operations to the HSM.
* The CA server authenticates to the YubiHSM using an **auth key ID + password**, which is typically stored in a config file on the CA server (referenced by the KSP, e.g. `C:\Program Files\Yubico\YubiHSM Auth\` or a connector config) - often left in **cleartext or weakly protected**.
* If an attacker gains local access/shell on the CA server (via any other privesc chain) and can read that config, they can authenticate directly to the YubiHSM themselves and use the CA's private key to **sign arbitrary certificates**, or simply export/duplicate the CA's issuance capability - equivalent to full CA (and therefore domain) compromise.
* This is a narrow, environment-specific vector - it only applies where a YubiHSM-backed CA is in use, but is fully game-over when it applies since the CA private key itself is the target, not a downstream certificate.

## Prerequisites

* CA is configured to use a YubiHSM2 for private key storage.
* Local access to the CA server (via any prior foothold) sufficient to read the YubiHSM connector/auth configuration files.

## Enumerate

{% code lineNumbers="true" %}
```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Certipy flags ESC12 when it detects a YubiHSM-backed CSP/KSP on the CA
```
{% endcode %}

## Exploit

{% hint style="info" %}
This exploit runs directly on the (Windows) CA server itself once you have local access, so there's no Linux/Windows tool choice here - `yubihsm-shell` ships as a cross-platform binary (`yubihsm-shell.exe` on Windows, `yubihsm-shell` on Linux) with identical syntax on both.
{% endhint %}

{% code lineNumbers="true" %}
```bat
REM On the CA server, locate the YubiHSM auth key/password (commonly in the connector config or KSP registration)
type "C:\Program Files\Yubico\YubiHSM Auth\<config-file>"
REM Use the recovered auth key ID + password with the YubiHSM shell/PKCS11 tooling to authenticate and use the CA's private key
yubihsm-shell.exe -a get-pseudo-random --authkey <id> --password <recovered-password>
```
{% endcode %}
