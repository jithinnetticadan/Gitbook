# JWT Attacks

{% hint style="info" %}
JWTs are most commonly used in authentication, session management, and access control mechanisms - these vulnerabilities can potentially compromise the entire website and its users.
{% endhint %}

## Overview

* Unlike with classic session tokens, all of the data that a server needs is stored client-side within the JWT itself. This makes JWTs a popular choice for highly distributed websites where users need to interact seamlessly with multiple back-end servers.
* A JWT consists of 3 parts: a header, a payload, and a signature.
* The header and payload parts of a JWT are just base64url-encoded JSON objects. The header contains metadata about the token itself, while the payload contains the actual "claims" about the user.
* The security of any JWT-based mechanism is heavily reliant on the cryptographic signature.

### JWT vs JWS vs JWE

* JSON Web Signature (JWS) (default) and JSON Web Encryption (JWE).
* JWE encrypts the contents.

* JWT attacks are used to impersonate another user, or escalate privileges of a user who has already been authenticated.

### How Do Vulnerabilities to JWT Attacks Arise?

* The signature of the JWT is not verified properly.

### Working with JWTs in Burp Suite

* Use the JWT Editor extension, available in the BApp Store.

## Accepting Arbitrary Signatures

* The Node.js library `jsonwebtoken` has `verify()` and `decode()` methods.
* Developers confuse these two methods and only pass incoming tokens to the `decode()` method.

## Accepting Tokens with No Signature

* The `alg` parameter mentions the algorithm that was used to sign the token.
* If we change it to any other algorithm and sign it, the server may consider it legitimate and it can successfully be bypassed.
* We can also set the value for the `alg` parameter as `none`, `None`, `nOne`, `noNe`, etc.
* Make sure that when `alg` is set to `none` or a similar string, remove the 3rd part (i.e. the signature) from the JWT and end with a "dot" (`.`).

## Brute-Forcing Secret Keys

* Signing algorithms such as HS256 (HMAC + SHA-256) use an arbitrary, standalone string as the secret key.
* Developers sometimes make mistakes like forgetting to change default or placeholder secrets.
* Wordlist: [jwt.secrets.list](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list)

### Brute-Forcing Secret Keys Using Hashcat

* You just need a valid, signed JWT from the target server and a wordlist of well-known secrets.
* **Command:**

```
hashcat -a 0 -m 16500 <jwt> <wordlist>
```

* Hashcat signs the header and payload from the JWT using each secret in the wordlist, then compares the resulting signature with the original one from the server.
* Alternate tool - `jwt_tool`.
* Once the secret is obtained: go to JWT Editor Keys -> select the key to generate -> no need to mention the key size (auto-adjusted) -> Generate -> modify the `k` value with the Base64-encoded secret obtained using Hashcat -> Apply.
* Sign the token in the Repeater tab after modifying the payload - when signing, maintain "Don't modify header" depending on the scenario.

## JWT Header Parameter Injections

* According to the JWS specification, only the `alg` header parameter is mandatory.
* **Other parameters:**
  * `jwk` (JSON Web Key) - Provides an embedded JSON object representing the key.
  * `jku` (JSON Web Key Set URL) - Provides a URL from which servers can fetch a set of keys containing the correct key.
  * `kid` (Key ID) - Provides an ID that servers can use to identify the correct key in cases where there are multiple keys to choose from. Depending on the format of the key, this may have a matching `kid` parameter.
* These user-controllable parameters each tell the recipient server which key to use when verifying the signature.

### Injecting Self-Signed JWTs via the `jwk` Parameter

* The JWS specification describes an optional `jwk` header parameter, which servers can use to embed their public key directly within the token itself in JWK format.
* **Example:**

```json
{
    "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
    "typ": "JWT",
    "alg": "RS256",
    "jwk": {
        "kty": "RSA",
        "e": "AQAB",
        "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
        "n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9m"
    }
}
```

* Servers should only use a limited whitelist of public keys to verify JWT signatures. However, misconfigured servers sometimes use any key that's embedded in the `jwk` parameter.
* Exploit this behavior by signing a modified JWT using your own RSA private key, then embedding the matching public key in the `jwk` header.
* Click **Attack**, then select **Embedded JWK**. When prompted, select your newly generated RSA key.

### Injecting Self-Signed JWTs via the `jku` Parameter

* Servers let you use the `jku` (JWK Set URL) header parameter to reference a JWK Set containing the key. When verifying the signature, the server fetches the relevant key from this URL.
* **Example:**

```json
{
    "keys": [
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "75d0ef47-af89-47a9-9061-7c02a610d5ab",
            "n": "o-yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9mk6GPM9gNN4Y_qTVX67WhsN3JvaFYw-fhvsWQ"
        },
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "d8fDFo-fS9-faS14a9-ASf99sa-7c1Ad5abA",
            "n": "fc3f-yy1wpYmffgXBxhAUJzHql79gNNQ_cb33HocCuJolwDqmk6GPM4Y_qTVX67WhsN3JvaFYw-dfg6DH-asAScw"
        }
    ]
}
```

