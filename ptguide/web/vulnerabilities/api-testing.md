# API Testing

Application Programming Interfaces enable software systems and apps to communicate and share data

### API Recon

* First need to find out as much information about the API as possible, to discover its attack surface.
* Once identified the endpoints, you need to determine how to interact with them.
* Find out information about the following:
  * The input data the API processes, including both compulsory and optional parameters.
  * The types of requests the API accepts, including supported HTTP methods and media formats.
  * Rate limits and authentication mechanisms.

### API Documentation

* Documentation can be both human-readable and machine-readable forms.
* Human-readable is designed for developers to understand how to use the API.
* Machine-readable is designed to be processed by S/W for automating tasks like API integration and validation. Written in structured formats like JSON or XML.
* **Discovering API Documentation**&#x20;
  * `/api`&#x20;
  * `/swagger/index.html`&#x20;
  * `/openapi.json`
  * Lab: Look for any endpoints that reveal any sensitive endpoints in the documentation and craft a request to exploit further.
* **Using Machine-Readable Documentation**
  * Use Burp Scanner to crawl & audit OpenAPI documentation
  * Parse OpenAPI documentation using OpenAPI Parser BApp

### Identifying API Endpoints

* Burp Scanner auto extracts some endpoints during crawls, but for a more heavyweight extraction, use the JS Link Finder BApp
* Identifying supported HTTP methods - use the built-in HTTP verbs list in Burp Intruder
* Identifying supported content types
* **Changing the Content-Type may enable you to**:&#x20;
  * Trigger errors that disclose useful information.&#x20;
  * Bypass flawed defenses.&#x20;
  * Take advantage of differences in processing logic.
* **Modify the Content-Type header, then reformat the request body accordingly**
* Using Intruder to find hidden endpoints
* **Use in-built wordlists or common relevant keywords**.
  * Lab - Look for API's that allow multiple HTTP methods and modify request based on the response obtained using new method. (modified the price of a product to 0)

### Finding Hidden Parameters

* Burp Intruder
* Param miner BApp - automatically guesses names relevant to the application, based on information taken from the scope.
* Content discovery tool

### Mass Assignment Vulnerabilities

* Identifying hidden parameters - examine objects returned by the API.&#x20;
* Lab - Identify the hidden parameters using other API's and modify the target API to purchase the product. (modify price or discount %)

### Server-Side Parameter Pollution&#x20;

* Occurs when a website embeds user input in server-side request to an internal API without adequate encoding
* Enables attacker to:
  * Override existing parameters.&#x20;
  * Modify the application behavior.&#x20;
  * Access unauthorized data.

### Testing for Server-Side Parameter Pollution in the Query String

* Place query syntax characters like #, &, and = in your input and observe
* **Truncate Query Strings**
  * Essential to URL-encode # character, else the front-end app will interpret it as a fragment identifier and won't be passed to the internal API
* **Injecting Invalid Parameters**
  * URL-encoded '&' character in attempt to add a second parameter to the server-side request.
* **Injecting Valid Parameters**
  * Use param miner, content discovery to identify a valid parameter and pass a value
* **Overriding Existing Parameters**
  * Try to override the original parameter
  * eg: GET /userSearch?name=peter%26name=carlos\&back=/home
* Lab - Identify the endpoint vulnerable to parameter pollution by using above methods. Observe the response revealing info about any params missing in the response. Look for any params such as reset token, password or email that the backend server would accept and provide a value.

### Testing for Server-Side parameter Pollution in REST Paths

* Uses parameters values along with url
* eg: GET /edit\_profile.php?name=peter (webapp), GET /api/private/users/peter (converted server side request)
* Leverage the path traversal technique to access other users&#x20;
* Lab - Perform path traversal and observe error message "Invalid route". Traverse to the end and access the 'openapi.json' documentation file to view contents. Adjust the field to contain reset token or something that is relevant. Observe still we are unable to obtain the value due to current API version. Traverse to an old/newer version(../../) that might provide the value. (make sure to use encoded # to fragment the trailing path)

### Testing for Server-Side Parameter Pollution in Structured Data Formats

* If allowed to update the name, which invokes backend request, we can modify the request to include additional params like role, access\_level etc that would escalate our privileges.
* When appending additional params we need to follow the syntax. Use " when required so that backend request would work without any syntax error.
* eg: name=peter","access\_level":"administrator or {"name": "peter","access\_level":"administrator"}
* According to the content-type used modify payload appropriately

### Testing with Automated Tools

* Burp Scanner, Backslash Powered Scanner BApp
