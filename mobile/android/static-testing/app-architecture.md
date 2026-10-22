# App Architecture

{% hint style="info" %}
Test only in-scope apps. Record package, version, source, device/API level, and original APK hash. Replace command placeholders before use.
{% endhint %}

## Android App Architecture

| Item             | Key Point                                                                                                                             |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Runtime          | ART interprets/compiles DEX; older Android used Dalvik.                                                                               |
| Sandbox          | OS-enforced isolation and separate app UIDs, not just a VM.                                                                           |
| Native code      | `.so` libraries remain inside the app's OS boundary.                                                                                  |
| App IDs          | Regular app IDs: 10000-19999; full UIDs also encode the user.                                                                         |
| Cross-app access | Review activities, services, receivers, and providers. Exported does not mean vulnerable.                                             |
| Users/profiles   | Primary, secondary, guest, restricted/child where supported, and managed/work profiles separate data. BYOD isolation is not absolute. |
| Root             | Does not automatically bypass SELinux or encryption.                                                                                  |
| Signing          | Required for installation; protects integrity/signer identity, not against decompilation.                                             |

Layers: Linux kernel > hardware abstraction > native/ART libraries > Java API framework > system/apps.

| Path                             | Purpose                     |
| -------------------------------- | --------------------------- |
| `/data/app/<package>`            | Installed artifacts.        |
| `/data/data/<package>`           | Private app data.           |
| `/sdcard/Android/data/<package>` | App-specific external data. |

Paths/access vary by Android version and device.
