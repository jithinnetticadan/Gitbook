# Acquire and Decompile

## App Acquisition

* Find the installed package and pull its APK:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">adb shell
    pm list packages | grep &#x3C;app-name-fragment>
    pm path &#x3C;package-name>
    exit
    adb pull &#x3C;device-apk-path> &#x3C;local-file.apk>
    </code></pre>
* Create a local output directory.
* Strip `package:` from each `pm path` result before pulling.
* Split APKs: collect all required splits; record the set.
* Acquisition: authorized device, supplied APK, or Play Store emulator. Testing may use a separate root-capable image.

## Decompile and Inspect

* Use the acquired APK and its relevant splits; select an interface below to inspect code or resources. These outputs differ: use Apktool's decoded SMALI/resources when a test needs them, even if another tool is preferred for reading code.

{% tabs %}
{% tab title="JADX" %}
* **Linux Bash / Windows PowerShell:** open the APK and search its classes, manifest and resources.
  * ```text
    jadx-gui '<app.apk>'
    ```
* Follow the observed class/caller into the code deciding the relevant security check. Decompiled Java/Kotlin-like output may differ from the actual bytecode.
{% endtab %}
{% tab title="Apktool" %}
* **Linux Bash / Windows PowerShell:** decode resources and SMALI into the path used by the static searches and patching recipes.
  * ```text
    apktool d '<app.apk>' -o '<decoded-directory>'
    ```
* Inspect `AndroidManifest.xml`, `res/`, `assets/` and all `smali*` directories; this is not Java decompilation.
{% endtab %}
{% tab title="dex2jar + JD-GUI" %}
* **Linux Bash:** convert the APK's DEX and open the resulting JAR in JD-GUI.
  * ```text
    d2j-dex2jar.sh '<app.apk>'
    ```
* **Windows PowerShell:**
  * ```powershell
    .\d2j-dex2jar.bat '<app.apk>'
    ```
