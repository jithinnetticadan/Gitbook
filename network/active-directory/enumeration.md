# Enumeration

#### Identify all live hosts within network [#host-discovery-scan](../recon.md#host-discovery-scan "mention")

#### Identify the Domain Controller & Services(DC)&#x20;

{% code lineNumbers="true" %}
```
nmap -p 88,135,139,389,445 -sV -sC -iL hosts.txt
```
{% endcode %}

#### Full Port Scan [#full-port-scan](../recon.md#full-port-scan "mention")

#### Parse SMB Shares [smb-139-445.md](../enumeration/smb-139-445.md "mention")

####
