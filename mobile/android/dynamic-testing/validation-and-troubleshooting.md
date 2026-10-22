# Validation, Reporting, and Troubleshooting

## Turn Observations Into Findings

State the attacker capability, reachable input/action, intended control, crossed security boundary, and impact. Keep tool output separate from the conclusion it supports.

1. Record a normal control case and the exact app/build/device/account state.
2. Reproduce with one controlled difference, preserving the relevant request/response, local artifact, or protected action.
3. Identify what the test changed. Did instrumentation expose an existing weakness, or manufacture the entire defect by replacing a secure implementation?
4. Repeat under the claimed attacker capability. Root, hooks, physical access, or a malicious local app may be valid threat models; disclose them rather than requiring every test to work without Frida.
5. Verify API behavior for claimed server impact. For local findings, verify the local data/action boundary; server involvement is not mandatory.

Static evidence can establish findings too. A complete exposed secret or demonstrably unsafe configuration does not become harmless because a particular runtime test was blocked. State what is established, what remains a hypothesis, and which flows were not covered.

## Connect Static Leads to Runtime Tests

| Static Lead | Focused Dynamic Check | Useful Evidence |
| --- | --- | --- |
| Exported component / URI parser | [IPC and link](component-testing.md) test with an appropriate caller/account | Caller identity, accepted input, protected result. |
| WebView bridge / permissive navigation | Controlled content reaches the actual bridge | Source URL/origin, reachable method, native effect. |
| Pinning / custom trust logic | [Network diagnosis](network-traffic-and-tls.md) for the executing stack/domain | Before/after TLS behavior and matching HTTP exchange. |
| Stored token / local role flag | [Lifecycle](local-data-logs-and-privacy.md) and [authorization](authentication-and-cryptography.md) test | Access prerequisite, retained data, actual authority. |
| Crypto constant / RNG / biometric callback | Trace key provenance, real use, and protected operation | Algorithm/policy, flow, realistic access, impact. |
| Backup flag / rules | Supported backup plus restore with a known marker | Included data, required consent/access, restored behavior. |

## Frequent False Positives

| Observation | Missing Evidence |
| --- | --- |
| Sensitive activity opens | Unauthorized data or operation, not just navigation. |
| Root can read a private file | Relevant attacker capability and protection requirement. |
| Hook prints "success" / changes a UI flag | Actual protected key/data/action or API outcome. |
| Burp sees no traffic | Routing, cache, TLS, protocol, or stack diagnosis; absence is not a vulnerability. |
| Logout replay returns `200` | Protected content/action and the applicable token policy. |
| APK contains weak crypto / suspicious code | Security-sensitive purpose, reachable use or other sufficient static evidence, and impact. |
| A hooked function never fires | Correct build/process/loader/signature/timing and flow coverage. |
| Client defense can be patched | A violated requirement or meaningful attack consequence, not just tester control of a client. |

## Troubleshooting Matrix

| Symptom | Cheapest Discriminating Checks | Next Action |
| --- | --- | --- |
| No Burp traffic | Trigger a known network action; browser/proxy test; check destination/protocol. | Follow [routing, trust, and pinning diagnosis](network-traffic-and-tls.md#diagnose-before-bypassing). |
| Pinning script has no effect | Confirm CA trust, actual stack, domain, class, overload, and a hook hit. | Observe the concrete verifier before changing it; avoid stacking generic scripts. |
| Frida cannot attach | ADB authorization, process alive, exact versions, ABI, server privilege/listener, Gadget configuration. | Re-run [preflight](preflight-and-frida-setup.md); try process listing before hooks. |
| Root detection blocks work | Identify file/package/property/command/native probe and caller. | Use [targeted diagnosis](runtime-defenses-and-integrity.md), an approved test build, or document blocked coverage. |
| Emulator detection blocks work | Compare actual build/hardware signals and integrity results. | Use a compatible physical lab device when appropriate; it may still fail attestation. |
| App exits with Frida | Compare server-only, attach-without-hooks, and one observational hook. | Collect exit evidence; distinguish detection from Frida/runtime incompatibility. |
| Hook never fires | Confirm action, process, runtime name, overload, classloader, load timing, implementation/override. | Follow [Java/native instrumentation](java-and-native-instrumentation.md); map the caller rather than guessing names. |
| Crash after instrumentation | Remove the last hook; check recursive calls, return types, null pointers, JNI ABI, offsets, logging overhead. | Restore pass-through behavior and retest; do not classify every crash as anti-hooking. |
| Only part of traffic appears | Compare domains, SDK clients, WebViews, native sockets, and QUIC. | Track coverage per stack/domain; record unobserved paths. |
| Static function not observed | Confirm installed version/splits, conditions, account/feature flags, native/reflection paths, caches. | Mark untested or establish an alternate path; lack of a hit does not prove unreachable code. |

Stop repeated bypass attempts when the next step exceeds scope, risks availability, or prevents higher-value tests. Preserve evidence of the constraint and use the [runtime-defense stop criteria](runtime-defenses-and-integrity.md#stop-criteria).

## Finding Template

```text
Title and affected component/build:
Requirement / expected security boundary:
Attacker capability and prerequisites:
Test accounts/roles and owned objects:
Baseline and reproduction steps:
Inputs / requests / hooks / artifact hashes:
Observed result versus expected result:
Impact and demonstrated access:
Local versus server enforcement:
Evidence references (redacted) and timestamps:
Limitations / untested variants:
Severity rationale and applicable MASVS/MASTG references:
Remediation and retest criteria:
```

Store raw tokens, private data, and memory dumps in the approved evidence location, not the GitBook. Redact shared excerpts while retaining enough detail to reproduce with synthetic data.

## Completion and Cleanup

* [ ] Package/build/splits, device state, tool versions, and original/patched configuration recorded.
* [ ] Critical login/logout/reset/refresh, authorization, IPC/links/WebView, network, storage/privacy, backup, and crypto flows tested or explicitly marked untested.
* [ ] Controls tested individually; negative/control cases and actual impacts captured.
* [ ] Findings distinguish observations, hypotheses, bypass prerequisites, and confirmed boundary failures.
* [ ] Proxy/Wi-Fi/VPN settings and trust changes restored; temporary CAs removed.
* [ ] Frida/Drozer servers stopped; test forwarding, scripts, staging copies, and companion apps removed.
* [ ] Test sessions revoked and approved records restored/deleted; dumps and captures retained or destroyed according to agreement.

Do not erase evidence or user data indiscriminately during cleanup. References: [OWASP MASTG](https://mas.owasp.org/MASTG/), [OWASP MASVS](https://mas.owasp.org/MASVS/).

**Related:** [Methodology and Baseline](methodology-and-baseline.md) | [Dynamic Testing](README.md)

**Previous:** [Business Logic and Backend Trust](business-logic-and-backend.md)