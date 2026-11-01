# Runtime Instrumentation

{% hint style="warning" %}
* Host `frida`, device server, and Gadget must use the **same exact Frida version**.
{% endhint %}

## Objection Session

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

<table><thead><tr><th width="155">Option/Mode</th><th>Use</th></tr></thead><tbody><tr><td><code>--name</code></td><td>Attach by process name; spawn by package ID. Gadget may expose a different name.</td></tr><tr><td>Global options</td><td><code>--name</code>, <code>--serial</code>, <code>--spawn</code>, <code>--no-pause</code> go <strong>before</strong> <code>start</code>/<code>run</code>.</td></tr><tr><td>Startup options</td><td><code>--startup-command</code>, <code>--startup-script</code> go <strong>after</strong> <code>start</code>; check <code>objection start --help</code>.</td></tr><tr><td><code>--no-pause</code></td><td>Immediate resume; omit when early hooks need a paused spawn.</td></tr><tr><td><code>run</code></td><td>One-shot execution; do not assume hooks persist after exit. Use <code>start</code> for monitoring.</td></tr></tbody></table>

## Classes and Activities

* <pre class="language-bash" data-line-numbers><code class="lang-bash">env
  android hooking list classes
  android hooking list class_methods &#x3C;class-name>
  android hooking search &#x3C;keyword> --only-classes
  android hooking watch &#x3C;class-name> --dump-args --dump-backtrace --dump-return
  android hooking watch '&#x3C;class-name>!&#x3C;method-name>' --dump-args --dump-backtrace --dump-return
  android intent launch_activity &#x3C;activity-name>
  </code></pre>
* **Syntax:** `watch` takes a class/pattern; `search` takes a query.
* `android hooking list` alone is a namespace; select `classes`, `class_methods`, or another supported subcommand.

## Clipboard, Screenshots, Memory, and SQLite

* <pre class="language-bash" data-line-numbers><code class="lang-bash">android clipboard monitor
  # FLAG_SECURE false changes app behavior.
  android ui FLAG_SECURE false
  memory dump all &#x3C;output-file>.dmp
  memory list modules
  memory list exports &#x3C;module-name>
  memory search 4141 --string
  # memory write changes live data and may crash the app.
  memory write &#x3C;address> &#x3C;value> --string
  android heap search instances &#x3C;class-name>
  android heap print fields &#x3C;instance-hashcode>
  android heap print methods &#x3C;instance-hashcode>
  sqlite connect &#x3C;database-file>
  </code></pre>
* Protect/delete memory dumps. Alternative: [Fridump](https://github.com/rootbsd/fridump).
* Review [CodeShare](https://codeshare.frida.re/) scripts, bypass success depends on app/version.
* Flutter: [reFlutter](https://github.com/ptswarm/reFlutter) for compatible instrumentation/traffic workflows.
* [RMS-Runtime-Mobile-Security](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security): classes, arguments/returns, components, API monitoring, scripts.
* MobSF: configure a compatible dynamic-analysis environment first.
* Use [Java and Native Instrumentation](java-and-native-instrumentation.md) for observational scripts, overload/classloader diagnosis, and JNI/native hooks.
* Identify the actual check before running root/pinning commands.
* Syntax source: [Objection command registry](https://github.com/sensepost/objection/blob/master/objection/console/commands.py); confirm against your installed release.