* JWK Sets like this are sometimes exposed publicly via a standard endpoint, such as `/.well-known/jwks.json`.
* Generate a new key -> copy the public key as JWK and serve it remotely by hosting a server -> in the JWT, modify the `kid` parameter to match the newly generated key and inject the `jku` parameter to fetch the remotely stored public key using the URL.

### Injecting Self-Signed JWTs via the `kid` Parameter

* Might use the `kid` parameter to point to a particular entry in a database, or even the name of a file.
* If this parameter is also vulnerable to directory traversal, an attacker could potentially force the server to use an arbitrary file from its filesystem as the verification key.
* **Example:**

```json
{
    "kid": "../../path/to/file",
    "typ": "JWT",
    "alg": "HS256",
    "k": "asGsADas3421-dfh9DGN-AFDFDbasfd8-anfjkvc"
}
```

* You could theoretically do this with any file, but one of the simplest methods is to use `/dev/null`, which is present on most Linux systems. As this is an empty file, fetching it returns null. Therefore, signing the token with a Base64-encoded null byte will result in a valid signature.
* If the server stores its verification keys in a database, the `kid` header parameter is also a potential vector for SQL injection attacks.
* Generate a symmetric key -> change the value of `k` to a Base64-encoded null byte (`AA==`) -> modify the `kid` param to contain the path (`/dev/null`) -> change payload params -> sign using the generated symmetric key.

## Algorithm Confusion Attacks

* Occurs when an attacker forces the server to verify the signature of a JWT using a different algorithm than intended by the website's developers.

### Symmetric vs. Asymmetric Algorithms

* JWTs can be signed using 2 kinds of algorithms:
  * **HS256** (HMAC + SHA-256) - a "symmetric" key. The server uses a single key to both sign and verify the token.
  * **RS256** (RSA + SHA-256) - uses an "asymmetric" key pair. The server uses a private key to sign the token, and a public key to verify the signature.

### How Do Algorithm Confusion Vulnerabilities Arise?

* Confusion occurs when the JWT is signed using a symmetric key, but the server supports both asymmetric & symmetric algorithms for verification. An attacker can use the public key obtained from the standard endpoint and sign the modified token after changing the algorithm to HS256, so the server uses the hardcoded public key as the HMAC secret key.
* Can also try the vice-versa option.
* The public key you use to sign the token must be identical to the public key stored on the server. This includes using the same format (such as X.509 PEM) and preserving any non-printing characters like newlines.

### Performing an Algorithm Confusion Attack

**Step 1 - Obtain the server's public key**

* Servers expose public keys as JSON Web Key (JWK) objects via `/jwks.json` or `/.well-known/jwks.json`.
* If the key isn't exposed publicly, you may be able to extract it from a pair of existing JWTs (discussed below in "Deriving Public Keys from Existing Tokens").

**Step 2 - Convert the public key to a suitable format**

* When verifying the signature of a token, the server uses its own copy of the key from the local filesystem or DB, which may be stored in a different format.
* For the attack to work, the version of the key that you use to sign the JWT must be identical to the server's local copy - every single byte must match.
* Assuming the format is X.509 PEM:
  1. With the JWT Editor extension loaded, in Burp's main tab bar, go to the JWT Editor Keys tab.
  2. Click **New RSA Key**. In the dialog, paste the JWK that you obtained earlier.
  3. Select the PEM radio button and copy the resulting PEM key.
  4. Go to the Decoder tab and Base64-encode the PEM.
  5. Go back to the JWT Editor Keys tab and click **New Symmetric Key**.
  6. In the dialog, click **Generate** to generate a new key in JWK format.
  7. Replace the generated value for the `k` parameter with the Base64-encoded PEM key that you just copied (do not remove the newline).
  8. Save the key.

**Step 3 - Modify your JWT**

* Once you have the public key in a suitable format, modify the JWT however you like. Make sure the `alg` header is set to `HS256` (or modify depending on the scenario).

**Step 4 - Sign the JWT using the public key**

* Sign the token using the HS256 algorithm with the RSA public key as the secret.

* **Lab** - Follow the above steps to perform algorithm confusion attacks.

## Deriving Public Keys from Existing Tokens

* Tools such as `jwt_forgery.py` or [rsa_sign2n](https://github.com/silentsignal/rsa_sign2n).
* **Simplified version:**

```
docker run --rm -it portswigger/sig2n <token1> <token2>
```

* Uses the JWTs that you provide to calculate one or more potential values of `n`.
* For each potential value, the script outputs:
  * A Base64-encoded PEM key in both X.509 and PKCS1 format.
  * A forged JWT signed using each of these keys.
* To identify the correct key, use Repeater to send a request containing each of the forged JWTs. Only one of these will be accepted by the server. Use the matching key to construct an algorithm confusion attack.

## Tools

* [JWTLens](https://jwtlens.netlify.app/)
* [JWTAuditor](https://jwtauditor.com/)