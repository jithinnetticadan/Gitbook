# App Patching and Signing

* **Dependencies:** Gadget must match the host's **exact Frida version** and the app ABI.
* Complete [Verify Client and Server Versions](../setup.md#verify-client-and-server-versions).

## Automated Patching

* <pre class="language-bash" data-line-numbers><code class="lang-bash">objection patchapk --help
  objection patchapk --source &#x3C;app.apk> --gadget-version &#x3C;frida-version>
  </code></pre>
* Replace `<frida-version>` with the host `frida --version` output; verify `--gadget-version` in the installed patcher's help.
* Source/architecture flags belong to `patchapk`
* `objection signapk --help`: alignment/signing with Objection's key.

## Targeted SMALI Branch Patch

* Decode with SMALI output, then locate the executing check across all DEX directories. **Host Bash:**
  * ```bash
    apktool d '<app.apk>' -o '<decoded-directory>'
    grep -RniE 'isRooted|checkRoot|RootBeer|checkSignatures|CertificatePinner' '<decoded-directory>'/smali*
    ```
* Trace the matching method/caller in JADX and SMALI. Example: a Boolean root check returns into `v0`, then branches to an existing `:blocked` label:
  * **Original:** `if-nez v0, :blocked`
  * **Test patch:** `if-eqz v0, :blocked`
* `if-eqz` branches on zero/null; `if-nez` branches on nonzero/non-null. Preserve the actual register/label; for an object-returning method, this tests nullness rather than a Boolean.
* Rebuild, align, sign, and verify using [Manual Patching](#manual-patching), starting at step 4; Gadget injection is not required for this variant.
* **Install and launch** on a test device without a differently signed copy of the package:
  * ```bash
    adb install '<aligned-test.apk>'
    adb shell monkey -p '<package-name>' -c android.intent.category.LAUNCHER 1
    ```
* Compare an unchanged rebuilt control with the branch patch, then repeat the blocked operation. A local bypass does not establish a backend authorization/integrity bypass. [Integrity comparison](runtime-defenses-and-integrity.md#repackaging-and-signature-checks).

## Manual Patching

1. Decode the APK
   * `apktool d -r <app.apk> -o <decoded-directory>`.
2. Download [Frida Gadget](https://github.com/frida/frida) matching the host's **exact Frida version** and the app ABI; decompress `.xz` and place `libfrida-gadget.so` in `lib/<abi>`.
3. Add the load call to an appropriate initialization path. Example SMALI:
   * <pre class="language-java" data-line-numbers><code class="lang-java">const-string v0, "frida-gadget"
      invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
      </code></pre>
4. Rebuild, align, then sign the disposable test artifact; use current SDK Build Tools supporting `-P 16`:
   * <pre class="language-bash" data-line-numbers><code class="lang-bash">apktool b &#x3C;decoded-directory> -o &#x3C;unsigned-test.apk>
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
