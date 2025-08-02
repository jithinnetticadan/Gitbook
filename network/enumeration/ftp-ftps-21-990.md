# FTP/FTPS - 21,990

#### Banner Grab

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" fullWidth="false" %}
```
use auxiliary/scanner/ftp/ftp_version
set rhosts <ip>
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
{% code fullWidth="false" %}
```
nmap -p 21 -sV <ip>
```
{% endcode %}
{% endtab %}
{% endtabs %}

#### Anonymous Login

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" fullWidth="false" %}
```
use auxiliary/scanner/ftp/anonymous
set rhosts <ip>
services -p 21 -R
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
{% code fullWidth="false" %}
```
nmap --script ftp-anon -p 21 <ip>
```
{% endcode %}
{% endtab %}

{% tab title="Terminal" %}
{% code fullWidth="false" %}
```
ftp://anonymous:anonymous@<ip>
```
{% endcode %}
{% endtab %}
{% endtabs %}

#### Unauth Enum

{% code fullWidth="false" %}
```
sudo nmap -sV -p21 --script "ftp-*" -A <ip>
```
{% endcode %}

#### Brute Force

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" fullWidth="false" %}
```
use auxiliary/scanner/ftp/ftp_login
set rhosts <ip>
services -p 21 -R
set pass_file
set user_file
```
{% endcode %}
{% endtab %}

{% tab title="Hydra" %}
{% code fullWidth="false" %}
```
hydra -t 1 -l {Username} -P {Passwordlist} -vV {IP} ftp
```
{% endcode %}
{% endtab %}
{% endtabs %}

#### FTP Bounce Port Scanner

```
use auxiliary/scanner/portscan/ftpbounce
```

