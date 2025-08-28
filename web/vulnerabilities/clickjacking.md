# Clickjacking

Interface-based attack in which a user is tricked into clicking on actionable content on a hidden website by clicking on some other content in a decoy website.

### Construct a Basic Clickjacking Attack

<details>

<summary>Clickjacking PoC</summary>

{% code lineNumbers="true" %}
```html
<!DOCTYPE html>
<html><head>
<title> Clickjacking </title></head>
<body><h1>Vulnerable to Clickjacking</h1>
<style>iframe {position:relative;width:750px;height: 550px;opacity: 0.0001;z-index: 2;}
div {position:absolute;top:500px;left:60px;z-index: 1;}
</style>
<div>Click me</div>
<iframe src="https://URL"></iframe>
</body></html><head>
```
{% endcode %}

</details>

* z-index determines the stacking order of the `iframe` and website layers.
* Lab - Adjust the clickbait button accordingly to lure the user to perform unintended action.

### Burp Clickbandit

* Lets you use your browser to perform the desired actions on the frameable page, then creates an HTML file containing a suitable clickjacking overlay.

### Clickjacking with Prefilled Form Input

* Websites that require form completion and submission permit prepopulation of form inputs using GET parameters prior to submission
* GET values form part of the URL then the target URL can be modified to incorporate values of the attacker's choosing and transparent "submit" button is overlaid
* Lab - Check whether form values can be prefilled using any GET request along with the parameters. Use this URL in the `iframe` tag.&#x20;

### Frame Busting Scripts

* Techniques are often browser and platform specific and because of the flexibility of HTML
* Effective attacker workaround against frame busters is use HTML5 `iframe` sandbox attribute set with the 'allow-forms' or 'allow-scripts' values & 'allow-top-navigation' value is omitted then the frame buster script can be neutralized as the `iframe` cannot check whether or not it is the top window.&#x20;
* eg: `<iframe id="victim_website" src="https://victim-website.com" sandbox="allow-forms"></iframe>`
* Lab - Use the sandbox attributes in `iframe` tag to bypass the frame busting protections.

### Combining Clickjacking with a DOM XSS Attack&#x20;

* Attacker first identifies the XSS exploit. It's combined with `iframe` target URL so that the user clicks on the button or link & executes the DOM XSS attack.
* Lab - Identify the module vulnerable to XSS. Use any GET method that can be used to auto-fill the parameters and use the malicious link in an `iframe` tag.

### Multistep Clickjacking

* Multiple actions can be implemented by the attacker using multiple divisions or `iframes`.
* Lab - Declare two classes for the text and follow the same procedure as above.
