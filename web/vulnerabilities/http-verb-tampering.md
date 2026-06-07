# HTTP Verb Tampering

{% hint style="info" %}
An HTTP Verb Tampering attack exploits web servers that accept many HTTP verbs and methods. This can be exploited by sending malicious requests using unexpected methods, which may lead to bypassing the web application's authorization mechanism or even bypassing its security controls against other web attacks. HTTP Verb Tampering attacks are one of many other HTTP attacks that can be used to exploit web server configurations by sending malicious HTTP requests.
{% endhint %}

| Verb      | Description                                                                                         |
| --------- | --------------------------------------------------------------------------------------------------- |
| `HEAD`    | Identical to a GET request, but its response only contains the `headers`, without the response body |
| `PUT`     | Writes the request payload to the specified location                                                |
| `DELETE`  | Deletes the resource at the specified location                                                      |
| `OPTIONS` | Shows different options accepted by a web server, like accepted HTTP verbs                          |
| `PATCH`   | Apply partial modifications to the resource at the specified location                               |

### Insecure Configurations <a href="#insecure-configurations" id="insecure-configurations"></a>

* A web server's authentication configuration may be limited to specific HTTP methods, which would leave some HTTP methods accessible without authentication.
* ```xml
  <Limit GET POST>
      Require valid-user
  </Limit>
  ```

### Insecure Coding <a href="#insecure-coding" id="insecure-coding"></a>

* Occurs when a web developer applies specific filters to mitigate particular vulnerabilities while not covering all HTTP methods with that filter.

{% code lineNumbers="true" %}
```php
$pattern = "/^[A-Za-z\s]+$/";

if(preg_match($pattern, $_GET["code"])) {
    $query = "Select * from ports where port_code like '%" . $_REQUEST["code"] . "%'";
    ...SNIP...
}
## Sanitization filter is only being tested on the GET parameter.
## If the GET requests do not contain any bad characters, then the query would be executed. 
## However, when the query is executed, the $_REQUEST["code"] parameters are being used, which may also contain POST parameters, leading to an inconsistency in the use of HTTP Verbs.
## In this case, an attacker may use a POST request to perform SQL injection, in which case the GET parameters would be empty (will not include any bad characters). 
## The request would pass the security filter, which would make the function still vulnerable to SQL Injection.
```
{% endcode %}

### Bypassing Basic Authentication <a href="#bypassing-basic-authentication" id="bypassing-basic-authentication"></a>

* We just need to try alternate HTTP methods to see how they are handled by the web server.&#x20;
* Automated vulnerability scanning tools can consistently identify HTTP Verb Tampering vulnerabilities caused by insecure server configurations, they usually miss identifying HTTP Tampering vulnerabilities caused by insecure coding.
* #### Identify <a href="#identify" id="identify"></a>
  * Identify which pages are restricted by authentication.
* #### Exploit <a href="#exploit" id="exploit"></a>
  * To try and exploit the page, we need to identify the HTTP request method used by the web application and try bypassing with other HTTP methods like HEAD, PUT etc.
  * **Note**: `HEAD` requests return the same headers as a GET request but without the response body. Servers may or may not perform the full backend processing required for GET — the only guarantee is that the headers are consistent.

### Bypassing Security Filters

* For eg: if a security filter was being used to detect injection vulnerabilities and only checked for injections in `POST` parameters (e.g. `$_POST['parameter']`), it may be possible to bypass it by simply changing the request method to `GET`.
* #### Identify <a href="#identify" id="identify"></a>
  * Web application uses certain filters on the back-end to identify injection attempts and then blocks any malicious requests.
* #### Exploit <a href="#exploit" id="exploit"></a>
  * To try and exploit this vulnerability, intercept the request in Burp Suite (Burp) and then use `Change Request Method` to change it to another method.

### Insecure Configuration Examples

<details>

<summary>Apache - 000-default.conf or .htaccess</summary>

{% code lineNumbers="true" %}
```xml
<Directory "/var/www/html/admin">
    AuthType Basic
    AuthName "Admin Panel"
    AuthUserFile /etc/apache2/.htpasswd
    <Limit GET>
        Require valid-user
    </Limit>
</Directory>
```
{% endcode %}

</details>

<details>

<summary>Tomcat - web.xml</summary>

{% code lineNumbers="true" %}
```xml
<security-constraint>
    <web-resource-collection>
        <url-pattern>/admin/*</url-pattern>
        <http-method>GET</http-method>
    </web-resource-collection>
    <auth-constraint>
        <role-name>admin</role-name>
    </auth-constraint>
</security-constraint>
```
{% endcode %}

</details>

<details>

<summary>ASP.NET - web.config</summary>

{% code lineNumbers="true" %}
```xml
<system.web>
    <authorization>
        <allow verbs="GET" roles="admin">
            <deny verbs="GET" users="*">
        </deny>
        </allow>
    </authorization>
</system.web>
```
{% endcode %}

</details>

### Insecure Code Examples

<details>

<summary>PHP</summary>

{% code lineNumbers="true" %}
```php
if (isset($_REQUEST['filename'])) {
    if (!preg_match('/[^A-Za-z0-9. _-]/', $_POST['filename'])) {
        system("touch " . $_REQUEST['filename']);
    } else {
        echo "Malicious Request Denied!";
    }
}
```
{% endcode %}

</details>
