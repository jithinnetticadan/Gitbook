# AD & PowerView Modules

### ActiveDirectory Module Setup

{% hint style="info" %}
Download Remote Server Administration Tools (RSAT) for Windows. (Admin Priv)

`Get-WindowsCapability -Name RSAT* -Online | Add-WindowsCapability -Online`
{% endhint %}

* `Get-Module -ListAvailable ActiveDirectory`&#x20;
* `Import-Module ActiveDirectory`&#x20;
* [ActiveDirectory-Module](https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2025-ps)

### PowerView Setup

* [PowerSploit](https://github.com/PowerShellMafia/PowerSploit)
* C:\PowerSploit-master\Recon -> PowerView.ps1
* `Import-Module .\PowerView.ps1`&#x20;
* [PowerView- Recon](https://powersploit.readthedocs.io/en/latest/Recon/)

### **Domain Enumeration - Generic**

<table><thead><tr><th>Enum Type</th><th>AD Module</th><th>PowerView</th></tr></thead><tbody><tr><td><strong>Domain Details</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADDomain
Get-Domain -Identity &#x3C;domain-name>
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-Domain
Get-Domain -Domain &#x3C;domain-name>
</code></pre></td></tr><tr><td><strong>Domain SID</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">(Get-ADDomain).DomainSID
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainSID
</code></pre></td></tr><tr><td><strong>Domain Password Policy</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">(Get-DomainPolicyData).systemaccess
(Get-DomainPolicyData -Domain &#x3C;domain-name>).systemaccess
Get-ADDefaultDomainPasswordPolicy
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainPolicyData
</code></pre></td></tr><tr><td><strong>Domain Controllers</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADDomainController
Get-ADDomainController -DomainName &#x3C;domain-name> -Discover
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainController
Get-DomainController -Domain &#x3C;domain-name>
</code></pre></td></tr><tr><td><strong>User Enum</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADUser -Filter * 
Get-ADUser -Identity &#x3C;username> 
Get-ADUser -Identity  &#x3C;username> -Properties * 
Get-ADUser -Filter "Name -like 'admin'" 
Get-ADUser -Identity &#x3C;name> -Properties *
Get-ADUser -Filter 'Description -like "built"' -Properties Description | select name, Description
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainUser or Get-NetUser
Get-DomainUser *admin*
Get-DomainUser -Identity &#x3C;name>
Get-DomainUser -AdminCount   
Get-DomainUser -Identity &#x3C;name> -Properties samaccountname, logonCount 
Get-DomainUser -LDAPFilter "Description=built" | Select name, Description
</code></pre></td></tr><tr><td><strong>Group Enum</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADGroup -Filter *
Get-ADGroup -Filter * | Select Name
Get-ADGroup -Filter * -Properties * 
Get-ADGroup -Filter 'Name -like "admin"' | select Name
Get-ADGroupMember -Identity "Group Name" -Recursive
Get-ADGroupMember -Identity "Enterprise Admins" -Server &#x3C;parent-domain> -Recursive
Get-ADPrincipalGroupMembership -Identity &#x3C;name>
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainGroup or Get-NetGroup 
Get-DomainGroup "*admin*" 
Get-DomainGroup | select Name
Get-DomainGroup -Domain &#x3C;name> 
Get-DomainGroup -UserName "name"
Get-DomainGroupMember -Identity "Domain Admins" -Recurse
Get-DomainGroupMember -Identity "Enterprise Admins" -Domain &#x3C;parent-domain> -Recurse
</code></pre></td></tr><tr><td><strong>Computer Enum</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADComputer -Filter *
Get-ADComputer -Filter * | Select Name, OperatingSystem 
Get-ADComputer -Filter * -Properties * 
Get-ADComputer -Filter 'OperatingSystem -like "Server 2022"' -Properties OperatingSystem | select Name,OperatingSystem 
Get-ADComputer -Filter * -Properties DNSHostName | %{Test-Connection -Count 1 -ComputerName $_.DNSHostName}
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainComputer or Get-NetComputer 
Get-DomainComputer | select Name 
Get-DomainComputer -OperatingSystem "Server 2022" 
Get-DomainComputer -Ping 
Get-NetLoggedon -ComputerName &#x3C;name> (requires local admin rights on target)
Get-LoggedonLocal -ComputerName &#x3C;name> ( requires remote registry service running)
Get-LastLoggedOn -ComputerName &#x3C;name> (requires remote registry + local admin)
(Get-DomainOU -Identity '&#x3C;OU>').distinguishedname | %{Get-DomainComputer -SearchBase $_} | select name
</code></pre></td></tr><tr><td><strong>Domain Controller Local Group Enum</strong> <sub>(requires admin rights on non-dc)</sub></td><td></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-NetLocalGroup -ComputerName &#x3C;dc-name>
Get-NetLocalGroupMember -ComputerName &#x3C;dc-name> -GroupName Administrators
</code></pre></td></tr><tr><td><strong>Non-null SPN Accounts</strong> <sub>(Consider for</sub> <a data-mention href="../exploitation/kerberoasting.md">kerberoasting.md</a><sub>)</sub></td><td></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainUser -SPN
</code></pre></td></tr><tr><td><strong>Share Enum</strong><br><a href="https://github.com/NetSPI/PowerHuntShares">PowerHuntShares</a></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Invoke-ShareFinder -Verbose 
Invoke-HuntSMBShares -NoPing -OutputDirectory C:\AD\ -HostList C:\domain-computer-enum-servers.txt
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Invoke-ShareFinder -Verbose 
Invoke-HuntSMBShares -NoPing -OutputDirectory C:\AD\ -HostList C:\domain-computer-enum-servers.txt
</code></pre></td></tr><tr><td><strong>File Enum</strong></td><td></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Invoke-FileFinder -Verbose
</code></pre></td></tr><tr><td><strong>File Server Enum</strong></td><td></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-NetFileServer
</code></pre></td></tr></tbody></table>

### **Domain Enumeration - ACL's**

{% hint style="info" %}
ACL is a list of Access Control Entries (ACE). Each ACE corresponds to individual permission or audit access

* **DACL**: Defines the permissions trustees (a user or group) have on an object
* **SACL**: Logs success and failure audit messages when an object is accessed
{% endhint %}

<table><thead><tr><th>Enum Type</th><th>AD Module</th><th>PowerView</th></tr></thead><tbody><tr><td><strong>ACLs - specific Object/Filter</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">(Get-Acl 'AD:\CN=Administrator,CN=Users,DC=&#x3C;update>,DC=&#x3C;update>,DC=local').Access
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainObjectACL -SamAccountName &#x3C;username> -ResolveGUIDs
Get-DomainObjectACL -SearchBase 'LDAP://CN=Domain Admins,CN=Users,DC=&#x3C;update>,DC=&#x3C;update>,DC=local' -ResolveGUIDs -Verbose 
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs -Verbose
</code></pre></td></tr><tr><td><strong>Search Interesting ACEs</strong></td><td><pre data-line-numbers><code>
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Find-InterestingDomainAcl -ResolveGUIDs
Find-InterestingDomainAcl -ResolveGUIDs | ?{$_.IdentityReferenceName -match "&#x3C;string>"} 
Invoke-ACLScanner -ResolveGUIDs
</code></pre></td></tr><tr><td><strong>ACLs associated for specified Path</strong></td><td><pre data-line-numbers><code>
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-PathAcl -Path "\\hostname\sysvol"
</code></pre></td></tr><tr><td><strong>Replication or GenericAll Rights</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">(Get-Acl "AD:$((Get-ADDomain).DistinguishedName)").Access | ?{($_.IdentityReference -match "&#x3C;username>") -and ($_.ObjectType -in @("1131f6aa-9c07-11d1-f79f-00c04fc2dcd2","1131f6ab-9c07-11d1-f79f-00c04fc2dcd2","89e95b76-444d-4c62-991a-0facbeda640c") -or $_.ActiveDirectoryRights -match "GenericAll")}
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainObjectAcl -SearchBase "DC=&#x3C;update>,DC=&#x3C;update>,DC=&#x3C;update>" -SearchScope Base -ResolveGUIDs | ?{($_.ObjectAceType -match 'replication-get') -or ($_.ActiveDirectoryRights -match 'GenericAll')} | ForEach-Object {$_ | Add-Member NoteProperty 'IdentityName' $(Convert-SidToName $_.SecurityIdentifier);$_} | ?{$_.IdentityName -match "&#x3C;username>"}
</code></pre></td></tr></tbody></table>

### **Domain Enumeration - GroupPolicyObjects (GPO)**

{% hint style="info" %}
* GPO can be linked to domains, sites and organizational units (OUs).GPO is a virtual collection of policy settings, security permissions, and scope of management (SOM) that you can apply to users and computers.
* GPO can be linked to domains, sites and organizational units (OUs).
* OU is the lowest-level AD container to which GPO can be applied.
{% endhint %}

<table><thead><tr><th>Enum Type</th><th>AD Module</th><th>PowerView</th></tr></thead><tbody><tr><td><strong>GPO List in Current Domain.</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainGPO
Get-DomainGPO -ComputerIdentity &#x3C;computer-name>
</code></pre></td></tr><tr><td><strong>GPO(s) which use Restricted Groups or groups.xml</strong> <sub>(add Domain Group as Local Group)</sub></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainGPOLocalGroup
</code></pre></td></tr><tr><td><strong>Users in a Local Group of a Machine</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainGPOComputerLocalGroupMapping -ComputerIdentity &#x3C;computer-name>
</code></pre></td></tr><tr><td><p></p><p><strong>Machines where User is Member of Specific Group</strong></p></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainGPOUserLocalGroupMapping -Identity &#x3C;username> -Verbose
</code></pre></td></tr><tr><td><strong>Get OUs</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADOrganizationalUnit -Filter * -Properties *
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainOU
(Get-DomainOU -Identity '&#x3C;OU-name>').gplink 
</code></pre></td></tr><tr><td><strong>Get GPO applied on an OU.</strong> <sub>(Read GPOname from gplink attribute from <code>Get-NetOU</code>)</sub></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainGPO -Identity "{gp-link}"
Get-DomainGPO -Identity (Get-DomainOU -Identity'&#x3C;OU>').gplink.substring(11,(Get-DomainOU -Identity '&#x3C;OU>').gplink.length-72)
</code></pre></td></tr></tbody></table>

### **Domain Enumeration - Trusts**

{% hint style="info" %}
* Trust is a relationship between two domains or forests which allows users of one domain or forest to access resources in the other domain or forest.
* Trust can be automatic (parent-child, same forest etc.) or established (forest, external).
* Trusted Domain Objects (TDOs) represent the trust relationships in a domain.
{% endhint %}

<table><thead><tr><th>Enum Type</th><th>AD Module</th><th>PowerView</th></tr></thead><tbody><tr><td><p></p><p><strong>Get List of all Domain Trusts</strong></p></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADTrust -Filter *
Get-ADTrust -Identity &#x3C;domain>
Get-ADForest | %{Get-ADTrust -Filter *}
//list the external trusts
(Get-ADForest).Domains | %{Get-ADTrust -Filter '(intraForest-ne $True) -and (ForestTransitive -ne $True)' -Server $_}
Get-ADTrust -Filter '(intraForest -ne $True) -and(ForestTransitive -ne $True)'
Get-ADTrust -Filter * -Server &#x3C;external-domain>
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainTrust
Get-DomainTrust -Domain &#x3C;update>
//list the external trusts
Get-ForestDomain | %{Get-DomainTrust -Domain $_.Name} | ?{$_.TrustAttributes -eq "FILTER_SIDS"}
Get-DomainTrust | ?{$_.TrustAttributes -eq "FILTER_SIDS"}
Get-ForestDomain -Forest &#x3C;external-domain> | %{Get-DomainTrust -Domain $_.Name}
</code></pre></td></tr><tr><td><strong>Get Details about Forest</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADForest
Get-ADForest -Identity &#x3C;forest-domain>
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-Forest
Get-Forest -Forest &#x3C;forest-domain>
</code></pre></td></tr><tr><td><strong>Get all Domains in Forest</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">(Get-ADForest).Domains
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ForestDomain
Get-ForestDomain -Forest &#x3C;forest-domain>
</code></pre></td></tr><tr><td><strong>Get all Global Catalogs for the Forest</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADForest | select -ExpandProperty GlobalCatalogs
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ForestGlobalCatalog
Get-ForestGlobalCatalog -Forest &#x3C;forest-domain>
</code></pre></td></tr><tr><td><strong>Map Trusts of a Forest</strong></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ADTrust -Filter 'msDS-TrustForestTrustInfo -ne "$null"'
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-ForestTrust
Get-ForestTrust -Forest &#x3C;forest-domain>
</code></pre></td></tr></tbody></table>

### **Domain Enumeration - User Hunting**

<table><thead><tr><th>Enum Type</th><th>AD Module</th><th>PowerView</th></tr></thead><tbody><tr><td><strong>Find all Machines where user has Local Admin Access</strong><br><sub>(See Find-WMILocalAdminAccess.ps1 &#x26; Find-PSRemotingLocalAdminAccess.ps1)</sub></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Find-LocalAdminAccess -Verbose
</code></pre></td></tr><tr><td><strong>Find Computers where Domain Admin/specified user/group has Active Sessions</strong><br><sub>(For Server 2019 onwards, require local admin)</sub></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Find-DomainUserLocation -Verbose
Find-DomainUserLocation -UserGroupIdentity "RDPUsers"
</code></pre></td></tr><tr><td><p></p><p><strong>Find Computers where Domain Admin Session is available &#x26; Current User has Admin Access</strong></p></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Find-DomainUserLocation -CheckAccess
</code></pre></td></tr><tr><td><p></p><p><strong>Find computers (File Servers and Distributed File servers) where Domain Admin Session is available</strong></p></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Find-DomainUserLocation -Stealth
</code></pre></td></tr><tr><td><strong>List Sessions on Remote Machines</strong><br><a href="https://github.com/Leo4j/Invoke-SessionHunter">Invoke-SessionHunter</a></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Invoke-SessionHunter -FailSafe
Invoke-SessionHunter -NoPortScan -Targets C:\AD\servers-except-DC.txt
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Invoke-SessionHunter -FailSafe
Invoke-SessionHunter -NoPortScan -Targets C:\AD\servers-except-DC.txt
</code></pre></td></tr></tbody></table>

### Tools

* [SharpView](https://github.com/dmchell/SharpView)
* [LAPSToolkit](https://github.com/leoloobeek/LAPSToolkit)
