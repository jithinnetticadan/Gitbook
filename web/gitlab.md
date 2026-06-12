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

* We can do this manually, of course, but scripts make our work much faster. We can write one ourselves in Bash or Python or use [this one](https://www.exploit-db.com/exploits/49821) to enumerate a list of valid users. The Python3 version of this same tool can be found [here](https://github.com/dpgg101/GitLabUserEnum).&#x20;











