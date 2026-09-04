# HTTP Request Smuggling

{% hint style="info" %}
Interfering with the way a website processes sequences of HTTP requests that are received from one or more users.
{% endhint %}

## Overview

* Allows an attacker to bypass security controls, gain unauthorized access to sensitive data, & compromise other application users.
* Primarily associated with HTTP/1 requests. However, websites that support HTTP/2 may be vulnerable.
* When the front-end server forwards requests to the back-end, it typically sends several requests over the same back-end network connection (`Connection: keep-alive`).

### How Do HTTP Request Smuggling Vulnerabilities Arise?

* Provides two different ways to specify where a request ends: the `Content-Length` header and the `Transfer-Encoding` header.
* Possible for a single message to use both methods at once, such that they conflict with each other.
* If both `Content-Length` and `Transfer-Encoding` headers are present, then the `Content-Length` header should be ignored.

### How to Perform an HTTP Request Smuggling Attack

* **CL.TE** - front-end server uses `Content-Length` header, back-end server uses `Transfer-Encoding` header.
* **TE.CL** - front-end server uses `Transfer-Encoding` header, back-end server uses `Content-Length` header.
* **TE.TE** - front-end and back-end servers both support `Transfer-Encoding` header, but one of the servers can be induced not to process it by obfuscating the header.
* Involves sending two requests to the application in quick succession (create separate tabs):
  * An **"attack"** request, designed to interfere with processing of the next request.
  * A **"normal"** request.

## CL.TE Vulnerabilities

{% hint style="info" %}
Need to provide just the first character (i.e. `G`) - the remaining will be taken from the next request.
{% endhint %}

* **Lab** - Include both CL & TE headers. Use HTTP/1.1 & `Connection: keep-alive`.
* **Payload:** `\r\n0\r\n\r\nG`

## TE.CL Vulnerabilities

{% hint style="info" %}
Need to provide `G` then `POST / HTTP/1.1` -> `Content-Type` -> `Content-Length` -> Body -> `0\r\n\r\n`.
{% endhint %}

* Ensure the "Update Content-Length" option is unchecked.
* Include the trailing sequence `\r\n\r\n` following the final `0`.
* Include the appropriate chunk size (hex value) by highlighting the content and viewing the Burp Inspector.
* **Lab** - Include CL & TE following the above rules.

## TE.TE Behavior: Obfuscate the TE Header

* Front-end & back-end servers both support the `Transfer-Encoding` header, but one of the servers can be induced not to process it by obfuscating the header.
* Example obfuscations:

```
Transfer-Encoding: xchunked
Transfer-Encoding : chunked
Transfer-Encoding: chunked
Transfer-Encoding: x
Transfer-Encoding:[tab]chunked
[space]Transfer-Encoding: chunked
X: X[\n]Transfer-Encoding: chunked
Transfer-Encoding
: chunked
```

* Depending on whether the front-end or back-end server can be induced not to process the obfuscated `Transfer-Encoding` header, the remainder of the attack will take the same form as the CL.TE or TE.CL vulnerabilities.
* **Lab** - Include both `Content-Length` & `Transfer-Encoding` where one is obfuscated. Also, uncheck "Update Content-Length" & include the trailing sequence `\r\n\r\n`.

## Find HTTP Request Smuggling Vulnerabilities

### Find CL.TE Vulnerabilities Using Timing Techniques

```http
POST / HTTP/1.1
Host: vulnerable-website.com
Transfer-Encoding: chunked
Content-Length: 4

1
A
X
```

* Front-end uses the CL header and will forward part of the request, omitting `X`. Back-end uses the TE header, processes the first chunk, & waits for the next chunk.

### Find TE.CL Vulnerabilities Using Timing Techniques

```http
POST / HTTP/1.1
Host: vulnerable-website.com
Transfer-Encoding: chunked
Content-Length: 6

0

X
```

* Front-end uses the TE header and will forward part of this request, omitting `X`. Back-end uses the CL header, expects more content in the body, and waits for the remaining content.

### Confirm CL.TE Vulnerabilities Using Differential Responses

