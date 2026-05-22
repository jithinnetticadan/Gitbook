# AD Certificate Services

{% hint style="info" %}
* Enables use of Public Key Infrastructure (PKI) in active directory forest.
* Helps in authenticating users and machines, encrypting and  &#x20;signing documents, filesystem, emails and more.
* Server Role that allows you to build a public key  &#x20;infrastructure (PKI) and provide public key cryptography, digital  &#x20; certificates, and digital signature capabilities for your organization.
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
