# Runtime Instrumentation

{% hint style="info" %}
* Use authorized devices/builds and test accounts; replace command placeholders before use.
* Isolate the lab, protect evidence, and restore it afterward.
{% endhint %}

{% hint style="warning" %}
* **Prerequisite:** complete [Mandatory Preflight](preflight-and-lab-setup.md#mandatory-preflight).
* Host `frida`, device server, and Gadget must use the **same exact Frida version**.
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

* Prefer long flags; global `-s` means spawn.
* Run interactive commands **inside Objection**, not the host shell.

### Classes, Hooks, and Local Checks

```
env
ios hooking list classes
ios hooking list class_methods <class-name>
ios hooking watch <class-name>
ios hooking watch '-[<class-name> <selector:>]' --dump-args --dump-return --dump-backtrace
ios sslpinning disable
ios jailbreak disable
```

* **Current syntax:** `watch` takes a class or quoted Objective-C pattern directly; older `watch class` / `watch method` forms are release-specific.
* Replace the selector with its exact colon count; use `+` for class methods. `--dump-args` may fail on non-object arguments; inspect types first.
* **Frida 17+:** current CLI tools supply the ObjC bridge; custom agents need bundled `frida-objc-bridge`. See [bridge setup](https://frida.re/docs/bridges/).

### Storage, Privacy, and Memory

```
ios pasteboard monitor
ios nsuserdefaults get
ios nsurlcredentialstorage dump
ios plist cat Info.plist
ios plist cat <app-bundle-path>/Info.plist
ios keychain dump
ios monitor crypto
ios info binary
ios cookies get
memory dump all <output-file>.dmp
```

* Relative `Info.plist` requires the app bundle as the current directory; otherwise use the bundle path reported by `env`.
* Interactive syntax varies: use in-session help; top-level `--help` does not define it.
* `ios monitor crypto` monitors supported CommonCrypto calls, not all cryptography; `ios monitor crypt` is incomplete. [Command registry](https://github.com/sensepost/objection/blob/master/objection/console/commands.py).
* Detection testing: Hestia, Shadow, Objection; verify device/app compatibility.
* Alternatives: [RMS](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security), [Grapefruit](https://github.com/ChiChou/grapefruit).
* Install in an isolated environment: `pip3 install frida-tools`, `pip3 install objection` (also installs Frida dependencies).

### Startup Hooks

```sh
objection --name <app-process-name> start --startup-command 'ios jailbreak disable'
objection --name <app-process-name> start --startup-command 'ios sslpinning disable'
```

* Verify `--startup-command`/`--startup-script` using `objection start --help` and the [CLI source](https://github.com/sensepost/objection/blob/master/objection/console/cli.py).
* Changing a detection return value does not prove server-side privilege bypass.

### r2frida

* **Host dependencies:** radare2 and a compatible r2frida plugin; radare2 alone does not install the plugin.
* Follow the plugin's current installation instructions and command syntax.

```
r2 frida://spawn/usb//<bundle-id>
:i?
:ic~<class-or-string>
:dtf <function-address>
```

* **URI correction:** `spawn/usb//<bundle-id>`; the extra slash in `spawn//usb//` misplaces the transport. [r2frida usage](https://github.com/nowsecure/r2frida#usage).
* Run the first line on the host, then `:` commands inside r2. Use `:dc` to resume a paused spawn; verify plugin syntax and active-process addresses.
* r2frida embeds its own Frida core; compatibility is not established by the Python `frida --version` alone.
* Inspect dumps with `strings <dump-file>`; protect them during analysis and delete them afterward.
