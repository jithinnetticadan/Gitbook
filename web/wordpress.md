# WordPress

{% hint style="info" %}
* An open-source Content Management System (CMS) that can be used for multiple purposes. It’s often used to host blogs and forums.
* WordPress is highly customizable as well as SEO friendly, which makes it popular among companies.
* However, its customizability and extensible nature make it prone to vulnerabilities through third-party themes and plugins.
* WordPress is written in PHP and usually runs on Apache with MySQL as the backend.
{% endhint %}

## Discovery/Footprinting <a href="#discoveryfootprinting" id="discoveryfootprinting"></a>

* Identify a WordPress site is by browsing to the `/robots.txt` file. The presence of the `/wp-admin` and `/wp-content` directories can be observed.
* WordPress stores its plugins in the `wp-content/plugins` directory. This folder is helpful to enumerate vulnerable plugins.
* Themes are stored in the `wp-content/themes` directory. These files should be carefully enumerated as they may lead to RCE.
* There are five types of users on a standard WordPress installation.
  1. Administrator: This user has access to administrative features within the website. This includes adding and deleting users and posts, as well as editing source code.
  2. Editor: An editor can publish and manage posts, including the posts of other users.
  3. Author: They can publish and manage their own posts.
  4. Contributor: These users can write and manage their own posts but cannot publish them.
  5. Subscriber: These are standard users who can browse posts and edit their profiles.

## Enumeration <a href="#wordpress-discovery-enumeration" id="wordpress-discovery-enumeration"></a>

* Viewing the page source with `cURL` and grepping for `WordPress` can help us confirm that WordPress is in use and footprint the version number.
  * `curl -s http://<URL> | grep WordPress`&#x20;
* Browsing the site and perusing the page source will give us hints to the theme in use, plugins installed, and even usernames if author names are published with posts.
* Navigate through the page source for each page, grepping for the `wp-content` directory, `themes` and `plugin` .
  * `curl -s http://<URL/path> | grep themes` , `curl -s http://<URL/path> | grep plugin`&#x20;
* Browse through the plugins, themes to obtain the version numbers and look for any known CVE's.

### Enumerate Users <a href="#enumerating-users" id="enumerating-users"></a>

* Login page found at `/wp-login.php`  throws error messages that helps to identify whether a user exist or not.&#x20;

## Automated Scan

* [WPScan](https://github.com/wpscanteam/wpscan) is an automated WordPress scanner and enumeration tool. It determines if the various themes and plugins used by a blog are outdated or vulnerable.
* WPScan is also able to pull in vulnerability information from external sources. We can obtain an API token from [WPVulnDB](https://wpvulndb.com/), which is used by WPScan to scan for PoC and reports. Token can then be supplied to wpscan using the `--api-token parameter`&#x20;
* `sudo wpscan --url http://<URL> --enumerate -t 5 --api-token <value>`  <sup><sub>(enumerates vulnerable plugins, themes, users, media, and backups)<sub></sup>
