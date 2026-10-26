# Objection and Runtime Instrumentation

{% hint style="info" %}
* Use an authorized test device and test accounts; replace command placeholders before use.
* Preserve originals, protect dumps, and restore the lab afterward.
{% endhint %}

{% hint style="warning" %}
* **Prerequisite:** complete [Mandatory Preflight](preflight-and-frida-setup.md#mandatory-preflight).
* Host `frida`, device server, and Gadget must use the **same exact Frida version**.
{% endhint %}

## Runtime Instrumentation

### Objection Session

```sh
objection --name <process-name> start
objection --name <package-name> --spawn start
objection --serial <device-serial> --name <process-name> start
objection --name <process-name> start --startup-script <script.js>
objection --name <process-name> start --startup-command 'android root disable'
objection --name <process-name> start --startup-command 'android sslpinning disable'
objection --name <process-name> run 'android root disable'
objection --name <process-name> run 'android sslpinning disable'
```

| Option/Mode     | Use                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------- |
| `--name`        | Attach by process name; spawn by package ID. Gadget may expose a different name.              |
| Global options  | `--name`, `--serial`, `--spawn`, `--no-pause` go **before** `start`/`run`.                    |
| Startup options | `--startup-command`, `--startup-script` go **after** `start`; check `objection start --help`. |
| `--no-pause`    | Immediate resume; omit when early hooks need a paused spawn.                                  |
| `run`           | One-shot execution; do not assume hooks persist after exit. Use `start` for monitoring.       |

* Prefer long flags; global `-s` means spawn.
* Run the commands below **inside Objection**; check in-session help for release-specific syntax.

### Classes and Activities

```
env
android hooking list classes
android hooking list class_methods <class-name>
android hooking search <keyword> --only-classes
android hooking watch <class-name> --dump-args --dump-backtrace --dump-return
android hooking watch '<class-name>!<method-name>' --dump-args --dump-backtrace --dump-return
android intent launch_activity <activity-name>
```

* **Current upstream syntax:** `watch` takes a class/pattern; `search` takes a query. Older `watch class` / `search classes` forms require an older compatible release.
* `android hooking list` alone is a namespace; select `classes`, `class_methods`, or another supported subcommand.

### Clipboard, Screenshots, Memory, and SQLite

```
android clipboard monitor
android ui FLAG_SECURE false
memory dump all <output-file>.dmp
memory list modules
memory list exports <module-name>
memory search 4141 --string
memory write <address> <value> --string
android heap search instances <class-name>
android heap print fields <instance-hashcode>
android heap print methods <instance-hashcode>
sqlite connect <database-file>
```

* `android heap options` is not a current command; use the heap commands above and the hashcode returned by `search instances`.
* `FLAG_SECURE false` changes app behavior; assess original screenshot protections separately.
* `memory write` changes live data and may crash the app.
* Protect/delete memory dumps. Alternative: [Fridump](https://github.com/rootbsd/fridump).
* Review [CodeShare](https://codeshare.frida.re/) scripts before use; bypass success depends on app/version.
* Flutter: [reFlutter](https://github.com/ptswarm/reFlutter) for compatible instrumentation/traffic workflows.
* RMS: classes, arguments/returns, components, API monitoring, scripts.
* MobSF: configure a compatible dynamic-analysis environment first.

* Use [Java and Native Instrumentation](java-and-native-instrumentation.md) for observational scripts, overload/classloader diagnosis, and JNI/native hooks.
* Identify the actual check before running root/pinning commands; a hook message alone is not a verified result.
* Syntax source: [Objection command registry](https://github.com/sensepost/objection/blob/master/objection/console/commands.py); confirm against your installed release.
