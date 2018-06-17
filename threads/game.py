# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from lib.shared import LogType, DebugLevel
from lib import data
from lib import tools
from lib import imgcompare
from .base import PausableThread

class GameThread(PausableThread):

	def __init__(self, parent, game_location):
		PausableThread.__init__(self, parent, game_location)

	def disconnect(self, exit):
		# press 'Esc' key
		self.press_key(data.KeyboardShortcuts['Esc'])
		# wait for menu to show
		self.sleep(1)
		# check for pause or suspend
		self.pause_event.wait()
		if self.suspend: return
		# click on disconnect/exit
		button = 'Exit Button' if exit == 'True' else 'Disconnect Button'
		self.click(data.Locations[button])
		# wait for confirmation to show
		self.sleep(1)
		# check for pause or suspend
		self.pause_event.wait()
		if self.suspend: return
		# confirm disconnect/exit
		self.press_key(data.KeyboardShortcuts['Enter'])

	def click(self, coord, double=False):
		# adjust coordinates
		if self.game_location:
			game_x, game_y, game_width, game_height = self.game_location
			#print('game_x: %d, game_y: %d, game_width: %d, game_height: %d' % (game_x, game_y, game_width, game_height))
			x, y = tools.adjust_click_position(coord['x'], coord['y'], coord['width'], coord['height'], game_x, game_y, game_width, game_height)
		else:
			x, y = (coord['x'], coord['y'])
		# click
		self.debug('Click on x: %d, y: %d, double: %s' % (x, y, double), DebugLevel.High)
		tools.perform_click(x, y, double)

	def double_click(self, coord):
		self.click(coord, True)

	def press_key(self, key):
		# press key
		self.debug('Press key: ' + key, DebugLevel.High)
		tools.press_key(key)

	def type_text(self, text):
		# type text
		self.debug('Type text: ' + text, DebugLevel.High)
		tools.type_text(text)

	def scroll(self, value):
		self.debug('Scroll to: %d' % value, DebugLevel.High)
		# save mouse position
		mouse_position = tools.get_mouse_position()
		if self.game_location:
			# get game center
			x, y = tools.coordinates_center(self.game_location)
			self.sleep(1)
		else:
			x, y = (None, None)
		# scroll
		tools.scroll_to(value, x, y)
		# wait for scroll to end
		self.sleep(1)
		# get back mouse to initial position
		tools.move_mouse_to(mouse_position)

	def monitor_game_screen(self, timeout=10, tolerance=0.0, screen=None, location=None, await_after_timeout=True):
		if self.game_location or location:
			# screen game
			if location is None:
				location = self.game_location
			if screen is None:
				prev_screen = tools.screen_game(location)
			else:
				prev_screen = screen
			elapsed_time = 0
			# wait for game screen to change
			while elapsed_time < timeout:
				# wait 1 second
				self.sleep(1)
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return False
				# take a new screen & compare it with the previous one
				new_screen = tools.screen_game(location)
				if new_screen.size != prev_screen.size:
					self.debug('Screen size has changed, retry', DebugLevel.High)
				else:
					diff_percent = round(imgcompare.image_diff_percent(prev_screen, new_screen), 2)
					has_changed = diff_percent > tolerance
					debug_level = DebugLevel.Normal if has_changed else DebugLevel.High
					self.debug('Game screen has changed: {}, diff: {}%, tolerance: {}, timeout: {}'.format(has_changed, diff_percent, tolerance, timeout), debug_level)
					if has_changed:
						return True
				prev_screen = new_screen
				elapsed_time += 1
			# if game screen hasn't change before timeout
			if await_after_timeout and elapsed_time == timeout:
				self.await()
				self.log('Game screen don\'t change', LogType.Error)

		return False

	def monitor_internet_state(self, timeout=30):
		elapsed_time = 0
		reported = False
		while elapsed_time < timeout:
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# get internet state
			state = tools.internet_on()
			if state:
				if reported:
					GObject.idle_add(self.parent.set_internet_state, state)
				return
			else:
				# print state
				self.debug(tools.print_internet_state(state), DebugLevel.High)
				if not reported:
					GObject.idle_add(self.parent.set_internet_state, state)
					reported = True
				# wait 1 second, before recheck
				time.sleep(1)
				elapsed_time += 1
		# if timeout reached
		if elapsed_time == timeout:
			self.await()
			self.log('Unable to connect to the internet', LogType.Error)

	def sleep(self, duration=1):
		elapsed_time = 0
		while elapsed_time < duration:
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# sleep
			time.sleep(1)
			# check internet state before continue
			self.monitor_internet_state()
			elapsed_time += 1
