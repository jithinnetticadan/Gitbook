# Dynamic Testing

{% hint style="info" %}
Use an authorized test device and test accounts. Preserve originals; protect dumps and restore the lab afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Before instrumentation, complete [Preflight and Frida Setup](preflight-and-frida-setup.md). Host `frida`, device `frida-server`, and any Gadget must use the **same exact Frida version**. Record an unmodified baseline before applying hooks or bypasses.
{% endhint %}

## Further Reading

* [Workbook Coverage](/broken/pages/jpVYwNJB7hvRLvqAN3dY): all 373 checklist IDs mapped to workflows, with source qualifications and conditional/legacy cases.
* Vidhan Thakur, _Android Dynamic Application Security Testing_, Field Guide 02 (63-page PDF), embedded on the [Android page](../). Commands and conclusions here are qualified against current platform/tool behavior; older guide snippets may not run unchanged.
* [Objection](https://github.com/sensepost/objection)
* [Runtime Mobile Security](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security)
* [HackTricks Android checklist](https://book.hacktricks.xyz/mobile-apps-pentesting/android-checklist)
* [SecJuice: Introduction to Frida and Objection](https://www.secjuice.com/objection-frida-guide/)
* [Frida installation](https://frida.re/docs/installation/)
* [Frida Android testing walkthrough from the notes](https://www.varutra.com/android-pentesting-using-frida/)
