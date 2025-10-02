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
Get-ADPrincipalGroupMembership -Identity &#x3C;name>Get-ADGroup -Filter *
Get-ADGroup -Filter * | Select Name
Get-ADGroup -Filter * -Properties * 
Get-ADGroup -Filter 'Name -like "admin"' | select Name
Get-ADGroupMember -Identity "Group Name" -Recursive
Get-ADPrincipalGroupMembership -Identity &#x3C;name>
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainGroup or Get-NetGroup 
Get-DomainGroup "*admin*" 
Get-DomainGroup | select Name
Get-DomainGroup -Domain &#x3C;name> 
Get-DomainGroup -UserName "name"
Get-DomainGroupMember -Identity "Domain Admins" -Recurse
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
</code></pre></td></tr><tr><td><strong>Domain Controller Local Group Enum</strong> <sub>(requires admin rights on non-dc)</sub></td><td></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-NetLocalGroup -ComputerName &#x3C;dc-name>
Get-NetLocalGroupMember -ComputerName &#x3C;dc-name> -GroupName Administrators
</code></pre></td></tr><tr><td><strong>Non-null SPN Accounts</strong> <sub>(Consider for</sub> <a data-mention href="../exploitation/kerberoasting.md">kerberoasting.md</a><sub>)</sub></td><td></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainUser -SPN
</code></pre></td></tr><tr><td><strong>Share Enum</strong><br><a href="https://github.com/NetSPI/PowerHuntShares">PowerHuntShares</a></td><td></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Invoke-ShareFinder -Verbose 
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
</code></pre></td></tr><tr><td><strong>Search Interesting ACEs</strong></td><td><pre data-line-numbers><code>
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Find-InterestingDomainAcl -ResolveGUIDs
</code></pre></td></tr><tr><td><strong>ACLs associated for specified Path</strong></td><td><pre data-line-numbers><code>
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-PathAcl -Path "\\hostname\sysvol"
</code></pre></td></tr></tbody></table>

### **Domain Enumeration - Group Policy Objects (GPO)**

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
</code></pre></td></tr><tr><td><strong>Get GPO applied on an OU.</strong> <sub>(Read GPOname from gplink attribute from <code>Get-NetOU</code>)</sub></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">
</code></pre></td><td><pre class="language-powershell" data-line-numbers><code class="lang-powershell">Get-DomainGPO -Identity "{gp-link}"
</code></pre></td></tr></tbody></table>

### **Domain Enumeration - Trusts**







