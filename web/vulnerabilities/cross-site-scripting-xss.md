# Cross-Site Scripting (XSS)

<details>

<summary>Custom Payloads</summary>

* `` 111">><details/open/%253e/ontoggle​=import(` ``
* [xssnow](https://xssnow.in/)

</details>

allows an attacker to compromise the interactions that users have with a vulnerable application \* allows an attacker to masquerade as a victim user, to carry out any actions that the user is able to perform, and to access any of the user's data. \* cross-origin iframes are prevented from calling alert() in google chrome, alternative for it is the print() \* Reflected XSS, where the malicious script comes from the current HTTP request \* Stored XSS, where the malicious script comes from the website's database. \* DOM-based XSS, where the vulnerability exists in client-side code rather than server-side code. - Impact of reflected XSS attacks \* Perform any action within the application that the user can perform. \* View any information that the user is able to view. \* Modify any information that the user is able to modify. \* Initiate interactions with other application users, including malicious attacks, that will appear to originate from the initial victim user. - Reflected XSS \* Reflected XSS into HTML context with nothing encoded - basic example of xss - payload alert(1); - provide the payloads in any entry point such as parameters, request body, url-parameters, HTTP Headers etc - Stored cross-site scripting \* Stored XSS into HTML context with nothing encoded - basic example same payload as above - DOM-based cross-site scripting \* need to place data into a source so that it is propagated to a sink and causes execution of arbitrary JavaScript \* most common source for DOM XSS is the URL, which is typically accessed with the window.location object. \* DOM - is a web browser's hierarchical representation of the elements on the page. \* Source is a JavaScript property that accepts data that is potentially attacker-controlled. eg location.search property because it reads input from the query string \* Sink is a potentially dangerous JavaScript function or DOM object that can cause undesirable effects if attacker-controlled data is passed to it. Eg eval() function Common sources - document.URL, document.documentURI, document.URLUnencoded, document.baseURI, location, document.cooki, document.referrer, window.name, history.pushState, history.replaceState, localStorage, sessionStorage, IndexedDB (mozIndexedDB, webkitIndexedDB, msIndexedDB), Database Common Sinks - document.write(), document.writeln(), document.domainm element.innerHTML, element.outerHTML, element.insertAdjacentHTML, element.onevent jQuery Sinks - add(), after(), append(), animate(), insertAfter(), insertBefore(), before(), html(), prepend(), replaceAll(), replaceWith(), wrap(), wrapInner(), wrapAll(), has(), constructor(), init(), index(), jQuery.parseHTML(), $.parseHTML() DOM XSS combined with reflected and stored data - Reflected DOM XSS \* makes use of json code to reflect the payload \* payload = "-alert(1);}// (\ used to escape the double-quotes being provided auto) - Stored DOM XSS \* go through the JavaScript code to determine how the inputs from user are being handled, whether the code checks any characters which is sanitized and displayed safely \* look for any methods that can bypass these checks \* payload <> (code encodes the first occurrence of angle brackets) - Controlling the web message source \* DOM XSS using web messages - window.addEventListener('message', function(e) { eval(e.data); }); **vulnerable code** - payload \* DOM XSS using web messages and a JavaScript URL -&#x20;\
window.addEventListener('message', function(e) {\
var url = e.data;\
if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {\
location.href = url;\
}\
}, false);&#x20;\- payload Testing HTML sinks - provide malicious string in a vulnerable source and search for it in the dev tool option Testing JavaScript execution sinks input string doesn't appear in DOM - make use of JavaScript debugger. Testing for DOM XSS using DOM Invader DOM XSS in document.write sink using source location.search Payload - "> DOM XSS in document.write sink using source location.search inside a select element Introduce a new URL query parameter Payload - ">\<img+src=1+onerror=alert(1)> DOM XSS in innerHTML sink using source location.search The innerHTML sink doesn't accept script elements on modern browser, nor will svg onload events fire. Hence need to use alternative elements like img or iframe. DOM XSS in jQuery

####

#### References

* [Beyond XSS: Explore the Web Front-end Security Universe](https://aszx87410.github.io/beyond-xss/en/)

