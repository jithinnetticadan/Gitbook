# Access Control

### Access Control Security Models

* Programmatic access control - matrix of user privileges is stored in a database, include roles or groups or individual users, collections or workflows of processes
* Discretionary access control (DAC) - Owners of resources assign permission to users - gets complex when no. of users increases
* Mandatory access control (MAC) - centrally controlled system of access control
* Role-based access control (RBAC) - provide access controls based on role

### Vertical Access Controls

* Admin privileges

### Horizontal Access Controls

* One user not allowed to view details of other user&#x20;

### Context-dependent Access Controls

* Based upon the state of the application or the user's interaction&#x20;
* For example, a retail website might prevent users from modifying the contents of their shopping cart after they have made payment.

### Testing

* **Unprotected Functionality**
  * search for any pages with admin functionalities (robots.txt or look in the server response mentioning the URL based on role)
* **Parameter-Based Access Control Methods**
  * User role controlled by request parameter - cookie value decides whether to provide admin access
  * User role can be modified in user profile - check for any parameter that checks the privilege in request or response
  * If found in response try sending that parameter assigning a different value to obtain high level privilege along with the request body
* **Platform Misconfiguration**&#x20;
  * _**URL-based can be circumvented**_
    * Some application support non-standard HTTP headers to override the URL in the original request, such as X-Original-URL and X-Rewrite-URL.
    * Bypass certain HTTP methods being performed on a particular URL&#x20;
  * _**Method-based can be circumvented**_
    * If restrictions are in place for POST method we can try executing the operation using GET method (vice-versa)
* **Horizontal Privilege Escalation**
  * Check for any parameter that can be tampered.
  * Check for any id's in any messages, posts, comments etc that mentions any unique id tagged to that user.
  * While changing the parameter tagged to user observe the response in redirection to login page
* **Horizontal - Vertical Privilege Escalation**
  * Similar to horizontal checks, only difference is gain access to privileged user.
  * Check whether after escalation if the current user password field is auto-populated, if so password can be obtained from the response
* **Insecure Direct Object References**
  * Check for any incremental parameter that can be tampered
* **Vulnerabilities in Multi-Step Processes**
  * In multi-step process of form filling or related kinds, there is a chance some steps might not have access controls set.
* **Referrer-Based**
  * Application enforces access control over the main administrative page at /admin, but for sub-pages such as /admin/delete
  * User only inspects the Referrer header. If the Referrer header contains the main /admin URL, then the request is allowed.
* **Location-Based**
  * Circumvented by the use of web proxies, VPNs, or manipulation of client-side geolocation mechanisms
