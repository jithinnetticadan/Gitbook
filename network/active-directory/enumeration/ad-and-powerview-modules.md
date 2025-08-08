# AD & PowerView Modules

### Enumeration With the ActiveDirectory Module

{% hint style="info" %}
Download Remote Server Administration Tools (RSAT) for Windows. (Admin Priv)

`Get-WindowsCapability -Name RSAT* -Online | Add-WindowsCapability -Online`
{% endhint %}

* `Get-Module -ListAvailable ActiveDirectory`&#x20;
* `Import-Module ActiveDirectory`&#x20;
* #### User Enumeration
  * `Get-ADUser -Filter *`&#x20;
  * `Get-ADUser -Identity <username>`&#x20;
  * `Get-ADUser -Identity  <username> -Properties *`&#x20;
  * `Get-ADUser -Filter "Name -like 'admin'"`&#x20;
* **Group Enumeration**
  * `Get-ADGroup -Filter *`
  * `Get-ADGroup -Filter * | Select Name`
  * `Get-ADGroupMember -Identity "Group Name"`
* **Computer Enumeration**
  * `Get-ADComputer -Filter *`
  * `Get-ADComputer -Filter * | Select Name, OperatingSystem`&#x20;
* `Get-ADDefaultDomainPasswordPolicy`
* For More -> [ActiveDirectory-Module](https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2025-ps)

### Enumeration With PowerView

* [PowerSploit](https://github.com/PowerShellMafia/PowerSploit)
* C:\PowerSploit-master\Recon -> PowerView.ps1
* `Import-Module .\PowerView.ps1`&#x20;
* **User Enumeration**
  * `Get-DomainUser` or `Get-NetUser`
  * `Get-DomainUser *admin*`
* **Group Enumeration**
  * `Get-DomainGroup` or `Get-NetGroup`&#x20;
  * `Get-DomainGroup "*admin*"`&#x20;
* **Computer Enumeration**
  * `Get-DomainComputer` or `Get-NetComputer`&#x20;
* Get-DomainUser -AdminCount
* `Get-DomainUser -SPN` lists accounts with non-null SPN. Consider for Kerberoasting.
* For More -> [Recon](https://powersploit.readthedocs.io/en/latest/Recon/)
