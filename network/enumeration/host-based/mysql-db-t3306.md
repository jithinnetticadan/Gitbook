# MySQL DB - T3306

### Default Configuration <a href="#default-configuration" id="default-configuration"></a>

* `cat /etc/mysql/mysql.conf.d/mysqld.cnf | grep -v "#" | sed -r`

### Dangerous Settings <a href="#dangerous-settings" id="dangerous-settings"></a>

* <table data-header-hidden><thead><tr><th width="162.14276123046875">Settings</th><th>Description</th></tr></thead><tbody><tr><td><code>user</code></td><td>Sets which user the MySQL service will run as.</td></tr><tr><td><code>password</code></td><td>Sets the password for the MySQL user.</td></tr><tr><td><code>admin_address</code></td><td>The IP address on which to listen for TCP/IP connections on the administrative network interface.</td></tr><tr><td><code>debug</code></td><td>This variable indicates the current debugging settings</td></tr><tr><td><code>sql_warnings</code></td><td>This variable controls whether single-row INSERT statements produce an information string if warnings occur.</td></tr><tr><td><code>secure_file_priv</code></td><td>This variable is used to limit the effect of data import and export operations.</td></tr></tbody></table>

### Footprinting <a href="#footprinting-the-service" id="footprinting-the-service"></a>

{% tabs %}
{% tab title="Metasploit" %}

{% endtab %}

{% tab title="Nmap" %}
{% code lineNumbers="true" %}
```shellscript
sudo nmap -sV -sC -p3306 --script mysql* <IP>
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Enumerate

{% code lineNumbers="true" %}
```shellscript
mysql -u <username> -p <password> -h <IP>
Commands
show databases;, use <database>;, show tables;, show columns from <table>;, select * from <table>;, select * from <table> where <column> = "<string>";
```
{% endcode %}
