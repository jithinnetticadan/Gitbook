# Recon

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

<pre data-line-numbers><code>site:target.com inurl:admin | inurl:.git
<strong>site:target.com ext:sql | ext:log
</strong>site:target.com intitle:"index of"
site:target.com filetype:env
</code></pre>

#### S3 Bucket Enum

{% code title="find subs -> find alive hosts -> sort & add hosts to file (output to terminal) -> fetch paths -> grep patterns" lineNumbers="true" fullWidth="true" %}
```
assetfinder --subs-only <domain> | httprobe | anew hosts; meg -d 1000 -v /; gf s3-buckets
```
{% endcode %}

####
