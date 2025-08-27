# JWT Attacks

JWTs are most commonly used in authentication, session management, and access control mechanisms, these vulnerabilities can potentially compromise the entire website and its users. - Unlike with classic session tokens, all of the data that a server needs is stored client-side within the JWT itself. This makes JWTs a popular choice for highly distributed websites where users need to interact seamlessly with multiple back-end servers. - A JWT consists of 3 parts: a header, a payload, and a signature. - The header and payload parts of a JWT are just base64url-encoded JSON objects. The header contains metadata about the token itself, while the payload contains the actual "claims" about the user. - security of any JWT-based mechanism is heavily reliant on the cryptographic signature.

* JWT vs JWS vs JWE
  * JSON Web Signature (JWS)(By default) and JSON Web Encryption (JWE)
  * JWE encrypts the contents
* JWT attacks are used to impersonate as another user or escalate privileges who has already been authenticated.
* How do vulnerabilities to JWT attacks arise?
  * signature of the JWT is not verified properly.
* Working with JWTs in Burp Suite
  * use JWT editor extender available in Bapp store
* Accepting arbitrary signatures
  * Node.js library jsonwebtoken has verify() and decode()
  * developers confuse these two methods and only pass incoming tokens to the decode() method.
* Accepting tokens with no signature
  * the 'alg' parameter mentions the algorithm that was used to sign the token
  * if we change it to any other algorithm and sign it the server consider it legitimate and successfully can be bypassed.
  * we can also mention value for 'alg' parameter as none,None,nOne,noNe, etc.
  * make sure when alg is set to none or similar strings, remove the 3rd part ie signature from jwt and end with a "dot"
* Brute-forcing secret keys
  * signing algorithms, such as HS256 (HMAC + SHA-256), use an arbitrary, standalone string as the secret key.
  * developers sometimes make mistakes like forgetting to change default or placeholder secrets.
  * https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list
  * Brute-forcing secret keys using hashcat
  * You just need a valid, signed JWT from the target server and a wordlist of well-known secrets.
  * Command = hashcat -a 0 -m 16500
  * Hashcat signs the header and payload from the JWT using each secret in the wordlist, then compares the resulting signature with the original one from the server.
  * Alternate tool - jwt\_tool
  * once the secret is obtained go to jwt editor keys -> select the key to generate -> no need to mention the key size auto adjusted -> generate -> modify 'k' value with base64 encoded secret obtained using hashcat -> apply
  * sign the token in repeater tab after modifying the payload -> when signing maintain 'don't modify header' depending on scenario
* JWT header parameter injections
  * According to the JWS specification, only the alg header parameter is mandatory
  * Other parameters
  * jwk (JSON Web Key) - Provides an embedded JSON object representing the key.
  * jku (JSON Web Key Set URL) - Provides a URL from which servers can fetch a set of keys containing the correct key.
  * kid (Key ID) - Provides an ID that servers can use to identify the correct key in cases where there are multiple keys to choose from. Depending on the format of the key, this may have a matching kid parameter.
  * these user-controllable parameters each tell the recipient server which key to use when verifying the signature.
* Injecting self-signed JWTs via the jwk parameter
  * JSON Web Signature (JWS) specification describes an optional jwk header parameter, which servers can use to embed their public key directly within the token itself in JWK format.
  * example { "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG", "typ": "JWT", "alg": "RS256", "jwk": { "kty": "RSA", "e": "AQAB", "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG", "n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ\_cb33K2vh9m" } }
  * servers should only use a limited whitelist of public keys to verify JWT signatures. However, misconfigured servers sometimes use any key that's embedded in the jwk parameter.
  * exploit this behavior by signing a modified JWT using your own RSA private key, then embedding the matching public key in the jwk header.
  * Click Attack, then select Embedded JWK. When prompted, select your newly generated RSA key.
* Injecting self-signed JWTs via the jku parameter
  * servers let you use the jku (JWK Set URL) header parameter to reference a JWK Set containing the key. When verifying the signature, the server fetches the relevant key from this URL.
  * example { "keys": \[ { "kty": "RSA", "e": "AQAB", "kid": "75d0ef47-af89-47a9-9061-7c02a610d5ab", "n": "o-yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ\_cb33K2vh9mk6GPM9gNN4Y\_qTVX67WhsN3JvaFYw-fhvsWQ" }, { "kty": "RSA", "e": "AQAB", "kid": "d8fDFo-fS9-faS14a9-ASf99sa-7c1Ad5abA", "n": "fc3f-yy1wpYmffgXBxhAUJzHql79gNNQ\_cb33HocCuJolwDqmk6GPM4Y\_qTVX67WhsN3JvaFYw-dfg6DH-asAScw" } ] }
  * JWK Sets like this are sometimes exposed publicly via a standard endpoint, such as /.well-known/jwks.json.
  * generate a new key -> copy public key as jwk and serve remotely by hosting a server > in jwt modify the kid parameter to match the new key generated and inject jku parameter to fetch the remotely stored public key using URL
