# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import threading
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from lib.shared import LogType, DebugLevel

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

class PausableThread(TimerThread):

	def __init__(self, parent, game_location):
		TimerThread.__init__(self)
		self.parent = parent
		self.game_location = game_location
		self.pause_event = threading.Event()
		self.pause_event.set()
		self.suspend = False

	def slow_down(self):
		time.sleep(0.1) # reduce thread speed

	def log(self, text, type=LogType.Normal):
		GObject.idle_add(self.parent.log, text, type)
		self.slow_down()

	def debug(self, text, level=DebugLevel.Normal):
		GObject.idle_add(self.parent.debug, text, level)
		self.slow_down()

	def reset(self):
		GObject.idle_add(self.parent.reset_buttons)

	def await(self):
		self.pause()
		GObject.idle_add(self.parent.set_buttons_to_paused)

	def pause(self):
		self.pause_timer()
		self.pause_event.clear()
		self.debug('Bot thread paused', DebugLevel.Low)

	def resume(self, game_location):
		self.game_location = game_location
		self.resume_timer()
		self.pause_event.set()
		self.debug('Bot thread resumed', DebugLevel.Low)

	def stop(self):
		self.stop_timer()
		self.suspend = True
		self.pause_event.set() # ensure that thread is resumed (if ever paused)
		#self.join() # wait for thread to exit
		self.debug('Bot thread stopped', DebugLevel.Low)
