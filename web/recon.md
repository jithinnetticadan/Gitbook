# Recon

#### Browser Extensions

* Retire.js
* Shodan
* FoxyProxy
* Wappalyzer
* TruffleHog

#### Automated Scan

```
nikto -h
nuclei -h
```

#### List Directories/Pages

#### S3 Bucket Enum

{% hint style="info" %}
```
assetfinder-find subs,httprobe-find alive hosts,anew-sort and add hosts to file (output to terminal),meg-fetch paths,gf-grep patterns
```
{% endhint %}

```
assetfinder --subs-only <domain> | httprobe | anew hosts; meg -d 1000 -v /; gf s3-buckets
```

####
