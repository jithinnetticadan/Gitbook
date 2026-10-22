# App Patching and Repackaging

{% hint style="info" %}
Use an authorized test device and test accounts. Preserve originals; protect dumps and restore the lab afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Gadget must match the host's **exact Frida version** and the app ABI. See [Verify Client and Server Versions](preflight-and-frida-setup.md#verify-client-and-server-versions).
{% endhint %}

## App Patching and Repackaging

### Automated Patching

```sh
objection patchapk --help
objection patchapk --source <app.apk> --gadget-version <frida-version>
```

* Replace `<frida-version>` with the host `frida --version` output; verify `--gadget-version` in the installed patcher's help.
* Source/architecture flags belong to `patchapk`; check its help.
* `objection signapk --help`: alignment/signing with Objection's key.
* Manual workflow below uses your own test keystore.

### Manual Patching

1. Decode the APK, omitting resource decoding if appropriate: `apktool d -r <app.apk> -o <decoded-directory>`.
2. Download [Frida Gadget](https://github.com/frida/frida) matching the host's **exact Frida version** and the app ABI; decompress `.xz` and place `libfrida-gadget.so` in `lib/<abi>`.
3.  Add the load call to an appropriate initialization path. Example SMALI:

    ```smali
    const-string v0, "frida-gadget"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
    ```
4.  Rebuild, sign, and align the disposable test artifact:

    ```sh
    apktool b <decoded-directory> -o <unsigned-test.apk>
    keytool -genkey -v -keystore <test.keystore> -alias <test-alias> -keyalg RSA -keysize 2048 -validity 10000
    zipalign -p 4 <unsigned-test.apk> <aligned-test.apk>
    apksigner sign --ks <test.keystore> --ks-key-alias <test-alias> <aligned-test.apk>
    apksigner verify <aligned-test.apk>
    ```

* `System.loadLibrary("frida-gadget")` requires **`libfrida-gadget.so`**, not `frida-gadget.so`.
* Execute in the target process: suitable Application initialization or MainActivity/OnboardingActivity constructor.
* Check free registers and `.locals`/`.registers` before using `v0`.
* Gadget configuration/default wait behavior can pause startup.
* Without `-o`, Apktool usually writes under `dist`.
* Align before `apksigner`; legacy SHA1withRSA/SHA1 `jarsigner` is not the modern default.
* An unrelated signing key normally prevents installing over the original, even with `adb install -r`. Preserve original APKs/splits and test data; use a disposable install. See [integrity validation](runtime-defenses-and-integrity.md#repackaging-and-signature-checks) for rebuilt controls and attestation caveats.

References: [Gadget](https://frida.re/docs/gadget/), [apksigner](https://developer.android.com/tools/apksigner), [non-root walkthrough](https://koz.io/using-frida-on-android-without-root/).
