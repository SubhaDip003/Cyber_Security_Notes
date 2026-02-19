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
  tags:
    visible: true
---

# Privilege Escalation

## PrivEsc Checklists

[HackTricks ](https://book.hacktricks.xyz/)

* [Linux](https://book.hacktricks.wiki/en/linux-hardening/linux-privilege-escalation-checklist.html)
* [Windows](https://book.hacktricks.wiki/en/windows-hardening/checklist-windows-privilege-escalation.html)

[PayloadAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)

* [Linux](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md)
* [Windows](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Windows%20-%20Privilege%20Escalation.md)

***

## Automated Enumeration Scripts

#### Linux Enumeration Scripts:

* [LinEnum](https://github.com/rebootuser/LinEnum.git)
* [Linuxprivchecker](https://github.com/sleventyeleven/linuxprivchecker)
* [LinPEAS](https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS)

#### Windows Enumeration Scripts:

* [SeatBelt](https://github.com/GhostPack/Seatbelt)
* [JAWS](https://github.com/411Hall/JAWS)
* [WinPEAS](https://github.com/peass-ng/PEASS-ng/blob/master/winPEAS/winPEASexe/README.md)

#### Server Enumeration Scripts:

* [PEASS-ng](https://github.com/peass-ng/PEASS-ng)

***

## Scheduled Tasks

There are specific directories that we may be able to utilize to add new cron jobs if we have the write permissions over them. These include:

1. /etc/crontab
2. /etc/cron.d
3. /var/spool/cron/crontabs/root

***

## Exposed Credentials

_User Command History Files:_

* Linux -> `bash_history`
* Windows:
* `PSReadLine` -> PSReadLine is a PowerShell module that provides command-line editing, syntax highlighting, and persistent command history. (`ConsoleHost_history.txt`)
* `Get-History` -> `Get-History` is a built-in PowerShell cmdlet that shows commands executed in the current PowerShell session only.

#### PSReadLine

PSReadLine is a PowerShell module that provides command-line editing, syntax highlighting, and persistent command history. By default, it saves command history in a file called: ConsoleHost\_history.txt

Default Location of PSReadLine History File

```
C:\Users\<Username>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

#### View PSReadLine History

**Method 1: View PSReadLine History Using PowerShell**

```powershell
notepad $env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

Get-Content $env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

**Method 2: View from File Explorer**

1. Press `Win + R`
2. Type:

```
%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\
```

3. Press Enter
4. Open ConsoleHost\_history.txt

&#x20;

**Method 3: Check Current PSReadLine Configuration**

```powershell
Get-PSReadLineOption
```

#### Deleting PSReadLine history

```powershell
Remove-Item (Get-PSReadLineOption).HistorySavePath
```

***

## SSH Keys

If we have read access over the .ssh directory for a specific user, we may read their private ssh keys found in /home/user/.ssh/id\_rsa or /root/.ssh/id\_rsa, and use it to log in to the server.

```bash
$ vim id_rsa
$ chmod 600 id_rsa
$ ssh root@10.10.10.10 -i id_rsa
root@10.10.10.10#
```

If we find ourselves with write access to a users/.ssh/ directory, we can place our public key in the user's ssh directory at /home/user/.ssh/authorized\_keys. This technique is usually used to gain ssh access after gaining a shell as that user. The current SSH configuration will not accept keys written by other users, so it will only work if we have already gained control over that user. We must first create a new key with ssh-keygen and the -f flag to specify the output file:

```bash
$ ssh-keygen -f key
Generating public/private rsa key pair.
Enter passphrase (empty for no passphrase): *******
Enter same passphrase again: *******
Your identification has been saved in key
Your public key has been saved in key.pub
The key fingerprint is:
SHA256:...SNIP... user@parrot
The key's randomart image is:
+---[RSA 3072]----+
|   ..o.++.+      |
...SNIP...
|     . ..oo+.    |
+----[SHA256]-----+
```

This will give us two files: key (which we will use with ssh -i) and key.pub, which we will copy to the remote machine. Let us copy key.pub, then on the remote machine, we will add it into /root/.ssh/authorized\_keys:

```bash
$ echo "ssh-rsa AAAAB...SNIP...M= user@parrot" >> /root/.ssh/authorized_keys
```

&#x20;Now, the remote server should allow us to log in as that user by using our private key:

```bash
$ ssh root@10.10.10.10 -i key
root@remotehost#
```
