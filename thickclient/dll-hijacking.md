# DLL Hijacking

#### Information

* It is a library that contains executable code used by apps to perform some tasks
* Elevate our privileges if app are running in admin mode

<details>

<summary>DLL Load Order</summary>

1. The directory from which the application is loaded
2. The current directory
3. The system directory (C:WindowsSystem32)
4. The 16-bit system directory
5. The Windows directory.
6. The directories that are listed in the PATH environment variable.

</details>

#### Tools

* [DLLSpy](https://github.com/cyberark/DLLSpy)
* **Procmon** : Filters ->  `Process Name contains "Process Name"` -> `Path ends with ".DLL"` -> `Result is "NAME NOT FOUND"` \
  [Sysinternals Suite](https://learn.microsoft.com/en-us/sysinternals/downloads/sysinternals-suite)
* **MsfVenom** : `msfvenom -p windows/exec CMD="C:\windows\system32\calc.exe" -f dll -a x84 -o calc.dll`&#x20;





{% file src="../.gitbook/assets/DLL Files.zip" %}
