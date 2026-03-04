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
```
{% endcode %}







### Tools

* [DNSenum](https://github.com/fwaeytens/dnsenum)

