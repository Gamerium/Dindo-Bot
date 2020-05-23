# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from lib import data, tools, parser
from .fighting import FightingThread

class TravelThread(FightingThread):

	def __init__(self, parent, game_location):
		FightingThread.__init__(self, parent, game_location)

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
		'''
		Always use the havenbag to 'from' location and searches the destination
		by clicking in the search bar and typing the name of destination
		'''
		self.press_key(data.KeyboardShortcuts['Havenbag'])
		self.wait_for_map_change()
		# check for pause or suspend
		self.pause_event.wait()
		if self.suspend: return
		self.click(data.Zaap['ZaapItself'])
		self.sleep(3.0)
		self.click(data.Zaap['SearchBar'])
		self.sleep(1.0)
		for letter in zaap_to:
			if letter == " ":
				letter = "space"
			self.press_key(letter)
		self.sleep(3.0)
		screen = tools.screen_game(self.game_location)
		self.double_click(data.Zaap['FirstDestination'])
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
