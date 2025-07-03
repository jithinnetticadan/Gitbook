# Traffic Analysis

#### Intercept HTTP traffic using Burpsuite&#xD;

* Burp -> Use the invisible proxy -> Set the Redirect Host/Host Resolution Override option depending on the numbers of hosts communicated.
* [https://portswigger.net/support/using-burp-suites-invisible-proxy-settings-to-test-a-non-proxy-aware-thick-client-application](https://portswigger.net/support/using-burp-suites-invisible-proxy-settings-to-test-a-non-proxy-aware-thick-client-application)
* Modify the C:\Windows\System32\drivers\etc\hosts file\
  eg: 127.0.0.1 \<target-host-url>

#### Intercept TCP/UDP traffic using Echo mirage

* Inject into the Process ID of target application.
* [https://sourceforge.net/projects/echomirage.oldbutgold.p/](https://sourceforge.net/projects/echomirage.oldbutgold.p/)

#### Intercept TCP/UDP traffic MITM-Relay+Burp&#x20;

* Prerequisite - pip install requests
* Local Port Forwarding \
  Add Rule: netsh interface portproxy add v4tov4 listenport=LPORT listenaddress=0.0.0.0 connectport=LPORT1 connectaddress=127.0.0.1\
  Delete Rule: netsh interface portproxy delete v4tov4 listenport=LPORT listenaddress=0.0.0.0
* python mitm\_relay.py -l 0.0.0.0 -r tcp/udp:LPORT1:RHOST:RPORT -p 127.0.0.0.1:8080
* [https://github.com/jrmdev/mitm\_relay](https://github.com/jrmdev/mitm_relay)
