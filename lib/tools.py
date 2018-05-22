# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import sys
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Wnck, GdkX11

# Return active game window(s) list
def get_game_window_list():
	game_window_list = {}

	# Linux X11
	if sys.platform.startswith('linux'):
		screen = Wnck.Screen.get_default()
		screen.force_update() # recommended per Wnck documentation
		window_list = screen.get_windows()

		for window in window_list:
			window_name = window.get_name()
			instance_name = window.get_class_instance_name()
			#print(window_name + ', ' + instance_name)
			if instance_name == 'Dofus':
				game_window_list[window_name] = window.get_xid()
	# Win32
	elif sys.platform == 'win32':
		print('Not implemented')
		# ToDo: add implementation for windows using windows API library

	return game_window_list

# Return game window
def get_game_window(window_xid):
	game_window = None

	# Linux X11
	if sys.platform.startswith('linux'):
		gdk_display = GdkX11.X11Display.get_default()
		game_window = GdkX11.X11Window.foreign_new_for_display(gdk_display, window_xid)
	# Win32
	elif sys.platform == 'win32':
		print('Not implemented')
		# ToDo: add implementation for windows using windows API library

	return game_window

# Return absolute path to resource
def get_resource_path(rel_path):
    dir_of_py_file = os.path.dirname(__file__)
    rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
    abs_path_to_resource = os.path.abspath(rel_path_to_resource)
    return abs_path_to_resource
