# Domain Enum

### Users

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">sudo nxc smb &#x3C;DC-IP> -u &#x3C;user> -p &#x3C;pass> --users
  cat usernames.txt | cut -d'\' -f2 | awk -F " " '{print $1}' | tee cleanusers.txt
  </code></pre>
* <pre class="language-bat" data-line-numbers><code class="lang-bat">net user /domain
  dsquery user
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

### Tools

* [Dsquery](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc732952\(v=ws.11\))
* [windapsearch](https://github.com/ropnop/windapsearch)
