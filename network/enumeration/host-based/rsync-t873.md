# Rsync - T873

{% hint style="info" %}
Tool for locally and remotely copying files. It can be used to copy files locally on a given machine and to/from remote hosts. Delta-transfer algorithm reduces the amount of data transmitted over the network when a version of the file already exists on the destination host. It does this by sending only the differences between the source files and the older version of the files that reside on the destination server. It is often used for backups and mirroring. It finds files that need to be transferred by looking at files that have changed in size or the last modified time. IIt can be configured to use SSH for secure file transfers by piggybacking on top of an established SSH server connection.
{% endhint %}

### Footprinting

{% tabs %}
{% tab title="Metasploit" %}

{% endtab %}

{% tab title="Nmap" %}
{% code lineNumbers="true" %}
```shellscript
sudo nmap -sV -sC -p 873 <IP>
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Enumeration

{% tabs %}
{% tab title="Terminal" %}
{% code lineNumbers="true" %}
```shellscript
Probing for Accessible Shares
nc -nv <IP> 873
#list
```
{% endcode %}
{% endtab %}

{% tab title="rsync" %}
{% code lineNumbers="true" %}
```shellscript
rsync -av --list-only rsync://<IP>/<sharename>
Sync all files loaclly
rsync -av rsync://<IP>/<sharename>
```
{% endcode %}
{% endtab %}
{% endtabs %}
