# coding:utf-8
import requests
import re
import time
import cmd
import copy

from pwn import *

class GameBox(object):

	def __init__(self, ip, port, pwn_func = None, flag_func= None, submit_func = None):
		self.ip = ip 
		self.port = port
		self.io = None
		self.connected = False
		self.reconnect_count = 2

		self.pwn_func = pwn_func
		self.flag_func = flag_func
		self.submit_func = submit_func

	def connect(self):
		try:
			assert self.ip, "ip not set."
			assert self.port , "port not set."
			assert self.pwn_func, "pwn function not set"

			self.io = remote(self.ip, self.port)
			self.pwn_func(self.io)

			while self.io.can_recv():
				self.io.recv()

			self.connected = True
			log.success('connected.')

		except Exception, e:
			log.failure(str(e))
			self.io = None
			self.connected = False

	def send_recv(self, buf):
		try:

			self.io.sendline(buf)
			time.sleep(0.1) # or io.can_recv() will return False.
			buf = ''
			while self.io.can_recv():
				buf += self.io.recv()

			return buf

		except Exception, e:
			log.failure(str(e))

	def get_flag(self):
		count = 0
		while count < self.reconnect_count:
			try:
				if not self.connected: 
					self.connect()
				if not self.connected: # this means host is down.
					break

				flag = self.flag_func(self.io)
				return flag

			except EOFError, e:
				count += 1
				log.info('EOF found. Repwning %d/%d ...' % (count, self.reconnect_count))
				self.connected = False  # this leads to reconnect
			except Exception, e:
				log.failure(str(e))
				break
		return None

	def submit_flag(self, flag= None):
		if flag is None:
			flag = self.get_flag()
		if flag is None:
			return False

		return self.submit_func(flag)

class BoxManager(cmd.Cmd):
	def __init__(self):
		cmd.Cmd.__init__(self)		
		self.prompt = 'CTFBox > '
		self.intro  = "CTF shell box for maintaining shells for gameboxs, harvest and submit flags automatically."

		self.boxs = []
		self.current_boxs = []

		self.loop_interval = 30

	def add_box(self, box):
		# try connecting when adding to box list.
		if not box.connected: box.connect()
		self.boxs.append(box)
		
		# default sync.
		self.current_boxs = copy.copy(self.boxs)

	def add(self, ip, port, pwn_func = None, flag_func= None, submit_func = None):
		box = GameBox(ip, port, pwn_func, flag_func, submit_func)
		self.add_box(box)

	def __parse_box(self, line):

		boxs = []
		try:
			if line == 'all':
				return self.boxs

			if line in ['None', 'clear', 'null']:
				return []

			# normal
			ids = line.split()
			for i in ids:
				try:
					boxs.append(self.boxs[int(i)])
				except Exception,e:
					log.failure('Unrecognized id %s: %s' % (i,e))
			
		except Exception, e:
			log.failure(str(e))

		return boxs

	def do_refresh(self, line):
		boxs = self.current_boxs
		if line:
			boxs = self.__parse_box(line)

		for box in boxs:
			if box.connected:
				box.io.close()
				box.io = None
			box.connect()

	def do_send(self, line):
		'''usage: send data [-- id1 id2 ..]\ndefault current session.'''
		try:
			data = line
			boxs_line = None

			if '--' in line:
				data, boxs_line= line.split('--')

			boxs = self.current_boxs
			if boxs_line:
				boxs = self.__parse_box(boxs_line)

			for box in boxs:
				print '%14s %7s' % (box.ip, box.port)
				print '-'*40
				buf = box.send_recv(data)
				print 'RECV:\n%s\n' % buf
				print '-'*40

		except Exception, e:
			log.failure(str(e))

	def do_shell(self, line):
		'''usage: shell id.'''
		try:
			box = self.boxs[int(line)]
			print 'Ctrl + D to exit'
			box.io.interactive()

		except Exception, e:
			log.failure('Invalid ID:'+ str(e))

	def do_flag(self, line):
		'''usage: flag [id1 id2 ..]\ndefault current session.'''
		boxs = self.current_boxs
		if line:
			boxs = self.__parse_box(line)

		count = 0
		for box in boxs:
			flag = box.get_flag()
			if flag is not None:
				log.success('%s %s' % (box.ip, flag))
				count +=1
		log.info('Flag count: %d' % count)

	def do_submit(self, line):
		'''usage: submit [id1 id2 ..]\ndefault current session.'''
		boxs = self.current_boxs
		if line:
			boxs = self.__parse_box(line)

		count = 0
		for box in boxs:
			flag = box.get_flag()
			if flag:
				r = box.submit_flag(flag)
				log.success('%s:%s %s %s' % (box.ip,box.port,flag, r))
				if r:
					count +=1
		log.info('Submit success count: %d' % count)

	def do_list(self, line):
		'''usage: list'''
		format_s = '%10s %5s %14s %7s %10s'
		print format_s %('SESS', 'ID', 'IP', 'PORT', 'CONNECTED')
		count = 0
		for i, box in enumerate(self.boxs):
			print format_s %((box in self.current_boxs), i, box.ip, box.port, box.connected)
			if box.connected: count += 1
		print '\t %s/%s connected.' % (count, len(self.boxs))

	# alias
	def do_ls(self, line):
		''' alias for list'''
		self.do_list(line)
	
	def do_session(self, line):
		'''usage: session [id1 id2 ..] | all'''
		# display sessions.
		if not line:
			print 'Current Session:'
			format_s = '%5s %10s %5s %10s'
			print format_s %('ID', 'IP','PORT','CONNECTED')
			for box in self.current_boxs:
				print format_s % (self.boxs.index(box), box.ip, box.port, box.connected)
			return

		boxs = self.__parse_box(line)
		for i in boxs:
			if i not in self.current_boxs:
				self.current_boxs.append(i)

	def do_unsession(self, line):
		'''usage: session [id1 id2 ..] | all '''
		boxs = self.__parse_box(line)
		for i in boxs:
			if i in self.current_boxs:
				self.current_boxs.remove(i)

	def do_python(self, code):
		'''usage: python [your python code]'''
		try:
			print repr(eval(code))
		except Exception, e:
			log.failure(str(e))

	def do_loop(self, line):
		'''usage: loop send | flag | submit [options]'''
		try:
			cmd, args, line = self.parseline(line)
			if cmd not in ['send', 'flag', 'submit']:
				log.failure('Can not loop %s' % line)
				return
			print 'Start loop.'
			while True:
				print '-'*4 + time.ctime() +'-'*4
				self.onecmd(line)
				time.sleep(self.loop_interval)
				
		except	KeyboardInterrupt,e:
			print '\nLoop END\n'

	def do_loop_interval(self, value):
		if not value:
			print 'Current interval: %s' % self.loop_interval
			return

		try:
			self.loop_interval = float(value)
		except Exception,e:
			log.failure('Invalid value:'+ str(e))


	def do_exit(self, line):
		return True

	def do_EOF(self, line):
		return True

	def start(self):
		try:
			self.cmdloop()
		except KeyboardInterrupt, e:
			log.info('CTFBox Exit')



