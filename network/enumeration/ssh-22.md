# SSH - 22

#### Brute Force

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" fullWidth="false" %}
```bash
use auxiliary/scanner/ssh/ssh_login
set rhosts <ip>
services -p 22 -R
set username <>
set password <>
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
```bash
nmap -p 22 --script ssh-brute <ip>
nmap -p 22 --script "ssh*" <ip>
```
{% endtab %}
{% endtabs %}



