# Host Header Attacks

| Header Injection | `\n` `\r\n` `\t` `%0d` `%0a` `%09` |
| ---------------- | ---------------------------------- |

{% hint style="info" %}
Used to identify which back-end component the client wants to communicate with, since multiple websites and apps can be accessed at the same IP.
{% endhint %}

## Possible Scenarios

* **Virtual hosting** - when a single web server hosts multiple websites or applications with single or different owners.
* **Routing traffic via an intermediary** - a load balancer, reverse proxy, or CDN used to route to different back-end servers hosting web apps.

## HTTP Host Header Attack

* If the server implicitly trusts the `Host` header and fails to validate it, an attacker may use this input to inject harmful payloads that manipulate server-side behavior.
* Attacks that inject a payload directly into the `Host` header are known as **"Host header injection"** attacks.
* Off-the-shelf web applications don't know what domain they are deployed on unless specified. To generate an absolute URL, they might fetch the value from the `Host` header.
* **Possible Issues:**
  * Web cache poisoning
  * Business logic flaws in specific functionality
  * Routing-based SSRF
  * Classic server-side vulnerabilities, such as SQL injection

## Testing for HTTP Host Header Attacks/Injection

### Supply an Arbitrary Host Header

* Test what happens when you supply an arbitrary domain name via the `Host` header.
* Either receive an error message `Invalid Host header` from the CDN/proxy, or the app defaults/falls back to a page of a particular website.

### Check for Flawed Validation

* Supply a non-numeric port, leave the domain name untouched, while potentially injecting a payload via the port.
* Bypass validation entirely by registering an arbitrary domain name that ends with the same sequence of characters as the whitelisted one.
* Take advantage of a less-secure subdomain that you have already compromised.

### Send Ambiguous Requests

* Inject duplicate `Host` headers.
* Supply an absolute URL, e.g.:

  ```http
  GET https://vulnerable-website.com/ HTTP/1.1
  Host: attacker.com
  ```

  (try using both HTTP and HTTPS)
* Add line wrapping - uncover quirky behavior by indenting HTTP headers with a space character or tab.
* Other techniques - refer to [Request Smuggling](http-request-smuggling.md "mention").

### Inject Host Override Headers

* `X-Forwarded-Host`, `X-Host`, `X-Forwarded-Server`, `X-HTTP-Host-Override`, `Forwarded`

## Exploiting the HTTP Host Header

### Password Reset Poisoning

* Attacker manipulates a vulnerable website into generating a password reset link pointing to a domain under their control.
* **Construct a password reset poisoning attack:**
  * Attacker obtains the victim's email and issues a reset request. Modify this request so the `Host` header contains the attacker's URL. The email sent to the user will then contain the attacker's domain along with the token. If the user accesses the link (or an AV/link-scanner does), the attacker obtains the token.
  * Use the `Host` header to inject HTML into sensitive emails.
* **Lab** - Change the Host header to the attacker's URL and try.
* **Lab** - Include an override header containing the attacker's domain.
* **Lab** - The Host header accepts arbitrary text, e.g. `Host: domain:<text>`. This misconfiguration can be used to inject an HTML tag that would append the remaining string to an attacker-controlled URL.

### Web Cache Poisoning via the Host Header

* The `Host` header is reflected in the response markup without HTML-encoding, or even used directly in script imports.
* To construct a cache poisoning attack, elicit a response from the server that reflects an injected payload.
* Standalone caches key on the `Host` header, so this approach works best on integrated, application-level caches but might work on standalone caches too.
* **Lab** - Include a duplicate Host header (or try any of the above techniques) and observe the value reflected in one of the `src` params. Store an XSS payload in the given path pointing to an attacker server. The victim is then served the cached response containing the link to the attacker server.

### Accessing Restricted Functionality

* Websites' access control features make flawed assumptions that allow bypassing restrictions by modifying the Host header.
* **Lab** - Modify the Host header to `localhost` to access admin pages.

### Accessing Internal Websites with Virtual Host Brute-Forcing

* Companies might host publicly accessible websites and private, internal sites on the same server.
* An attacker can access any virtual host on any server they have access to, provided they can guess the hostnames or brute-force using Intruder.

### Routing-Based SSRF

* Check whether the server tries to resolve an arbitrary domain mentioned in the Host header, using Collaborator. Even if a DNS response is obtained, modify the Host header to contain an internal IP and access the admin panel (brute-force the internal IP using Intruder).
* **Lab** - Provide an absolute URL along with the path, e.g. `GET https://domain.com/path HTTP/2`, with the Host header containing a Collaborator link. Modify the Host header, use Intruder to find the private IP that gives access to the admin panel.

### Connection State Attacks

* Websites reuse connections for multiple request/response cycles with the same client.
* Encounter servers that perform validation only on the first request they receive over a new connection. Bypass this validation by sending a normal request, then following up with your malicious one down the same connection.
* **Lab** - Use the Group feature in the Repeater tab. Send requests in sequence using the same connection, where the first request is normal and the following one contains a malformed request where the Host header points to a private IP and provides an absolute URL (like the previous lab). Make sure the `Connection` header is set to `keep-alive`.

### SSRF via a Malformed Request Line

* Proxies fail to validate the request line properly, which allows you to supply unusual, malformed input with unfortunate results.
* **Payload:** `GET @private-intranet/example HTTP/1.1`
* The resulting upstream URL will be `http://backend-server@private-intranet/example`, where `backend-server` is considered the username.