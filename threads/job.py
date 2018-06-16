# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gui.custom import MiniMap
from .farming import FarmingThread

class JobThread(FarmingThread):

	def __init__(self, parent, game_location):
		FarmingThread.__init__(self, parent, game_location)
		self.minimap_enabled = parent.settings['EnableMiniMap']

	def update_minimap(self, points, points_name=None, points_color=None):
		if self.minimap_enabled:
			self.debug('Update MiniMap')
			# clear minimap
			GObject.idle_add(self.parent.minimap.clear)
			# update minimap
			GObject.idle_add(self.parent.minimap.add_points, points, points_name, points_color)
