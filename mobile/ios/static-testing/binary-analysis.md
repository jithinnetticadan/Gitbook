# Binary Analysis

## App and Binary Review

* Find the executable via `Info.plist`; inspect linked frameworks.
* Objective-C/Swift metadata differ; missing class-dump output does not prove absent functionality.
* Source: `.h` declarations; `.m` Objective-C implementations.
* Layers: hardware/firmware and software; user data is separate from OS data. Jailbreak changes inspection capabilities.

### Binary Protections

* Run on macOS; interpret indicators in context:
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">otool -hv &#x3C;app-binary> | grep PIE
    otool -I -v &#x3C;app-binary> | grep stack_chk
    otool -I -v &#x3C;app-binary> | grep objc_release
    otool -arch all -Vl &#x3C;app-binary> | grep -A5 LC_ENCRYPT
    otool -l &#x3C;app-binary> | grep -A4 LC_ENCRYPTION_INFO
    </code></pre>

<table><thead><tr><th width="121">Check</th><th width="284.0001220703125">Indicator</th><th>Limitation</th></tr></thead><tbody><tr><td>PIE</td><td>Supports address randomization.</td><td>Not proof of overall binary security.</td></tr><tr><td>Canaries</td><td><code>stack_chk_guard</code>, <code>stack_chk_fail</code>.</td><td>Checks some stack corruption at return; not all code.</td></tr><tr><td>ARC</td><td><code>_objc_release</code>.</td><td>Reference-lifetime management, not complete memory safety.</td></tr><tr><td>Encryption</td><td><code>cryptid=1</code> encrypted; <code>0</code> unencrypted.</td><td>Development/decrypted copies need not be App Store-encrypted.</td></tr></tbody></table>

### Sensitive and Risky API Indicators

* Search symbols, then inspect call sites and data flow:
* <pre class="language-bash" data-line-numbers><code class="lang-bash">otool -Iv &#x3C;app-binary> | grep -w '_CC_MD5'
  otool -Iv &#x3C;app-binary> | grep -w '_CC_SHA1'
  otool -Iv &#x3C;app-binary> | grep -w '_random'
  otool -Iv &#x3C;app-binary> | grep -w '_srand'
  otool -Iv &#x3C;app-binary> | grep -w '_rand'
  otool -Iv &#x3C;app-binary> | grep -w '_malloc'
  otool -Iv &#x3C;app-binary> | grep -E '_(gets|memcpy|strncpy|strlen|vsnprintf|sscanf|strtok|alloca|sprintf|printf|vsprintf)'
  </code></pre>
* Source/text search: `grep -R -E '_CC_MD5|_CC_SHA1|_rand|_malloc' <analysis-directory>`.
* Review hash purpose and security-sensitive randomness; unused/system-linked matches may be false positives.
* `malloc`/`memcpy`/`strlen`/`printf` are not inherently vulnerabilities. Check bounds, sizes, format strings, and allocation failures.
* Validate MobSF API findings. Parse Mach-O symbols/strings; text grep does not analyze binary code.
* Disassemble with: `otool -tV <app-binary>`
* For class metadata, see [Decryption and Class Information](../dynamic-testing/decryption-and-class-information.md).
