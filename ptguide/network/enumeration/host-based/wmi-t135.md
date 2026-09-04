# WMI - T135

{% hint style="info" %}
WMI allows read and write access to almost all settings on Windows systems. WMI is typically accessed via PowerShell, VBScript, or the Windows Management Instrumentation Console (`WMIC`). WMI is not a single program but consists of several programs and various databases, also known as repositories.
{% endhint %}

### **Quick WMI checks**

| `wmic qfe get Caption,Description,HotFixID,InstalledOn`                              | Prints the patch level and description of the Hotfixes applied                                         |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `wmic computersystem get Name,Domain,Manufacturer,Model,Username,Roles /format:List` | Displays basic host information to include any attributes within the list                              |
| `wmic process list /format:list`                                                     | A listing of all processes on host                                                                     |
| `wmic ntdomain list /format:list`                                                    | Displays information about the Domain and Domain Controllers                                           |
| `wmic useraccount list /format:list`                                                 | Displays information about all local accounts and any domain accounts that have logged into the device |
| `wmic group list /format:list`                                                       | Information about all local groups                                                                     |
| `wmic sysaccount list /format:list`                                                  | Dumps information about any system accounts that are being used as service accounts.                   |

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

### Lateral Movement [#moving-laterally-using-wmi](../../exploitation/lateral-movement/#moving-laterally-using-wmi "mention")

### Tools

* [wmiexec.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/wmiexec.py)
