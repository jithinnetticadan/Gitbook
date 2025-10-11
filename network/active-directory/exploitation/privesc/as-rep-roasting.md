# AS-REP Roasting

{% hint style="info" %}
AS-REP Roasting dumps user account hashes that have Kerberos pre-authentication disabled. Unlike Kerberoasting, these users do not need to be service accounts—the only requirement is that the “Do not require Kerberos pre-authentication” flag (UF\_DONT\_REQUIRE\_PREAUTH) is set on the user account.

During standard Kerberos authentication, the user’s hash encrypts a timestamp, which the Key Distribution Center (KDC) decrypts to verify the user’s identity. However, if pre-authentication is disabled, the KDC skips this verification step and returns an encrypted AS-REP blob without confirming the user’s identity. This blob can then be captured and cracked offline to recover the user’s password.
{% endhint %}

### Identifying Vulnerable Accounts

* **Tools**
  * [Rubeus](https://github.com/GhostPack/Rubeus) _(Windows only) -_ `Rubeus.exe asreproast`&#x20;
  * [Impacket’s GetNPUsers.py](https://github.com/fortra/impacket) _(Linux/Windows) -_ `GetNPUsers.py <domain>/ -dc-ip <ip> -usersfile users.txt -format hashcat -outputfile hashes.txt -no-pass`&#x20;

### Cracking Password Hashes and Accessing the Network

* **Tools**
  * [Hashcat](https://hashcat.net/hashcat/) _(Cross-platform) -_ `hashcat -m 18200 hashes.txt wordlist.txt`&#x20;
  * Authenticate as these compromised users, request Kerberos tickets, or directly access other network resources.

### Mitigations

* Enforce Kerberos pre-authentication for all user accounts
* Strong, complex passwords slow down offline cracking
* Monitor anomalous AS-REP requests on the KDC

### Key Takeaways

* AS-REP Roasting is a low-noise, unauthenticated Kerberos attack
* Rubeus simplifies discovery on Windows; GetNPUsers.py offers manual control
* Success depends on password strength and proper pre-auth enforcement

