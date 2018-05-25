# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import sys
import os
import gi
gi.require_version('Wnck', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Wnck, Gdk, GdkX11
from datetime import datetime

try:
	# For Python 3.0 and later
	import urllib.request as urllib2
except ImportError:
	# Fall back to Python 2's urllib2
	import urllib2

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
			#print('[' + instance_name + '] ' + window_name)
			if instance_name == 'Dofus':
				game_window_list[window_name] = window.get_xid()
	# Win32
	elif sys.platform == 'win32':
		print('Not implemented')
		# ToDo: add implementation using windows API library

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
		# ToDo: add implementation using windows API library

	return game_window

# Return absolute path to resource
def get_resource_path(rel_path):
    dir_of_py_file = os.path.dirname(__file__)
    rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
    abs_path_to_resource = os.path.abspath(rel_path_to_resource)
    return abs_path_to_resource

# Return internet state
def internet_on():
	try:
		urllib2.urlopen('http://www.google.com', timeout=2)
		return True
	except urllib2.URLError as err: 
		return False

# Take a screenshot of given window
def take_window_screenshot(window, save_to='screenshot'):
	# Linux X11
	if sys.platform.startswith('linux'):
		#window.show()
		size = window.get_geometry()
		pb = Gdk.pixbuf_get_from_window(window, 0, 0, size.width, size.height)
		pb.savev(save_to + '.png', 'png', (), ())
	# Win32
	elif sys.platform == 'win32':
		print('Not implemented')
		# ToDo: add implementation using windows API library (@see also PIL module)

# Return pixel color of given window & pixel
def get_window_pixel_color(window, x, y):
	# Linux X11
	if sys.platform.startswith('linux'):
		#window.show()
		pb = Gdk.pixbuf_get_from_window(window, x, y, 1, 1)
		return pb.get_pixels()
	# Win32
	elif sys.platform == 'win32':
		print('Not implemented')
		# ToDo: add implementation using windows API library

# Return date as a string
def get_date():
	return datetime.now().strftime('%d-%m-%y')

# Return time as a string
def get_time():
	return datetime.now().strftime('%H:%M:%S')

# Return date & time as a string
def get_date_time():
	return datetime.now().strftime('%d-%m-%y_%H-%M-%S')

# Save text to file
def save_text_to_file(text, filename, mode='w'):
	file = open(filename, mode)
	file.write(text)
	file.close()

# Return file content
def read_file(filename):
	file = open(filename, 'r')
	content = file.read()
	file.close()

	return content
