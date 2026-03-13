# DNS - TU53

### Default Configuration

* DNS server [Bind9](https://www.isc.org/bind/) is very often used on Linux-based distributions.&#x20;
* **Local DNS Configuration -** `cat /etc/bind/named.conf.local`&#x20;

### Dangerous Settings

* <table data-header-hidden><thead><tr><th width="153">Option</th><th>Description</th></tr></thead><tbody><tr><td><code>allow-query</code></td><td>Defines which hosts are allowed to send requests to the DNS server.</td></tr><tr><td><code>allow-recursion</code></td><td>Defines which hosts are allowed to send recursive requests to the DNS server.</td></tr><tr><td><code>allow-transfer</code></td><td>Defines which hosts are allowed to receive zone transfers from the DNS server.</td></tr><tr><td><code>zone-statistics</code></td><td>Collects statistical data of zones.</td></tr></tbody></table>

### Footprinting the Service

* **DIG - NS Query -** `dig ns <domain> @<DNS-server-IP>`&#x20;
* **DIG - Version Query -** `dig CH TXT version.bind <DNS-server-IP>`&#x20;
* **DIG - ANY Query -** `dig any <domain> @<DNS-server-IP>`&#x20;
* **DIG - AXFR Zone Transfer -** `dig axfr <domain> @<DNS-server-IP>`&#x20;
* **DIG - AXFR Zone Transfer - Internal -** `dig axfr internal.<domain> @<DNS-server-IP>` &#x20;

### **Subdomain Brute Forcing**

{% code lineNumbers="true" %}
```shellscript
for sub in $(cat /opt/useful/seclists/Discovery/DNS/subdomains-top1million-110000.txt);do dig $sub.<domain> @<DNS-server-IP> | grep -v ';|SOA' | sed -r '/^\s*$/d' | grep $sub | tee -a subdomains.txt;done
dnsenum --dnsserver <DNS-server-IP> --enum -p 0 -s 0 -o subdomains.txt -f /opt/useful/seclists/Discovery/DNS/subdomains-top1million-110000.txt <domain>
dnsenum --enum <target-domain> -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -r
gobuster dns -d <domain.com> -w /usr/share/SecLists/Discovery/DNS/namelist.txt //gobuster dns --help
https://crt.sh/
site:*.domain.com -site:www.domain.com
dnsrecon -t brt -d <domain.com>
sublist3r.py -d <domain.com>
```
{% endcode %}

### Common dig Commands <a href="#common-dig-commands" id="common-dig-commands"></a>

<table><thead><tr><th width="233.28570556640625">Command</th><th>Description</th></tr></thead><tbody><tr><td><code>dig domain.com</code></td><td>Performs a default A record lookup for the domain.</td></tr><tr><td><code>dig domain.com A</code></td><td>Retrieves the IPv4 address (A record) associated with the domain.</td></tr><tr><td><code>dig domain.com AAAA</code></td><td>Retrieves the IPv6 address (AAAA record) associated with the domain.</td></tr><tr><td><code>dig domain.com MX</code></td><td>Finds the mail servers (MX records) responsible for the domain.</td></tr><tr><td><code>dig domain.com NS</code></td><td>Identifies the authoritative name servers for the domain.</td></tr><tr><td><code>dig domain.com TXT</code></td><td>Retrieves any TXT records associated with the domain.</td></tr><tr><td><code>dig domain.com CNAME</code></td><td>Retrieves the canonical name (CNAME) record for the domain.</td></tr><tr><td><code>dig domain.com SOA</code></td><td>Retrieves the start of authority (SOA) record for the domain.</td></tr><tr><td><code>dig @1.1.1.1 domain.com</code></td><td>Specifies a specific name server to query; in this case 1.1.1.1</td></tr><tr><td><code>dig +trace domain.com</code></td><td>Shows the full path of DNS resolution.</td></tr><tr><td><code>dig -x 192.168.1.1</code></td><td>Performs a reverse lookup on the IP address 192.168.1.1 to find the associated host name. You may need to specify a name server.</td></tr><tr><td><code>dig +short domain.com</code></td><td>Provides a short, concise answer to the query.</td></tr><tr><td><code>dig +noall +answer domain.com</code></td><td>Displays only the answer section of the query output.</td></tr><tr><td><code>dig domain.com ANY</code></td><td>Retrieves all available DNS records for the domain (Note: Many DNS servers ignore <code>ANY</code> queries to reduce load and prevent abuse, as per <a href="https://datatracker.ietf.org/doc/html/rfc8482">RFC 8482</a>).</td></tr></tbody></table>

### DNS Tools

* [DNSenum](https://github.com/fwaeytens/dnsenum)
* nslookup
* dig
* [fierce](https://github.com/mschwager/fierce)
* [dnsrecon](https://github.com/darkoperator/dnsrecon)
* theHarvester
* [assetfinder](https://github.com/tomnomnom/assetfinder)
* [amass](https://github.com/owasp-amass/amass)
* [puredns](https://github.com/d3mondev/puredns)

### Virtual Host Fuzzing

* Make sure to update the /etc/hosts file for brute-force

{% code lineNumbers="true" %}
```shellscript
gobuster vhost -u http://<target_IP_address> -w <wordlist_file> --append-domain
ffuf -w <wordlist> -H "Host: FUZZ.domain.com" -u http://<ip>
```
{% endcode %}

### Virtual Hosts Discovery Tools

* [gobuster](https://github.com/OJ/gobuster)
* [Feroxbuster](https://github.com/epi052/feroxbuster)
* [ffuf](https://github.com/ffuf/ffuf)
