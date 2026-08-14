# DNS - TU53

### Default Configuration

* DNS server [Bind9](https://www.isc.org/bind/) is very often used on Linux-based distributions.
* **Local DNS Configuration -** `cat /etc/bind/named.conf.local`

### Dangerous Settings

* <table data-header-hidden><thead><tr><th width="153">Option</th><th>Description</th></tr></thead><tbody><tr><td><code>allow-query</code></td><td>Defines which hosts are allowed to send requests to the DNS server.</td></tr><tr><td><code>allow-recursion</code></td><td>Defines which hosts are allowed to send recursive requests to the DNS server.</td></tr><tr><td><code>allow-transfer</code></td><td>Defines which hosts are allowed to receive zone transfers from the DNS server.</td></tr><tr><td><code>zone-statistics</code></td><td>Collects statistical data of zones.</td></tr></tbody></table>

### Footprinting the Service

* #### External DNS
  * **DIG - NS Query -** `dig ns <domain> @<DNS-server-IP>`
  * **DIG - Version Query -** `dig CH TXT version.bind <DNS-server-IP>`
  * **DIG - ANY Query -** `dig any <domain> @<DNS-server-IP>`
  * **DIG - AXFR Zone Transfer -** `dig axfr <domain> @<DNS-server-IP>` or `fierce --domain <example.com>`
  * **DIG - AXFR Zone Transfer - Internal -** `dig axfr internal.<domain> @<DNS-server-IP>`
* #### AD DNS
  * `adidnsdump -u <domain>\\<username> ldap://<DC-IP>` <sup><sub>(run again with the<sub></sup> <sup><sub>`-r`<sub></sup> <sup><sub>, attempts to resolve unknown records by performing<sub></sup> <sup><sub>`A`<sub></sup> <sup><sub>query)<sub></sup>

### Subdomain Brute Forcing

{% tabs %}
{% tab title="Manual" %}
{% code lineNumbers="true" %}
```shellscript
for sub in $(cat /opt/useful/seclists/Discovery/DNS/subdomains-top1million-110000.txt);do dig $sub.<domain> @<DNS-server-IP> | grep -v ';|SOA' | sed -r '/^\s*$/d' | grep $sub | tee -a subdomains.txt;done
https://crt.sh/
site:*.domain.com -site:www.domain.com
```
{% endcode %}
{% endtab %}

{% tab title="dnsenum" %}
{% code lineNumbers="true" %}
```shellscript
dnsenum --dnsserver <DNS-server-IP> --enum -p 0 -s 0 -o subdomains.txt -f /opt/useful/seclists/Discovery/DNS/subdomains-top1million-110000.txt <domain>
dnsenum --enum <target-domain> -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -r
```
{% endcode %}
{% endtab %}

{% tab title="gobuster" %}
{% code lineNumbers="true" %}
```shellscript
gobuster dns -d <domain.com> -w /usr/share/SecLists/Discovery/DNS/namelist.txt //gobuster dns --help
```
{% endcode %}
{% endtab %}

{% tab title="dnsrecon" %}
{% code lineNumbers="true" %}
```shellscript
dnsrecon -t brt -d <domain.com>
```
{% endcode %}
{% endtab %}

{% tab title="sublist3r" %}
```shellscript
sublist3r.py -d <domain.com>
```
{% endtab %}

{% tab title="subfinder" %}
{% code lineNumbers="true" %}
```shellscript
subfinder -d <domain> -v 
```
{% endcode %}
{% endtab %}

{% tab title="Subbrute" %}
{% code lineNumbers="true" %}
```shellscript
## resolvers -> DNS Nme servers
subbrute.py inlanefreight.com -s ./names.txt -r ./resolvers.txt
```
{% endcode %}
{% endtab %}
{% endtabs %}

### Common `dig` Commands <a href="#common-dig-commands" id="common-dig-commands"></a>

<table><thead><tr><th width="233.28570556640625">Command</th><th>Description</th></tr></thead><tbody><tr><td><code>dig domain.com</code></td><td>Performs a default A record lookup for the domain.</td></tr><tr><td><code>dig domain.com A</code></td><td>Retrieves the IPv4 address (A record) associated with the domain.</td></tr><tr><td><code>dig domain.com AAAA</code></td><td>Retrieves the IPv6 address (AAAA record) associated with the domain.</td></tr><tr><td><code>dig domain.com MX</code></td><td>Finds the mail servers (MX records) responsible for the domain.</td></tr><tr><td><code>dig domain.com NS</code></td><td>Identifies the authoritative name servers for the domain.</td></tr><tr><td><code>dig domain.com TXT</code></td><td>Retrieves any TXT records associated with the domain.</td></tr><tr><td><code>dig domain.com CNAME</code></td><td>Retrieves the canonical name (CNAME) record for the domain.</td></tr><tr><td><code>dig domain.com SOA</code></td><td>Retrieves the start of authority (SOA) record for the domain.</td></tr><tr><td><code>dig @1.1.1.1 domain.com</code></td><td>Specifies a specific name server to query; in this case 1.1.1.1</td></tr><tr><td><code>dig +trace domain.com</code></td><td>Shows the full path of DNS resolution.</td></tr><tr><td><code>dig -x 192.168.1.1</code></td><td>Performs a reverse lookup on the IP address 192.168.1.1 to find the associated host name. You may need to specify a name server.</td></tr><tr><td><code>dig +short domain.com</code></td><td>Provides a short, concise answer to the query.</td></tr><tr><td><code>dig +noall +answer domain.com</code></td><td>Displays only the answer section of the query output.</td></tr><tr><td><code>dig domain.com ANY</code></td><td>Retrieves all available DNS records for the domain (Note: Many DNS servers ignore <code>ANY</code> queries to reduce load and prevent abuse, as per <a href="https://datatracker.ietf.org/doc/html/rfc8482">RFC 8482</a>).</td></tr></tbody></table>

### Reverse Lookup

{% tabs %}
{% tab title="dnsrecon" %}
{% code lineNumbers="true" %}
```bash
dnsrecon -r 192.168.1.0-192.168.1.255 -n <DNS-Server-IP> -d <domain>
```
{% endcode %}
{% endtab %}

{% tab title="Second Tab" %}

{% endtab %}
{% endtabs %}

### Virtual Host Fuzzing

* Make sure to update the /etc/hosts file for brute-force
* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">gobuster vhost -u http://&#x3C;target_IP_address> -w &#x3C;wordlist_file> --domain &#x3C;value>
  ffuf -w &#x3C;wordlist> -H "Host: FUZZ.domain.com" -u http://&#x3C;ip>
  </code></pre>

### Virtual Hosts Discovery Tools

* [gobuster](https://github.com/OJ/gobuster)
* [Feroxbuster](https://github.com/epi052/feroxbuster)
* [ffuf](https://github.com/ffuf/ffuf)

### CT Logs Enumeration <a href="#searching-ct-logs" id="searching-ct-logs"></a>

{% hint style="info" %}
Certificate Transparency logs are public, append-only ledgers that record the issuance of SSL/TLS certificates. Whenever a Certificate Authority (CA) issues a new certificate, it must submit it to multiple CT logs. Independent organizations maintain these logs and are open for anyone to inspect.
{% endhint %}

* Tools -> [crt.sh](https://crt.sh/), [Censys](https://search.censys.io/)
* ```shellscript
  curl -s "https://crt.sh/?q=<domain>&output=json" | jq -r '.[] | select(.name_value | contains("<search_string>")) | .name_value' | sort -u
  ```

### SubDomain Takeover

* A DNS's canonical name (`CNAME`) record is used to map different domains to a parent domain. Many organizations use third-party services like AWS, GitHub, Akamai, Fastly, and other content delivery networks (CDNs) to host their content.
* [can-i-take-over-xyz](https://github.com/EdOverflow/can-i-take-over-xyz)

### DNS Spoofing <a href="#dns-spoofing" id="dns-spoofing"></a>

* #### Local DNS Cache Poisoning
  * [Ettercap](https://www.ettercap-project.org/) or [Bettercap](https://www.bettercap.org/)
  * `sudo nano /etc/ettercap/etter.dns`
  * Modify the Target Domain with A record pointing to atatcker IP

### Tools

* [DNSenum](https://github.com/fwaeytens/dnsenum)
* [DNSdumpster](https://dnsdumpster.com/)
* [Subfinder](https://github.com/projectdiscovery/subfinder)
* [Sublist3r](https://github.com/aboul3la/Sublist3r)
* [Subbrute](https://github.com/TheRook/subbrute)
* nslookup
* dig
* [fierce](https://github.com/mschwager/fierce)
* [dnsrecon](https://github.com/darkoperator/dnsrecon)
* theHarvester
* [assetfinder](https://github.com/tomnomnom/assetfinder)
* [amass](https://github.com/owasp-amass/amass)
* [puredns](https://github.com/d3mondev/puredns)
* [adidnsdump](https://github.com/dirkjanm/adidnsdump)
