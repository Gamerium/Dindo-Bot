# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gui.custom import MiniMap
from lib.shared import LogType, DebugLevel
from lib import maps, data, tools, parser
from .farming import FarmingThread

class JobThread(FarmingThread):

	def __init__(self, parent, game_location):
		FarmingThread.__init__(self, parent, game_location)
		self.podbar_enabled = parent.settings['Job']['EnablePodBar']
		self.minimap_enabled = parent.settings['Job']['EnableMiniMap']

	def collect(self, map_name, store_path):
		map_data = parser.parse_data(maps.load(), map_name)
		if map_data:
			# show resources on minimap
			self.update_minimap(map_data, 'Resource', MiniMap.point_colors['Resource'])
			# collect resources
			for i, resource in enumerate(map_data):
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
				# TODO: check pixel color
				# click on resource
				self.debug("Collecting resource {'x': %d, 'y': %d, 'color': %s}" % (resource['x'], resource['y'], resource['color']))
				self.click(resource)
				# wait before collecting next one
				if i == 0:
					self.sleep(5) # wait 5 more seconds for 1st resource
				self.sleep(4)
				# remove current resource from minimap (index = 0)
				self.remove_from_minimap(0)
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
				# TODO: check for level up
				# TODO: check for fight
				# get pod
				if self.get_pod() >= 99:
					# pod is full, go to store
					if store_path != 'None':
						# TODO: implement go_to_store function
						print('go to store')
					else:
						self.wait()
						self.log('Bot is full pod', LogType.Error)

	def get_pod(self):
		# open inventory
		self.debug('Opening inventory')
		screen = tools.screen_game(self.game_location)
		self.press_key(data.KeyboardShortcuts['Inventory'])
		# wait for inventory to open
		self.monitor_game_screen(tolerance=2.5, screen=screen)
		# check for pause or suspend
		self.pause_event.wait()
		if self.suspend: return
		# get podbar color & percentage
		location = self.get_box_location('PodBar')
		screen = tools.screen_game(location)
		color, percentage = tools.get_dominant_color(screen)
		# close inventory
		self.debug('Closing inventory')
		screen = tools.screen_game(self.game_location)
		self.press_key(data.KeyboardShortcuts['Inventory'])
		# wait for inventory to close
		self.monitor_game_screen(tolerance=2.5, screen=screen)
		# check for pause or suspend
		self.pause_event.wait()
		if self.suspend: return
		# check if podbar is empty
		if tools.color_matches(color, data.Colors['Empty PodBar'], tolerance=10):
			return 0
		else:
			# update pod bar
			self.set_pod(percentage)
			return percentage

	def set_pod(self, percentage):
		if self.podbar_enabled:
			self.debug('Update PodBar (percentage: {}%)'.format(percentage))
			# set podbar value
			GObject.idle_add(self.parent.podbar.set_fraction, percentage / 100.0)

	def update_minimap(self, points, points_name=None, points_color=None):
		if self.minimap_enabled:
			self.debug('Update MiniMap')
			# clear minimap
			GObject.idle_add(self.parent.minimap.clear)
			# update minimap
			GObject.idle_add(self.parent.minimap.add_points, points, points_name, points_color)

	def remove_from_minimap(self, index):
		if self.minimap_enabled:
			self.debug('Remove point from MiniMap (index: %d)' % index)
			GObject.idle_add(self.parent.minimap.remove_point, index)
