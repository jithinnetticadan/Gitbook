# Hardcoded Credentials

## [Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon)

* Monitor the process to observe teh actions taken by the application.
* If the executable creates a temp file and deletes after execution.
* In order to capture these files, it is required to change the permissions of the `Temp` or the folder where its created folder to disallow file deletions. To do this, we right-click the folder
  * `Properties` -> `Security` -> `Advanced` -> `username` -> `Disable inheritance` -> `Convert inherited permissions into explicit permissions on this object` -> `Edit` -> `Show advanced permissions`, we deselect the `Delete subfolders and files`, and `Delete` checkboxes.
  * Click `OK` -> `Apply` -> `OK` -> `OK` on the open windows.
* View the contents of the file that was created.
