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
* {% code lineNumbers="true" %}
  ```batch
  Certify.exe cas
  //Enumerate the templates
  Certify.exe find
  //Enumerate vulnerable templates
  Certify.exe find /vulnerable
  ```
  {% endcode %}
