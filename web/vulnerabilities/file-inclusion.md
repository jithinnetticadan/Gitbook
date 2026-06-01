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

### Basic LFI <a href="#basic-lfi" id="basic-lfi"></a>

* Able to change the **absolute** file path being pulled to read the content of a different local file.
* Source Code: `include($_GET['language']);`
* This trick would work if the whole input was used within the `include()` function without any additions
* **Common readable files**
  * Linux: `/etc/passwd`
  * Windows: `C:\Windows\boot.ini`&#x20;

### Path Traversal <a href="#path-traversal" id="path-traversal"></a>

* Bypass restrictions by traversing directories using **relative paths**
* Source Code: `include("./languages/" . $_GET['language']);`
* Add `../` before our file name, which refers to the parent directory.
* Trick would work even if the entire parameter was used in the `include()` function or prefixed with some value.
* e.g. `../../../../etc/passwd`&#x20;

### Filename Prefix <a href="#filename-prefix" id="filename-prefix"></a>

* Some cases wher our input may be appended after a different string
* Source Code: `include("lang_" . $_GET['language']);`
* Instead of directly using path traversal, we can prefix a `/` before our payload, and this should consider the prefix as a directory, and then we should bypass the filename and be able to traverse directories
* eg. `/../../etc/passwd`&#x20;

### Appended Extensions <a href="#appended-extensions" id="appended-extensions"></a>

* We would not have to write the extension every time we need to change the language. This may also be safer as it may restrict us to only including PHP files
* `include($_GET['language'] . ".php");`
* Append `#` to consider the extension as fragment.

### Second-Order Attacks <a href="#second-order-attacks" id="second-order-attacks"></a>

* Occurs when web application functionalities may be insecurely pulling files from the back-end server based on user-controlled parameters.
* For example, a web application may allow us to download our avatar through a URL like (`/profile/$username/avatar.png`). If we craft a malicious LFI username (e.g. `../../../etc/passwd`), then it may be possible to change the file being pulled to another local file on the server and grab it instead of our avatar.
