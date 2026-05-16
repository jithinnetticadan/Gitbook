# Domain Enum

### Users

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">sudo nxc smb &#x3C;DC-IP> -u &#x3C;user> -p &#x3C;pass> --users
  </code></pre>

### Group

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">sudo nxc smb &#x3C;DC-IP> -u &#x3C;user> -p &#x3C;pass> --groups
  </code></pre>

### Logged On Users

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">sudo nxc smb &#x3C;DC-IP> -u &#x3C;user> -p &#x3C;pass> --loggedon-users

  </code></pre>

### Domain Admins

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">python3 windapsearch.py --dc-ip &#x3C;DC-IP> -u &#x3C;user@domain> -p &#x3C;pass> --da
  </code></pre>

### Privileged Users

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">python3 windapsearch.py --dc-ip &#x3C;DC-IP> -u &#x3C;user@domain> -p &#x3C;pass> --PU
  </code></pre>
