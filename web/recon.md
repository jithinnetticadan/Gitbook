# Recon & Enum

<details>

<summary>Browser Extension</summary>

* Retire.js
* Shodan
* FoxyProxy
* Wappalyzer
* TruffleHog
* Teeto
* Cookie-Editor
* OWASP Penetration Testing Kit

</details>

<details>

<summary>Browser Tricks</summary>

* chrome://net-internals/
* edge://net-internals/

</details>

### Passive Recon

{% code lineNumbers="true" %}
```shellscript
whois <domain> ## WhoisFreaks website
```
{% endcode %}

### Automated Recon

* [FinalRecon](https://github.com/thewhiteh4t/FinalRecon)
* [Recon-ng](https://github.com/lanmaster53/recon-ng)
* [theHarvester](https://github.com/laramies/theHarvester)
* [SpiderFoot](https://github.com/smicallef/spiderfoot)
* [OSINT Framework](https://osintframework.com/)

### Subdomain Enumeration

{% code lineNumbers="true" fullWidth="false" %}
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

### vHost Enumeration

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
gobuster vhost -u "url" --domain domain.com -w <wordlist> --append-domain //gobuster vhost --help
ffuf -w <wordlist> -H "Host: FUZZ.domain.com" -u http://<ip>
```
{% endcode %}

### Google Dorking

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
site:target.com inurl:admin | inurl:.git
site:target.com ext:sql | ext:log
site:target.com intitle:"index of"
site:target.com filetype:env
intext:<domain> inurl:amazonaws.com //Search for AWS
intext:<domain> inurl:blob.core.windows.net //Search for Azure
```
{% endcode %}

### Banner Grabbing

```shellscript
whatweb <IP>
whatweb --no-errors <subnet>
curl -I <domain/URL>
nikto -h <domain/URL> -Tuning b
wafw00f <domain/URL>
BuiltWith
Netcraft
```

### Crawling/Spidering

* **List Directories**
* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">gobuster dir -u "url" -w /usr/share/seclists/Discovery/Web-Content/common.txt
  ffuf -s -w &#x3C;worslist>:FUZZ -u http://&#x3C;host>/FUZZ
  dirb &#x3C;url> &#x3C;wordlist>
  robots.txt
  https://example.com/.well-known/ -> security.txt, change-password, openid-configuration, assetlinks.json, mta-sts.txt
  </code></pre>
* Tools -> [reconspider](https://github.com/bhavsec/reconspider) (need `pip install scrapy`), Apache Nutch, BurpSuite, OWASPZap
* **List Pages**

### Automated Scan

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
nikto -h <target> -Tuning x 6 -port 80,443 -nossl/ssl -header "Host: target.com" -header "Cookie: " -Cgidirs all -followredirects -Format htm -output nikto-report.html
nuclei -u <ip> -t http/,ssl/, -s critical,high,medium,low -o nuclei-output.txt -rl 150 -c 50 -ni -stats
nuclei -u <ip> -as -s critical,high,medium,low -o nuclei-output.txt -rl 150 -c 50 -ni -stats
arachni - https://github.com/Arachni/arachni
Nessus
OpenVAS
```
{% endcode %}

#### S3 Bucket Enum

{% code title="find subs -> find alive hosts -> sort & add hosts to file (output to terminal) -> fetch paths -> grep patterns" fullWidth="false" %}
```shellscript
assetfinder --subs-only <domain> | httprobe | anew hosts; meg -d 1000 -v /; gf s3-buckets
```
{% endcode %}

#### Other Steps

* Check the page source to obtain credentials added in comments
* Finding Public Exploits (searchsploit, [Exploit DB](https://www.exploit-db.com/), [Rapid7 DB](https://www.rapid7.com/db/), or [Vulnerability Lab](https://www.vulnerability-lab.com/))

### Tools

* Banner Grabbing - Netcat, curl
* Port Scanning - Nmap, Masscan, Unicornscan
* OS Fingerprinting - Nmap, Xprobe2
* Service Enumeration - Nmap
* Vulnerability Scanning - Nessus, OpenVAS, Nikto, Nuclei
* Network Mapping - Traceroute, Nmap
* Web Spidering - Burp Suite Spider, OWASP ZAP Spider, Scrapy
* &#x20;[Trufflehog](https://github.com/trufflesecurity/truffleHog)
* [Greyhat Warfare](https://buckets.grayhatwarfare.com/)
* [linkedin2username](https://github.com/initstring/linkedin2username)
