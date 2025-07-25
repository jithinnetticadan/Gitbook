# Binary Protection

<details>

<summary>Binary Guards</summary>

* DEP / NX : Prevents execution in non-executable memory regions
* ASLR : Randomizes memory layout to prevent predictable exploits
* High Entropy ASLR : Enhances ASLR randomness using 64-bit address space
* Stack Canaries (/GS) : Detects stack buffer overflows using guard values
* SafeSEH : Validates SEH handlers to prevent hijacking
* SEHOP : Validates SEH chain at runtime
* Control Flow Guard (CFG) : Validates indirect calls/jumps to prevent ROP
* Control Flow Integrity (CFI) : Enforces valid control flow paths
* Image Rebase / Relocation : Enables ASLR by allowing non-fixed loading
* Code Signing (Authenticode) : Verifies binary integrity and origin
* Strong Naming (.NET) : Ensures .NET assemblies are tamper-resistant
* Exploit Protection : Runtime hardening (ROP, heap integrity, etc.)
* W^X (Write XOR Execute) : Prevents memory from being writable and executable
* Guard Pages : Detects overflows/underflows via inaccessible memory
* Self-Integrity Checks : Detects tampering at runtime
* Anti-Debugging : Prevents or detects debugger attachment
* Anti-Tamper : Detects unauthorized binary modifications

</details>

#### Compatibility Chart

|   |   |   |
| - | - | - |
|   |   |   |
|   |   |   |
|   |   |   |

#### Tools

* **PESecurity** : [https://github.com/NetSPI/PESecurity](https://github.com/NetSPI/PESecurity)\
  `Set-ExecutionPolicy Bypass -Scope Process`\
  `Import-Module .\Get-PESecurity.psm1`\
  `Get-PESecurity -file <path-to-file>`\
  `Get-PESecurity -directory <path-todirectory> -recursive`
* **Binscoper** : [https://www.microsoft.com/en-us/download/details.aspx?id=44995](https://www.microsoft.com/en-us/download/details.aspx?id=44995)\
  `Binscope.exe /verbose /html /logfile outputfilepath.html <exe-file>`

