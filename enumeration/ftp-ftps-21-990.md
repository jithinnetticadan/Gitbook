# FTP/FTPS - 21,990

#### Anonymous Login

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" fullWidth="true" %}
```
use auxiliary/scanner/ftp/anonymous
set rhosts <ip>
service -p 21 -R
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
{% code fullWidth="true" %}
```
nmap --script ftp-* -p 21 <ip>
```
{% endcode %}
{% endtab %}

{% tab title="Terminal" %}
{% code fullWidth="true" %}
```
ftp://anonymous:anonymous@<ip>
```
{% endcode %}
{% endtab %}
{% endtabs %}

#### Unauth Enum

{% code fullWidth="true" %}
```
sudo nmap -sV -p21 -sC -A <ip>
```
{% endcode %}
