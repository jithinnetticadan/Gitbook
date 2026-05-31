# Cross-Site Scripting (XSS)

<details>

<summary>Custom Payloads</summary>

* [xssnow](https://xssnow.in/)

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

### Reflected XSS

* Reflected XSS into HTML context with nothing encoded
* `<script>alert(1);</script>`
* provide the payloads in any entry point such as parameters, request body, url-parameters, HTTP Headers etc

### Stored XSS

* Stored XSS into HTML context with nothing encoded
* basic example same payload as above

### DOM-Based XSS

* Place data into a source so that it is propagated to a sink and causes execution of arbitrary JavaScript
* Most common source for DOM XSS is the URL, which is typically accessed with the window.location object.
* DOM - is a web browser's hierarchical representation of the elements on the page.
* **Source** is a JavaScript property that accepts data that is potentially attacker-controlled. eg location.search property because it reads input from the query string.
* **Sink** is a potentially dangerous JavaScript function or DOM object that can cause undesirable effects if attacker-controlled data is passed to it. Eg eval() function.
* **Common Sources** - `document.URL, document.documentURI, document.URLUnencoded, document.baseURI, location, document.cooki, document.referrer, window.name, history.pushState, history.replaceState, localStorage, sessionStorage, IndexedDB (mozIndexedDB, webkitIndexedDB, msIndexedDB), Database`&#x20;
* **Common Sinks** - `document.write(), document.writeln(), document.domainm element.innerHTML, element.outerHTML, element.insertAdjacentHTML, element.onevent`&#x20;
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



#### References

* [Beyond XSS: Explore the Web Front-end Security Universe](https://aszx87410.github.io/beyond-xss/en/)

