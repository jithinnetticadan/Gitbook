# R-Services - T512,513,514

{% hint style="info" %}
R-Services are a suite of services hosted to enable remote access or issue commands between Unix hosts over TCP/IP. r-services transmit information from client to server(and vice versa.) over the network in an unencrypted format, making it possible for attackers to intercept network traffic (passwords, login information, etc.) by performing man-in-the-middle (`MITM`) attacks.
{% endhint %}

### r-commands

<table data-header-hidden><thead><tr><th width="79.85711669921875">CMD</th><th width="103">Service Daemon</th><th width="77.71417236328125">Port</th><th>Description</th></tr></thead><tbody><tr><td><code>rcp</code></td><td><code>rshd</code></td><td>514</td><td>Copy a file or directory bidirectionally from the local system to the remote system (or vice versa) or from one remote system to another. It works like the <code>cp</code> command on Linux but provides <code>no warning to the user for overwriting existing files on a system</code>.</td></tr><tr><td><code>rsh</code></td><td><code>rshd</code></td><td>514</td><td>Opens a shell on a remote machine without a login procedure. Relies upon the trusted entries in the <code>/etc/hosts.equiv</code> and <code>.rhosts</code> files for validation.</td></tr><tr><td><code>rexec</code></td><td><code>rexecd</code></td><td>512</td><td>Enables a user to run shell commands on a remote machine. Requires authentication through the use of a <code>username</code> and <code>password</code> through an unencrypted network socket. Authentication is overridden by the trusted entries in the <code>/etc/hosts.equiv</code> and <code>.rhosts</code> files.</td></tr><tr><td><code>rlogin</code></td><td><code>rlogind</code></td><td>513</td><td>Enables a user to log in to a remote host over the network. It works similarly to <code>telnet</code> but can only connect to Unix-like hosts. Authentication is overridden by the trusted entries in the <code>/etc/hosts.equiv</code> and <code>.rhosts</code> files.</td></tr></tbody></table>

### Footprinting

{% tabs %}
{% tab title="Nmap" %}
{% code lineNumbers="true" %}
```shellscript
sudo nmap -sV -sC -p 512,513,514 <IP>
```
{% endcode %}
{% endtab %}
{% endtabs %}

### **Enumeration**

{% tabs %}
{% tab title="r-commands" %}
{% code lineNumbers="true" %}
```shellscript
Logging in Using Rlogin
rlogin <IP> -l <username>
Listing Authenticated Users
rwho
Listing Authenticated Users
rusers -al <IP>
```
{% endcode %}
{% endtab %}
{% endtabs %}
