# Reverse Engineering

#### Tools:

* [dotPeek](https://www.jetbrains.com/decompiler/) : .Net Decompiler, Covert exe -> cs files
* [dnSpy](https://github.com/dnSpy/dnSpy) : .Net Runtime-Tracing, Modify Source Code & Recompile
* [de4dot](https://github.com/de4dot/de4dot)
* [ILSpy](https://github.com/icsharpcode/ILSpy) & [Reflexil](https://github.com/sailro/Reflexil) - .Net Decompile & edit assembly code and save as new exe file (copy the dll file in reflexil to ilspy folder and launch) - view button -> reflexil (to view the assembly code and modify)
*  [Ilasm.exe (IL Assembler)](https://learn.microsoft.com/en-us/dotnet/framework/tools/ilasm-exe-il-assembler)  &#x20;& [Ildasm.exe (IL Disassembler)](https://learn.microsoft.com/en-us/dotnet/framework/tools/ildasm-exe-il-disassembler)\
  C:\Windows\Microsoft.NET\Framework\\\<version>
* [jd-gui](https://github.com/java-decompiler/jd-gui) - Java decompiler
  * Java Archive file (JAR) contents can be extracted by right-clicking on it and selecting `Extract files`.
  * Below command to be run after an modifications done such as removing the hashes taht are used for vaidation, etc
  * `jar -cmf .\META-INF\MANIFEST.MF ..\app.jar *`  <sup><sub>(ensure MANIFEST file ends with a new line)<sub></sup>
  * Delete the `1.RSA` and `1.SF` file
  * `javac -cp app.jar app.jar.src\htb\fatty\client\gui\ClientGuiTest.java`  <sup><sub>(Run after modifying the sourcecode.)<sub></sup>
* **Immunity Debugger**, [IDA Pro](https://hex-rays.com/ida-pro), [binary.ninja](https://binary.ninja/) - C/C++ decompiler\

* [decompiler-explorer](https://github.com/decompiler-explorer/decompiler-explorer) & [dogbolt.org](https://dogbolt.org/)
* [Ghidra](https://www.ghidra-sre.org/)
* [OllyDbg](http://www.ollydbg.de/)
* [Radare2](https://www.radare.org/r/index.html)
* [x64dbg](https://x64dbg.com/)
  * Navigate to `Options` -> `Preferences`, and uncheck everything except `Exit Breakpoint`&#x20;
  * By unchecking the other options, the debugging will start directly from the application's exit point, and we will avoid going through any `dll` files that are loaded before the app starts.
  * We can select `file` -> `open` and select the `app.exe` to import it and start the debugging.
  * Once imported, we right click inside the `CPU` view and `Follow in Memory Map`
* [JADX](https://github.com/skylot/jadx)[Frida](https://frida.re/)
* [Frida](https://frida.re/)

#### References

* [Immunity Debugger Basics - Binary Analysis](https://www.pentesting.org/binary-analysis-guide/)
