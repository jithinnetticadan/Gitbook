# Binary Protection

<details>

<summary>Binary Guards</summary>

* **DEP / NX** : Prevents execution in non-executable memory regions
* **ASLR** : Randomizes memory layout to prevent predictable exploits
* **High Entropy ASLR** : Enhances ASLR randomness using 64-bit address space
* **Stack Canaries (GS)** : Detects stack buffer overflows using guard values
* **SafeSEH** : Validates SEH handlers to prevent hijacking
* **SEHOP** : Validates SEH chain at runtime
* **Control Flow Guard (CFG)** : Validates indirect calls/jumps to prevent ROP
* **Control Flow Integrity (CFI)** : Enforces valid control flow paths
* **Image Rebase / Relocation** : Enables ASLR by allowing non-fixed loading
* **Code Signing (Authenticode)** : Verifies binary integrity and origin
* **Strong Naming (.NET)** : Ensures .NET assemblies are tamper-resistant
* **Exploit Protection** : Runtime hardening (ROP, heap integrity, etc.)
* **W^X (Write XOR Execute)** : Prevents memory from being writable and executable
* **Guard Pages** : Detects overflows/underflows via inaccessible memory
* **Self-Integrity Checks** : Detects tampering at runtime
* **Anti-Debugging** : Prevents or detects debugger attachment
* **Anti-Tamper** : Detects unauthorized binary modifications

</details>

#### Compatibility Chart

<table><thead><tr><th width="238.66668701171875">Protection</th><th width="56.66668701171875" data-type="checkbox">32-bit</th><th width="53.6666259765625" data-type="checkbox">64-bit</th><th width="355">Supported Technologies</th></tr></thead><tbody><tr><td>DEP / NX</td><td>true</td><td>true</td><td>C/C++, .NET, Java, Delphi, Go, Rust, NetCOBOL, VB, Python, Electron, Swift</td></tr><tr><td>ASLR</td><td>true</td><td>true</td><td>C/C++, .NET, Java, Delphi, Go, Rust, NetCOBOL, VB, Python, Electron, Swift</td></tr><tr><td><strong>High Entropy ASLR</strong></td><td>false</td><td>true</td><td>C/C++, .NET (64-bit), NetCOBOL (.NET), Swift</td></tr><tr><td><strong>Stack Canaries (GS)</strong></td><td>true</td><td>true</td><td>C/C++, Rust, Go</td></tr><tr><td><strong>SafeSEH</strong></td><td>true</td><td>false</td><td>C/C++ (MSVC 32-bit)</td></tr><tr><td><strong>SEHOP</strong></td><td>true</td><td>true</td><td>C/C++, .NET, NetCOBOL</td></tr><tr><td><strong>Control Flow Guard (CFG)</strong></td><td>false</td><td>true</td><td>C/C++ (MSVC), .NET Native</td></tr><tr><td><strong>Control Flow Integrity (CFI)</strong></td><td>true</td><td>true</td><td>C/C++ (Clang, MSVC), Rust</td></tr><tr><td><strong>Image Rebase / Relocation</strong></td><td>true</td><td>true</td><td>C/C++, .NET, Delphi, NetCOBOL</td></tr><tr><td><strong>Code Signing (Authenticode)</strong></td><td>true</td><td>true</td><td>C/C++, .NET, Java, Delphi, NetCOBOL, Python, Electron, Swift</td></tr><tr><td><strong>Strong Naming (.NET)</strong></td><td>true</td><td>true</td><td>.NET, NetCOBOL (.NET)</td></tr><tr><td><strong>Exploit Protection</strong></td><td>true</td><td>true</td><td>C/C++, .NET, Java, NetCOBOL</td></tr><tr><td><strong>W^X (Write XOR Execute)</strong></td><td>true</td><td>true</td><td>C/C++, Rust, Go</td></tr><tr><td><strong>Guard Pages</strong></td><td>true</td><td>true</td><td>C/C++, .NET, Java</td></tr><tr><td><strong>Self-Integrity Checks</strong></td><td>true</td><td>true</td><td>C/C++, .NET, Java, NetCOBOL</td></tr><tr><td><strong>Anti-Debugging</strong></td><td>true</td><td>true</td><td>C/C++, .NET, Java, Delphi, NetCOBOL</td></tr><tr><td><strong>Anti-Tamper</strong></td><td>true</td><td>true</td><td>C/C++, .NET, Java, Delphi, NetCOBOL</td></tr></tbody></table>

#### Tools

* [PESecurity](https://github.com/NetSPI/PESecurity)

{% code lineNumbers="true" %}
```powershell
Set-ExecutionPolicy Bypass -Scope Process
Import-Module .\Get-PESecurity.psm1
Get-PESecurity -file <path-to-file>
Get-PESecurity -directory <path-todirectory> -recursive
```
{% endcode %}

* [BinScoper](https://www.microsoft.com/en-us/download/details.aspx?id=44995) - `Binscope.exe /verbose /html /logfile outputfilepath.html <exe-file>`
