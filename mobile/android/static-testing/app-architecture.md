# App Architecture

## Android App Architecture

<table><thead><tr><th width="179">Item</th><th>Key Point</th></tr></thead><tbody><tr><td>Runtime</td><td>ART interprets/compiles DEX; older Android used Dalvik.</td></tr><tr><td>Sandbox</td><td>OS-enforced isolation and separate app UIDs, not just a VM.</td></tr><tr><td>Native code</td><td><code>.so</code> libraries remain inside the app's OS boundary.</td></tr><tr><td>App IDs</td><td>Regular app IDs: 10000-19999; full UIDs also encode the user.</td></tr><tr><td>Cross-app access</td><td>Review activities, services, receivers, and providers. Exported does not mean vulnerable.</td></tr><tr><td>Users/profiles</td><td>Primary, secondary, guest, restricted/child where supported, and managed/work profiles separate data. BYOD isolation is not absolute.</td></tr><tr><td>Root</td><td>Does not automatically bypass SELinux or encryption.</td></tr><tr><td>Signing</td><td>Required for installation; protects integrity/signer identity, not against decompilation.</td></tr></tbody></table>

* Layers: Linux kernel > hardware abstraction > native/ART libraries > Java API framework > system/apps.

<table><thead><tr><th width="301.0001220703125">Path</th><th>Purpose</th></tr></thead><tbody><tr><td><code>/data/app/&#x3C;package></code></td><td>Installed artifacts.</td></tr><tr><td><code>/data/data/&#x3C;package></code></td><td>Private app data.</td></tr><tr><td><code>/sdcard/Android/data/&#x3C;package></code></td><td>App-specific external data.</td></tr></tbody></table>

* Paths and access vary by Android version and device.
