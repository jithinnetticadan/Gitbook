# GitLab

{% hint style="info" %}
Web-based Git-repository hosting tool that provides wiki capabilities, issue tracking, and continuous integration and deployment pipeline functionality. It is open-source and originally written in Ruby, but the current technology stack includes Go, Ruby on Rails, and Vue.js.
{% endhint %}

## Discovery <a href="#footprinting-discovery" id="footprinting-discovery"></a>

* We can quickly determine that GitLab is in use in an environment by just browsing to the GitLab URL.
* To footprint the GitLab version number in use is by browsing to the `/help` page when logged in.
* If the GitLab instance allows us to register an account, we can log in and browse to this page to confirm the version. If we cannot register an account, we may have to try a low-risk exploit such as [this](https://www.exploit-db.com/exploits/49821).

## Enumeration <a href="#enumeration" id="enumeration"></a>

* Try browsing to `/explore` and see if there are any public projects that may contain something interesting.
* Public projects can be interesting because we may be able to use them to find out more about the company's infrastructure, find production code that we can find a bug in after a code review, hard-coded credentials, a script or configuration file containing credentials, or other secrets such as an SSH private key or API key.
* We can also use the registration form to enumerate valid users, browse to the `/users/sign_up` page.

## Exploitation

### Username Enumeration <a href="#username-enumeration" id="username-enumeration"></a>

* [Bash-Script](https://www.exploit-db.com/exploits/49821) or [GitLabUserEnum](https://github.com/dpgg101/GitLabUserEnum)
  * `./gitlab_userenum.sh --url http://<URL>:8081/ --userlist users.txt`

### Authenticated Remote Code Execution <a href="#authenticated-remote-code-execution" id="authenticated-remote-code-execution"></a>

* GitLab Community Edition version 13.10.2 and lower suffered from an authenticated remote code execution [vulnerability](https://hackerone.com/reports/1154542) due to an issue with ExifTool handling metadata in uploaded image files.
* Isue was fixed by GitLab rather quickly, but some companies are still likely using a vulnerable version. We can use this [exploit](https://www.exploit-db.com/exploits/49951) to achieve RCE.
