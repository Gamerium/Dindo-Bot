# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from lib.shared import LogType, DebugLevel
from lib import data
from lib import tools
from lib import parser
from lib import imgcompare
from .game import GameThread

class TravelThread(GameThread):

	def __init__(self, parent, game_location):
		GameThread.__init__(self, parent, game_location)

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

	def move(self, direction):
		# get coordinates
		coordinates = parser.parse_data(data.Movements, direction)
		if coordinates:
			# click
			self.click(coordinates)
			# wait for map to change
			self.wait_for_map_change()

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

	def wait_for_map_change(self, timeout=30, tolerance=2.5, screen=None):
		# wait for map to change
		self.debug('Waiting for map to change')
		if self.monitor_game_screen(timeout=timeout, tolerance=tolerance, screen=screen):
			# wait for map to load
			self.debug('Waiting for map to load')
			self.sleep(3)

	def use_zaap(self, zaap_from, zaap_to):
		# get coordinates
		zaap_from_coordinates = parser.parse_data(data.Zaap['From'], zaap_from)
		zaap_to_coordinates = parser.parse_data(data.Zaap['To'], zaap_to)
		if zaap_from_coordinates and zaap_to_coordinates:
			# if a keyboard shortcut is set (like for Havenbag)
			if 'keyboard_shortcut' in zaap_from_coordinates:
				# press key
				self.press_key(zaap_from_coordinates['keyboard_shortcut'])
				# wait for map to change
				self.wait_for_map_change()
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
			# click on zaap from
			screen = tools.screen_game(self.game_location)
			self.click(zaap_from_coordinates)
			# wait for zaap list to show
			self.debug('Waiting for zaap list to show')
			self.monitor_game_screen(tolerance=2.5, screen=screen)
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# if we need to scroll zaap list
			if 'scroll' in zaap_to_coordinates:
				# scroll
				self.scroll(zaap_to_coordinates['scroll'])
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
			# double click on zaap to
			screen = tools.screen_game(self.game_location)
			self.double_click(zaap_to_coordinates)
			# wait for map to change
			self.wait_for_map_change(screen=screen)

	def use_zaapi(self, zaapi_from, zaapi_to):
		# get coordinates
		zaapi_from_coordinates = parser.parse_data(data.Zaapi['From'], zaapi_from)
		zaapi_to_coordinates = parser.parse_data(data.Zaapi['To'], zaapi_to)
		if zaapi_from_coordinates and zaapi_to_coordinates:
			# click on zaapi from
			screen = tools.screen_game(self.game_location)
			self.click(zaapi_from_coordinates)
			# wait for zaapi list to show
			self.debug('Waiting for zaapi list to show')
			self.monitor_game_screen(tolerance=2.5, screen=screen)
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# choose tab/location from zaapi list
			self.click(zaapi_to_coordinates['location'])
			self.sleep(2)
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# if we need to scroll zaapi list
			if 'scroll' in zaapi_to_coordinates:
				# scroll
				self.scroll(zaapi_to_coordinates['scroll'])
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
			# double click on zaapi to
			screen = tools.screen_game(self.game_location)
			self.double_click(zaapi_to_coordinates)
			# wait for map to change
			self.wait_for_map_change(screen=screen)

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
