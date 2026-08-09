# Report Guide

{% hint style="warning" %}
The report is graded, not just the compromise. A strong technical run with a weak/incomplete report can still fail. Write it as if the reader has never seen the engagement and needs to be able to reproduce every finding from your description alone.
{% endhint %}

## Assessment Types (Context)

* **Vulnerability Assessment** - automated scan only (authenticated or unauthenticated), no exploitation. Report often validates scanner results (confirming real issues vs. false positives) and highlights themes/patterns rather than individual findings.
* **Penetration Testing** - goes beyond scanning into exploitation. Perspectives:
  * **Black box** - no info beyond company name/network connection.
  * **Grey box** - given in-scope IPs/CIDR ranges only.
  * **White box** - given credentials, source code, configs, etc.
  * **Zero evasion** - uncover as many vulnerabilities as possible, no stealth.
  * **Hybrid evasive** - start stealthy, get progressively "noisier" to test detection maturity; once detected, often shifts to non-evasive for the rest of the assessment.
  * **Evasive** - remain undetected as long as possible, simulating an advanced attacker; sometimes a long-term engagement with few client staff aware.
* **Internal vs External** - external = anonymous internet attacker targeting public systems (often OSINT-driven); internal = anonymous or authenticated user behind the firewall, typically aiming for foothold -> privesc -> lateral movement -> AD compromise.
* **Inter-disciplinary assessments** - Purple Team (pentester + incident responder validating detections), Cloud-focused, Comprehensive IoT (network + cloud + application + hardware specialists).
* **Web Application Pentest** - may be app-only (role-based/authenticated) or app + underlying infrastructure (initial compromise via the app, then pivot into the network/AD).
* **Hardware Pentest** - IoT devices, laptops, kiosks, ATMs - establish rules of engagement before the assessment, especially around destructive testing.

## Deliverable Types

* **Draft Report** - issued first so the client can review, comment (management response, wording, ordering), and request a walkthrough call before finalizing.
* **Final Report** - issued after client review/sign-off; some auditors will only accept a Final (not Draft) report for compliance.
* **Post-Remediation Report** - retest of *only* the original findings on *only* the originally affected hosts, within a bounded time limit (not a full re-assessment). Avoid open-ended scope creep - new hosts, new large scans, or long delays between original test and retest all break the "apples to apples" comparison. If the environment has changed too much, consider recommending a fresh assessment or a Breach and Attack Simulation (BAS) tool for periodic checks instead.
* **Attestation Report/Letter** - a short (1-2 page), sanitized document for the client's vendors/customers, with no technical finding details or credentials - just number of findings, approach, and general comments.
* **Slide Deck** - presentation for technical or executive audiences; use relatable anecdotes/current events (not fear-mongering) to hold attention, especially for executive audiences.
* **Spreadsheet of Findings** - tabular version of all finding fields for the client's sorting/ticketing needs; no executive summary/narrative. Pivot tables by severity/category help the client prioritize.

### Vulnerability Notifications (Out-of-Band)

* [ ] Draft one immediately for any finding that is: **directly exploitable** + **internet-exposed** + results in **unauthenticated RCE or sensitive data exposure** (or equivalent via weak/default creds).
* [ ] Set expectations with the client during kickoff for anything beyond this baseline (e.g. all high/critical findings, regardless of internal/external).
* [ ] Keep the notification itself lean - technical details + reproducible tool evidence only, no fluff, so the client's team can act immediately.

## Report Structure

A strong report consists of the following sections, in this order:

1. **Executive Summary**
2. **Summary of Recommendations**
3. **Attack Chain** (if applicable - internal compromise occurred)
4. **Findings**
5. **Appendices**

### 1. Executive Summary

{% hint style="info" %}
Written for someone with **zero technical background** - the person who allocates the budget to fix what you found. If they can't follow it, the rest of the report's value drops sharply.
{% endhint %}

**Do:**

