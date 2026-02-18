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

</details>

<details>

<summary>Browser Tricks</summary>

* chrome://net-internals/
* edge://net-internals/

</details>

#### Banner Grabbing

```shellscript
whatweb <IP>
whatweb --no-errors <subnet>
```

#### Automated Scan

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
nikto -h <target> -Tuning x 6 -port 80,443 -nossl/ssl -Cgidirs all -followredirects -Format htm -output nikto-report.html
nuclei -u <ip> -t http/,ssl/, -s critical,high,medium,low -o nuclei-output.txt -rl 150 -c 50 -ni -stats
nuclei -u <ip> -as -s critical,high,medium,low -o nuclei-output.txt -rl 150 -c 50 -ni -stats
arachni - https://github.com/Arachni/arachni
```
{% endcode %}

#### List Directories/Pages

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
gobuster dir -u "url" -w /usr/share/seclists/Discovery/Web-Content/common.txt
ffuf -w <worslist>:FUZZ -u http://<host>/FUZZ
dirb <url> <wordlist>
```
{% endcode %}

#### Subdomain Enumeration

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
gobuster dns -d <domain.com> -w /usr/share/SecLists/Discovery/DNS/namelist.txt //gobuster dns --help
https://crt.sh/
site:*.domain.com -site:www.domain.com
dnsrecon -t brt -d <domain.com>
sublist3r.py -d <domain.com>
```
{% endcode %}

#### vHost Enumeration

{% code lineNumbers="true" fullWidth="false" %}
```shellscript
gobuster vhost -u "url" --domain domain.com -w <wordlist> --append-domain //gobuster vhost --help
ffuf -w <wordlist> -H "Host: FUZZ.domain.com" -u http://<ip>
```
{% endcode %}

#### Google Dorking

<pre class="language-shellscript" data-line-numbers data-full-width="false"><code class="lang-shellscript">site:target.com inurl:admin | inurl:.git
site:target.com ext:sql | ext:log
site:target.com intitle:"index of"
site:target.com filetype:env
intext:&#x3C;domain> inurl:amazonaws.com //Search for AWS
<strong>intext:&#x3C;domain> inurl:blob.core.windows.net //Search for Azure
</strong></code></pre>

#### S3 Bucket Enum

<pre class="language-shellscript" data-title="find subs -> find alive hosts -> sort &#x26; add hosts to file (output to terminal) -> fetch paths -> grep patterns" data-full-width="false"><code class="lang-shellscript"><strong>assetfinder --subs-only &#x3C;domain> | httprobe | anew hosts; meg -d 1000 -v /; gf s3-buckets
</strong></code></pre>

#### Other Steps

* Check the page source to obtain credentials added in comments
* Finding Public Exploits (searchsploit, [Exploit DB](https://www.exploit-db.com/), [Rapid7 DB](https://www.rapid7.com/db/), or [Vulnerability Lab](https://www.vulnerability-lab.com/))
