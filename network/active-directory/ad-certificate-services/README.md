# AD Certificate Services

{% hint style="info" %}
* Enables use of Public Key Infrastructure (PKI) in active directory forest.
* Helps in authenticating users and machines, encrypting and
  &#x20;signing documents, filesystem, emails and more.
* Server Role that allows you to build a public key
  &#x20;infrastructure (PKI) and provide public key cryptography, digital
  &#x20; certificates, and digital signature capabilities for your organization.
* CA - The certification authority that issues certificates. The server with AD CS role (DC or separate) is the CA.
* Certificate - Issued to a user or machine and can be used for authentication, encryption, signing etc.
* CSR - Certificate Signing Request made by a client to the CA to request a certificate.
* Certificate Template - Defines settings for a certificate. Contains information like - enrolment permissions, EKUs, expiry etc.
* EKU OIDs - Extended Key Usages Object Identifiers. These dictate the use of a certificate template (Client authentication, Smart Card Logon, SubCA etc.)
{% endhint %}

<details>

<summary><strong>Workflow</strong></summary>

<figure><img src="../../../.gitbook/assets/ADCS Flow.png" alt=""><figcaption></figcaption></figure>

</details>

### Enumerate

* [Certify](https://github.com/GhostPack/Certify)
* [Certipy](https://github.com/ly4k/Certipy)
* <pre class="language-batch" data-line-numbers><code class="lang-batch">Certify.exe cas
  //Enumerate the templates
  Certify.exe find
  //Enumerate vulnerable templates
  Certify.exe find /vulnerable

  </code></pre>

### No PKINIT? <a href="#no-pkinit" id="no-pkinit"></a>

{% hint style="info" %}
Attacker may be able to obtain a certificate but be unable to use it for pre-authentication as specific victims (e.g., a domain controller machine account) due to the KDC not supporting the appropriate EKU. The tool [PassTheCert](https://github.com/AlmondOffSec/PassTheCert/) was created for such situations. It can be used to authenticate against LDAPS using a certificate and perform various attacks (e.g., changing passwords or granting DCSync rights). This attack is outside the scope of this module but is worth reading about [here](https://offsec.almond.consulting/authenticating-with-certificates-when-pkinit-is-not-supported.html).
{% endhint %}

### Tools

* [certi](https://github.com/zer1t0/certi)

## Chaining ESC Techniques

{% hint style="info" %}
More often one ESC gives you the *primitive* needed to trigger another. Common real-world combos:
{% endhint %}

* **ESC4 -> ESC1** - You don't have a directly vulnerable template, but you have `GenericAll`/`WriteDacl` over a template's AD object (ESC4). Use that write access to flip the template's flags (`ENROLLEE_SUPPLIES_SUBJECT`, add Client Auth EKU), turning it into an ESC1 condition, then exploit it as ESC1.
* **ESC7 -> ESC6** - You hold the `Manage CA` role (ESC7) but no template is independently vulnerable. Use `Manage CA` rights to enable `EDITF_ATTRIBUTESUBJECTALTNAME2` on the CA, which is exactly the ESC6 condition, then request an arbitrary-SAN cert from any Client Auth template.
* **ESC7 -> Approval Bypass** - You hold `Manage Certificates` (ESC7) and a template requires manager approval before issuance. Submit a request as yourself (with an admin SAN if also ESC1-eligible), then use your Certificate Manager rights to approve your own pending request, bypassing the human-review control entirely.
* **ESC8/ESC11 as an entry point into ESC9/ESC10/ESC16** - Coercion + NTLM relay (ESC8/ESC11) gets you a machine account certificate, which can be used for an initial DCSync. If that path is blocked (relay hardened, EPA enabled), check whether the DC(s) still have weak `StrongCertificateBindingEnforcement`/Schannel mapping (ESC9/ESC10/ESC16) - a UPN-spoof attack against a domain user account you already control may achieve the same admin-impersonation outcome without needing coercion at all.
* **ESC13 as a stealthier alternative to ESC1** - if a privileged-group-linked issuance policy exists, enrolling for it (ESC13) leaves a less obvious trail than an ESC1 SAN-spoofed "administrator" certificate, since no altered identity field is required - worth checking `certipy find` output for OID-to-group links before defaulting to ESC1/ESC3.
* **ESC14 as a persistence mechanism** - after achieving DA via any of the above, writing to a target's `altSecurityIdentities` (ESC14) is a durable, template-independent backdoor: it survives template hardening/patches since it doesn't rely on any AD CS misconfiguration at all.

