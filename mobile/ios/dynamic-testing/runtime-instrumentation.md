# Runtime Instrumentation

{% hint style="info" %}
Use authorized devices/builds and test accounts. Isolate the lab, protect evidence, and restore it afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Complete the [Mandatory Preflight](preflight-and-lab-setup.md#mandatory-preflight) first. Host `frida`, device server, and Gadget must use the **same exact Frida version**.
{% endhint %}

## Runtime Analysis and Instrumentation

### Frida and Objection Connection

```sh
frida-ps -Uai
frida -U -n <app-process-name>
frida-trace -U -m '*[NSURLRequest *]' <app-process-name>
objection --name <app-process-name> start
```

* Objective-C selectors: `-` instance method, `+` class method.
* Find identifiers: `frida-ps -Uai | grep '<app-name-fragment>'`.
* Attach by process name; spawn by bundle ID. Gadget may expose a different target name.
* Current Objection: `--name` selects the target; `start` opens a session.

```sh
objection version
objection --help
objection start --help
objection --name <bundle-id> --spawn start
objection --serial <device-serial> --name <app-process-name> start
objection --local --name <simulator-process-name> start
objection --name <app-process-name> start --startup-script <script.js>
objection --name <app-process-name> run 'ios info binary'
```

| Option/Mode   | Use                                                                                   |
| ------------- | ------------------------------------------------------------------------------------- |
| Global flags  | `--name`, `--serial`, `--local`, `--spawn`, `--no-pause` go **before** `start`/`run`. |
| Startup flags | Go **after** `start`; verify `objection start --help`.                                |
| `--local`     | iOS Simulator, not a physical device; compatible instrumentation required.            |
| `--no-pause`  | Immediate resume; omit for early hooks needing a paused spawn.                        |
| `run`         | One-shot; do not assume hooks survive exit. Use `start` for monitoring.               |

Use long flags: global `-s` means spawn. Interactive commands below run **inside Objection**, not the host shell.

### Classes, Hooks, and Local Checks

```
env
ios hooking list classes
ios hooking list class_methods
ios hooking watch class <class-name>
ios hooking watch method <method-name> --dump-args --dump-return --dump-backtrace
ios sslpinning disable
ios jailbreak disable
```

### Storage, Privacy, and Memory

```
ios pasteboard monitor
ios nsuserdefaults get
ios nsurlcredentialstorage dump
ios plist cat Info.plist
ios keychain dump
ios monitor crypt
ios info binary
ios cookies get
memory dump all <output-file>.dmp
```

* Interactive syntax varies: use in-session help; top-level `--help` does not define it.
* Detection testing: Hestia, Shadow, Objection; verify device/app compatibility.
* Alternatives: [RMS](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), [Grapefruit](https://github.com/ChiChou/grapefruit).
* Install in an isolated environment: `pip3 install frida-tools`, `pip3 install objection` (also installs Frida dependencies).

### Startup Hooks

```sh
objection --name <app-process-name> start --startup-command 'ios jailbreak disable'
objection --name <app-process-name> start --startup-command 'ios sslpinning disable'
```

Check `--startup-command`/`--startup-script` in `objection start --help` and the [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py). Instrumenting a detection return value does not establish server-side privilege bypass.

### r2frida

Requires radare2 and a compatible r2frida plugin installed in the host environment; installing radare2 alone does not provide the plugin. Follow the plugin's current installation and command syntax.

```
r2 frida://spawn//usb//<bundle-id>
:i?
:ic~<class-or-string>
:dtf <function-address>
```

Verify plugin syntax; addresses apply to the active process. Inspect dumps with `strings <dump-file>`; protect/delete them afterward.
