# Dynamic Testing

{% hint style="info" %}
* Use an authorized test device and test accounts; replace command placeholders before use.
* Preserve originals, protect dumps, and restore the lab afterward.
{% endhint %}

{% hint style="warning" %}
* **Prerequisites:** follow the selected workflow; ordinary ADB/API tests do not require Frida or root.
* **Instrumentation:** complete [Preflight and Frida Setup](preflight-and-frida-setup.md); pin host `frida`, server, and Gadget to the same exact version.
* Record an unmodified baseline before hooks or bypasses.
{% endhint %}

## Further Reading

* [Source checklist](../README.md): attached Android pentest workbook; validate each item's platform, prerequisites, and applicability. A checklist is not proof of completed coverage.
* Vidhan Thakur, _Android Dynamic Application Security Testing_, Field Guide 02 (63-page PDF), embedded on the [Android page](../). Commands and conclusions here are qualified against current platform/tool behavior; older guide snippets may not run unchanged.
* [Objection](https://github.com/sensepost/objection)
* [Runtime Mobile Security](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security)
* [HackTricks Android checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/android-checklist)
* [SecJuice: Introduction to Frida and Objection](https://www.secjuice.com/objection-frida-guide/)
* [Frida installation](https://frida.re/docs/installation/)
* [Frida Android testing walkthrough from the notes](https://www.varutra.com/android-pentesting-using-frida/)
