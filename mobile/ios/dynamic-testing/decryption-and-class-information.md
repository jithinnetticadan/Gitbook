# Decryption and Class Information

## Decryption and Class Information

* FairPlay-encrypted apps need a suitable decrypted executable for static code analysis.
* Tools: [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump), [Clutch](https://github.com/KJCracks/Clutch), [bfinject](https://github.com/BishopFox/bfinject).
* Configure the selected tool's Python dependencies and SSH connection; example: `python dump.py <bundle-id>`.
* Extract the app and identify its executable. Choose a static or runtime method to locate the class/selector used by the feature.

{% tabs %}
{% tab title="class-dump" %}
* **Mac terminal:** dump compatible Objective-C metadata from the decrypted binary.
  * ```bash
    class-dump '<app-binary>'
    ```
{% endtab %}
{% tab title="radare2 / rabin2" %}
* **Mac terminal:** list classes or header-style class metadata from the binary.
  * ```bash
    rabin2 -c '<app-binary>'
    rabin2 -cc '<app-binary>'
    ```
{% endtab %}
{% tab title="Objection" %}
* **Mac terminal:** attach to the running app with a compatible Frida connection.
  * ```bash
    frida-ps -Uai
    objection --name '<app-process-name>' start
    ```
* **Objection console:** find the runtime class and its selectors.
  * ```text
    ios hooking list classes
    ios hooking list class_methods <class-name>
    ```
{% endtab %}
{% tab title="Grapefruit" %}
* **Mac terminal:**
  * ```bash
    frida-ps -Uai
    igf
    ```
* Select the running app and inspect its Objective-C classes/methods; use the relevant selector in the test's runtime hook.
{% endtab %}
{% endtabs %}

* Hopper, Ghidra or IDA Free can inspect the executable when source-level class metadata is unavailable. Objective-C and Swift metadata expose different information.
* For encryption-dependent checks, see [Binary Analysis](../static-testing/binary-analysis.md).
