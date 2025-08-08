# BloodHound

Enumerates key AD elements such as:

* Group memberships
* Session data
* Access Control Lists (ACLs)
* Domain trusts
* Privileged relationships (like local administrator rights)

{% hint style="warning" %}
**Note:** Your BloodHound and SharpHound versions must match for the best results.
{% endhint %}

#### **Types of Data Collectors**

* [SharpHound](https://github.com/SpecterOps/SharpHound)
  * `.\SharpHound.exe --CollectionMethods All --Domain tryhackme.loc --ExcludeDCs`  //domain joined machine
* [AzureHound](https://github.com/SpecterOps/AzureHound)
* [BloodHound.py](https://github.com/dirkjanm/BloodHound.py) (Python Collector)
  * `bloodhound-python -u <username> -p <password> -d <domain> -ns <dns-server> -c All --zip`&#x20;

#### Security Considerations

* Use the **`--ExcludeDCs`** flag to avoid querying domain controllers
* Employ stealthier collection methods, such as **`DCOnly`**, to limit interactions with sensitive systems
* Run collectors from systems with appropriate antivirus exclusions or non-domain-joined machines using the `runas` command with the `/netonly` flag to authenticate without joining the domain

### BloodHound-CE

* [BloodHound](https://github.com/SpecterOps/BloodHound)
* Import the data collected **Administration** -> **File Ingest** -> **Upload**
* **Exploring BloodHound Data**
  * Nodes: Represent users, computers, groups, etc.
  * Edges: Represent relationships and permissions between nodes.
* Using Built-in Queries : Cypher -> Click the folder icon to browse prebuilt queries

#### Attack Path Discovery

1. Click the **Pathfinding** button in the top bar
2. Set a compromised user as the **Start Node**
3. Set a target (any Admin Groups Identified earlier) as the **End Node**
4. Run the search with the desired edge filters

