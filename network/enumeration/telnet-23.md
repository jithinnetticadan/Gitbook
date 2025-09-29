# Telnet - 23

#### Brute Force

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" %}
```bash
use auxiliary/scanner/telnet/telnet_login
set rhosts <ip>
services -p 23 -R
set username <>
set password <>
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
```
```
{% endtab %}
{% endtabs %}
