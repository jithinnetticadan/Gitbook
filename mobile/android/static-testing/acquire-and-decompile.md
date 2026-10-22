# Acquire and Decompile

{% hint style="info" %}
* Test only in-scope apps; replace command placeholders before use.
* Record package, version, source, device/API level, and original APK hash.
{% endhint %}

## Acquire the APK

* Find the installed package and pull its APK:

```sh
adb shell
pm list packages | grep <app-name-fragment>
pm path <package-name>
exit
adb pull <device-apk-path> <local-file.apk>
```

* Create a local output directory.
* Strip `package:` from each `pm path` result before pulling.
* Split APKs: collect all required splits; record the set.
* Acquisition: authorized device, supplied APK, or Play Store emulator. Testing may use a separate root-capable image.

## Decompile and Inspect

```sh
jadx-gui <app.apk>
apktool d <app.apk> -o <decoded-directory>
```

* Compare JADX code with Apktool resources/SMALI; resolve obfuscation or tool differences.
* Inspect `.so` native libraries separately.
* Optional DEX-to-JAR and string scanning:

```sh
d2j-dex2jar.sh <app.apk>
apkleaks -f <app.apk>
```

* Open the generated JAR in JD-GUI. dex2jar converts DEX to Java bytecode, not original source.
* MobSF: inspect decompiled code/SMALI; validate automated findings manually.

## Reconnaissance and Build Comparison

* Inventory: package/version, source, acquisition date, APK/split SHA-256 hashes, signer, SDK levels, and backend environment.
* Compare the delivered build with public/store metadata; staged rollouts may differ.

| Source / Artifact                        | Review                                                                                     | Scope / Interpretation                                                                                                                                                    |
| ---------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Owner-supplied build / installed package | Exact production build, architecture/config splits, feature modules                        | Prefer a reproducible, authorized build. Preserve originals and record any unavailable splits.                                                                            |
| Historical APK / public mirror           | Removed endpoints, old secrets, regressions, version drift                                 | Authenticate provenance and signing identity; do not install unknown packages on a personal device. A historical issue is not automatically present in the current build. |
| Public repositories / archives           | Package/domain references, configuration, test endpoints, accidentally published keystores | Do not use discovered credentials beyond authorized validation. A certificate is public; a usable private key is different.                                               |
| Play Store / developer metadata          | Publisher/domain, release history, Data Safety, permission disclosures                     | Compare disclosures against observed processing. Do not infer target SDK solely from store descriptions.                                                                  |
| Endpoints and public CT/DNS records      | API/GraphQL hosts, staging/legacy domains, SDK collectors                                  | Add candidates to the scope inventory; a related hostname is not permission to probe it.                                                                                  |
| Assets / resources                       | `resources.arsc`, `res/raw`, HTML/JS bundles, configuration, offline test records          | Decode binary resources with Apktool/JADX; a plain archive listing alone does not interpret them.                                                                         |

### App Bundles and Delivered Features

* **AAB:** publishing artifact, not an installable APK for `adb install`.
* **Dependencies:** owner-provided bundle, compatible [bundletool](https://developer.android.com/tools/bundletool), and Java environment.
* Build/inspect the device-specific APK set; record any test re-signing.
* `pm path` lists installed splits, not every downloadable feature.
* Trigger authorized on-demand features; reacquire and inspect their code, permissions, resources, endpoints, and libraries.
* Compare base/split versions and signers; Android normally requires a consistent package/signature set.
* Prove unusual modified-split acceptance on the actual device; do not assume it.
* **Legacy Instant Apps:** confirm the deployment exists and applies to the assessed version; historical delivery modes may be unsupported.
* Map [framework clues](../dynamic-testing/methodology-and-baseline.md#fingerprint-the-implementation) to the code actually executed.

## Framework-Specific Recovery

| Framework              | Artifact / Approach                                                                                                                                          | Dependency / Caveat                                                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| React Native, plain JS | Inspect/beautify the delivered JS bundle and available source maps                                                                                           | Minification reversal does not recover original source/comments. Confirm the bundle is text before choosing JS tooling.                                   |
| React Native, Hermes   | Identify bytecode version and use a compatible disassembler/decompiler such as [hermes-dec](https://github.com/P1sec/hermes-dec)                             | Hermes formats change; mismatched tooling can produce incomplete/misleading output.                                                                       |
| Unity IL2CPP           | Pair the matching `libil2cpp.so` and metadata; use [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) plus native analysis                              | Generated declarations are not full original C# source. Protected metadata may need authorized runtime observation; no generic dump method is guaranteed. |
| Xamarin / Mono         | Inspect assemblies and assembly-store metadata with a compatible extractor such as [pyxamstore](https://github.com/jakev/pyxamstore), then a .NET decompiler | Record runtime/store format and managed-versus-AOT behavior.                                                                                              |
| .NET MAUI              | Inspect version-specific assembly stores, including ELF-wrapped/compressed layouts where present                                                             | Do not treat every MAUI release as the same blob format; validate recovered assembly headers/types and relevant native code.                              |
| Cordova / Ionic        | Inspect packaged `assets/www`, JS/HTML, plugin configuration, and native bridge code                                                                         | Web assets may be bundled/transformed or fetched later; they are not necessarily the whole application.                                                   |
| Flutter                | Inspect Dart/assets, native libraries, platform channels, and build-specific tooling                                                                         | Framework identification does not identify every network/crypto implementation. Use targeted runtime evidence.                                            |
