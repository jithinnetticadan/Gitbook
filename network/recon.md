---
layout:
  width: wide
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
  tags:
    visible: true
  actions:
    visible: true
---

# Recon

{% hint style="info" %}
**Footprinting Methodology** — work through these phases in order for every target/engagement:

1. **Host Discovery** – identify which hosts in scope are alive ([#identifying-hosts](recon.md#identifying-hosts "mention"))
2. **Port Scanning** – full TCP + UDP sweeps to find every open port ([#tcp-port-scan](recon.md#tcp-port-scan "mention"), [#udp-scan](recon.md#udp-scan "mention"))
3. **Service/Version Detection & NSE Scripts** – `-sV`/`-sC` and category-based script scans ([#script-scan](recon.md#script-scan "mention"))
4. **Result Parsing & Evidence Collection** – EyeWitness/Aquatone screenshots, import into Metasploit DB ([#parse-nmap-results](recon.md#parse-nmap-results "mention"))
5. **Manual Service Enumeration** – deep-dive every open port using the matching [host-based](enumeration/host-based/ "mention") page
6. **Vulnerability Identification** – Nuclei/searchsploit against the versions found ([#identifying-potential-vulnerabilities](recon.md#identifying-potential-vulnerabilities "mention"))
{% endhint %}

## Identifying Hosts

### Passive Methods

* Use wireshark to observe some ARP requests and replies, MDNS, and other basic [layer two](https://www.juniper.net/documentation/us/en/software/junos/multicast-l2/topics/topic-map/layer-2-understanding.html) packets
* `sudo tcpdump -i <interface>`
* [tcpdump](https://linux.die.net/man/8/tcpdump), [net-creds](https://github.com/DanMcInerney/net-creds), pktmon.exe, and [NetMiner](https://www.netminer.com/en/product/netminer.php)
* `sudo responder -I <interface> -A` <sup><sub>(Analyse mode)<sub></sup>

### Active Methods

* #### Host Discovery Scan

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
nmap -n -sn -PE -PP -PS22,80,443,445,3389 -PA22,80,443,445  --max-retries 2 --open -iL target.txt --excludefile exclude.txt -oA livehosts
nmap -sn -oA hostdiscovery -iL hosts.txt | grep for | cut -d" " -f5
fping -asgq <cidr-range>
## Troubleshoot
nmap -sn -oA hostdiscovery -iL hosts.txt -PE --packet-trace --reason --disable-arp-ping
```
{% endcode %}

* #### Banner Grabbing

```shellscript
nmap -sV -p- --script=banner <target>
nc -nv <IP> <port>
```

* #### LiveHost Scan

{% code fullWidth="false" %}
```shellscript
## Use sudo for -sS default beahaviour, without sudo defaults to -sT
nmap -p T:22,80-90,8080,445,443,8443,3389 -sV -sS -n -Pn --max-retries 2 --open -iL target.txt --excludefile exclude.txt -oA livehosts
nmap -sV -sC -sV -p- <IP>
sudo nmap -v -A -iL hosts.txt -oA Aggressive_Scan
```
{% endcode %}

<details>

<summary>Segregate IP's based on services</summary>

* [awesome-nmap-grep](https://github.com/leonjza/awesome-nmap-grep)

{% code lineNumbers="true" %}
```bash
#save as ips.sh
grep <port> */*.gnmap *.gnmap | cut -d ' ' -f2 |sort|uniq | grep -v "Nmap\|Ports" > service_ips.txt
grep "port-no/open/protocol" */*.gnmap *.gnmap | cut -d ' ' -f2 |sort|uniq | grep -v "Nmap\|Ports" > service_ips.txt
grep <service-nmae> */*.gnmap *.gnmap | cut -d ' ' -f2 |sort|uniq | grep -v "Nmap\|Ports" > service_ips.txt
grep -vi nmap */*.gnmap *.gnmap | cut -d ' ' -f2 |sort|uniq | grep -v "Nmap\|Ports" > live_ips.txt
grep -h "\\\\" */*.nmap *.nmap | grep "\: $" | cut -d ' ' -f4 |sort -g|uniq | grep -v "Nmap\|Ports" > smb2_ips.txt

printf "\nNmap IP Summary:\n"
for i in *.gnmap; do
    [ -f "$i" ] || break
    sed '1d;$d' $i | cut -d ' ' -f2 |sort|uniq > $i.ip
    wc -l $i.ip
done
```
{% endcode %}

</details>

* #### TCP Port Scan

```shellscript
nmap -sS -p- -sV -T3 -iL hosts.txt -oA full_port_scan
nmap -v -sS -Pn -sV -sC --max-retries 2 --open -p T:1,7,9,11,13,15,19,21,22,23,25,32,37,42,43,49,53,69,70,79,80,80-90,81,82,83,84,85,88,102,105,107,109,110,111,113,115,119,123,135,137,139,143,161,179,199,222,264,384,389,402,407,427,443,444,445,465,500,502,512,512-514,513,515,523,524,540,548,554,587,617,623,631,636,689,705,758,771,783,814,855,871,873,888,902,903,910,912,921,945,990,993,995,998,1000,1024,1030,1035,1080,1089,1090,1091,1098,1099,1100,1101,1102,1103,1128,1129,1158,1198,1199,1211,1220,1234,1241,1270,1300,1311,1352,1433,1434,1440,1468,1494,1521,1530,1533,1556,1577,1581,1582,1583,1604,1619,1630,1723,1755,1801,1811,1882,1883,1900,1947,2000,2049,2080,2082,2083,2100,2103,2121,2181,2199,2207,2222,2323,2362,2375,2376,2379,2380,2381,2443,2525,2533,2598,2601,2604,2638,2809,2947,2967,3000,3037,3050,3057,3080,3128,3200,3205,3217,3260,3268,3269,3273,3299,3300,3306,3311,3312,3343,3351,3389,3443,3460,3493,3500,3528,3628,3632,3660,3690,3780,3790,3817,3873,3938,4000,4092,4095,4105,4322,4343,4369,4433,4443,4444,4445,4446,4447,4448,4457,4567,4659,4679,4712,4713,4730,4750,4786,4840,4848,5000,5000-5200,5022,5037,5038,5040,5051,5060,5061,5093,5168,5222,5247,5250,5275,5347,5351,5353,5355,5392,5400,5405,5432,5432-5435,5433,5443,5498,5520,5521,5540,5554,5555,5560,5580,5600,5601,5631,5632,5666,5671,5672,5683,5701,5800,5814,5900,5920,5938,5984,5985,5986,5988,5989,6000,6001,6002,6050,6060,6070,6080,6082,6101,6106,6112,6262,6379,6400,6405,6410,6502,6503,6504,6514,6542,6556,6660,6661,6667,6905,6988,7000,7001,7021,7071,7077,7080,7100,7144,7181,7210,7373,7443,7474,7510,7547,7579,7580,7676,7700,7770,7777,7778,7787,7800,7801,7879,7900,7902,7990,7999,8000,8000-8200,8008,8009,8012,8014,8020,8023,8028,8030,8080,8081,8086,8087,8088,8089,8090,8095,8098,8099,8127,8161,8180,8205,8222,8300,8303,8333,8400,8443,8471,8488,8503,8512,8545,8649,8686,8730,8787,8800,8812,8834,8880,8883,8888,8899,8901,8902,8903,8983,9000,9001,9002,9042,9060,9080,9081,9084,9090,9091,9092,9099,9100,9111,9152,9160,9200,9300,9380,9389,9390,9391,9418,9440,9443,9471,9495,9524,9527,9530,9595,9600,9809,9855,9988,9999,10000,10001,10008,10050,10051,10080,10098,10162,10202,10203,10443,10616,10628,11000,11099,11211,11234,11333,12174,12203,12221,12345,12397,12401,12489,13184,13364,13500,13724,13782,13838,14330,15200,15671,15672,16102,16992,16993,17185,17200,17472,17775,17776,17777,17778,17781,17782,17783,17784,17790,17791,17798,17988,18080,18264,18881,19300,19810,19888,20000,20010,20031,20034,20080,20101,20111,20171,20222,20293,20389,20390,20391,20394,20396,20398,20404,20410,20411,20443,22001,22002,22099,22222,23472,23791,23943,25000,25025,25565,25672,26000,26122,27000,27017,27019,27080,27864,27888,28017,28222,28784,30000,31001,31099,32764,32913,34205,34443,34962,34963,34964,36972,37718,37777,37890,37891,37892,38008,38010,38080,38102,38292,40007,40317,41025,41080,41523,41524,44334,44441,44442,44443,44444,44818,45230,46823,46824,47001,47002,48000,48001,48004,48005,48006,48007,48008,48009,48010,48899,49152,49153,49154,50000,50013,50070,50090,52302,52311,52752,55553,55580,57772,61616,62078,62514,65100,65535 --script "modbus-discover,supermicro-ipmi-conf,smb-protocols,http-default-accounts,smb-vuln-cve2009-3103,http-vuln-cve2011-3192,msrpc-enum,cisco-siet,smb-security-mode,smb-os-discovery,broadcast-hid-discoveryd,broadcast-jenkins-discover,http-hp-ilo-info,http-sap-netweaver-leak,https-redirect,rdp-ntlm-info,smb-vuln-webexec,ubiquiti-discovery,banner,finger,ftp-anon,http-git,http-gitweb-projects-enum,http-headers,http-methods,http-open-proxy,http-php-version,http-title,http-trace,http-vmware-path-vuln,http-vuln-cve2010-0738,ajp-headers,imap-capabilities,iscsi-info,ldap-rootdse,ms-sql-info,msrpc-enum,mysql-info,nbstat,nfs-ls,nfs-showmount,nfs-statfs,p2p-conficker,pop3-capabilities,realvnc-auth-bypass,rmi-dumpregistry,rpcinfo,rsync-list-modules,smb-enum-shares,smb-os-discovery,smb-system-info,snmp-interfaces,snmp-netstat,upnp-info,snmp-sysdescr,ssl-heartbleed,ssl-cert-intaddr,ssl-cert,vnc-info and not fingerprint-strings" --script-args=cisco-siet.get,checkconficker=1,safe=1,smbbasic=1 --script-timeout 60s -iL target(from-hostdicovery).txt --excludefile exclude.txt -oA tcp_liveonly
## Troubleshoot
sudo nmap -iL hosts.txt -p- --packet-trace --disable-arp-ping -Pn -n --reason
## Common ports -p 80,443,8000,8080,8180,8888,10000
## Nmap grep cheatsheet to "cut through the noise" and extract the most useful information from the scan.
https://github.com/leonjza/awesome-nmap-grep
```

* #### UDP Scan

{% code fullWidth="false" %}
```shellscript
nmap -Pn -sV -sU -sC -v -T3 --max-retries 2 --host-timeout 15m --open -p U:53,69,88,111,123,137,161,427,500,623,942,1434,1900,2228,3702,5060,5351,5353,5632,10001,11211,30718,41794,65535,65535 --script "banner,ipmi-version,tftp-enum,upnp-info,snmp-brute,snmp-hh3c-logins,snmp-info,snmp-interfaces,snmp-ios-config,snmp-netstat,snmp-processes,snmp-sysdescr,snmp-win32-services,snmp-win32-shares,snmp-win32-software,snmp-win32-users" --script-timeout 60s --min-hostgroup 128 --version-intensity 0 -iL target(from-hostdoscovery).txt --excludefile exclude.txt -oA udp_liveonly
## Troubleshoot
sudo nmap -iL hosts.txt -p- -sV -sU -Pn -n --disable-arp-ping --packet-trace --reason 
## Nmap grep cheatsheet to "cut through the noise" and extract the most useful information from the scan.
https://github.com/leonjza/awesome-nmap-grep
```
{% endcode %}

* #### Script Scan

```shellscript
grep -ri "<keyword>" /usr/share/nmap/scripts/
## limit the scan to specific ports that were earlier identified as open
nmap -sC -p- -oA script_scan -iL hosts.txt
## Scan Categories - auth, broadcast, brute, default, discovery, dos, exploit, external, fuzzer, intrusive, malware, safe, version, vuln
nmap -p- -oA script_scan -iL hosts.txt --script auth,broadcast,brute,default,discovery,exploit,fuzzer,intrusive,safe,vuln
## Nmap grep cheatsheet to "cut through the noise" and extract the most useful information from the scan.
https://github.com/leonjza/awesome-nmap-grep
```

### Parse Nmap Results

* [**EyeWitness**](https://github.com/FortyNorthSecurity/EyeWitness) <sup><sub>(for web app evidence collection)<sub></sup>
  * `eyewitness --web -x *.xml -d <folder>`
  * `eyewitness -f scope.txt -d eyewitness-results`
* [**`Aquatone`**](https://github.com/michenriksen/aquatone) `or` [`aquatone`](https://github.com/shelld3v/aquatone) <sup><sub>`(for web app evidence collection)`<sub></sup>
  * `cat nmap.xml | ./aquatone -nmap`
* **Metasploit**
  * `workspace -a <name>` -> `workspace <name>` -> `db_import *.xml` -> `load alias` -> `alias sv services`
  * Full Metasploit workflow (modules, sessions, meterpreter, msfvenom): [metasploit-framework.md](exploitation/metasploit-framework.md "mention")
* [awesome-nmap-grep](https://github.com/leonjza/awesome-nmap-grep) - Nmap grep cheatsheet to "cut through the noise" and extract the most useful information from the scan.

## Identifying Users

### Passive

* [#usernames-wordlist-generation](exploitation/credential-attacks/password-spraying-stuffing-and-defaults.md#usernames-wordlist-generation "mention")
* Username List -> [Insidetrust](https://github.com/insidetrust/statistically-likely-usernames)

### Active

* [#username-enumeration](exploitation/credential-attacks/password-spraying-stuffing-and-defaults.md#username-enumeration "mention")
* `kerbrute userenum -d <domain> --dc <IP> wordlist.txt -o valid_ad_users` <sup><sub>(<sub></sup>[<sup><sub>Kerbrute<sub></sup>](https://github.com/ropnop/kerbrute)<sup><sub>)<sub></sup>

## Identifying Potential Vulnerabilities

### Active

* #### Automated HTTP/S Scan

{% code lineNumbers="true" %}
```shellscript
autorecon -t targets.txt -o autorecon-results
nmapAutomator.sh <IP> All
nmapAutomator.sh <IP> Vulns
sudo nmap -iL host.txt -p- -sV --script vuln 
```
{% endcode %}

### Passive

* #### Exploit Checks

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
searchsploit -p -w -e --nmap nmap.xml -j searchsploit-output.json
ExploitDB
```
{% endcode %}

## Tools

* Fuller OSINT lookup technique table (WHOIS, DNS, web archive, social media, code repos): [passive.md](../osint/passive.md "mention")
* Banner Grabbing - Netcat, curl
* Port Scanning - Nmap, Masscan, Unicornscan
* OS Fingerprinting - Nmap, Xprobe2
* Service Enumeration - Nmap
* Vulnerability Scanning - Nessus, OpenVAS, Nikto, Nuclei
* Network Mapping - Traceroute, Nmap
* Web Spidering - Burp Suite Spider, OWASP ZAP Spider, Scrapy
* [Fping](https://fping.org/)
* [Domaintools](https://www.domaintools.com/)
* [PTRArchive](http://ptrarchive.com/)
* [ICANN](https://lookup.icann.org/lookup)
* [BGP Toolkit](https://bgp.he.net/)
* [viewdns.info](https://viewdns.info/)
* [AutoRecon](https://github.com/AutoRecon/AutoRecon)
* [nmapAutomator](https://github.com/21y4d/nmapAutomator)
