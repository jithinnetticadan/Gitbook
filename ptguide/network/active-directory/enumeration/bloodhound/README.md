# BloodHound

Enumerates key AD elements such as:

* Group memberships
* Session data
* Access Control Lists (ACLs)
* Domain trusts
* Privileged relationships (like local administrator rights)

{% hint style="warning" %}
**Note:** Your BloodHound and Data Collector versions must match for the best results. It recommended to download the collector binary from the same bloodhound instance.
{% endhint %}

## **Types of Data Collectors**

* [RustHound-CE](https://github.com/g0h4n/RustHound-CE) <sup><sub>(efficient as it collects more details like certificate  templates etc compared to netexec and python ingestors)<sub></sup>
  * `rusthound-ce.exe -u <username> -p <password> -d <domain> -c All -z`   <sup><sub>(linux/windows)<sub></sup>
* **NetExec**
  * `nxc ldap <dc-ip> -u <username> -p <password> --bloodhound --collection All --dns-server <dc-ip>`
* [SharpHound](https://github.com/SpecterOps/SharpHound)
  * `SharpHound.exe --CollectionMethods All --Domain <value> --ExcludeDCs` <sub>(domain joined machine)</sub>
  * `.\SharpHound.exe -c All --zipfilename <file>` <sub>(domain joined machine)</sub>
  * `SharpHound.exe --args --collectionmethods Group,GPOLocalGroup,Session,Trusts,ACL,Container,ObjectProps,SPNTargets,CertServices --ExcludeDCs` <sub>(less noisy)</sub>
* [AzureHound](https://github.com/SpecterOps/AzureHound)
* [BloodHound.py](https://github.com/dirkjanm/BloodHound.py) (Python Collector)
  * `bloodhound-python -u <username> -p <password> -d <domain> -ns <dns-server/dc-ip> -c All --zip`
* [SOAPHound](https://github.com/FalconForceTeam/SOAPHound) (Stealthier)
  * Talks to Active Driectory Web Services (ADWS - Port 9389) in place of sending\
    LDAP queries - just like the AD Module.
  * `SOAPHound.exe --buildcache -c C:\AD\Tools\cache.txt` <sub>(Build a cache that includes basic info about domain objects.)</sub>
  * `SOAPHound.exe -c C:\AD\Tools\cache.txt --bhdump -o C:\AD\Tools\bloodhound-output --nolaps` <sub>(Collect BloodHound compatible data)</sub>
* [SoaPy](https://github.com/xforcered/SoaPy)

## Security Considerations

* Use the **`--ExcludeDCs`** flag to avoid querying domain controllers
* Employ stealthier collection methods, such as **`DCOnly`**, to limit interactions with sensitive systems
* Run collectors from systems with appropriate antivirus exclusions or non-domain-joined machines using the `runas` command with the `/netonly` flag to authenticate without joining the domain

## BloodHound-CE/Legacy

* [BloodHound-CE](https://github.com/SpecterOps/BloodHound)
* [BloodHound-Legacy](https://github.com/SpecterOps/BloodHound-Legacy)
* Import the data collected **Administration** -> **File Ingest** -> **Upload**
* **Exploring BloodHound Data**
  * Nodes: Represent users, computers, groups, etc.
  * Edges: Represent relationships and permissions between nodes.
* Using Built-in Queries : Cypher -> Click the folder icon to browse prebuilt queries

### Attack Path Discovery

1. Click the **Pathfinding** button in the top bar
2. Set a compromised user as the **Start Node**
3. Set a target (any Admin Groups Identified earlier) as the **End Node**
4. Run the search with the desired edge filters

## Tools

* [SharpCollection](https://github.com/Flangvik/SharpCollection)
