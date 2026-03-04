# DNS - TU53

### Default Configuration

* DNS server [Bind9](https://www.isc.org/bind/) is very often used on Linux-based distributions.&#x20;
* **Local DNS Configuration -** `cat /etc/bind/named.conf.local`

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