* Injecting self-signed JWTs via the kid parameter
  * might use the kid parameter to point to a particular entry in a database, or even the name of a file.
  * If this parameter is also vulnerable to directory traversal, an attacker could potentially force the server to use an arbitrary file from its filesystem as the verification key.
  * example { "kid": "../../path/to/file", "typ": "JWT", "alg": "HS256", "k": "asGsADas3421-dfh9DGN-AFDFDbasfd8-anfjkvc" }
  * You could theoretically do this with any file, but one of the simplest methods is to use /dev/null, which is present on most Linux systems. As this is an empty file, fetching it returns null. Therefore, signing the token with a Base64-encoded null byte will result in a valid signature.
  * If the server stores its verification keys in a database, the kid header parameter is also a potential vector for SQL injection attacks.
  * generate a symmetric key -> change the value of 'k' to base64 encoded null byte (AA==) -> modify the kid param to contain the path (/dev/null) -> change payload params -> sign using generated symmetric key
* Algorithm confusion attacks
  * Occur when attacker forces server to verify the signature of a JSON web token (JWT) using different algorithm than is intended by the website's developers.
  * Symmetric vs asymmetric algorithms
    * JWTs can be signed using 2 algorithms % HS256 (HMAC + SHA-256) ie "symmetric" key. Server uses single key to both sign and verify the token. % RS256 (RSA + SHA-256) use an "asymmetric" key pair. Server uses private key to sign the token, and public key to verify the signature.
  * How do algorithm confusion vulnerabilities arise?
    * Confusion occurs when the JWT is signed using symmetric key but server supports both asymmetric & symmetric for verification. Attacker can use the public key obtained using the standard endpoint and sign the modified token after modifying the algorithm to HS256 so the server will use teh hardcoded public key as the HMAC secret key.
    * Can try vice-versa option
    * Public key you use to sign the token must be identical to the public key stored on server. This includes using same format (such as X.509 PEM) and preserving any non-printing characters like newlines.
  * Performing an algorithm confusion attack
    * Step 1 - Obtain the server's public key % Servers expose public keys as JSON Web Key (JWK) objects via /jwks.json or /.well-known/jwks.json % If the key isn't exposed publicly, you may be able to extract it from a pair of existing JWTs. (discussed in detail below)
    * Step 2 - Convert the public key to a suitable format % When verifying the signature of token, it will use its own copy of the key from local filesystem or DB that may be stored in a different format. % In order for the attack to work, the version of the key that you use to sign the JWT must be identical to the server's local copy as well as every single byte must match. % Assume format is in X.509 PEM format $ With the JWT Editor extension loaded, in Burp's main tab bar, go to the JWT Editor Keys tab. $ Click New RSA Key. In the dialog, paste the JWK that you obtained earlier. $ Select the PEM radio button and copy the resulting PEM key. $ Go to the Decoder tab and Base64-encode the PEM. $ Go back to the JWT Editor Keys tab and click New Symmetric Key. $ In the dialog, click Generate to generate a new key in JWK format. $ Replace the generated value for the k parameter with a Base64-encoded PEM key that you just copied. (Do not remove the newline) $ Save the key.
    * Step 3 - Modify your JWT % Once you have the public key in suitable format, modify the JWT however you like. Make sure alg header is set to HS256 or modify depending on scenario.
    * Step 4 - Sign the JWT using the public key % Sign the token using the HS256 algorithm with the RSA public key as the secret.
    * Lab - Follow the above steps to perform algorithm confusion attacks
* Deriving public keys from existing tokens
  * Tools such as jwt\_forgery.py or https://github.com/silentsignal/rsa\_sign2n
  * Simplified version - "docker run --rm -it portswigger/sig2n "
  * Uses the JWTs that you provide to calculate one or more potential values of 'n'
  * For each potential value, our script outputs: % A Base64-encoded PEM key in both X.509 and PKCS1 format. % A forged JWT signed using each of these keys.
  * To identify correct key, use Repeater to send request containing each of the forged JWTs. Only one of these will be accepted by the server. Use the matching key to construct an alg confusion attack.
