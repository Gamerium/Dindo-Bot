# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import sys
import os
import gi
gi.require_version('Wnck', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Wnck, Gtk, Gdk, GdkX11
from datetime import datetime
import pyautogui

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
		windows = pyautogui.getWindows()
		for window_name in windows:
			if 'Dofus' in window_name: # TODO: check process/instance name instead of window name
				game_window_list[window_name] = windows[window_name]

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
		hwnd = window_xid
		game_window = pyautogui.Window(hwnd)

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
	# Others
	else:
		x, y = window.get_position()
		region = window.get_geometry() # or window.get_allocation() ?
		screenshot = pyautogui.screenshot(region=(x, y, region.width, region.height))
		screenshot.save(save_to + '.png')

# Return pixel color of given x, y coordinates
def get_pixel_color(x, y):
	# Linux X11
	if sys.platform.startswith('linux'):
		window = Gdk.get_default_root_window()
		pb = Gdk.pixbuf_get_from_window(window, x, y, 1, 1)
		return tuple(pb.get_pixels()) # value returned isn't numeric RGB, maybe a GTK3 bug?
	# Others
	else:
		return pyautogui.pixel(x, y)

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

# Return platform name
def get_platform():
	return sys.platform

# Return command line arguments
def get_cmd_args():
	return sys.argv[1:]

# Return widget absolute position
def get_widget_absolute_position(widget):
	# get widget position (relative to root window)
	if type(widget) in (Gtk.DrawingArea, Gtk.EventBox, Gtk.Socket):
		pos = widget.get_window().get_origin()
		return (pos.x, pos.y)
	else:
		pos = widget.get_allocation()
		abs_x, abs_y = widget.get_window().get_root_coords(pos.x, pos.y)
		return (abs_x, abs_y)

# Check if point is inside given bounds
def point_is_inside_bounds(point_x, point_y, bound_x, bound_y, bound_width, bound_height):
	if point_x > bound_x and point_x < (bound_x + bound_width) and point_y > bound_y and point_y < (bound_y + bound_height):
		return True
	else:
		return False

# Fit point coordinates to given size
def fit_point_to_size(x, y, width, height, new_width, new_height):
	if width > new_width and height > new_height:
		new_x = x / (width / float(new_width))
		new_y = y / (height / float(new_height))
	else:
		new_x = x * (width / float(new_width))
		new_y = y * (height / float(new_height))

	return (int(new_x), int(new_y))
