# FTP/FTPS - 21,990

#### Banner Grab

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" fullWidth="true" %}
```
use auxiliary/scanner/ftp/ftp_version
set rhosts <ip>
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
{% code fullWidth="true" %}
```
nmap -p 2-sV <ip>
```
{% endcode %}
{% endtab %}
{% endtabs %}

#### Anonymous Login

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" fullWidth="true" %}
```
use auxiliary/scanner/ftp/anonymous
set rhosts <ip>
services -p 21 -R
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
{% code fullWidth="true" %}
```
nmap --script ftp-anon -p 21 <ip>
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
sudo nmap -sV -p21 --script ftp-* -A <ip>
```
{% endcode %}

#### Brute Force

<pre data-line-numbers data-full-width="true"><code><strong>use auxiliary/scanner/ftp/ftp_login
</strong><strong>set rhosts &#x3C;ip>
</strong><strong>services -p 21 -R
</strong><strong>set pass_file
</strong><strong>set user_file
</strong></code></pre>

#### FTP Bounce Port Scanner

```
use auxiliary/scanner/portscan/ftpbounce
```

