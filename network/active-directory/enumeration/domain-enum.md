# Domain Enum

### Users

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">sudo nxc smb &#x3C;DC-IP> -u &#x3C;user> -p &#x3C;pass> --users
  cat usernames.txt | cut -d'\' -f2 | awk -F " " '{print $1}' | tee cleanusers.txt
  </code></pre>
* <pre class="language-bat" data-line-numbers><code class="lang-bat">net user /domain
  dsquery user
  whoami /user
  wmic useraccount where name="&#x3C;username>" get sid
  </code></pre>

### Group

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">sudo nxc smb &#x3C;DC-IP> -u &#x3C;user> -p &#x3C;pass> --groups
  </code></pre>
* <pre class="language-bat" data-line-numbers><code class="lang-bat">net groups /domain
  </code></pre>

### Logged On Users

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">sudo nxc smb &#x3C;DC-IP> -u &#x3C;user> -p &#x3C;pass> --loggedon-users
  </code></pre>

### Domain Admins

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">python3 windapsearch.py --dc-ip &#x3C;DC-IP> -u &#x3C;user@domain> -p &#x3C;pass> --da
  </code></pre>
* <pre class="language-bat" data-line-numbers><code class="lang-bat">net group "Domain Admins" /domain
  </code></pre>

### Privileged Users

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">python3 windapsearch.py --dc-ip &#x3C;DC-IP> -u &#x3C;user@domain> -p &#x3C;pass> --PU
  </code></pre>

### Computers

* <pre class="language-bat" data-line-numbers><code class="lang-bat">dsquery computer
  netdom query /domain:&#x3C;value> workstation
  </code></pre>

### Domain Controllers

* <pre class="language-bat" data-line-numbers><code class="lang-bat">netdom query /domain:&#x3C;value> dc
  </code></pre>

### Domain Trust

* <pre class="language-bat" data-line-numbers><code class="lang-bat">netdom query /domain:&#x3C;value> trust
  </code></pre>

### Deleted Objects <sup><sub>(hidden in BloodHound)<sub></sup>

* <pre class="language-bash" data-line-numbers><code class="lang-bash">bloodyad -u &#x3C;user> -p &#x3C;pass> -d &#x3C;domain> -i &#x3C;DC-IP> get writable --right WRITE
  bloodyad -u &#x3C;user> -p &#x3C;pass> -d &#x3C;domain> -i &#x3C;DC-IP> get children --target 'CN=Deleted Objects,DC=corp,DC=local'
  # use --filter "(objectClass=user)" to get only the user details
  bloodyad -u &#x3C;user> -p &#x3C;pass> -d &#x3C;domain> -i &#x3C;DC-IP> get search -c 1.2.840.113556.1.4.2064 --resolve-sd --base 'CN=Deleted Objects,DC=ad,DC=trilocor,DC=local'
  ldapsearch -x -H ldap://&#x3C;DC-IP> -D "&#x3C;user>@&#x3C;domain>" -w &#x3C;pass> -b "CN=Deleted Objects,DC=corp,DC=local" -E "1.2.840.113556.1.4.417"

  # To restore the user
  bloodyad -u &#x3C;user> -p &#x3C;pass> -d &#x3C;domain> -i &#x3C;DC-IP> set restore &#x3C;SID>
  </code></pre>

### Tools

* [Dsquery](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc732952\(v=ws.11\))
* [windapsearch](https://github.com/ropnop/windapsearch)
