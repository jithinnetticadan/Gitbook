# App Patching and Repackaging

{% hint style="warning" %}
* **Dependencies:** Gadget must match the host's **exact Frida version** and the app ABI.
* Complete [Verify Client and Server Versions](preflight-and-frida-setup.md#verify-client-and-server-versions).
{% endhint %}

## Automated Patching

* <pre class="language-bash" data-line-numbers><code class="lang-bash">objection patchapk --help
  objection patchapk --source &#x3C;app.apk> --gadget-version &#x3C;frida-version>
  </code></pre>
* Replace `<frida-version>` with the host `frida --version` output; verify `--gadget-version` in the installed patcher's help.
* Source/architecture flags belong to `patchapk`
* `objection signapk --help`: alignment/signing with Objection's key.

## Manual Patching

1. Decode the APK
   1. &#x20;`apktool d -r <app.apk> -o <decoded-directory>`.
2. Download [Frida Gadget](https://github.com/frida/frida) matching the host's **exact Frida version** and the app ABI; decompress `.xz` and place `libfrida-gadget.so` in `lib/<abi>`.
3. Add the load call to an appropriate initialization path. Example SMALI:
   1. <pre class="language-java" data-line-numbers><code class="lang-java">const-string v0, "frida-gadget"
      invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
      </code></pre>
4. Rebuild, align, then sign the disposable test artifact; use current SDK Build Tools supporting `-P 16`:
   1. <pre class="language-bash" data-line-numbers><code class="lang-bash">apktool b &#x3C;decoded-directory> -o &#x3C;unsigned-test.apk>
      keytool -genkey -v -keystore &#x3C;test.keystore> -alias &#x3C;test-alias> -keyalg RSA -keysize 2048 -validity 10000
      zipalign -P 16 -v 4 &#x3C;unsigned-test.apk> &#x3C;aligned-test.apk>
      apksigner sign --ks &#x3C;test.keystore> --ks-key-alias &#x3C;test-alias> &#x3C;aligned-test.apk>
      apksigner verify &#x3C;aligned-test.apk>
      </code></pre>

* **Legacy 4 KiB-only alternative:** use instead of the alignment line above, before signing. Deprecated `-p` does not provide 16 KiB alignment.
  * ```bash
    zipalign -p 4 <unsigned-test.apk> <aligned-test.apk>
    ```
* **16 KiB check:** APK ZIP alignment does not repair incompatible ELF segments; Gadget and other native libraries must also support the device's page size. [Alignment reference](https://developer.android.com/tools/zipalign).
* `System.loadLibrary("frida-gadget")` requires **`libfrida-gadget.so`**, not `frida-gadget.so`.
* Execute in the target process: suitable Application initialization or MainActivity/OnboardingActivity constructor.
* Check free registers and `.locals`/`.registers` before using `v0`.
* Gadget configuration/default wait behavior can pause startup.
* Without `-o`, Apktool usually writes under `dist`.
* Align before `apksigner`; legacy SHA1withRSA/SHA1 `jarsigner` is not the modern default.
* References: [Gadget](https://frida.re/docs/gadget/), [apksigner](https://developer.android.com/tools/apksigner), [non-root walkthrough](https://koz.io/using-frida-on-android-without-root/).