* This converts DEX to Java bytecode, not original source. Resource/SMALI checks still need the appropriate decoded artifacts.
{% endtab %}
{% tab title="MobSF" %}
* Upload the acquired APK to a running compatible MobSF instance; open the static analysis result and inspect the decompiled source/manifest and the actual call sites behind each finding. Scanner output alone is a lead, not proof of reachability.
{% endtab %}
{% tab title="GDA" %}
* **Windows GUI:** open the APK in [GDA](https://github.com/charles2gan/GDA-android-reversing-Tool); search the relevant class/string and inspect its callers and SMALI view. Compare suspicious decompiler output with actual bytecode.
{% endtab %}
{% endtabs %}

* Compare JADX code with Apktool resources/SMALI; resolve obfuscation or tool differences. Inspect `.so` native libraries separately.
* **APKLeaks:** use the [secret-scanning command](secrets-and-cloud.md#secrets-cloud-configuration-and-endpoints).
* Use [#automated-tools](./#automated-tools "mention") as well.

### Compiled Resources and Packaged Configuration

* **Host Bash, SDK Build Tools (`aapt2`), Apktool, and unzip:**
  * ```bash
    unzip -l '<app.apk>' | grep -E 'resources\.arsc|res/raw/|assets/'
    aapt2 dump resources '<app.apk>' > resource-table.txt
    grep -niE 'firebase|api[_-]?key|https?://|bucket|secret' resource-table.txt
    apktool d '<app.apk>' -o '<decoded-directory>'
    grep -RniE 'https?://|firebase|bucket|api[_-]?key|secret' '<decoded-directory>/res' '<decoded-directory>/assets'
    ```
* `res/values/strings.xml` is reconstructed from `resources.arsc`; its absence from the ZIP does not mean strings are absent. Repeat for relevant resource splits.
* Inspect `res/raw` and `assets` for JSON/XML configuration, JS bundles, certificates, and endpoints; trace values into the consuming code. Continue with [Secrets and Cloud](secrets-and-cloud.md).

## Reconnaissance and Build Comparison

* Inventory: package/version, source, acquisition date, APK/split SHA-256 hashes, signer, SDK levels, and backend environment.
* Compare the delivered build with public/store metadata; staged rollouts may differ.

| Source / Artifact                        | Review                                                                                     | Scope / Interpretation                                                                                                                                                    |
| ---------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Owner-supplied build / installed package | Exact production build, architecture/config splits, feature modules                        | Record the delivered build and any unavailable splits.                                                                            |
| Historical APK / public mirror           | Removed endpoints, old secrets, regressions, version drift                                 | Compare provenance, signing identity, and current-build applicability. |
| Public repositories / archives           | Package/domain references, configuration, test endpoints, accidentally published keystores | Distinguish public certificates from usable private keys.                                               |
| Play Store / developer metadata          | Publisher/domain, release history, Data Safety, permission disclosures                     | Compare disclosures against observed processing. Do not infer target SDK solely from store descriptions.                                                                  |
| Endpoints and public CT/DNS records      | API/GraphQL hosts, staging/legacy domains, SDK collectors                                  | Correlate discovered hosts with the app endpoints and backend environment.                                                                                  |
| Assets / resources                       | `resources.arsc`, `res/raw`, HTML/JS bundles, configuration, offline test records          | Decode binary resources with Apktool/JADX; a plain archive listing alone does not interpret them.                                                                         |

### App Bundles and Delivered Features

* **AAB:** publishing artifact, not an installable APK for `adb install`.
* **Dependencies:** owner-provided bundle, compatible [bundletool](https://developer.android.com/tools/bundletool), and Java environment.
* Build/inspect the device-specific APK set; record any test re-signing.
  * ```bash
    java -jar bundletool.jar get-device-spec --output=device.json
    java -jar bundletool.jar build-apks --bundle='<app.aab>' --output=test.apks --device-spec=device.json --ks='<test.keystore>' --ks-key-alias='<test-alias>'
    java -jar bundletool.jar extract-apks --apks=test.apks --output-dir=delivered-apks --device-spec=device.json
    java -jar bundletool.jar install-apks --apks=test.apks
    ```
* Keystore passwords are prompted for by bundletool; use the signing key corresponding to the intended test install.
* `pm path` lists installed splits, not every downloadable feature.
* Trigger authorized on-demand features; reacquire and inspect their code, permissions, resources, endpoints, and libraries.
* Compare base/split versions and signers; Android normally requires a consistent package/signature set.
* Prove unusual modified-split acceptance on the actual device; do not assume it.
* **Legacy Instant Apps:** confirm the deployment exists and applies to the assessed version; historical delivery modes may be unsupported.
* Map [framework clues](../dynamic-testing/methodology-and-baseline.md#fingerprint-the-implementation) to the code actually executed.

## Framework-Specific Recovery

<table><thead><tr><th width="195.0001220703125">Framework</th><th>Artifact / Approach</th><th>Dependency / Caveat</th></tr></thead><tbody><tr><td>React Native, plain JS</td><td>Inspect/beautify the delivered JS bundle and available source maps</td><td>Minification reversal does not recover original source/comments. Confirm the bundle is text before choosing JS tooling.</td></tr><tr><td>React Native, Hermes</td><td>Identify bytecode version and use a compatible disassembler/decompiler such as <a href="https://github.com/P1sec/hermes-dec">hermes-dec</a></td><td>Hermes formats change; mismatched tooling can produce incomplete/misleading output.</td></tr><tr><td>Unity IL2CPP</td><td>Pair the matching <code>libil2cpp.so</code> and metadata; use <a href="https://github.com/Perfare/Il2CppDumper">Il2CppDumper</a> plus native analysis</td><td>Generated declarations are not full original C# source. Protected metadata may need authorized runtime observation; no generic dump method is guaranteed.</td></tr><tr><td>Xamarin / Mono</td><td>Inspect assemblies and assembly-store metadata with a compatible extractor such as <a href="https://github.com/jakev/pyxamstore">pyxamstore</a>, then a .NET decompiler</td><td>Record runtime/store format and managed-versus-AOT behavior.</td></tr><tr><td>.NET MAUI</td><td>Inspect version-specific assembly stores, including ELF-wrapped/compressed layouts where present</td><td>Do not treat every MAUI release as the same blob format; validate recovered assembly headers/types and relevant native code.</td></tr><tr><td>Cordova / Ionic</td><td>Inspect packaged <code>assets/www</code>, JS/HTML, plugin configuration, and native bridge code</td><td>Web assets may be bundled/transformed or fetched later; they are not necessarily the whole application.</td></tr><tr><td>Flutter</td><td>Inspect Dart/assets, native libraries, platform channels, and build-specific tooling</td><td>Framework identification does not identify every network/crypto implementation. Use targeted runtime evidence.</td></tr></tbody></table>
