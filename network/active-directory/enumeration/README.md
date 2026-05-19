# Enumeration

### **Basic Commands**

<table data-header-hidden><thead><tr><th width="196.85711669921875">Command</th><th>Result</th></tr></thead><tbody><tr><td><code>hostname</code></td><td>Prints the PC's Name</td></tr><tr><td><code>[System.Environment]::OSVersion.Version</code></td><td>Prints out the OS version and revision level</td></tr><tr><td><code>wmic qfe get Caption,Description,HotFixID,InstalledOn</code></td><td>Prints the patches and hotfixes applied to the host</td></tr><tr><td><code>ipconfig /all</code></td><td>Prints out network adapter state and configurations</td></tr><tr><td><code>set</code></td><td>Displays a list of environment variables for the current session (ran from CMD-prompt)</td></tr><tr><td><code>echo %USERDOMAIN%</code></td><td>Displays the domain name to which the host belongs (ran from CMD-prompt)</td></tr><tr><td><code>echo %logonserver%</code></td><td>Prints out the name of the Domain controller the host checks in with (ran from CMD-prompt)</td></tr><tr><td><code>systeminfo</code></td><td>All above information with single command</td></tr></tbody></table>

#### Password Policy

* Understand Password Policy
  * `nxc smb <dc-ip> --pass-pol`  <sup><sub>(if Null session allowed)<sub></sup>
  * `nxc smb <dc-ip> -u <user> -p <pass> --pass-pol`
  * `rpcclient -U "" -N <DC-IP>`  -> `getdompwinfo`
  * `enum4linux -P <DC-IP>`  or `enum4linux-ng -P <DC-IP> -oA file`&#x20;
  * `ldapsearch -H <DC-IP> -x -b "DC=<value>,DC=<values>" -s sub "*" | grep -m 1 -B 10 pwdHistoryLength`
  * `net accounts /domain`
  * [#domain-enumeration-generic](ad-and-powerview-modules.md#domain-enumeration-generic "mention")
* [Password Policy Guide](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994562\(v=ws.11\))

#### [credential-attacks](../../exploitation/credential-attacks/ "mention")

#### Spawn a Shell using credentials obtained using above or [initial-access-foothold](initial-access-foothold/ "mention")

#### Understand the User Compromised

* `whoami /all`&#x20;
* _**Interesting Privileges**_ [#windows-privileges](../../exploitation/privilege-escalation/windows.md#windows-privileges "mention")
  * SeImpersonatePrivilege
  * SeAssignPrimaryTokenPrivilege
  * SeBackupPrivilege
  * SeRestorePrivilege
  * SeDebugPrivilege
* _**Group Memberships**_

#### System and Domain Information

* `hostname`
* `systeminfo` (requires admin privileges)
* `set`  (environment variables)
* `Get-ChildItem Env:` or simply `dir env:`  (Powershell)

#### Enumerating Users and Groups with NET commands (CMD)

* `net help`&#x20;
* _**Domain Users**_
  * `net user /domain`&#x20;
  * `net user <username> /domain`
* _**Local Users**_
  * `net user`&#x20;
* _**Domain Groups**_
  * `net group /domain`&#x20;
  * Domain Admins, Administrators, Enterprise Admins, Server Operators and Backup Operators and any group with “Admin”
  * `net group  <Group-Name> /domain`&#x20;
* _**Local Groups**_
  * `net localgroup`&#x20;
  * `net localgroup <Group-Name>`&#x20;

#### **Logged-on Users and Sessions**

* `query user` or `quser`&#x20;
* We can find their credentials or tokens in memory
* Dump LSASS to get the password hash or Kerberos ticket
* `tasklist` displays a list of currently running processes.&#x20;
* `net session` lists the SMB sessions

#### **Identifying Service Accounts** (admin only)

* Search Using WMIC - `wmic service get` or `wmic service get Name,StartName`  or  `Get-WmiObject Win32_Service | select Name, StartName`&#x20;
* Search Using SC - `sc query state= all`  -> `sc qc <serivice-name>`&#x20;

#### Environment Variables and Registry

* `set`&#x20;
* _**Saved Auto-Logon Credentials**_
  * &#x20;Check `DefaultPassword` if saved and `AutoAdminLogon`  set to 1
  * `reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v keyword`&#x20;
  * HKLM\Security\Cache - credentials will be hashed and require cracking.
* _**Installed Applications**_
  * `reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall`&#x20;
* _**Searching the Registry**_
  * `reg query HKLM /f "password" /t REG_SZ /s`&#x20;

#### Scheduled Tasks

* `schtasks /query`
* `schtasks /create`
* `schtasks /run <task-name>`&#x20;

#### [bloodhound](bloodhound/ "mention")

#### [ad-and-powerview-modules.md](ad-and-powerview-modules.md "mention")

#### Tools

* [ADRecon](https://github.com/adrecon/ADRecon)
* [Group3r](https://github.com/Group3r/Group3r)
* [PingCastle](https://www.pingcastle.com/documentation/)
* [Active Directory Explorer](https://docs.microsoft.com/en-us/sysinternals/downloads/adexplorer)
* [rpcclient](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html)
* [enum4linux](https://labs.portcullis.co.uk/tools/enum4linux)/[enum4linux-ng](https://github.com/cddmp/enum4linux-ng)
* [windapsearch](https://github.com/ropnop/windapsearch)
* [ldapsearch](https://linux.die.net/man/1/ldapsearch)
