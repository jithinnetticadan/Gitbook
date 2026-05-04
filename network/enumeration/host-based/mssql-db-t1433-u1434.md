# MSSQL DB - T1433,U1434

### MSSQL Databases

* <table><thead><tr><th width="114.71435546875">Default System Database</th><th>Description</th></tr></thead><tbody><tr><td><code>master</code></td><td>Tracks all system information for an SQL server instance</td></tr><tr><td><code>model</code></td><td>Template database that acts as a structure for every new database created. Any setting changed in the model database will be reflected in any new database created after changes to the model database</td></tr><tr><td><code>msdb</code></td><td>The SQL Server Agent uses this database to schedule jobs &#x26; alerts</td></tr><tr><td><code>tempdb</code></td><td>Stores temporary objects</td></tr><tr><td><code>resource</code></td><td>Read-only database containing system objects included with SQL server</td></tr></tbody></table>

### Default Configuration

* When an admin initially installs and configures MSSQL to be network accessible, the SQL service will likely run as `NT SERVICE\MSSQLSERVER` .

### Dangerous Settings

* MSSQL clients not using encryption to connect to the MSSQL server
* The use of self-signed certificates when encryption is being used. It is possible to spoof self-signed certificates
* The use of [named pipes](https://docs.microsoft.com/en-us/sql/tools/configuration-manager/named-pipes-properties?view=sql-server-ver15)
* Weak & default `sa` credentials. Admins may forget to disable this account

### Footprinting

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" %}
```shellscript
use auxilliary/scanner/mssql/mssql_ping
set rhosts <IP>
run
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}
{% code lineNumbers="true" %}
```shellscript
sudo nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=sa,mssql.password=<pass>,mssql.instance-name=MSSQLSERVER -sV -p 1433 <IP>
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Login BruteForce

### Enumeration

{% tabs %}
{% tab title="Manual" %}

{% endtab %}

{% tab title="PowerUpSQL" %}
{% code lineNumbers="true" %}
```powershell
//Discovery (SPN Scanning)
Get-SQLInstanceDomain
//Check Accessibility
Get-SQLConnectionTestThreaded
Get-SQLInstanceDomain | Get-SQLConnectionTestThreaded -Verbose
//Gather Information
Get-SQLInstanceDomain | Get-SQLServerInfo -Verbose
```
{% endcode %}
{% endtab %}

{% tab title="Impacket-mssqlclient" %}
{% code lineNumbers="true" %}
```shellscript
python3 mssqlclient.py <ussername>@<IP> -windows-auth
select name from sys.databases
```
{% endcode %}
{% endtab %}

{% tab title="sqsh" %}
{% code lineNumbers="true" %}
```shellscript
sqsh -S <IP> -U user -P pass
```
{% endcode %}
{% endtab %}

{% tab title="sqlcmd" %}
{% code lineNumbers="true" %}
```bat
sqlcmd -S <IP> -U <user> -P <pass>
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Linked SQL Servers Enumeration

{% tabs %}
{% tab title="PowerUpSQL" %}
{% code lineNumbers="true" %}
```powershell
Get-SQLServerLink -Instance <server-name> -Verbose
//Nested Enumeration
Get-SQLServerLinkCrawl -Instance <server-name> -Verbose
```
{% endcode %}
{% endtab %}

{% tab title="Manual" %}
{% code lineNumbers="true" %}
```sql
SELECT * FROM master..sysservers
SELECT * FROM OPENQUERY("<link-server1>", 'SELECT * FROM master..sysservers')
//Nested Enumeration
SELECT * FROM OPENQUERY("<link-server1>",'SELECT * FROM OPENQUERY(''<link-server2>'',''SELECT * FROM master..sysservers'')')
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Tools

* [PowerUpSQL](https://github.com/NetSPI/PowerUpSQL)
* &#x20;[sqsh](https://en.wikipedia.org/wiki/Sqsh)
* [sqlcmd](https://docs.microsoft.com/en-us/sql/tools/sqlcmd-utility)
* [SQL Server Management Studio or SSMS](https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)
* [dbeaver](https://github.com/dbeaver/dbeaver)
* [mssql-cli](https://github.com/dbcli/mssql-cli)
* [mssqlclient.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/mssqlclient.py)
* [SQL Server PowerShell](https://docs.microsoft.com/en-us/sql/powershell/sql-server-powershell?view=sql-server-ver15)
* [HeidiSQL](https://www.heidisql.com/)
* [SQLPro](https://www.macsqlclient.com/)
