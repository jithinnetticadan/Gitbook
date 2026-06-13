# LDAP Injection

{% hint style="info" %}
Exploits web applications that use LDAP (Lightweight Directory Access Protocol) for authentication or storing user information. The attacker can `inject malicious code` or `characters` into LDAP queries to alter the application's behaviour, `bypass security measures`, and `access sensitive data` stored in the LDAP directory.
{% endhint %}

## Discovery

* <table><thead><tr><th width="85.2855224609375">Input</th><th>Description</th></tr></thead><tbody><tr><td><code>*</code></td><td>An asterisk <code>*</code> can <code>match any number of characters</code>.</td></tr><tr><td><code>( )</code></td><td>Parentheses <code>( )</code> can <code>group expressions</code>.</td></tr><tr><td><code>|</code></td><td>A vertical bar <code>|</code> can perform <code>logical OR</code>.</td></tr><tr><td><code>&#x26;</code></td><td>An ampersand <code>&#x26;</code> can perform <code>logical AND</code>.</td></tr><tr><td><code>(cn=*)</code></td><td>Input values that try to bypass authentication or authorisation checks by injecting conditions that <code>always evaluate to true</code> can be used. For example, <code>(cn=*)</code> or <code>(objectClass=*)</code> can be used as input values for a username or password fields.</td></tr></tbody></table>

## Enumeration <a href="#enumeration" id="enumeration"></a>

* `nmap -p- -sC -sV --open --min-rate=1000 <IP>`  <sup><sub>(nmap detects a<sub></sup> <sup><sub> </sup><sup><sub>`http`<sub></sup> <sup><sub> </sup><sup><sub>server running on port<sub></sup> <sup><sub> </sup><sup><sub>`80`<sub></sup> <sup><sub> </sup><sup><sub>and an<sub></sup> <sup><sub> </sup><sup><sub>`ldap`<sub></sup> <sup><sub> </sup><sup><sub>server running on port<sub></sup> <sup><sub> </sup><sup><sub>`389)`<sub></sup>