* If the attack is successful, the last two lines of the request are treated by the back-end as belonging to the next request that is received. This causes the subsequent "normal" request to contain the last 2 lines considered by the back-end, which will eventually throw an error message.
* **Lab** - Combine the above labs and smuggle a request that calls for an invalid resource.

### Confirm TE.CL Vulnerabilities Using Differential Responses

* **Lab** - Perform similar steps as above; smuggle a request that calls an invalid resource from the server.

## Exploit HTTP Request Smuggling Vulnerabilities

### Bypass Front-End Security Controls

* Front-end is used to implement some security controls, deciding whether to allow individual requests.
* Back-end then honors every request without further checking.
* **Lab** - Modify the smuggled request where the Host header contains `localhost` and the admin panel can be accessed. Also form the smuggled request in such a way that the 'normal' request is considered part of the smuggled body.
* If vulnerable to CL.TE, do not keep `\r\n` at the end of the body, so that the normal request is considered as the body and to prevent duplicate headers or 2 HTTP methods.

### Reveal Front-End Request Rewriting

* Front-end performs some rewriting of requests before they are forwarded to the back-end:
  * Terminate the TLS connection and add headers describing the protocol and ciphers used.
  * Add an `X-Forwarded-For` header containing the user's IP address.
  * Determine the user's ID based on their session token and add a header identifying the user.
  * Add sensitive information that is of interest for other attacks.
* If smuggled requests are missing some headers that are added by the front-end, the back-end might not process the requests in the normal way.

```http
POST / HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 124
Transfer-Encoding: chunked

0

POST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 200
Connection: close

search=test
```

* Steps to reveal the headers that need to be included in smuggled requests:
  1. Find a POST request that reflects the value of a request parameter into the application's response.
  2. Shuffle the parameters so that the reflected parameter appears last in the message body.
  3. Smuggle this request to the back-end server, followed directly by a normal request whose rewritten form you want to reveal.
  4. The value in the `Content-Length` header of the smuggled request determines how long the back-end server believes the request is.
* **Lab** - The Comment request reflects the comment. Smuggle this request where the 'comment' parameter is placed at the end so that the normal request is included in the comments section. Obtain the headers required and smuggle a request that would give sensitive info or a session token.

### Bypass Client Authentication

* Some apps request a client certificate for authentication that is used by the back-end as part of the access control mechanism.
* The component that authenticates the client passes relevant details from the certificate to the app/back-end via non-standard HTTP headers (e.g. `X-SSL-CLIENT-CN: carlos`).
* Assuming you're able to send the right combination of headers and values, this may enable you to bypass access controls.
* Isn't usually exploitable, as the front-end tends to overwrite these headers. However, smuggled requests are hidden from the front-end, so any headers they contain will be sent to the back-end unchanged.

### Capture Other Users' Requests

* If the app contains any functionality that allows you to store and later retrieve textual data, you can use this to capture the contents of other users' requests.
* Suitable functions to use as the vehicle for this attack: comments, emails, profile descriptions, screen names, etc.
* To perform the attack, smuggle a request that submits data to the storage function, with the parameter containing the data to store positioned last in the request.
* Limitation: this technique will generally only capture data up until the parameter delimiter (i.e. `&`) applicable for the smuggled request.
* **Lab** - Smuggle the 'comment' request where the comment parameter should be placed at the end so that the victim's request will be appended to the comments.

### Exploit Reflected XSS

* If an app is vulnerable to request smuggling and also contains reflected XSS, you can use the request smuggling attack to hit other users of the application.
* Requires no interaction with the victim. Used to exploit XSS behavior in parts of the request that cannot be trivially controlled, such as HTTP request headers.
* **Lab** - View the Post page vulnerable to XSS in the `User-Agent` header. Smuggle the View Post request containing the XSS payload in the `User-Agent` header.

### Turn an On-Site Redirect into an Open Redirect

* Apps perform on-site redirects from one URL to another and place the hostname from the request's Host header into the redirect URL.
* Smuggle a request that would redirect the victim user to an attacker-controlled website. This works even if `Location` does not contain `https`. E.g. `Bypass://attacker-website.com/example`.

### Perform Web Cache Poisoning

