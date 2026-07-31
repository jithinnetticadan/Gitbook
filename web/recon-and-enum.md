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

## Passive Recon

{% hint style="info" %}
Fuller OSINT technique table (DNS history, web archive, social media, code repos): [passive.md](../osint/passive.md "mention")
{% endhint %}

{% code lineNumbers="true" %}
```shellscript
whois <domain> ## WhoisFreaks website
```
{% endcode %}

### Automated OSINT Tools

* [FinalRecon](https://github.com/thewhiteh4t/FinalRecon)
* [Recon-ng](https://github.com/lanmaster53/recon-ng)
* [theHarvester](https://github.com/laramies/theHarvester)
* [SpiderFoot](https://github.com/smicallef/spiderfoot)
* [OSINT Framework](https://osintframework.com/)

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

### Passive Fingerprinting

* BuiltWith
* Netcraft

## Active Recon - Unauthenticated

### Subdomain Enumeration

{% hint style="info" %}
Certificate Transparency log searches, subdomain takeover checks, and DNS spoofing are covered in [dns-tu53.md](../network/enumeration/host-based/dns-tu53.md "mention").
{% endhint %}

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
ffuf -s -w subdomains-top1million-5000.txt:FUZZ -u https://FUZZ.domain.com/
```
{% endcode %}

### vHost Enumeration

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
gobuster vhost -u "url" --domain domain.com -w <wordlist> --append-domain //gobuster vhost --help
ffuf -s -w subdomains-top1million-5000.txt:FUZZ -H "Host: FUZZ.domain.com" -u http://<ip>
```
{% endcode %}

### Banner Grabbing

```shellscript
whatweb <IP>
whatweb --no-errors <subnet>
curl -I <domain/URL>
nikto -h <domain/URL> -Tuning b
wafw00f <domain/URL>
```

### Crawling/Spidering

* **List Directories**
* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">gobuster dir -u "url" -w /usr/share/seclists/Discovery/Web-Content/common.txt
  gobuster dir -u http://url -w /usr/share/wordlists/dirb/common.txt -x .php -t 300
  ffuf -s -w &#x3C;worslist>:FUZZ -u http://&#x3C;host>/FUZZ
  dirb &#x3C;url> &#x3C;wordlist>
  robots.txt
  https://example.com/.well-known/ -> security.txt, change-password, openid-configuration, assetlinks.json, mta-sts.txt
  ## Recursive Scanning
  ffuf -s -v -w &#x3C;worslist>:FUZZ -u http://&#x3C;host>/FUZZ -recursion -recursion-depth 1 -e '.php,.html'
  </code></pre>
* Tools -> [reconspider](https://github.com/bhavsec/reconspider) (need `pip install scrapy`), Apache Nutch, BurpSuite, OWASPZap
* **List Pages**
* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">ffuf -s -w &#x3C;worslist>:FUZZ -u http://&#x3C;host>/pageFUZZ
  </code></pre>

### Parameter Fuzzing

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">ffuf -s -w burp-parameter-names.txt:FUZZ -u http://&#x3C;url>:PORT/admin.php?FUZZ=key -fs xxx
  ffuf -s -w burp-parameter-names.txt:FUZZ -u -u http://&#x3C;url>:PORT/admin.php -X POST -d 'FUZZ=key' -H 'Content-Type: application/x-www-form-urlencoded' -fs xxx
  </code></pre>

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

{% hint style="info" %}
Full searchsploit command + JSON output flag: [#identifying-potential-vulnerabilities](../network/recon.md#identifying-potential-vulnerabilities "mention") -> Exploit Checks
{% endhint %}

* Check the page source to obtain credentials added in comments
* Finding Public Exploits (searchsploit, [Exploit DB](https://www.exploit-db.com/), [Rapid7 DB](https://www.rapid7.com/db/), or [Vulnerability Lab](https://www.vulnerability-lab.com/))

## Active Recon - Authenticated

{% hint style="info" %}
Once you have a low-privilege session (registered user, default creds, etc.), re-run discovery **with** the session cookie/token to surface endpoints hidden from anonymous users.
{% endhint %}

* Repeat directory/parameter fuzzing with an authenticated session:
  * `gobuster dir -u <url> -w <wordlist> -H "Cookie: session=<value>"`
  * `ffuf -s -w <wordlist>:FUZZ -u <url>/FUZZ -H "Authorization: Bearer <token>"`
* Diff the authenticated vs. unauthenticated site map to find admin-only routes, hidden features, and staff panels.
* Enumerate per-role differences (admin vs. standard user vs. guest) — feeds directly into [access-control.md](vulnerabilities/access-control.md "mention") and [insecure-direct-object-references-idor.md](vulnerabilities/insecure-direct-object-references-idor.md "mention") testing.
* Look for API/schema disclosure only reachable when logged in: `/swagger.json`, `/openapi.json`, `/graphql` introspection — see [api-testing.md](vulnerabilities/api-testing.md "mention").
* Inspect session artifacts issued after login (JWTs, cookies) — see [jwt-attacks.md](vulnerabilities/jwt-attacks.md "mention").

## Tools

{% hint style="info" %}
Generic scanning tool categories (port scanning, OS fingerprinting, vulnerability scanning): [recon.md](../network/recon.md "mention")
{% endhint %}

* [Trufflehog](https://github.com/trufflesecurity/truffleHog) <sup><sub>(secrets in JS bundles/repos)<sub></sup>
* [Greyhat Warfare](https://buckets.grayhatwarfare.com/) <sup><sub>(public S3 bucket search engine)<sub></sup>
* [linkedin2username](https://github.com/initstring/linkedin2username)
* [FinalRecon](https://github.com/thewhiteh4t/FinalRecon)
