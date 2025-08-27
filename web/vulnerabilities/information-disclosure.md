# Information Disclosure

### Some basic examples of information disclosure are as follows:

* Revealing the names of hidden directories, their structure, and their contents via a robots.txt file or directory listing
* Providing access to source code files via temporary backups
* Explicitly mentioning database table or column names in error messages
* Unnecessarily exposing highly sensitive information, such as credit card details
* Hard-coding API keys, IP addresses, database credentials, and so on in the source code
* Hinting at the existence or absence of resources, usernames, and so on via subtle differences in application behavior

{% code lineNumbers="true" %}
```
Robots.txt - reveal hidden directories
Information about frameworks or sensitive data
Enabling debugging features -/cgi-bin/phpinfo.php
```
{% endcode %}

### How to test for information disclosure vulnerabilities

* **Fuzzing**
  * Try submitting different data types or fuzz crafted strings and observe the response from the server
    * Use `Burp Intruder` to add payloads and fuzz the parameters using pre-built wordlists&#x20;
    * Status codes, length, response time, grep matching rules - keywords (error, invalid, SELECT, SQL etc), grep extraction rules&#x20;
    * Use `Logger++` extension to define advanced filters
  * Using `Burp Scanner` - Schedule automated scans to crawl and audit the target site
  * Using `Burp's engagement tools - Search, Find Comments, Discover Content`
  * Engineering informative responses - Observe error messages - Stack Trace

### Files for Web Crawlers

* Search for robots.txt or sitemap.xml

### Directory Listings

* Accessing temporary files and crash dumps

### Developer Comments

* View page source, browser developer tools

### Hardcoded password in backup files/source code

### Trace Enabled

* Discloses internal authentication headers

### Version control history info in /.git file&#x20;

* Get access to the entire source code
* `git cat-file -p "--value--"`
* `git log`
* `git diff "--value1--" "--value2--"`
