# Access Control

Access control security models \* Programmatic access control - matrix of user privileges is stored in a database, include roles or groups or individual users, collections or workflows of processes \* Discretionary access control (DAC) - Owners of resources assign permission to users - gets complex when no. of users increases \* Mandatory access control (MAC) - centrally controlled system of access control \* Role-based access control (RBAC) - providing access controls based on role - Vertical access controls - admin privileges - Horizontal access controls - one user not allowed to view details of other user - Context-dependent access controls - based upon the state of the application or the user's interaction \* For example, a retail website might prevent users from modifying the contents of their shopping cart after they have made payment. - Vertical and Horizontal privEsc

* Testing - Unprotected functionality
  * search for any pages with admin functionalities (robots.txt or look in the server response mentioning the URL based on role) - Parameter-based access control methods
  * User role controlled by request parameter - cookie value decides whether to provide admin access
  * User role can be modified in user profile - check for any parameter that checks the privilege in request or response $ If found in response try sending that parameter assigning a different value to obtain high level privilege along with the request body - Broken access control resulting from platform misconfiguration URL-based access control can be circumvented
  * Some application support non-standard HTTP headers to override the URL in the original request, such as X-Original-URL and X-Rewrite-URL. $ to bypass certain HTTP methods being performed on a particular URL Method-based access control can be circumvented
  * If restrictions are in place for POST method we can try executing the operation using GET method (vice-versa) - Horizontal privilege escalation
  * check for any parameter that can be tampered.
  * check for any id's in any messages, posts, comments etc that mentions any unique id tagged to that user.
  * while changing the parameter tagged to user observe the response in redirection to login page - Horizontal to vertical privilege escalation
  * similar to horizontal checks, only difference is gain access to privileged user.
  * check whether after escalation if the current user password field is auto-populated, if so password can be obtained from the response - Insecure direct object references
  * check for any incremental parameter that can be tampered - Access control vulnerabilities in multi-step processes
  * in multi-step process of form filling or related kinds, there is a chance some steps might not have access controls set. - Referrer-based access control
  * application enforces access control over the main administrative page at /admin, but for sub-pages such as /admin/deleteUser only inspects the Referrer header. If the Referrer header contains the main /admin URL, then the request is allowed. - Location-based access control
  * circumvented by the use of web proxies, VPNs, or manipulation of client-side geolocation mechanisms
