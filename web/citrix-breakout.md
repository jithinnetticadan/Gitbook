# Citrix Breakout

{% hint style="info" %}
Basic Methodology for break-out:

1. Gain access to a `Dialog Box`.
2. Exploit the Dialog Box to achieve `command execution`.
3. `Escalate privileges` to gain higher levels of access.
{% endhint %}

## Bypassing Path Restrictions <a href="#bypassing-path-restrictions" id="bypassing-path-restrictions"></a>

* When we attempt to visit `C:\Users` using File Explorer, we find it is restricted and results in an error. This indicates that group policy has been implemented to restrict users from browsing directories in the `C:\` drive using File Explorer.
* It is possible to utilize windows dialog boxes as a means to bypass the restrictions imposed by group policy. Once a Windows dialog box is obtained, the next step often involves navigating to a folder path containing native executables that offer interactive console access (i.e.: cmd.exe).
* Features like Save, Save As, Open, Load, Browse, Import, Export, Help, Search, Scan, and Printon numerous desktop applications usually provide an attacker with an opportunity to invoke a Windows dialog box. There are multiple ways to open dialog box in windows using tools such as Paint, Notepad, Wordpad, etc.
* `MS Paint` as an example
  * Run `Paint` from start menu and click on `File > Open` to open the Dialog Box.
  * With the windows dialog box open for paint, we can enter the [UNC](https://learn.microsoft.com/en-us/dotnet/standard/io/file-path-formats#unc-paths) path `\\127.0.0.1\c$\users\<username>` under the File name field, with File-Type set to `All Files` and upon hitting enter we gain access to the desired directory.
* Accessing SMB share using above technique. <sup><sub>(<sub></sup><sup><sub>`\\10.13.38.95\share`<sub></sup><sup><sub>)<sub></sup>

### Alternate Explorer <a href="#alternate-explorer" id="alternate-explorer"></a>

* [Explorer++](https://explorerplusplus.com/)
* In cases where strict restrictions are imposed on File Explorer, alternative File System Editors like `Q-Dir` or `Explorer++` can be employed as a workaround.

### Alternate Registry Editors <a href="#alternate-registry-editors" id="alternate-registry-editors"></a>

* [Simpleregedit](https://sourceforge.net/projects/simpregedit/), [Uberregedit](https://sourceforge.net/projects/uberregedit/) and [SmallRegistryEditor](https://sourceforge.net/projects/sre/) are examples of such GUI tools that facilitate editing the Windows registry without being affected by the blocking imposed by group policy.

### Modify existing shortcut file <a href="#modify-existing-shortcut-file" id="modify-existing-shortcut-file"></a>

* Unauthorized access to folder paths can also be achieved by modifying existing Windows shortcuts and setting a desired executable's path in the `Target` field.
* The following steps outline the process:
  1. `Right-click` the desired shortcut.
  2. Select `Properties`
  3. Within the `Target` field, modify the path to the intended folder for access.
  4. Execute the Shortcut and cmd will be spawned.
* In cases where an existing shortcut file is unavailable, transfer an existing shortcut file using an SMB server or we can create a new shortcut file using PowerShell Malicious .lnk File

### Script Execution <a href="#script-execution" id="script-execution"></a>

* When script extensions such as `.bat`, `.vbs`, or `.ps` are configured to automatically execute their code using their respective interpreters, it opens the possibility of dropping a script that can serve as an interactive console or facilitate the download and launch of various third-party applications which results into bypass of restrictions in place

1. Create a new text file and name it "evil.bat".
2. Open "evil.bat" with a text editor such as Notepad.
3. Input the command "cmd" into the file
4. Save the file.

### Bypassing UAC <a href="#bypassing-uac" id="bypassing-uac"></a>

* [#uac-bypass](../network/exploitation/privilege-escalation/windows.md#uac-bypass "mention")

## Resources

* [Breaking out of Citrix and other Restricted Desktop environments](https://www.pentestpartners.com/security-blog/breaking-out-of-citrix-and-other-restricted-desktop-environments/)
* [Breaking out of Windows Environments](https://node-security.com/posts/breaking-out-of-windows-environments/)