* Be specific with metrics ("25 occurrences of X", not "several" or "multiple").
* Keep it to 1.5-2 pages - if longer, collapse topics into higher-level themes/categories.
* Describe *what* you could access in relatable terms (HR documents, banking systems) rather than technical labels ("Domain Admin").
* Describe what process/procedure broke down, not just "install patches" - e.g. if 500 accounts share `Welcome1!`, the fix isn't just a password reset, it's giving the Help Desk a way to set strong initial passwords.
* If experienced enough, give a rough effort estimate (low/moderate/significant) for remediation so a client doesn't overreact and break something rushing a fix.
* Acknowledge things the client did well (e.g. no missing-patch findings = mature patch management) - this builds trust and encourages continued investment.
* Hedge observational claims - "testing activity seemed to go largely undetected" rather than asserting it as fact (they may simply not have told you).

**Do NOT:**

* Name/recommend specific vendors (suggest technology categories like EDR/log aggregation, not CrowdStrike/Splunk by name).
* Use acronyms for protocols/attack types (SNMP, MitM, etc.) - IP/VPN are borderline-acceptable exceptions.
* Spend more time on low-impact issues than on the significant findings.
* Use jargon/vocabulary the reader would need to look up.
* Reference technical sections of the report - the reader is here specifically because they don't want/need that detail.

**Vocabulary substitutions (examples, not exhaustive):**

| Technical Term | Executive-Friendly Alternative |
| --- | --- |
| VPN, SSH | A protocol used for secure remote administration |
| SSL/TLS | Technology used to facilitate secure web browsing |
| Hash | The output of an algorithm commonly used to validate file integrity |
| Password Spraying | An attack trying a single easily-guessable password against a large list of accounts |
| Password Cracking | An offline attack converting a password's cryptographic form back to human-readable text |
| Buffer overflow / deserialization | An attack resulting in remote command execution on the target host |
| OSINT | Hunting/using public data about a company and its employees without touching their network |
| SQL injection / XSS | A vulnerability where user input isn't sanitized, letting an attacker manipulate the application's logic |

### 2. Summary of Recommendations

* List short/medium/long-term recommendations tied back to specific findings - don't include recommendations that aren't actionable from findings reported later in the document.
* Long-term recommendations may be broader/best-practice (e.g. "create baseline security templates," "perform periodic social engineering + awareness training").
* A single finding can map to both a short-term fix (patch now) and a long-term one (fix the *process* that let it happen - e.g. patch management review, or SDLC review for app findings).
* If you skip this section, expect the client to ask you to prioritize for them anyway - "when everything is important, nothing is important."

### 3. Attack Chain

{% hint style="info" %}
Only include this if internal compromise occurred (typically an Internal PT, or an External PT that pivoted internally). Shows how multiple findings chain together - a finding that's medium-risk alone can become high-risk combined with one or two others, and this section is where you demonstrate that.
{% endhint %}

**Structure:** a short summary paragraph of the overall chain, then walk through each step with supporting command output/screenshots and a narrative in between - don't just caption figures, explain what's happening and why between them.