* Attacker causes the app to store some malicious content in the cache, and this content is served from the cache to other application users.
* Smuggled request reaches the back-end, which responds as before with the off-site redirect. Front-end caches this response against what it believes is the URL in the second request, for a request made by the victim.
* Any other users accessing the same resource will be served with the poisoned cached response redirecting them to the attacker's website.
* **Lab** - Find a request that gives a redirect response. Smuggle this request with the Host header modified. Send any other normal request that users would visit. The normal request would receive a redirect response that was cached and would redirect all users to the attacker's website.

### Perform Web Cache Deception

* Attacker causes the app to store some sensitive content belonging to another user in the cache, and the attacker then retrieves this content from the cache.
* Example: Find a request that returns sensitive info specific to the user. Smuggle this request, so that when a user requests a static page, the smuggled request gets appended with the session cookies of the user and the front-end caches the response to the static page with the sensitive content. The attacker can now view the sensitive info by accessing the static page.
* Important caveat: the attacker doesn't know the URL against which the sensitive content will be cached, since this will be whatever URL the victim user happened to be requesting when the smuggled request took effect. The attacker might need to fetch a large number of static URLs to discover the captured content.
* **Lab** - Follow the above steps, but make sure that when requesting the static page, the session cookie is different and not tied to the attacker's account.

## Advanced Request Smuggling

### HTTP/2 Request Smuggling

* **HTTP/2 message length** - messages are sent over the wire as a series of separate "frames". Each frame is preceded by an explicit length field, which tells the server exactly how many bytes to read in. Therefore, the length of the request is the sum of its frame lengths.
* **HTTP/2 Downgrading:**
  * Front-end rewrites the incoming HTTP/2 request using HTTP/1 syntax, effectively generating its HTTP/1 equivalent so the back-end can process the request.
  * The HTTP/1 back-end response is then converted to HTTP/2 and served to the user.

#### H2.CL Vulnerabilities

* HTTP/2 requests don't have to specify their length explicitly in a header.
* During downgrading, this means front-end servers often add an HTTP/1 `Content-Length` header.
* The spec dictates that any `content-length` header in an HTTP/2 request must match the length calculated using the built-in mechanism, but this isn't always validated properly before downgrading.

```http
POST / HTTP/2
Host: YOUR-LAB-ID.web-security-academy.net
Content-Length: 0

GET /resources HTTP/1.1
Host: foo
Content-Length: 5

x=1
```

* **Lab** - The smuggled request redirects the user to an attacker-controlled website, since the Host header can be modified.

#### H2.TE Vulnerabilities

* Chunked transfer encoding is incompatible with HTTP/2, and the spec recommends that any `Transfer-Encoding` header should be stripped/blocked entirely.
* If the front-end fails to strip/block it, and downgrades the request for an HTTP/1 back-end that does support chunked encoding, this enables request smuggling.

#### Hidden HTTP/2 Support

* Enable the `Allow HTTP/2 ALPN override` option.

### Response Queue Poisoning

{% hint style="info" %}
Possible both via classic HTTP/1 request smuggling & by exploiting HTTP/2 downgrading.
{% endhint %}

* Causes the front-end to start mapping responses from the back-end to the wrong requests.
* Achieved by smuggling a complete request, thereby eliciting two responses from the back-end when the front-end is only expecting one.
* **Impact:** the attacker can capture other users' responses simply by issuing arbitrary follow-up requests.
* **Constructing a response queue poisoning attack:**
  * The TCP connection between front-end and back-end is reused for multiple request/response cycles.
  * Attacker is able to successfully smuggle a complete, standalone request that receives its own distinct response from the back-end.
  * The attack does not result in either server closing the TCP connection. Servers generally close incoming connections when they receive an invalid request because they can't determine where the request is supposed to end.

**Smuggle a Complete Request:**

```http
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Type: x-www-form-urlencoded
Content-Length: 61
Transfer-Encoding: chunked

0

GET /anything HTTP/1.1
Host: vulnerable-website.com

GET / HTTP/1.1
Host: vulnerable-website.com

```

* **Lab** - Make sure the smuggled request ends with `\r\n\r\n`. Smuggle a request that responds with a 404 response to the victim's request. The attacker sends a normal request and is served with the victim's intended response.

