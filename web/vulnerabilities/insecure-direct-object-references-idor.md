# Insecure Direct Object References (IDOR)

{% hint style="info" %}
IDOR vulnerabilities occur when a web application exposes a direct reference to an object, like a file or a database resource, which the end-user can directly control to obtain access to other similar objects. If any user can access any resource due to the lack of a solid access control system, the system is considered to be vulnerable.
{% endhint %}

## Identifying IDORs

* **URL Parameters & APIs**
  * Whenever we receive a specific file or resource, we should study the HTTP requests to look for URL parameters or APIs with an object reference (e.g. `?uid=1` or `?filename=file_1.pdf`). These are mostly found in URL parameters or APIs but may also be found in other HTTP headers, like cookies.
  * Try incrementing the values of the object references to retrieve other data, like (`?uid=2`) or (`?filename=file_2.pdf`).
  * We can also use a fuzzing application to try thousands of variations and see if they return any data.
* **AJAX Calls**
  * We may also be able to identify unused parameters or APIs in the front-end code in the form of JavaScript AJAX calls.
  * Some web applications developed in JavaScript frameworks may insecurely place all function calls on the front-end and use the appropriate ones based on the user role.
* **Hash/Encoded ID's**
  * Suppose the reference was encoded with a common encoder (e.g. `base64`).
  * We could decode it and view the plaintext of the object reference, change its value, and then encode it again to access other data.
* **Compare User Roles**
  * We may need to register multiple users and compare their HTTP requests and object references.
  * This may allow us to understand how the URL parameters and unique identifiers are being calculated and then calculate them for other users to gather their data.

## IDOR Enumeration <a href="#mass-idor-enumeration" id="mass-idor-enumeration"></a>

### Insecure Parameters <a href="#insecure-parameters" id="insecure-parameters"></a>

* Fuzz the vulnerable parameter to get details of an object that we do not gebrally have access.

### Mass Enumeration <a href="#mass-enumeration" id="mass-enumeration"></a>

* Look for any patterns used in the naming convention of files and create a bash script to generate a wordlist that can be used for fuzzing.

## Bypassing Encoded References <a href="#bypassing-encoded-references" id="bypassing-encoded-references"></a>

* Web application uses hashing it in an `md5` format. Hashes are one-way functions, so we cannot decode them to see their original values.
* We can attempt to hash various values, like `uid`, `username`, `filename`, and many others, and see if any of their `md5` hashes match the actual value. If we find a match, then we can replicate it for other users and collect their files.
* #### Function Disclosure <a href="#function-disclosure" id="function-disclosure"></a>
  * As most modern web applications are developed using JavaScript frameworks, like `Angular`, `React`, or `Vue.js`, many web developers may make the mistake of performing sensitive functions on the front-end, which would expose them to attackers.

## IDOR in Insecure APIs <a href="#idor-in-insecure-apis" id="idor-in-insecure-apis"></a>

* **IDOR Insecure Function Calls** enable us to call APIs or execute functions as another user.
* Such functions and APIs can be used to change another user's private information, reset another user's password, or even buy items using another user's payment information.

## Chaining IDOR Vulnerabilities <a href="#chaining-idor-vulnerabilities" id="chaining-idor-vulnerabilities"></a>

### Information Disclosure <a href="#information-disclosure" id="information-disclosure"></a>

* **IDOR Information Disclosure vulnerability** - We obtain details of another user, file or other relevant information that was intended was current user.

### Modifying Other Users' Details <a href="#modifying-other-users-details" id="modifying-other-users-details"></a>

* **IDOR Insecure Function Calls**
* If the attacker is able to update the profile details of another user, modify user's email address and then request a password reset link, which will be sent to the email address we specified, thus allowing us to take control over their account.
* Another potential attack is `placing an XSS payload in the 'about' field`, which would get executed once the user visits their `Edit profile` page, enabling us to attack the user.

## Mitigations

* Object-Level Access Control - we must map the RBAC to all objects and resources.
* Object Referencing - we should never use object references in clear text or simple patterns (e.g. `uid=1`). We should always use strong and unique references, like salted hashes.
