# Unquoted Services

{% code lineNumbers="true" %}
```batch
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\" | findstr /i /v """
sc qc <service-name>
```
{% endcode %}

[#unquoted-service-paths](../network/exploitation/windows-privesc.md#unquoted-service-paths "mention")

#### References

* [How-to-fix-the-windows-unquoted-service-path-vulnerability](https://isgovern.com/blog/how-to-fix-the-windows-unquoted-service-path-vulnerability/)