### Request Smuggling via CRLF Injection

* In HTTP/1, you can sometimes exploit discrepancies between how servers handle standalone newline (`\n`) characters to smuggle prohibited headers.
* HTTP/2 messages are binary rather than text-based; the boundaries of each header are based on explicit, predetermined offsets rather than delimiter characters.
* This means `\r\n` has no special significance within a header value and can be included inside the value itself without causing the header to be split.
* **Lab** - Use the Inspector module to add a header `foo` with value `bar\r\nTransfer-Encoding: chunked`. This would show that the request is smuggled. Smuggle a request that reflects the contents in the response (refer to Capturing Other Users' Requests).

### HTTP/2 Request Splitting

* In response queue poisoning, you learned how to split a single HTTP request into two complete requests inside the message body on the back-end.
* When HTTP/2 downgrading is in play, you can also cause this split to occur in the headers instead.
* This approach is more versatile because you aren't dependent on using request methods that are allowed to contain a body. For example, you can even use a GET request, compared to earlier cases where all smuggled requests used the POST method.
* **Accounting for front-end rewriting** - need to understand how the request is rewritten by the front-end and account for this when adding any HTTP/1 headers manually.
* Need to adjust the positioning of any internal headers or headers for the first request that you want to inject.
* **Lab** - Refer to Response Queue Poisoning and smuggle a request within a header value that can be injected using the Inspector module. The front-end would auto-append `\r\n\r\n` while rewriting, so no need to include it in the smuggled request.

### HTTP Request Tunnelling

* Many of the attacks above were possible because the front-end & back-end exchanged multiple requests over the same connection.
* Some servers only allow requests originating from the same IP address or the same client to reuse the connection.
* Technique to bypass front-end security measures that may prevent you from sending certain requests. You would get a response appended to another response.
* Request tunnelling is possible with HTTP/1 and HTTP/2 but is considerably more difficult to detect in HTTP/1-only environments due to keep-alive connections.
* In HTTP/2, on the other hand, each "stream" should only ever contain a single request and response.
* The attack was successful if you receive an HTTP/2 response with what appears to be an HTTP/1 response in the body.
* **Leaking internal headers via HTTP/2 request tunnelling** - trick the front-end into appending the internal headers inside what will become a body param on the back-end.

#### Blind Request Tunnelling

* If you successfully tunnel a request, the servers will forward both responses to the client, with the response to the tunnelled request nested inside the body of the main response (if the front-end reads in all the data).
* If the front-end only reads in the number of bytes specified in the `Content-Length`, this results in **blind tunnelling**.
* Blind tunnelling can be exploited by issuing a `HEAD` request, as it contains a `Content-Length` that reveals the length of the actual `GET` request which is yet to be issued. The tunnelled response would appear as the response body to the `HEAD` request.
* **Lab** - Refer to the solution. Need to smuggle requests within the header name and not the value.

#### Web Cache Poisoning via HTTP/2 Request Tunnelling

* _(Future reference - to be documented.)_

## Browser-Powered Request Smuggling

### CL.0 Request Smuggling

* In some instances, servers can be persuaded to ignore the `Content-Length` header, meaning they assume that each request finishes at the end of the headers.
* **Testing for CL.0 vulnerabilities:**
  1. First send a request containing another partial request in its body, then send a normal follow-up request.
  2. Check whether the response to the follow-up request was affected by the smuggled prefix.
  3. To try this using Burp Repeater:
     * Create one tab containing the setup request and another containing an arbitrary follow-up request.
     * Add the two tabs to a group in the correct order.
     * Using the drop-down menu next to the Send button, change the send mode to "Send group in sequence (single connection)".
     * Change the `Connection` header to `keep-alive`.
     * Send the sequence and check the responses.
* **Lab** - Follow the above steps and find a request that could be vulnerable to such attacks. Mostly it's static files such as `.js`, `.svg`, etc.
* Websites that downgrade HTTP/2 to HTTP/1 may be vulnerable to an equivalent "H2.0" issue if the back-end ignores the `Content-Length` of the downgraded request.
