# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from lib import data
from .base import PausableThread

class GameThread(PausableThread):

	def __init__(self, parent, game_location):
		PausableThread.__init__(self, parent, game_location)

	def disconnect(self):
		# press 'Esc' key
		self.press_key(data.KeyboardShortcuts['Esc'])
		# wait for menu to show
		self.sleep(1)
		# check for pause or suspend
		self.pause_event.wait()
		if self.suspend: return
		# click on disconnect/exit
		self.click(data.Locations['Exit Button'])
		# wait for confirmation to show
		self.sleep(1)
		# check for pause or suspend
		self.pause_event.wait()
		if self.suspend: return
		# confirm disconnect
		self.click(data.Locations['Exit Confirm Button'])
