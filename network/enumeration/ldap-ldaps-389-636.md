# Ldap/Ldaps - 389,636

#### Anonymous Bind

{% code lineNumbers="true" %}
```
ldapsearch -x -H ldap://<ip> -s base
ldapsearch -x -H ldap://<ip> -b "dc=<update>,dc=<update>" "(objectClass=person)"
```
{% endcode %}

#### Automated Enumeration

```
enum4linux-ng -A <ip> -oA results.txt
```

#### Tools

* [LdapAdmin](https://sourceforge.net/projects/ldapadmin/files/)
