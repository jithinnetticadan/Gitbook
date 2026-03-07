# WMI - T135

{% hint style="info" %}
WMI allows read and write access to almost all settings on Windows systems. WMI is typically accessed via PowerShell, VBScript, or the Windows Management Instrumentation Console (`WMIC`). WMI is not a single program but consists of several programs and various databases, also known as repositories.
{% endhint %}

### Footprinting <a href="#footprinting-the-service-2" id="footprinting-the-service-2"></a>

{% tabs %}
{% tab title="wmiexec" %}
{% code lineNumbers="true" %}
```shellscript
Impacket-wmiexec <user>:"<pass>"@<IP> cmd
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Tools

[wmiexec.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/wmiexec.py)
