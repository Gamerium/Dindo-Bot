# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gui.custom import MiniMap
from lib.shared import LogType, DebugLevel, GameVersion
from lib import maps, data, tools, parser
from .farming import FarmingThread

class JobThread(FarmingThread):

	def __init__(self, parent, game_location):
		FarmingThread.__init__(self, parent, game_location)
		self.podbar_enabled = parent.settings['State']['EnablePodBar']
		self.minimap_enabled = parent.settings['State']['EnableMiniMap']
		self.check_resources_color = parent.settings['Farming']['CheckResourcesColor']
		self.collection_time = parent.settings['Farming']['CollectionTime']
		self.first_resource_additional_collection_time = parent.settings['Farming']['FirstResourceAdditionalCollectionTime']
		self.game_version = parent.settings['Game']['Version']

	def collect(self, map_name, store_path):
		map_data = parser.parse_data(maps.load(), map_name)
		if map_data:
			# show resources on minimap
			self.update_minimap(map_data, 'Resource', MiniMap.point_colors['Resource'])
			# collect resources
			is_first_resource = True
			for resource in map_data:
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
				# check resource color
				if not self.check_resource_color(resource):
					# go to next resource
					continue
				# screen game
				screen = tools.screen_game(self.game_location)
				# click on resource
				self.debug("Collecting resource {'x': %d, 'y': %d, 'color': %s}" % (resource['x'], resource['y'], resource['color']))
				self.click(resource)
				if self.game_version == GameVersion.Retro:
					# re-click to validate
					self.click({'x': resource['x'] + 30, 'y': resource['y'] + 40, 'width': resource['width'], 'height': resource['height']})
				# wait before collecting next one
				if is_first_resource:
					is_first_resource = False
					self.sleep(self.first_resource_additional_collection_time) # wait more for 1st resource
				self.sleep(self.collection_time)
				# remove current resource from minimap (index = 0)
				self.remove_from_minimap(0)
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
				# check for screen change
				self.debug('Checking for screen change')
				if self.monitor_game_screen(tolerance=2.5, screen=screen, timeout=1, wait_after_timeout=False):
					# check for fight
					if self.game_version != GameVersion.Retro && self.wait_for_box_appear(box_name='Fight Button', timeout=1):
						self.wait()
						self.log('Fight detected! human help wanted..', LogType.Error)
					else:
						# it should be a popup (level up, ...)
						self.debug('Closing popup')
						screen = tools.screen_game(self.game_location)
						self.press_key(data.KeyboardShortcuts['Enter'] if self.game_version == GameVersion.Retro else data.KeyboardShortcuts['Esc'])
						# wait for popup to close
						self.monitor_game_screen(tolerance=2.5, screen=screen)
					# check for pause or suspend
					self.pause_event.wait()
					if self.suspend: return
				# get pod
				if self.game_version != GameVersion.Retro and self.get_pod() >= 99:
					# pod is full, go to store
					if store_path != 'None':
						self.go_to_store(store_path)
					else:
						self.wait()
						self.log('Bot is full pod', LogType.Error)

	def check_resource_color(self, resource):
		# check pixel color
		if self.check_resources_color:
			game_x, game_y, game_width, game_height = self.game_location
			x, y = tools.adjust_click_position(resource['x'], resource['y'], resource['width'], resource['height'], game_x, game_y, game_width, game_height)
			color = tools.get_pixel_color(x, y)
			resource['color'] = parser.parse_color(resource['color'])
			if resource['color'] is not None and not tools.color_matches(color, resource['color'], tolerance=10):
				self.debug("Ignoring non-matching resource {'x': %d, 'y': %d, 'color': %s} on pixel {'x': %d, 'y': %d, 'color': %s}" % (resource['x'], resource['y'], resource['color'], x, y, color))
				# remove current resource from minimap (index = 0)
				self.remove_from_minimap(0)
				return False

		return True

	def go_to_store(self, store_path):
		self.debug('Go to store (path: %s)' % store_path)
		if store_path in data.BankPath:
			instructions = data.BankPath[store_path]
		else:
			instructions = tools.read_file(tools.get_full_path(store_path))
		if instructions:
			self.interpret(instructions, ignore_start_from_step=True)
		else:
			self.wait()
			self.debug('Could not interpret store path')
			self.log('Bot is maybe full pod', LogType.Error)

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
			percentage = 0
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
