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
