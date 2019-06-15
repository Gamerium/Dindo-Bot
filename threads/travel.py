# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from lib import data, tools, parser
from .game import GameThread

class TravelThread(GameThread):

	def __init__(self, parent, game_location):
		GameThread.__init__(self, parent, game_location)

	def move(self, direction):
		# get coordinates
		coordinates = parser.parse_data(data.Movements, direction)
		if coordinates:
			# click
			self.click(coordinates)
			# wait for map to change
			self.wait_for_map_change()

	def wait_for_map_change(self, timeout=30, tolerance=2.5, screen=None, load_time=3):
		# wait for map to change
		self.debug('Waiting for map to change')
		if self.monitor_game_screen(timeout=timeout, tolerance=tolerance, screen=screen):
			# wait for map to load
			self.debug('Waiting for map to load (%d sec)' % load_time)
			self.sleep(load_time)

	def use_zaap(self, zaap_from, zaap_to):
		# get coordinates
		zaap_from_coordinates = parser.parse_data(data.Zaap['From'], zaap_from)
		zaap_to_coordinates = parser.parse_data(data.Zaap['To'], zaap_to)
		if zaap_from_coordinates and zaap_to_coordinates:
			# if a keyboard shortcut is set (like for Havenbag)
			if 'keyboardShortcut' in zaap_from_coordinates:
				# press key
				self.press_key(zaap_from_coordinates['keyboardShortcut'])
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