* [ ] Break each step into its own figure - don't cram multiple actions into one screenshot/output block.
* [ ] If setup is required (e.g. Metasploit module config), show the full config in one figure, then the execution result in a second.
* [ ] After demonstrating with your preferred tool, mention (don't re-demo) alternative tools that could validate the same finding.
* [ ] Evidence must be **completely defensible** - e.g. a Basic Auth login popup screenshot alone doesn't prove cleartext transmission; pair it with a Wireshark capture of the cleartext request. For GUI-based findings (web app, RDP), capture the address bar / `ifconfig`/`ipconfig` output to prove it's the client's actual host, not a random image.
* [ ] Redact credentials/hashes (this report may be passed around many audiences).
* [ ] Turn off your browser bookmarks bar and disable unprofessional extensions before screenshotting, or use a dedicated clean browser profile for testing.

**Typical shape of a real attack chain (for reference - abbreviate to your own actual findings):**

Foothold via LLMNR/NBT-NS poisoning (Responder) -> crack the captured NTLMv2 hash offline (Hashcat) -> enumerate SPNs and run BloodHound to find that a Kerberoastable service account has local admin on a specific host -> Kerberoast + crack that account -> use it to dump LSA secrets on that host, revealing an autologon admin credential with rights across all servers -> use that access to extract another logged-in user's Kerberos TGT (`Rubeus`) -> that user has DCSync rights -> pass-the-ticket, then DCSync via Mimikatz -> full domain compromise, followed by a password-cracking pass across the dumped NTDS hashes for the appendix analysis.

### 4. Findings

See [How to Write Up a Finding](#how-to-write-up-a-finding) below - this is covered in its own section since it's the largest part of the report.

### 5. Appendices

**Static appendices (include in every report):**

* **Scope** - URLs, network ranges, facilities, etc. Auditors receiving your report will need this.
* **Methodology** - the repeatable process followed to ensure thoroughness/consistency. Tie this back to [Methodology](methodology.md "mention").
* **Severity Ratings** - if not a direct CVSS mapping, articulate your own severity criteria clearly enough to defend it if questioned.
* **Biographies** - required for PCI-driven assessments (tester qualifications); good practice even otherwise for client confidence.

**Dynamic appendices (as applicable):**

* **Exploitation Attempts and Payloads** - track everything you did (like an incident responder would need to). List custom payload details, especially anything dropped to disk that you can't clean up yourself, so the client's forensics team can distinguish you from a real attacker.
* **Compromised Credentials** - list compromised accounts (or just note "all domain accounts" if the whole domain was compromised, rather than an exhaustive list).
* **Configuration Changes** - itemize anything you changed in the client's environment (ideally with prior written approval) so it can be reverted.
* **Additional Affected Scope** - a table of every affected host for a finding with too many to list inline, referenced from the finding itself.
* **Information Gathering** (External PT) - whois data, subdomains, discovered emails, breach-data hits (DeHashed), SSL/TLS config analysis, externally accessible ports/services. Adds value even to a low/no-finding report.
* **Domain Password Analysis** - after DCSync/NTDS dump, crack offline with Hashcat (multiple wordlists/rules, brute-force short NTLM if feasible), then run [DPAT](https://github.com/clr2of8/DPAT) - see [Domain Dominance](methodology.md "mention") in the methodology. Pull key stats into this appendix (or attach the full DPAT report):
  * Number of password hashes obtained
  * Number of password hashes cracked
  * Percent of password hashes cracked
  * Top 10 passwords
  * Password length breakdown
  * Number of Domain Admin passwords cracked
  * Number of Enterprise Admin passwords cracked

### Report Type Differences

* **External PT with no internal compromise** - no Attack Chain section; focus on information gathering, OSINT, externally exposed services. Skip Compromised Credentials/Configuration Changes/Domain Password Analysis appendices.
* **Web Application Security Assessment** - focus mainly on Executive Summary + Findings, typically framed around the OWASP Top 10.
* **Physical/Red Team/Social Engineering** - written more narratively than a standard technical report.

## How to Write Up a Finding

### Breakdown of a Finding

Required for every finding:

* [ ] Description of the finding and affected platform(s).
* [ ] Impact if left unresolved.
* [ ] Affected systems/networks/environments/applications.
* [ ] Remediation recommendation.
* [ ] Reference link(s) with further reading.
* [ ] Steps to reproduce + collected evidence.

Optional but valuable: CVE, OWASP/MITRE IDs, CVSS (or equivalent score), ease of exploitation/probability of attack.

{% hint style="warning" %}
Tailor generic "stock" findings (e.g. "Default Credentials") to the actual context - a default credential on a DeskJet printer is a very different risk than one on the building's HVAC controller or a critical web app.
{% endhint %}

### Showing Reproduction Steps Adequately

* One step per figure - don't blend multiple actions into a single screenshot the reader has to untangle.
* Write a narrative *between* figures explaining what's happening and why, not just a caption under each image.
* Prefer copy-pasteable raw command/request text over a screenshot when the client needs to reproduce it themselves (e.g. a Burp screenshot is worse than the actual raw request/payload for a web finding).
* List alternative tools that validate the same finding (mention + reference link only, don't re-demonstrate).

### Effective Remediation Recommendations

**Example 1**

* Bad: "Reconfigure your registry settings to harden against X."
* Good: "The following registry hives should be updated with the specified values: `[full path]`. Change value X to value Y. Note: changes to critical components like the registry should be tested in a small group before large-scale rollout."

**Example 2**

* Bad: "Implement `[expensive commercial tool]` to address this finding."
* Good: "`[Vendor]` has published a workaround as an interim solution (reference link below). Commercial tools also exist to disable the vulnerable functionality entirely, but may be cost-prohibitive."

{% hint style="info" %}
Being specific costs you research time now but builds client trust, strengthens your own knowledge for the report review call, and avoids giving a client days of guesswork or a recommendation they simply can't afford.
{% endhint %}

### Selecting Quality References

* Prefer vendor-agnostic sources - a vendor's own article usually pitches their product rather than explaining the fix.
* Thorough, free (not paywalled), to-the-point write-ups - not a 900-page RFC/NIST document if a summary will do.
* Clean, ad-light sites.
* Your own blog posts are ideal when available - reinforces your expertise and doesn't send the client to a competitor's site.

## Reporting Tips & Tricks

### Templates

* Maintain a blank template per assessment type (even obscure ones) - never repurpose a previous client's report by editing it in place, you risk leaving their name/data behind.

### MS Word Tips & Tricks

{% hint style="warning" %}
Use Word for **Windows**, not Mac - Mac Word lacks the VB Editor and produces broken PDFs (trimmed margins, dead ToC hyperlinks).
{% endhint %}

* **Font/Table styles** - use named styles, not manual bold/italic/color ("direct formatting"), so a single style update propagates everywhere instead of requiring 45 manual fixes.
* **Captions** - use Word's built-in caption feature (right-click -> Insert Caption) so figure/table numbers auto-renumber when you add/remove content.
* **Page numbers** - makes it far easier to discuss specific report sections with the client ("what does paragraph 2 on page 12 mean?").
* **Table of Contents / List of Figures/Tables** - standard for a professional report; both rely on styles/captions being used consistently.
* **Bookmarks** - for internal hyperlinks (e.g. to an appendix), and for macros that strip out whole bookmarked sections when combining templates.
* **Custom Dictionary** - auto-correct recurring typos (doesn't travel with the template, must be configured per-machine).
* **Language settings** - set your code/terminal font style's language to skip spell-check on command output, so running spellcheck doesn't flag hundreds of false positives.
* **Custom bullet/numbering** - auto-number findings/appendices.
* **Quick Access Toolbar** - add Back (after following a hyperlink), Undo/Redo, Save if not using shortcuts.
* **Useful hotkeys:**
  * `F4` - repeat the last action (e.g. re-apply a font style to newly selected text).
  * `Ctrl+A` then `F9` - update all fields (ToC, lists) at once.
  * `Ctrl+S` - save often, Word crashes happen.
  * `Ctrl+Alt+S` - split the window into two panes.
  * `Shift+F5` - jump the cursor back to the last edit location.

### Automation

* Word macros (`.dotm` templates, Windows only) can prompt for and auto-insert client name/dates/scope/testing type into placeholders, and strip out whole bookmarked sections that don't apply to a given assessment type - reducing template maintenance to a single master document.

### Reporting Tools / Findings Database

* At minimum, maintain a sanitized findings library to copy/paste from - prevents wasted time and inconsistent recommendations across a team.
* **Free:** [Ghostwriter](https://github.com/GhostManager/Ghostwriter), [Dradis CE](https://dradisframework.com/ce/), [VECTR](https://github.com/SecurityRiskAdvisors/VECTR), [WriteHat](https://github.com/blacklanternsecurity/writehat).
* **Paid:** [AttackForge](https://attackforge.com/), [PlexTrac](https://plextrac.com/), [Rootshell Prism](https://www.rootshellsecurity.net/why-prism/).

### Misc Tips & Tricks

* [ ] Tell a story - explain *why* each finding matters, not just that it was possible.
* [ ] Write as you go - don't leave reporting to the last day of the testing window.
* [ ] Keep notes organized chronologically so they're easy to reference while writing.
* [ ] Show enough evidence to demonstrate/reproduce, but don't clutter the report with excessive screenshots/output.
* [ ] Annotate screenshots (arrows/boxes - e.g. [Greenshot](https://getgreenshot.org/)) so the reader isn't guessing what to look at.
* [ ] Redact sensitive data (passwords, hashes, secrets) - use solid-shape redaction, never blur.
* [ ] Redact/replace unprofessional tool output strings (e.g. `(Pwn3d!)` from CrackMapExec) - check tool configs for a way to customize this globally instead of editing every report.
* [ ] Check Hashcat cracked-password output for anything crude/offensive before it goes in the report - swap for something innocuous.
* [ ] Proofread grammar/spelling/formatting; spell out acronyms on first use. Grammarly/LanguageTool are more capable than Word's built-in checker, but confirm data-handling policy before using them on confidential client data.
* [ ] Console screenshots: solid background (not transparent, not showing your desktop), readable theme (dark background/light text is easiest to reproduce; consider a light background if the client will print).
* [ ] Keep hostname/username in screenshots professional - not `azzkicker@clientsmasher`.
* [ ] Establish and follow a QA process (see below) and a consistent style guide across the team.
* [ ] Autosave your notetaking tool and Word; back up notes/evidence off the testing VM as you go - don't rely on a single machine.
* [ ] Script/automate repetitive reporting tasks wherever possible.

## Client Communication

* **Start notification** (sent at kickoff): tester name, scope/type description, source IP(s), testing dates, primary/secondary contacts.
* **Stop notification** (sent at end of each day): signals end of testing for the day; a good moment to give a high-level findings summary if the report will be large, so nothing blindsides the client later.
* **Ongoing dialogue during testing:**
  * Found extra scope (subnet/subdomain)? Ask before testing it.
  * Found a high-risk external RCE/SQLi? Stop and notify immediately, then confirm how to proceed.
  * Host down from scanning? Report it proactively rather than letting the client discover it.
  * Achieved DA/EA? Give a heads-up (alerts may fire) and ask if there's anything specific they want prioritized with that access, or anything explicitly off-limits even with DA rights.
* Keep detailed notes/tool logs at all times - if asked "did you touch host X on day Y," you need a concrete, documented answer.

## QA & Delivery Process

1. **Self-review** - at minimum, walk away and re-read with fresh eyes (sleep on it) before submitting for QA.
2. **Peer QA** - ideally at least one reviewer who isn't the author; larger teams may split QA into technical-accuracy and styling/cosmetics passes. Minor fixes (typos, phrasing) can be corrected directly by the reviewer; missing/poorly-illustrated evidence or findings should go back to the author.
3. **Track Changes on** - review what QA changed so you stop repeating the same mistakes; add recurring issues to your QA checklist.
4. **Draft delivered** to the client; allow ~1 week for their review, then offer a **Report Review Meeting** to walk through findings, answer questions, and collect feedback.
5. **Final report** issued after the client is satisfied - same content as the draft unless changes were agreed, with the `DRAFT` marking changed to `FINAL`. Some auditors will only accept a Final report.
6. **Archive** all testing data per your organization's retention policy until at least any post-remediation retest is complete.

## Engagement Notes Template

{% hint style="info" %}
This is the working scratch structure to fill in *during* the engagement - it feeds directly into the Report Structure above, it is not the deliverable itself.
{% endhint %}

`External Penetration Test - <Client Name>`

* `Scope` (including in-scope IP addresses/ranges, URLs, any fragile hosts, testing timeframes, and any limitations or other relative information we need handy)
* `Client Points of Contact`
* `Credentials`
* `Discovery/Enumeration`
  * `Scans`
  * `Live hosts`
* `Application Discovery`
  * `Scans`
  * `Interesting/Notable Hosts`
* `Exploitation`
  * `<Hostname or IP>`
  * `<Hostname or IP>`
* `Post-Exploitation`
  * `<Hostname or IP>`
  * `<Hostname or IP>`