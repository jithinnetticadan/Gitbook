# Ldap/Ldaps - T389,636

#### Anonymous Bind

{% code lineNumbers="true" %}
```shellscript
ldapsearch -x -H ldap://<ip> -s base
ldapsearch -x -H ldap://<ip> -b "dc=<update>,dc=<update>" "(objectClass=person)"
```
{% endcode %}

#### Automated Enumeration

```shellscript
enum4linux-ng -A <ip> -oA results.txt
```

#### Tools

* [LdapAdmin](https://sourceforge.net/projects/ldapadmin/files/)
