# Recon & Enum

<details>

<summary>Browser Extension</summary>

* Retire.js

- Shodan

* FoxyProxy

- Wappalyzer

* TruffleHog

</details>

#### Automated Scan

{% code lineNumbers="true" fullWidth="true" %}
```
nikto -h <target> -Tuning x 6 -port 80,443 -nossl/ssl -Cgidirs all -Format htm -output nikto-report.html
nuclei -h
```
{% endcode %}

#### List Directories/Pages

#### Google Dorking

{% code lineNumbers="true" %}
```
site:target.com inurl:admin | inurl:.git
site:target.com ext:sql | ext:log
site:target.com intitle:"index of"
site:target.com filetype:env
```
{% endcode %}

#### S3 Bucket Enum

<pre data-title="find subs -> find alive hosts -> sort &#x26; add hosts to file (output to terminal) -> fetch paths -> grep patterns" data-full-width="true"><code><strong>assetfinder --subs-only &#x3C;domain> | httprobe | anew hosts; meg -d 1000 -v /; gf s3-buckets
</strong></code></pre>

####
