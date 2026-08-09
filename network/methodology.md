# Methodology

{% hint style="warning" %}
This is **not** a rigid, linear checklist to run once per machine and forget. Treat it as a loop you repeat constantly - every new user, every new privilege level, every new machine, every new subnet. A credential can turn up anywhere: a code comment, a saved browser login, a config file, a memory dump, a backup, a clipboard, a Sticky Note, PowerShell history. If the "standard" checks come back empty, keep thinking of other places to look before moving on - don't miss a link just because it wasn't on the obvious list.
{% endhint %}

## Big Picture

```
External Foothold  --->  Root/Admin on that box  --->  Pivot  --->  Internal Network
                                                                          |
                                                                          v
        Domain Compromise  <---  Escalate + Lateral Move  <---  AD Enumeration
```

* **External** - compromise an internet/perimeter-facing box (web app, exposed service) as a low-priv user, then escalate to root/admin on it.
* **Pivot** - from that root/admin foothold, find a route into a network you couldn't previously reach.
* **Internal (AD)** - repeat the same loop machine-by-machine, layered with AD-specific enumeration, until Domain Admin / the objective is reached.

Every phase below runs on the same underlying engine: **the Core Loop.**

## Pre-Engagement Checklist

* [ ] Confirm scope - in-scope IPs/ranges/URLs, any fragile/do-not-scan hosts, testing window.
* [ ] Confirm VPN/lab connectivity and DNS resolution for target domain(s).
* [ ] Set up note-taking (CherryTree/Obsidian/Joplin) and a screenshot/logging tool (`script -a`, Snipping Tool, or terminal logging) before touching anything.
* [ ] Create the host tracker (see [Track As You Go](#track-as-you-go "mention") below) before you start - not after the first box.
* [ ] Re-read the objective/flags required so you know what "done" looks like.

## The Core Loop

{% hint style="danger" %}
**Golden rule:** every time you compromise a new user OR a new machine, restart enumeration **from zero** on that context. Do not assume anything carries over from the previous user/machine, and do not assume your first enumeration pass on this new context was complete just because it found the thing that got you here. Treat every new foothold as if you know nothing about it yet.
{% endhint %}

Repeat this loop at **every** stage of the engagement - external and internal, for every new user and every new machine:

1. **Enumerate** the current target/foothold thoroughly, from scratch - web app, open ports, running services. See [Recon](recon.md "mention") for external footprinting and [Enumeration](enumeration/README.md "mention") for host/service-based enumeration.
2. **Exploit** a vulnerability/misconfiguration to gain access, or authenticate with credentials already found.
3. **Enumerate as the new user, starting from zero** - don't just check the one thing you expect; go through the full checklist again as if this were a brand-new machine. Always list files including hidden ones (`ls -la` / `dir /a`) as a default habit right after every login/shell. What does this user have access to? Any credentials lying around (files, history, configs, saved sessions)? See [Credentials Harvesting](exploitation/credentials-harvesting/ "mention").
4. **Privilege escalate** on the current machine - [Linux](exploitation/privilege-escalation/linux.md "mention") / [Windows](exploitation/privilege-escalation/windows.md "mention").
5. **Re-enumerate from zero again, even after reaching root/admin.** Don't assume the trail ends here - new files, credential stores, and network interfaces are often only visible or decryptable at the highest privilege level on the box.
6. **Check for pivot opportunities** - network interfaces, routing tables, ARP cache, and any other subnets reachable from this host. See [Pivoting, Tunneling & Port Forwarding](exploitation/pivoting-tunneling-and-port-forwarding.md "mention") (ligolo-ng, chisel, sshuttle, proxychains).
7. **Move to the next machine/network and restart the entire loop from step 1 - from zero.** Never carry forward an assumption that this new machine is similar to the last one.

## Checklist for Every Loop Iteration

{% hint style="warning" %}
Run through this list at every single pass of the loop above - these are the things that are easiest to forget while heads-down chasing the next box.
{% endhint %}

* [ ] **Flag hunt** - after *this* privilege gain, check for `local.txt`/`proof.txt`/flag files in home directories, Desktop, and the current user's profile. Don't wait until "the end."
* [ ] **Credential/hash reuse - broader than you think** - spray any credential or hash found against *every* known user and host so far, not just where it was found. Also try it against **other usernames**, not just the one it was cracked for - e.g. a cracked `sa` (MSSQL) password may also work for `Administrator`, since admins frequently reuse passwords across accounts.
* [ ] **Local vs. domain account** - confirm whether a found credential is a local account (scoped to one box) or a domain account (works everywhere) before assuming it unlocks other machines.
* [ ] **Background enumeration** - is Responder/`ntlmrelayx` (or equivalent) still passively listening? Start it as soon as you're internal and leave it running while you manually enumerate elsewhere.
* [ ] **Other paths logged?** - note every potential entry point you've spotted so far, even ones you're not pursuing right now - don't tunnel-vision on the first lead.
* [ ] **Evidence captured** - command + output + timestamp screenshotted/logged for this step, not deferred to "write up later."
* [ ] **Time check** - stuck on this step for 45-60+ minutes with no progress? Don't repeat the same failed attempt - deliberately switch approach/tool/wordlist, step back and re-enumerate, or switch targets instead of sinking more time in.
* [ ] **Payload actually blocked, or vuln not real?** - if an exploit/payload failed, rule out AV/EDR/firewall interference with an alternate payload before writing off the technique entirely.

## Phase 1 - External Network

### 1.1 Footprinting & Port Scanning

* [ ] Host discovery sweep across the full external scope.
* [ ] Full TCP **and** UDP port scan (not just top-1000) - see [Recon](recon.md "mention").
* [ ] Service/version detection (`-sV`) + NSE default/vuln scripts on every open port.
* [ ] Screenshot every web service found (EyeWitness/Aquatone) so nothing gets skipped visually.
* [ ] Re-run scans if a host was unreachable/timed out the first time - don't assume "no response" = "no service."

### 1.2 Service-by-Service Enumeration

For every open port, work through the matching page under [Enumeration](enumeration/host-based/README.md "mention") - don't skip a service just because it looks minor (SNMP, FTP, and SMTP are common easy wins):

| Port(s) | Service | Reference |
| --- | --- | --- |
| 21/2121/990 | FTP/FTPS | [FTP/FTPS](enumeration/host-based/ftp-ftps-t21-2121-990.md "mention") |
| 22 | SSH | [SSH](enumeration/host-based/ssh-t22.md "mention") |
| 25/465/587 | SMTP | [SMTP](enumeration/host-based/smtp-t25-465-587-2525.md "mention") |
| 53 | DNS | [DNS](enumeration/host-based/dns-tu53.md "mention") |
| 80/443 | HTTP/S | [Recon & Enum](../web/recon-and-enum.md "mention") + [Vulnerabilities](../web/vulnerabilities/README.md "mention") |
| 88 | Kerberos | [Kerberos](enumeration/host-based/kerberos-u88.md "mention") |
| 111/2049 | NFS | [NFS](enumeration/host-based/nfs-tu111-2049.md "mention") |
| 135/49152-65535 | RPC | [RPC](enumeration/host-based/rpc-tu135-137-138-139.md "mention") |
| 139/445 | SMB | [SMB](enumeration/host-based/smb-t139-445-u137-138.md "mention") |
| 161/162 | SNMP | [SNMP](enumeration/host-based/snmp-u161-162.md "mention") |
| 389/636 | LDAP/S | [LDAP/LDAPS](enumeration/host-based/ldap-ldaps-t389-636.md "mention") |
| 1433 | MSSQL | [MSSQL DB](enumeration/host-based/mssql-db-t1433-2433-u1434.md "mention") |
| 1521 | Oracle DB | [Oracle DB](enumeration/host-based/oracle-db-t1521-1526.md "mention") |
| 3306 | MySQL | [MySQL DB](enumeration/host-based/mysql-db-t3306.md "mention") |
| 3389 | RDP | [RDP](enumeration/host-based/rdp-t3389.md "mention") |
| 5432 | PostgreSQL | [Postgres DB](enumeration/host-based/postgres-db-t5432.md "mention") |
| 5985/5986 | WinRM | [WinRM](enumeration/host-based/winrm-t5985-5986.md "mention") |
| 8080/10000 | Webmin/alt-HTTP | [Webmin](enumeration/host-based/webmin-t10000.md "mention") |

### 1.3 Web Application Testing Checklist

* [ ] Passive + active recon: [Recon & Enum](../web/recon-and-enum.md "mention") (subdomains, vhosts, dorking, crawling, authenticated crawl once you have any creds).
* [ ] **Virtual hosts** - if the app behaves differently (or not at all) by IP, add the hostname to `/etc/hosts` and browse by the **exact URL/hostname**, not the raw IP.
* [ ] Authentication testing - brute force/defaults, [Authentication](../web/vulnerabilities/authentication/README.md "mention").
* [ ] Injection - [SQL Injection](../web/vulnerabilities/sql-injection.md "mention"), [OS Injection](../web/vulnerabilities/os-injection.md "mention"), [XXE](../web/vulnerabilities/xml-external-entity-xxe-injection.md "mention"), [SSTI](../web/vulnerabilities/server-side-template-injection-ssti.md "mention").
* [ ] File-based - [File Upload](../web/vulnerabilities/file-upload.md "mention") (on Windows/IIS, if a straightforward upload is blocked, try a backslash-prefixed path like `\\file\shell.aspx` - the server may auto-correct/normalize it in a way that slips past extension/path validation), [File Inclusion](../web/vulnerabilities/file-inclusion.md "mention").
* [ ] **File disclosure/LFI found?** - look up the target software's **default config file paths and filenames** online rather than guessing blindly; the exact path is almost always documented. If nginx is present, also check `cat /etc/nginx/sites-enabled/default` for vhost/config info once you have file read access.
* [ ] Access control / logic flaws - [Access Control](../web/vulnerabilities/access-control.md "mention"), [IDOR](../web/vulnerabilities/insecure-direct-object-references-idor.md "mention").
* [ ] Client-side - [XSS](../web/vulnerabilities/cross-site-scripting-xss.md "mention"), [CSRF](../web/vulnerabilities/cross-site-request-forgery-csrf.md "mention"), [CORS](../web/vulnerabilities/cross-origin-resource-sharing-cors.md "mention").
* [ ] Known CMS/app-specific checks if fingerprinted - WordPress/Jenkins/GitLab/Tomcat/etc pages under `web/`.
* [ ] Check for a matching CVE/public exploit once the exact software + version is confirmed (searchsploit/ExploitDB).

### 1.4 Gaining Initial Foothold

* [ ] Try the most obvious vector first (public exploit, default creds, upload-to-shell) before deep manual work.
* [ ] If nothing obvious works, revisit 1.1-1.3 - a missed service or an unauthenticated-but-forgotten endpoint is the most common reason for a stuck box.

### 1.5 Linux Privilege Escalation Checklist

Full command reference: [Privilege Escalation - Linux](exploitation/privilege-escalation/linux.md "mention"). Quick-fire checklist so nothing gets skipped:

* [ ] Kernel/OS version -> known kernel exploit?
* [ ] `sudo -l` - what can this user run as root?
* [ ] SUID/SGID binaries -> check against GTFOBins.
* [ ] Linux capabilities (`getcap -r / 2>/dev/null`).
* [ ] Cron jobs / systemd timers - writable scripts or PATH abuse.
* [ ] Writable files/services owned by root that this user can modify.
* [ ] Docker/LXD group membership (container escape to root).
* [ ] NFS exports with `no_root_squash`.
* [ ] Credentials in config files, env vars, history, `/var/www`, `/opt`.
* [ ] Check if `/etc/passwd` is writable by mistake - if so, you can remove the password field for `root` entirely (or add a new UID 0 entry) to gain root without needing a password at all.
* [ ] Run linPEAS/les.sh even if you think you already found the path - confirm nothing else was missed.

### 1.6 Windows Privilege Escalation Checklist

Full command reference: [Privilege Escalation - Windows](exploitation/privilege-escalation/windows.md "mention"). Quick-fire checklist:

* [ ] `systeminfo` / patch level -> known local privesc exploit (PrintNightmare, etc.)?
* [ ] `whoami /priv` and `whoami /groups` - dangerous privileges (SeImpersonate, SeBackup, SeDebug, etc.)?
* [ ] Service misconfigurations - unquoted service paths, weak service/binary permissions, `AlwaysInstallElevated`.
* [ ] Scheduled tasks running as SYSTEM/admin with a writable target.
* [ ] Stored credentials - Credential Manager, PuTTY/WinSCP sessions, unattend.xml, registry autologon, IIS web.config.
* [ ] Token impersonation opportunities (Potato-family exploits) if SeImpersonate/SeAssignPrimaryToken is present - or, via an existing Meterpreter session, list and steal a privileged process token directly:
  ```
  meterpreter > ps
  meterpreter > steal_token <PID>
  ```
* [ ] Always test known **high-impact Windows RCEs** (EternalBlue/MS17-010, PrintNightmare, SMBGhost, etc.) against SMB/RPC services - even if the port isn't directly reachable, port-forward to it first (e.g. a service only bound internally/to localhost) and test from there.
* [ ] Run winPEAS even if you think you already found the path - confirm nothing else was missed.

### 1.7 Post-Root Re-Enumeration (External Box)

* [ ] Re-check for additional credentials now visible only as root/admin (LSASS dump, `/etc/shadow`, password managers, browser profiles for all users).
* [ ] List all network interfaces and routes - this is the box that gets you into the internal network.
* [ ] Check for any second NIC / dual-homed configuration - this is usually the intended pivot point.

## Phase 2 - Pivoting

### 2.1 Identify Pivot Targets

* [ ] `ip a`/`ifconfig` and `ip route`/`route print` on the compromised box - what other subnets does it see?
* [ ] `arp -a` - what hosts has this box already talked to?
* [ ] Any existing VPN/RDP/SSH sessions on the box that reveal other internal hosts?

### 2.2 Establish the Tunnel

* [ ] Pick a tool based on what's available: ligolo-ng (agent-based, cleanest for full subnet routing), chisel (simple reverse SOCKS/port-forward), sshuttle (if SSH access), or manual SSH `-D`/`-L`/`-R` + proxychains.
* [ ] See [Pivoting, Tunneling & Port Forwarding](exploitation/pivoting-tunneling-and-port-forwarding.md "mention") for exact commands.

### 2.3 Validate the Pivot

* [ ] Confirm connectivity through the tunnel before assuming it works - `proxychains nmap -sT -Pn <internal-host>` or a simple curl/ping equivalent through the tunnel.
* [ ] Re-scan the newly reachable subnet the same way as Phase 1 (host discovery -> full port scan) - don't assume you already know what's there.

## Phase 3 - Internal Network / Active Directory

### 3.1 Initial AD Enumeration - Unauthenticated

* [ ] Null session / anonymous SMB enumeration.
* [ ] LDAP anonymous bind.
* [ ] DNS zone transfer attempt / zone enumeration.
* [ ] NetBIOS/SMB host + share listing across the subnet (`nxc smb <range>`).

### 3.2 Initial AD Enumeration - With Any Credentials

* [ ] Full BloodHound collection (SharpHound/bloodhound-python) as soon as *any* domain credential (even a low-priv one) is available - see [BloodHound](active-directory/enumeration/bloodhound/README.md "mention").
* [ ] Domain/forest trusts, GPOs, OU structure - [AD & PowerView Modules](active-directory/enumeration/ad-and-powerview-modules.md "mention"), [Domain Enum](active-directory/enumeration/domain-enum.md "mention").
* [ ] Share enumeration across the domain (Snaffler/PowerHuntShares/manual) - SYSVOL, NETLOGON, and any custom shares.
* [ ] `nxc`/BloodHound password/description-field/GPP sweep for quick wins.

### 3.3 Credential Access Techniques

* [ ] Kerberoasting - [Kerberoasting](active-directory/exploitation/credential-harvesting/kerberoasting.md "mention").
* [ ] AS-REP Roasting - [AS-REP Roasting](active-directory/enumeration/initial-access-foothold/as-rep-roasting.md "mention").
* [ ] LLMNR/NBT-NS poisoning with Responder - [LLMNR/NBT-NS Poisoning](active-directory/enumeration/initial-access-foothold/llmnr-nbt-ns-poisoning.md "mention") (should already be running passively per the checklist above).
* [ ] Coercion + relay attacks (PetitPotam/PrinterBug/DFSCoerce) - [Coercion/Relay Attacks](active-directory/enumeration/initial-access-foothold/coercion-relay-attacks.md "mention").
* [ ] GPP/cpassword in SYSVOL - [Group Policy Preferences (GPP)](active-directory/exploitation/credential-harvesting/group-policy-preferences-gpp.md "mention").
* [ ] DCSync, if rights already allow it - [ACL's - DCSync](active-directory/exploitation/credential-harvesting/acls-dcsync.md "mention").

### 3.4 Privilege Escalation Paths (AD)

* [ ] ACL abuse discovered via BloodHound (GenericAll/GenericWrite/WriteDacl/ForceChangePassword/AddMember, etc.) - [Lateral Movement (ACLs)](active-directory/exploitation/lateral-movement/README.md "mention").
* [ ] Kerberos delegation abuse (unconstrained/constrained/RBCD) - [Kerberos Delegation](active-directory/exploitation/privesc/kerberos-delegation.md "mention").
* [ ] AD CS - run `certipy find -vulnerable` on every engagement, even if AD CS wasn't mentioned as in-scope - [AD Certificate Services](active-directory/ad-certificate-services/README.md "mention") (ESC1-16 + chaining).
* [ ] Crack any Kerberoast/AS-REP hashes obtained, then loop back to [Checklist for Every Loop Iteration](#checklist-for-every-loop-iteration "mention") (credential reuse).

### 3.5 Lateral Movement

* [ ] Pass-the-hash / overpass-the-hash with any NTLM hash obtained.
* [ ] PsExec/WinRM/WMI/scheduled-task remote execution - [Lateral Movement](exploitation/lateral-movement/README.md "mention").
* [ ] Watch for the Kerberos "double hop" issue when chaining through a WinRM session - [Kerberos Double Hop Issue](active-directory/exploitation/lateral-movement/kerberos-double-hop-issue.md "mention").
* [ ] Re-run 3.1-3.4 from the newly compromised machine's vantage point - it may see hosts/shares the previous box couldn't.

### 3.6 Domain Dominance / Final Objective

* [ ] DCSync once DA-equivalent rights are held.
* [ ] Golden/Silver/Diamond ticket if persistence/further movement is needed - [Golden Ticket](active-directory/exploitation/privesc/golden-ticket.md "mention"), [Silver Ticket](active-directory/exploitation/privesc/silver-ticket.md "mention"), [Diamond Ticket](active-directory/exploitation/privesc/diamond-ticket.md "mention").
* [ ] **Password audit with** [**DPAT**](https://github.com/clr2of8/DPAT) - once you've DCSync'd/dumped NTDS and cracked as many hashes as possible, run DPAT against the NTDS dump + cracked passwords list. This generates the password-reuse/weak-password statistics (top 10 passwords, % cracked, DA/EA passwords cracked, etc.) needed for the report appendix - don't leave this until after the exam, capture it now while the data is fresh.
* [ ] Confirm every required flag across every compromised machine has actually been captured and recorded - not just DA.

### 3.7 Post-Compromise Re-Enumeration

* [ ] Check for trusts to other domains/forests - is there a second domain in scope reachable from here?
* [ ] Re-check BloodHound with the new (higher) privilege level - previously hidden ACLs/paths may now resolve.
* [ ] Confirm no additional subnets are reachable from the newly compromised DC/servers.

## Places Credentials Hide (Don't Skip These)

* Source code, comments, `.git` history/logs
* Browser saved passwords, history, autofill, session cookies
* Configuration files (web app configs, `.env`, CI/CD pipeline definitions)
* Command history (`.bash_history`, PowerShell `ConsoleHost_history.txt`)
* Memory (LSASS/Mimikatz, `/proc`/mimipenguin)
* Backup files, scheduled tasks, cron jobs - found a `.vhd`/`.vhdx`/`.vmdk`? Mount it, see [Mount VHDX/VMDK](enumeration/os-based/mount-vhdx-vmdk.md "mention") - backups are a common place to find credentials or a full copy of `ntds.dit`/SAM.
* Environment variables, clipboard, Windows Sticky Notes
* Hardcoded credentials in scripts/binaries
* Shares (SMB/NFS) - Snaffler, PowerHuntShares, or manual browsing
* AD-specific: GPP/SYSVOL, user/computer description fields, BloodHound-surfaced ACL-abuse paths

{% hint style="info" %}
When any of these turn up a hit, go re-run step 3 of the Core Loop with the new credential/access - it may unlock a completely different path you'd already written off.
{% endhint %}

## Track As You Go

Keep a running tracker for every host you touch - it's easy to forget a lead once you're 3 machines further into the engagement.

| Host/IP | Access Level | Creds/Hashes Found | Notes / Next Steps |
| ------- | ------------- | ------------------- | ------------------- |
|         |               |                     |                     |

Update it the moment you gain a new user, crack a hash, or find a new credential - not at the end of the day.

## Exam-Day Time Management

* [ ] Time-box each machine/phase - if truly stuck for 45-60+ minutes, switch targets and come back later with fresh eyes.
* [ ] Prioritize capturing available flags over perfecting a fully clean chain - partial credit exists, a skipped flag doesn't.
* [ ] Reserve time at the end of the exam window specifically for re-checking the tracker for any unresolved leads before submitting.
* [ ] Keep evidence/screenshots organized by host as you go so report writing afterward isn't a second full pass through everything.