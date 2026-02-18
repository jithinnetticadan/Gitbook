# Infrastructure Based

### Domain Information

#### Online Presence

* SSL certificate - includes more than just a subdomain, and this means that the certificate is used for several domains.
* **Certificate Transparency**
* `curl -s https://crt.sh/?q=<domain>&output=json | jq .`
* `curl -s https://crt.sh/?q=<domain>&output=json | jq . | grep name | cut -d":" -f2 | grep -v "CN=" | cut -d'"' -f2 | awk '{gsub(/\n/,"\n");}1;' | sort -u`
* [crt.sh](https://crt.sh/)

#### **Company Hosted Servers**

* `for i in $(cat subdomainlist);do host $i | grep "has address" | grep <domain> | cut -d" " -f1,4;done`&#x20;
* `for i in $(cat subdomainlist);do host $i | grep "has address" | grep <domain> | cut -d" " -f4 >> ip-addresses.txt;done` <sub>(To obtain IP-Addresses)</sub>
* `for i in $(cat ip-addresses.txt);do shodan host $i;done`
* [Shodan](https://www.shodan.io/) can be used to find devices and systems permanently connected to the Internet

#### **DNS Records**

* `dig any <domain>`&#x20;

## Cloud Resources

* Google Search for AWS - `intext:<domain> inurl:amazonaws.com`
* Google Search for Azure - `intext:<domain> inurl:blob.core.windows.net`
* Target Website-Source Code: Third-party providers such as [domain.glass](https://domain.glass/), [GrayHatWarfare](https://buckets.grayhatwarfare.com/) tell us about the company's infrastructure.
* Private and Public SSH Keys Leaked
