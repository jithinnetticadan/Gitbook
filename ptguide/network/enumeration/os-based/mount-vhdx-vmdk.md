# Mount VHDX/VMDK

{% hint style="info" %}
Three specific file types of interest are `.vhd`, `.vhdx`, and `.vmdk` files. These are `Virtual Hard Disk`, `Virtual Hard Disk v2` (both used by Hyper-V), and `Virtual Machine Disk` (used by VMware).&#x20;
{% endhint %}

### Mount VMDK on Linux

* `guestmount -a file.vmdk -i --ro /mnt/vmdk`
* In windows,for a `.vmdk` file, we can right-click and choose `Map Virtual Disk` from the menu. Next, we will be prompted to select a drive letter.
* If this fails, we can use VMWare Workstation `File --> Map Virtual Disks` to map the disk onto our base system. We could also add the `.vmdk` file onto our attack VM as an additional virtual hard drive, then access it as a lettered drive.
* We can even use `7-Zip` to extract data from a .`vmdk` file. This [guide](https://www.nakivo.com/blog/extract-content-vmdk-files-step-step-guide/) illustrates many methods for gaining access to the files on a `.vmdk` file.

### Mount VHD/VHDX on Linux

* `guestmount --add file.vhdx --ro /mnt/vhdx/ -m /dev/sda1`
* In Windows, we can right-click on the file and choose `Mount`, or use the `Disk Management` utility to mount a `.vhd` or `.vhdx` file. If preferred, we can use the [Mount-VHD](https://docs.microsoft.com/en-us/powershell/module/hyper-v/mount-vhd?view=windowsserver2019-ps) PowerShell cmdlet.

### Retrieving Hashes

* If we can locate a backup of a live machine, we can access the `C:\Windows\System32\Config` directory and pull down the `SAM`, `SECURITY` and `SYSTEM` registry hives.
* [#sebackup-serestore](../../exploitation/privilege-escalation/windows.md#sebackup-serestore "mention")
