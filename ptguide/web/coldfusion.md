# ColdFusion

{% hint style="info" %}
* ColdFusion is a programming language and a web application development platform based on Java.
* It is used to build dynamic and interactive web applications that can be connected to various APIs and databases such as MySQL, Oracle, and Microsoft SQL Server.
* ColdFusion Markup Language (`CFML`) is the proprietary programming language used in ColdFusion to develop dynamic web applications. It has a syntax similar to HTML, making it easy to learn for web developers.
* CFML includes tags and functions for database integration, web services, email management, and other common web development tasks. Its tag-based approach simplifies application development by reducing the amount of code needed to accomplish complex tasks.
* ColdFusion supports other programming languages, such as JavaScript and Java, allowing developers to use their preferred programming language within the ColdFusion environment.
{% endhint %}

## Discovery <a href="#coldfusion-discovery-enumeration" id="coldfusion-discovery-enumeration"></a>

* ColdFusion exposes a fair few ports by default:

<table><thead><tr><th width="102.9998779296875">Port Number</th><th width="108.4287109375">Protocol</th><th>Description</th></tr></thead><tbody><tr><td>80</td><td>HTTP</td><td>Used for non-secure HTTP communication between the web server and web browser.</td></tr><tr><td>443</td><td>HTTPS</td><td>Used for secure HTTP communication between the web server and web browser. Encrypts the communication between the web server and web browser.</td></tr><tr><td>1935</td><td>RPC</td><td>Used for client-server communication. Remote Procedure Call (RPC) protocol allows a program to request information from another program on a different network device.</td></tr><tr><td>25</td><td>SMTP</td><td>Simple Mail Transfer Protocol (SMTP) is used for sending email messages.</td></tr><tr><td>8500</td><td>SSL</td><td>Used for server communication via Secure Socket Layer (SSL).</td></tr><tr><td>5500</td><td>Server Monitor</td><td>Used for remote administration of the ColdFusion server.</td></tr></tbody></table>

* ColdFusion typically uses port 80 for HTTP and port 443 for HTTPS by default.
  * `nmap -p- -sC -Pn <IP> --open`
* ColdFusion pages typically use ".cfm" or ".cfc" file extensions.

## Enumeration <a href="#coldfusion-discovery-enumeration" id="coldfusion-discovery-enumeration"></a>

* Check the HTTP response headers of the web application. ColdFusion typically sets specific headers, such as "Server: ColdFusion" or "X-Powered-By: ColdFusion"
* Error messages may contain references to ColdFusion-specific tags or functions.
* ColdFusion creates several default files during installation, such as "admin.cfm" or "CFIDE/administrator/index.cfm"

## Exploitation

### Leverage Known Exploits based on version identified.
