# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import sys
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, Gdk, GdkX11, Wnck
from datetime import datetime
from Xlib import display, X
from PIL import Image
from . import parser
import pyautogui
import time
import socket
import webbrowser

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
def internet_on(host='8.8.8.8', port=53, timeout=3):
	'''
	Host: 8.8.8.8 (google-public-dns-a.google.com)
	OpenPort: 53/tcp
	Service: domain (DNS/TCP)
	'''
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except Exception as ex:
		#print(ex.message)
		return False

# Return internet state as a string
def print_internet_state(state=None):
	if state is None:
		state = internet_on()
	return 'Internet is ' + ('on' if state else 'off')

# Take a screenshot of given window
def take_window_screenshot(window, save_to='screenshot'):
	# Linux X11
	if sys.platform.startswith('linux'):
		size = window.get_geometry()
		pb = Gdk.pixbuf_get_from_window(window, 0, 0, size.width, size.height)
		pb.savev(save_to + '.png', 'png', (), ())
	# Others
	else:
		x, y = window.get_position()
		region = window.get_geometry() # or window.get_allocation() ?
		screenshot = pyautogui.screenshot(region=(x, y, region.width, region.height))
		screenshot.save(save_to + '.png')

# Convert Gdk.Pixbuf to Pillow image
def pixbuf2image(pix):
	data = pix.get_pixels()
	width = pix.props.width
	height = pix.props.height
	stride = pix.props.rowstride
	mode = 'RGB'
	if pix.props.has_alpha == True:
		mode = 'RGBA'
	image = Image.frombytes(mode, (width, height), data, 'raw', mode, stride)
	return image

# Return a screenshot of the game
def screen_game(region, save_to=None):
	# Linux X11
	if sys.platform.startswith('linux'):
		dsp = display.Display()
		root = dsp.screen().root
		x, y, width, height = region
		raw = root.get_image(x, y, width, height, X.ZPixmap, 0xffffffff)
		if hasattr(Image, 'frombytes'):
			# for Pillow
			screenshot = Image.frombytes('RGB', (width, height), raw.data, 'raw', 'BGRX')
		else:
			# for PIL
			screenshot = Image.fromstring('RGB', (width, height), raw.data, 'raw', 'BGRX')
		if save_to is not None:
			screenshot.save(save_to + '.png')
		return screenshot
	# Others
	else:
		screenshot = pyautogui.screenshot(region=region)
		return screenshot

# Convert bytes to integer
def bytes_to_int(bytes):
	return int(bytes.encode('hex'), 16)

# Return pixel color of given x, y coordinates
def get_pixel_color(x, y):
	# Linux X11
	if sys.platform.startswith('linux'):
		window = Gdk.get_default_root_window()
		pb = Gdk.pixbuf_get_from_window(window, x, y, 1, 1)
		barray = pb.get_pixels()
		return '(%s, %s, %s)' % (bytes_to_int(barray[0]), bytes_to_int(barray[1]), bytes_to_int(barray[2]))
	# Others
	else:
		return pyautogui.pixel(x, y)

# Return date as a string in the given format
def get_date(format='%d-%m-%y'):
	return datetime.now().strftime(format)

# Return time as a string
def get_time():
	return get_date('%H:%M:%S')

# Return date & time as a string
def get_date_time():
	return get_date('%d-%m-%y_%H-%M-%S')

# Return timestamp
def get_timestamp(as_int=True):
	timestamp = time.mktime(datetime.now().timetuple())
	return int(timestamp) if as_int else timestamp

# Save text to file
def save_text_to_file(text, filename, mode='w'):
	file = open(filename, mode)
	file.write(text)
	file.close()

# Return file content
def read_file(filename):
	if os.path.isfile(filename):
		file = open(filename, 'r')
		content = file.read()
		file.close()
		return content
	else:
		return None

# Return platform name
def get_platform():
	return sys.platform

# Return command line arguments
def get_cmd_args():
	return sys.argv[1:]

# Return widget location
def get_widget_location(widget):
	# get widget allocation (relative to parent)
	allocation = widget.get_allocation()
	# get widget position (relative to root window)
	if type(widget) in (Gtk.DrawingArea, Gtk.EventBox, Gtk.Socket):
		pos = widget.get_window().get_origin()
		return (pos.x, pos.y, allocation.width, allocation.height)
	else:
		pos_x, pos_y = widget.get_window().get_root_coords(allocation.x, allocation.y)
		return (pos_x, pos_y, allocation.width, allocation.height)

# Check if position is inside given bounds
def position_is_inside_bounds(pos_x, pos_y, bounds_x, bounds_y, bounds_width, bounds_height):
	if pos_x > bounds_x and pos_x < (bounds_x + bounds_width) and pos_y > bounds_y and pos_y < (bounds_y + bounds_height):
		return True
	else:
		return False

# Fit position coordinates to given destination
def fit_position_to_destination(x, y, window_width, window_height, dest_width, dest_height):
	# new coordinate = old coordinate / (window size / destination size)
	new_x = x / (window_width / float(dest_width))
	new_y = y / (window_height / float(dest_height))

	return (int(new_x), int(new_y))

# Adjust click position
def adjust_click_position(click_x, click_y, window_width, window_height, dest_x, dest_y, dest_width, dest_height):
	# get screen size
	screen_width, screen_height = pyautogui.size()
	if screen_width > window_width and screen_height > window_height:
		# fit position to destination size
		new_x, new_y = fit_position_to_destination(click_x, click_y, window_width, window_height, dest_width, dest_height)
		#print('new_x: %s, new_y: %s, dest_x: %s, dest_y: %s' % (new_x, new_y, dest_x, dest_y))
		# scale to screen
		x = new_x + dest_x
		y = new_y + dest_y
	else:
		x = click_x
		y = click_y

	return (x, y)

# Perform a simple click or double click on x, y position
def perform_click(x, y, double=False):
	old_position = pyautogui.position()
	if double:
		pyautogui.doubleClick(x=x, y=y, interval=0.1)
	else:
		pyautogui.click(x=x, y=y)
	pyautogui.moveTo(old_position)

# Press key
def press_key(key):
	keys = parser.parse_key(key)
	count = len(keys)
	if count == 1:
		pyautogui.press(keys[0])
	elif count == 2:
		pyautogui.hotkey(keys[0], keys[1])

# Scroll to value
def scroll_to(value, x=None, y=None):
	pyautogui.scroll(value, x, y)

# Create directory(s) if not exist
def create_directory(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

# Check if color matches expected color
def color_matches(color, expected_color, tolerance=0):
	r, g, b = color
	red, green, blue = expected_color

	return (abs(r - red) <= tolerance) and (abs(g - green) <= tolerance) and (abs(b - blue) <= tolerance)

# Return the percentage of a color in an image
def get_color_percentage(image, expected_color, tolerance=10):
	# get image colors
	width, height = image.size
	image = image.convert('RGB')
	colors = image.getcolors(width * height)
	# check if the expected color exist
	expected_color_count = 0
	for count, color in colors:
		if color_matches(color, expected_color, tolerance):
			expected_color_count += count
	# convert to percentage
	if height == 0: height = 1
	if width == 0: width = 1
	percentage = ((expected_color_count / height) / float(width)) * 100

	return round(percentage, 2)

# Open given file in text editor
def open_file_in_editor(filename):
	# Linux
	if sys.platform.startswith('linux'):
		editor = os.getenv('EDITOR')
		if editor:
			os.system('%s %s' % (editor, filename))
		else:
			webbrowser.open(filename)
	# Others
	else:
		os.system(filename)
