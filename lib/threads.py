# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import threading
import time

class BotThread(threading.Thread):

	def __init__(self, bot_window):
		threading.Thread.__init__(self)
		self.bot_window = bot_window
		self._event = threading.Event()
		self._suspend = False

	def run(self):
		self.resume(True) # ensure that thread is resumed
		self.bot_window._debug('Bot thread started')

		while True:
			# check for pause or suspend
			self._wait_if_paused()
			if self._suspend: break
			# do the job
			print('test')
			time.sleep(1)

	def pause(self):
		self._event.clear()
		self.bot_window._debug('Bot thread paused')

	def resume(self, silent=False):
		self._event.set()
		if not silent:
			self.bot_window._debug('Bot thread resumed')

	def stop(self):
		self._suspend = True
		self.resume(True) # ensure that thread is resumed
		self.join() # wait for the thread to exit
		self.bot_window._debug('Bot thread stopped')

	def _wait_if_paused(self):
		self._event.wait()
