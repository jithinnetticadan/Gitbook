# PRTG Network Monitor

{% hint style="info" %}
* An agentless network monitor software used to monitor bandwidth usage, uptime and collect statistics from various hosts, including routers, switches, servers, and more.
* It works with an autodiscovery mode to scan areas of a network and create a device list. Once this list is created, it can gather further information from the detected devices using protocols such as ICMP, SNMP, WMI, NetFlow, and more.
* Devices can also communicate with the tool via a REST API. The software runs entirely from an AJAX-based website, but there is a desktop application available for Windows, Linux, and macOS.
{% endhint %}

## Discovery <a href="#discoveryfootprintingenumeration" id="discoveryfootprintingenumeration"></a>

* `sudo nmap -sV -p- --open -T4 <IP/CIDR>`
* It can typically be found on common web ports such as 80, 443, or 8080.
* We can see the service as part of the nmap scan `Indy httpd 17.3.33.2830 (Paessler PRTG bandwidth monitor)`

## Enumeration <a href="#discoveryfootprintingenumeration" id="discoveryfootprintingenumeration"></a>

* Default credentials `prtgadmin:prtgadmin`.&#x20;

## Exploitation

### Leveraging Known Vulnerabilities <a href="#leveraging-known-vulnerabilities" id="leveraging-known-vulnerabilities"></a>







