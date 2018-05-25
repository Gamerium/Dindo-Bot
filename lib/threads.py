# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import threading
import time
from .tools import read_file, internet_on
from .shared import LogType
from . import parser
from . import data

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

'''
	TimerThread is a quick implementation of thread class with a timer (not really powerful, but it do the job)
'''
class TimerThread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.start_time = 0
		self.elapsed_time = 0

	def start_timer(self):
		self.elapsed_time = 0
		self.start_time = time.time()

	def pause_timer(self):
		if self.start_time > 0: # if timer started
			self.elapsed_time += time.time() - self.start_time # save elapsed time
			self.start_time = 0 # pause timer

	def resume_timer(self):
		if self.start_time == 0: # if timer paused or even not started
			self.start_time = time.time() # restart timer

	def stop_timer(self):
		self.pause_timer()

	def get_elapsed_time(self):
		if self.start_time > 0: # if timer started
			self.elapsed_time += time.time() - self.start_time # save elapsed time
			self.start_time = time.time() # restart timer

		return time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time))

class BotThread(TimerThread):

	def __init__(self, bot_window):
		TimerThread.__init__(self)
		self.bot_window = bot_window
		self.pause_event = threading.Event()
		self.pause_event.set()
		self.suspend = False

	def run(self):
		self.start_timer()
		self.debug('Bot thread started')

		# get instructions & interpret them
		self.debug('Bot path: %s' % self.bot_window.bot_path)
		if self.bot_window.bot_path:
			instructions = read_file(self.bot_window.bot_path)
			self.interpret(instructions)

			# tell user that we have complete the path
			if not self.suspend:
				self.log('Bot path completed', LogType.Success)

		# reset bot window buttons
		self.reset()

		self.debug('Bot thread ended (elapsed time: %s)' % self.get_elapsed_time())

	def interpret(self, instructions):
		# split instructions
		lines = instructions.splitlines()

		for line in lines:
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: break

			# parse instruction
			self.debug('Instruction: ' + line)
			instruction = parser.parse_instruction(line)
			self.debug('Parse result: ' + str(instruction))

			# begin interpretation
			if instruction['name'] == 'Move':
				position = parser.parse_data(data.Movements, instruction['value'])
				print(str(position))

			elif instruction['name'] == 'Enclos':
				enclos_pos = parser.parse_data(data.Enclos, instruction['value'], ['x', 'y'])
				enclos_type = parser.parse_data(data.Enclos, instruction['value'], ['type'])
				print(str(enclos_pos) + ', type: ' + str(enclos_type))

			elif instruction['name'] == 'Zaap':
				zaap_from = parser.parse_data(data.Zaap['From'], instruction['from'])
				zaap_to = parser.parse_data(data.Zaap['To'], instruction['to'])
				print(str(zaap_from) + ' - ' + str(zaap_to))

			elif instruction['name'] == 'Zaapi':
				zaapi_from = parser.parse_data(data.Zaapi['From'], instruction['from'])
				zaapi_to = parser.parse_data(data.Zaapi['To'], instruction['to'])
				print(str(zaapi_from) + ' - ' + str(zaapi_to))

			else:
				self.debug('Unknown instruction')

			time.sleep(1)

	def log(self, text, type=LogType.Normal):
		GObject.idle_add(self.bot_window._log, text, type)

	def debug(self, text):
		GObject.idle_add(self.bot_window._debug, text)

	def reset(self):
		GObject.idle_add(self.bot_window.reset_buttons)

	def pause(self):
		self.pause_timer()
		self.pause_event.clear()
		self.debug('Bot thread paused')

	def resume(self):
		self.resume_timer()
		self.pause_event.set()
		self.debug('Bot thread resumed')

	def stop(self):
		self.stop_timer()
		self.suspend = True
		self.pause_event.set() # ensure that thread is resumed (if ever paused)
		self.join() # wait for thread to exit
		self.debug('Bot thread stopped')
