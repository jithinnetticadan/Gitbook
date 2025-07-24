# Binary Protection

#### Binary Guards

* ASLR
* DEP
* SafeSEH
* StrongNaming
* Authenticode
* Control Flow Guard
* HighEntropyVA

#### Tools

* **PESecurity** : [https://github.com/NetSPI/PESecurity](https://github.com/NetSPI/PESecurity)\
  `Set-ExecutionPolicy Bypass -Scope Process`\
  `Import-Module .\Get-PESecurity.psm1`\
  `Get-PESecurity -file <path-to-file>`\
  `Get-PESecurity -directory <path-todirectory> -recursive`
* **Binscoper** : [https://www.microsoft.com/en-us/download/details.aspx?id=44995](https://www.microsoft.com/en-us/download/details.aspx?id=44995)\
  `Binscope.exe /verbose /html /logfile outputfilepath.html <exe-file>`

