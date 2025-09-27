# AD & PowerView Modules

### Enumeration With the ActiveDirectory Module

{% hint style="info" %}
Download Remote Server Administration Tools (RSAT) for Windows. (Admin Priv)

`Get-WindowsCapability -Name RSAT* -Online | Add-WindowsCapability -Online`
{% endhint %}

* `Get-Module -ListAvailable ActiveDirectory`&#x20;
* `Import-Module ActiveDirectory`&#x20;
* **Domain Details**
  * `Get-ADDomain`
  * `Get-Domain -Identity <domain-name>`
* **Domain SID**
  * `(Get-ADDomain).DomainSID`
* **Domain Password Policy**
  * `(Get-DomainPolicyData).systemaccess`
  * `(Get-DomainPolicyData -Domain <domain-name>).systemaccess`
  * `Get-ADDefaultDomainPasswordPolicy`
* **Domain Controllers**
  * `Get-ADDomainController`
  * `Get-ADDomainController -DomainName <domain-name> -Discover`
* #### User Enumeration
  * `Get-ADUser -Filter *`&#x20;
  * `Get-ADUser -Identity <username>`&#x20;
  * `Get-ADUser -Identity  <username> -Properties *`&#x20;
  * `Get-ADUser -Filter "Name -like 'admin'"`&#x20;
  * `Get-ADUser -Identity <name> -Properties *`
  * `Get-ADUser -Filter 'Description -like "built"' -Properties Description | select name, Description`
* **Group Enumeration**
  * `Get-ADGroup -Filter *`
  * `Get-ADGroup -Filter * | Select Name`
  * `Get-ADGroup -Filter * -Properties *`&#x20;
  * `Get-ADGroup -Filter 'Name -like "admin"' | select Name`
  * `Get-ADGroupMember -Identity "Group Name" -Recursive`
  * `Get-ADPrincipalGroupMembership -Identity <name>`&#x20;
* **Computer Enumeration**
  * `Get-ADComputer -Filter *`
  * `Get-ADComputer -Filter * | Select Name, OperatingSystem`&#x20;
  * `Get-ADComputer -Filter * -Properties *`&#x20;
  * `Get-ADComputer -Filter 'OperatingSystem -like "Server 2022"' -Properties OperatingSystem | select Name,OperatingSystem`&#x20;
  * `Get-ADComputer -Filter * -Properties DNSHostName | %{Test-Connection -Count 1 -ComputerName $_.DNSHostName}`
* For More -> [ActiveDirectory-Module](https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2025-ps)

### Enumeration With PowerView

* [PowerSploit](https://github.com/PowerShellMafia/PowerSploit)
* C:\PowerSploit-master\Recon -> PowerView.ps1
* `Import-Module .\PowerView.ps1`&#x20;
* **Domain Details**
  * `Get-Domain`
  * `Get-Domain -Domain <domain-name>`
* **Domain SID**
  * `Get-DomainSID`
* **Domain Password Policy**
  * `Get-DomainPolicyData`
* **Domain Controllers**
  * `Get-DomainController`
  * `Get-DomainController -Domain <domain-name>` &#x20;
* **User Enumeration**
  * `Get-DomainUser` or `Get-NetUser`
  * `Get-DomainUser *admin*`
  * `Get-DomainUser -Identity <name>`
  * `Get-DomainUser -AdminCount`  &#x20;
  * `Get-DomainUser -Identity <name> -Properties samaccountname, logonCount`&#x20;
  * `Get-DomainUser -LDAPFilter "Description=built" | Select name, Description`
* **Group Enumeration**
  * `Get-DomainGroup` or `Get-NetGroup`&#x20;
  * `Get-DomainGroup "*admin*"`&#x20;
  * `Get-DomainGroup | select Name`
  * `Get-DomainGroup -Domain <name>`&#x20;
  * `Get-DomainGroup -UserName "name"`
  * `Get-DomainGroupMember -Identity "Domain Admins" -Recurse`
* **Computer Enumeration**
  * `Get-DomainComputer` or `Get-NetComputer`&#x20;
  * `Get-DomainComputer | select Name`&#x20;
  * `Get-DomainComputer -OperatingSystem "`_`Server 2022`_`"`&#x20;
  * `Get-DomainComputer -Ping`&#x20;
  * `Get-NetLoggedon -ComputerName <name>` <sub>(requires local admin rights on target)</sub>
  * `Get-LoggedonLocal -ComputerName <name>` <sub>( requires remote registry service running)</sub>
  * `Get-LastLoggedOn -ComputerName <name>` <sub>(requires remote registry + local admin)</sub>
* **Domain Controller Local Group Enumeration** <sub>(requires admin rights on non-dc)</sub>
  * `Get-NetLocalGroup -ComputerName <dc-name>`
  * `Get-NetLocalGroupMember -ComputerName <dc-name> -GroupName Administrators`
* `Get-DomainUser -SPN` lists accounts with non-null SPN. Consider for [kerberoasting.md](../exploitation/kerberoasting.md "mention").
* **Share Enumeration**
  * `Invoke-ShareFinder -Verbose`&#x20;
  * [PowerHuntShares](https://github.com/NetSPI/PowerHuntShares)
    * `Invoke-HuntSMBShares -NoPing -OutputDirectory C:\AD\ -HostList C:\servers.txt`
* **File Enumeration**
  * `Invoke-FileFinder -Verbose`&#x20;
* **File Server Enumeration**
  * **Get-NetFileServer**
* For More -> [Recon](https://powersploit.readthedocs.io/en/latest/Recon/)
