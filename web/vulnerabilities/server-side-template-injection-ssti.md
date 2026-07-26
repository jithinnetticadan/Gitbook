# Server-Side Template Injection (SSTI)

{% hint style="info" %}
Attacker is able to use native template syntax to inject a malicious payload into a template.
{% endhint %}

## Overview

* Templating engines: Mako, Twig, Jade, Smarty, Jinja2, Freemarker, Velocity.
* Template engines are designed to generate web pages by combining fixed templates with volatile data.
* Attackers inject arbitrary template directives to manipulate the template engine, enabling them to take complete control of the server.

### How Do Server-Side Template Injection Vulnerabilities Arise?

* Attacks can occur when user input is concatenated directly into a template, rather than passed in as data.
* Static templates that simply provide placeholders into which dynamic content is rendered are generally not vulnerable.
* **Not Vulnerable:** `$output = $twig->render("Dear {first_name},", array("first_name" => $user.first_name));`
* **Vulnerable:** `$output = $twig->render("Dear " . $_GET['name'])`;

## Construct a Server-Side Template Injection Attack

### Detect

* Try fuzzing the template by injecting: `${{<%[%'"}}%\`
* Use an in-built wordlist.
* SSTI occurs in two distinct contexts:
  * **Plaintext context** - templates allow you to freely input content either using HTML tags or native syntax. Try `${7*7}` instead of checking for XSS payloads.
  * **Code context** - user input being placed within a template expression.

### Identify the Template Engine

* Error messages from fuzzing the input parameters will reveal the engine.
* Otherwise, manually try engine-specific payloads available online.

## Exploit SSTI Vulnerabilities

### Read

* Read its documentation after identifying the template engine.
* **Lab** - Read the docs for the ERB template, execute/craft the payloads obtained from PayloadsAllTheThings.
* **Lab** - Read the docs for the Tornado template, import the `os` library and execute commands.

### Read About the Security Implications

* Outline all the potentially dangerous things that people should avoid doing with the template.
* **Lab** - Fuzz the parameter without default payloads to obtain an error message and identify the template engine. Craft a payload following the template syntax based on the security concern mentioned in the documentation.

### Look for Known Exploits

* **Lab** - Fuzz the parameter to identify the template engine. Look for any active exploits available.

## Explore

* Intruder provides a built-in wordlist for brute-forcing variable names.
* Template engines expose a "self" or "environment" object of some kind, which acts like a namespace containing all supported objects, methods & attributes.
* Websites will contain both built-in objects provided by the template and custom, site-specific objects supplied by the web developer.
* **Lab** - Fuzz the parameter to identify the template engine. Use the `debug` payload to enumerate the objects and exploit further using the template documentation.

## Create a Custom Attack

* Template engines execute templates inside a sandbox, which can make exploitation difficult, or even impossible.
* Proceed with traditional auditing techniques by reviewing each function for exploitable behavior.

### Construct a Custom Exploit Using an Object Chain

* First step is to identify the objects and methods to which you have access.
* Refer to the documentation to understand which objects to target.
* **Lab** - Fuzz the parameter. Refer to the documentation to bypass the sandboxed environment and construct a payload to read a file.

### Construct a Custom Exploit Using Developer-Supplied Objects

* Template engines run in a secure, locked-down environment by default.
* Developer-created objects that are exposed to the template can offer a further, less battle-hardened attack surface.
* **Lab** - Fuzz -> Identify the template engine -> Deduce info from error messages and craft a payload. Refer to the solution.

## References

* [cobalt/a-pentesters-guide-to-server-side-template-injection-ssti](https://www.cobalt.io/blog/a-pentesters-guide-to-server-side-template-injection-ssti)
