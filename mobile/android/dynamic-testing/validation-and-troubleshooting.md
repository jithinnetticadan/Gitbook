# Troubleshooting and Test Cleanup

## Connect Static Leads to Runtime Tests

| Static Lead                                | Focused Dynamic Check                                                                                    | Verify                                                     |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Exported component / URI parser            | [IPC and link](component-testing.md) test with an appropriate caller/account                             | Caller identity, accepted input, protected result.         |
| WebView bridge / permissive navigation     | Controlled content reaches the actual bridge                                                             | Source URL/origin, reachable method, native effect.        |
| Pinning / custom trust logic               | [Network diagnosis](network-traffic-and-tls.md) for the executing stack/domain                           | Before/after TLS behavior and matching HTTP exchange.      |
| Stored token / local role flag             | [Lifecycle](local-data-logs-and-privacy.md) and [authorization](authentication-and-cryptography.md) test | Access prerequisite, retained data, actual authority.      |
| Crypto constant / RNG / biometric callback | Trace key provenance, real use, and protected operation                                                  | Algorithm/policy, flow, realistic access, impact.          |
| Backup flag / rules                        | Supported backup plus restore with a known marker                                                        | Included data, required consent/access, restored behavior. |

## Troubleshooting Matrix

| Symptom                        | Cheapest Discriminating Checks                                                                                | Next Action                                                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| No Burp traffic                | Trigger a known network action; browser/proxy test; check destination/protocol.                               | Follow [routing, trust, and pinning diagnosis](network-traffic-and-tls.md#diagnose-before-bypassing).                |
| Pinning script has no effect   | Confirm CA trust, actual stack, domain, class, overload, and a hook hit.                                      | Observe the concrete verifier before changing it; avoid stacking generic scripts.                                    |
| Frida cannot attach            | ADB authorization, process alive, exact versions, ABI, server privilege/listener, Gadget configuration.       | Re-run [preflight](preflight-and-frida-setup.md); try process listing before hooks.                                  |
| Root detection blocks work     | Identify file/package/property/command/native probe and caller.                                               | Use [targeted diagnosis](runtime-defenses-and-integrity.md), an approved test build, or document blocked coverage.   |
| Emulator detection blocks work | Compare actual build/hardware signals and integrity results.                                                  | Use a compatible physical lab device when appropriate; it may still fail attestation.                                |
| App exits with Frida           | Compare server-only, attach-without-hooks, and one observational hook.                                        | Capture the exit reason; distinguish detection from Frida/runtime incompatibility.                                   |
| Hook never fires               | Confirm action, process, runtime name, overload, classloader, load timing, implementation/override.           | Follow [Java/native instrumentation](java-and-native-instrumentation.md); map the caller rather than guessing names. |
| Crash after instrumentation    | Remove the last hook; check recursive calls, return types, null pointers, JNI ABI, offsets, logging overhead. | Restore pass-through behavior and retest; do not classify every crash as anti-hooking.                               |
| Only part of traffic appears   | Compare domains, SDK clients, WebViews, native sockets, and QUIC.                                             | Track coverage per stack/domain; record unobserved paths.                                                            |
| Static function not observed   | Confirm installed version/splits, conditions, account/feature flags, native/reflection paths, caches.         | Mark untested or establish an alternate path; lack of a hit does not prove unreachable code.                         |

* Stop repeated bypass attempts when the next step exceeds scope, risks availability, or prevents higher-value tests.
* Follow the [runtime-defense stop criteria](runtime-defenses-and-integrity.md#stop-criteria).

## Test Completion and Cleanup

* [ ] Critical login/logout/reset/refresh, authorization, IPC/links/WebView, network, storage/privacy, backup, and crypto flows tested or marked untested.
* [ ] Each control tested individually with a normal control case.
* [ ] Proxy/Wi-Fi/VPN settings and trust changes restored; temporary CAs removed.
* [ ] Frida/Drozer servers stopped; test forwarding, scripts, staging copies, and companion apps removed.
* [ ] Test sessions revoked and approved records restored/deleted; dumps and captures retained or destroyed according to agreement.

* Do not erase unrelated user data during cleanup.
* Reference: [OWASP MASTG](https://mas.owasp.org/MASTG/).
