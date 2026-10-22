# Objection and Runtime Instrumentation

{% hint style="info" %}
Use an authorized test device and test accounts. Preserve originals; protect dumps and restore the lab afterward. Replace command placeholders before use.
{% endhint %}

{% hint style="warning" %}
Complete the [Mandatory Preflight](preflight-and-frida-setup.md#mandatory-preflight) first. Host `frida`, device server, and Gadget must use the **same exact Frida version**.
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

Use long flags: global `-s` means spawn. Commands below run **inside Objection**; use in-session help for release-specific syntax.

### Classes and Activities

```
env
android hooking list
android hooking search classes <keyword>
android hooking watch class <class-name> --dump-args --dump-backtrace --dump-return
android intent launch_activity <activity-name>
```

### Clipboard, Screenshots, Memory, and SQLite

```
android clipboard monitor
android ui FLAG_SECURE false
memory dump all <output-file>.dmp
memory list modules
memory list exports <module-name>
memory search 4141 --string
memory write <address> <value> --string
android heap options
sqlite connect <database-file>
```

* `android heap options` / `android hooking list`: historical examples; confirm in-session help (`help android heap`).
* `FLAG_SECURE false` changes app behavior; assess original screenshot protections separately.
* `memory write` changes live data and may crash the app.
* Protect/delete memory dumps. Alternative: [Fridump](https://github.com/rootbsd/fridump).
* Review [CodeShare](https://codeshare.frida.re/) scripts before use; bypass success depends on app/version.
* Flutter: [reFlutter](https://github.com/ptswarm/reFlutter) for compatible instrumentation/traffic workflows.
* RMS: classes, arguments/returns, components, API monitoring, scripts.
* MobSF: configure a compatible dynamic-analysis environment first.

For observational scripts, overload/classloader diagnosis, and JNI/native hooks, continue with [Java and Native Instrumentation](java-and-native-instrumentation.md). Identify the actual check before running root/pinning commands; a hook message alone is not a verified result.
