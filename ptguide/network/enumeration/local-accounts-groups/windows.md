# Windows

## User Enumeration

* `whoami`
* `whoami /priv`
* `net user <username>`
* `Get-LocalUser`
* `Get-LocalUser -Name <username>`

## Groups Enumeration

* `whoami /groups`
* `net localgroup` <sup><sub>(List All Local Groups)<sub></sup>
* `net localgroup "Administrators"`  <sup><sub>(See Members of a Specific Group)<sub></sup>
* `Get-LocalGroupMember -Group "Administrators"`
