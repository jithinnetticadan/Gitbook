# Runtime Instrumentation

* Host `frida`, device server, and Gadget must use the **same exact Frida version**.

## Attach or Spawn

* **Choose Frida or Objection below; run the selected commands on the host.** Attach to a running process, or spawn by package ID for startup checks.
* Frida loads custom scripts; Objection provides packaged commands and hooks using Frida internally. Both require a working Frida connection.
* **App/process listing:** [Frida connection check](../setup.md#verify-client-and-server-versions).

{% tabs %}
{% tab title="Frida" %}
- **Attach to a running process:**
  * ```bash
    frida -U -n <process-name>
    ```
- **Attach and load a script:**
  * ```bash
    frida -U -n <process-name> -l <hook.js>
    ```
- **Spawn and load a script:**
  * ```bash
    frida -U -f <package-name> -l <hook.js>
    ```
- Frida CLI resumes spawned processes by default; use `--pause` and REPL `%resume` when needed.
- **CLI options:**
  * ```bash
    frida --help
    ```
- Custom script examples: [Java and Native Instrumentation](java-and-native-instrumentation.md).
{% endtab %}

{% tab title="Objection" %}
* **Attach to a running process:**
  * ```bash
    objection --name <process-name> start
    ```
* **Spawn and start a session:**
  * ```bash
    objection --name <package-name> --spawn start
    ```
* **Device selection, startup scripts/hooks, and one-shot commands:**
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">objection --serial &#x3C;device-serial> --name &#x3C;process-name> start
    objection --name &#x3C;process-name> start --startup-script &#x3C;script.js>
    objection --name &#x3C;process-name> start --startup-command 'android root disable'
    objection --name &#x3C;process-name> start --startup-command 'android sslpinning disable'
    objection --name &#x3C;process-name> run 'android root disable'
    objection --name &#x3C;process-name> run 'android sslpinning disable'
    </code></pre>

<table><thead><tr><th width="155">Option/Mode</th><th>Use</th></tr></thead><tbody><tr><td><code>--name</code></td><td>Attach by process name; spawn by package ID. Gadget may expose a different name.</td></tr><tr><td>Global options</td><td><code>--name</code>, <code>--serial</code>, <code>--spawn</code>, <code>--no-pause</code> go <strong>before</strong> <code>start</code>/<code>run</code>.</td></tr><tr><td>Startup options</td><td><code>--startup-command</code>, <code>--startup-script</code> go <strong>after</strong> <code>start</code>; check <code>objection start --help</code>.</td></tr><tr><td><code>--no-pause</code></td><td>Immediate resume; omit when early hooks need a paused spawn.</td></tr><tr><td><code>run</code></td><td>One-shot execution; do not assume hooks persist after exit. Use <code>start</code> for monitoring.</td></tr></tbody></table>
{% endtab %}
{% tab title="RMS" %}
* **Host, installed RMS:** verify the running Frida server and start RMS; open `http://127.0.0.1:5491/` and select the target package in the device/app screen.
  * ```text
    frida-ps -U
    rms
    ```
* Use the class dump and hook/trace view to select the observed class and method, then exercise the app action. RMS uses Frida in the target process; its API Monitor is Android-only. The upstream notes recommend one connected device and Chrome for its web UI.
{% endtab %}
{% tab title="House" %}
* **Legacy House checkout, host terminal:** with its compatible Python/Frida dependencies installed and server running, start the UI on the port shown. Check [upstream compatibility](https://github.com/nccgroup/house); it was tested with older Frida versions.
  * ```text
    frida-ps -U
    python app.py 8000
    ```
* Open `http://127.0.0.1:8000/`, select the target and use Enumeration for loaded classes/methods, then the hook/tracing view for the observed method. A Frida/Python version mismatch may block this alternative.
{% endtab %}
{% tab title="Grapefruit" %}
* **Installed Grapefruit, host terminal:** current upstream `igf` requires Node.js 22.18+ and a compatible device Frida server. Open the local UI and choose the target process.
  * ```text
    frida-ps -U
    igf
    ```
* Use the class/method inspector or runtime hooking view to trace the same observed method. Grapefruit is an inspection interface; do not assume it supplies a universal pinning or root-detection bypass.
{% endtab %}
{% endtabs %}

* **Result:** trigger the same app action, verify the selected hook or trace fires, and compare its observed result with the uninstrumented control. GUI tools share Frida's target-process context; they do not prove an unprivileged external app can call an exported component.

## Classes and Hooks

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

## Keystore and Device Checks

* **Inside Objection:**
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">android keystore list
    android keystore detail
    android keystore watch
    android root disable
    android sslpinning disable
    </code></pre>

## Clipboard, Screenshots, Memory, and SQLite

* <pre class="language-bash" data-line-numbers><code class="lang-bash">android clipboard monitor
  android ui FLAG_SECURE false
  memory dump all &#x3C;output-file>.dmp
  memory list modules
  memory list exports &#x3C;module-name>
  memory search 4141 --string
  memory write &#x3C;address> &#x3C;value> --string
  android heap search instances &#x3C;class-name>
  android heap print fields &#x3C;instance-hashcode>
  android heap print methods &#x3C;instance-hashcode>
  sqlite connect &#x3C;database-file>
  </code></pre>
* `android ui FLAG_SECURE false` is an analysis-only override: it disables the protection in the instrumented run and cannot establish the original app's screenshot behavior. Test the unmodified app with the [capture and recents workflow](platform-and-version-specific-tests.md#autofill-sms-and-capture-transitions).
* Alternative memory tool: [fridump3](https://github.com/rootbsd/fridump3/).
* Review [CodeShare](https://codeshare.frida.re/) scripts, bypass success depends on app/version.
* Flutter: [reFlutter](https://github.com/ptswarm/reFlutter) for compatible instrumentation/traffic workflows.
* [RMS-Runtime-Mobile-Security](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security): classes, arguments/returns, components, API monitoring, scripts; select its tab in [Attach or Spawn](#attach-or-spawn).
* MobSF: configure a compatible dynamic-analysis environment first.
* Use [Java and Native Instrumentation](java-and-native-instrumentation.md) for observational scripts, overload/classloader diagnosis, and JNI/native hooks.
* Identify the actual check before running root/pinning commands.
* Syntax source: [Objection command registry](https://github.com/sensepost/objection/blob/master/objection/console/commands.py); confirm against your installed release.

## Runtime Memory Search

* Exercise the relevant login/payment flow with a unique test marker, then search the running app's memory for that marker and any associated credential value.

{% tabs %}
{% tab title="Objection" %}
* **Host terminal:** attach to the running app.
  * ```text
    frida-ps -Uai
    objection --name '<process-name>' start
    ```
* **Objection console:** search the marker or dump accessible app memory.
  * ```text
    memory search <test-marker> --string
    memory dump all <output-file>.dmp
    ```
{% endtab %}
{% tab title="fridump3" %}
* **Host, Frida 17+ compatible [fridump3.1](https://github.com/Xenorf/fridump3.1):** use the running process name and search the extracted strings for the marker.
  * ```text
    frida-ps -Uai
    fridump3 -u -s -o ./memory-capture "<running-process-name>"
    ```
{% endtab %}
{% tab title="Grapefruit" %}
* **Host terminal:** start the installed interface and select the running app.
  * ```text
    frida-ps -Uai
    igf
    ```
* Use the memory scanner to search the marker in the selected process and inspect the matching region.
{% endtab %}
{% endtabs %}

* **Search a Fridump3 capture for the test marker:**

{% tabs %}
{% tab title="Linux" %}
* ```bash
  grep -RniF '<test-marker>' './memory-capture'
  ```
{% endtab %}
{% tab title="Windows" %}
* ```powershell
  Get-ChildItem './memory-capture' -Recurse -File | Select-String -SimpleMatch '<test-marker>'
  ```
{% endtab %}
{% endtabs %}

* Repeat the relevant operation after logout or expiry. A marker present during normal use is a lead; determine whether a retained credential remains usable and what access is needed to read the process.
