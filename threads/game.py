# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from lib.shared import LogType, DebugLevel
from lib import data, tools, imgcompare, accounts
from .base import PausableThread

class GameThread(PausableThread):

	def __init__(self, parent, game_location):
		PausableThread.__init__(self, parent, game_location)

	def connect(self, account_id):
		# Login button detection
		self.debug('Detecting Login button')
		if self.wait_for_box_appear(box_name='Login Button', timeout=10):
			# get account
			account = accounts.get(account_id)
			if account:
				# slow down
				self.sleep(1)
				# (1) type login
				self.double_click(data.Locations['Login Input'])
				self.press_key(data.KeyboardShortcuts['Backspace']) # clean
				self.type_text(account['login'])
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
				# (2) type password
				self.double_click(data.Locations['Password Input'])
				self.press_key(data.KeyboardShortcuts['Backspace']) # clean
				self.type_text(account['pwd'])
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
				# (3) hit enter
				self.debug('Hit Play')
				self.press_key(data.KeyboardShortcuts['Enter'])
				# wait for Play button to appear
				self.debug('Waiting for Play button to appear')
				if self.wait_for_box_appear(box_name='Play Button'):
					# (4) hit enter again
					self.debug('Hit Play')
					self.press_key(data.KeyboardShortcuts['Enter'])
					# wait for load to start
					self.debug('Waiting for load to start')
					self.sleep(2)
					# check for pause or suspend
					self.pause_event.wait()
					if self.suspend: return
					# wait for screen to change
					self.wait_for_screen_change(load_time=5)
				elif not self.suspend:
					self.pause()
					self.log('Unable to connect to account', LogType.Error)
			else:
				self.pause()
				self.log('Account not found', LogType.Error)
		elif not self.suspend:
			self.pause()
			self.log('Login button detection failed', LogType.Error)

	def disconnect(self, exit=False):
		# (1) press 'Esc' key
		self.press_key(data.KeyboardShortcuts['Esc'])
		# wait for menu to show
		self.sleep(1)
		# check for pause or suspend
		self.pause_event.wait()
		if self.suspend: return
		# (2) click on disconnect/exit
		button = 'Exit Button' if exit == 'True' else 'Disconnect Button'
		self.click(data.Locations[button])
		# wait for confirmation to show
		self.sleep(1)
		# check for pause or suspend
		self.pause_event.wait()
		if self.suspend: return
		# (3) confirm disconnect/exit
		self.press_key(data.KeyboardShortcuts['Enter'])

	def wait_for_screen_change(self, timeout=30, tolerance=2.5, load_time=3):
		# wait for screen to change
		self.debug('Waiting for screen to change')
		if self.monitor_game_screen(timeout=timeout, tolerance=tolerance):
			# wait for screen to load
			self.debug('Waiting for screen to load (%d sec)' % load_time)
			self.sleep(load_time)

	def has_box_appeared(self, box_name, box_color=None):
		# set box color
		if box_color is None:
			if box_name in data.Colors:
				box_color = data.Colors[box_name]
			else:
				return False
		location = self.get_box_location(box_name)
		screen = tools.screen_game(location)
		percentage = tools.get_color_percentage(screen, box_color)
		has_appeared = percentage >= 70
		debug_level = DebugLevel.Normal if has_appeared else DebugLevel.High
		self.debug(f"{box_name} has appeared: {has_appeared}, percentage: {percentage}", debug_level)
		return has_appeared

	def wait_for_box_appear(self, box_name, box_color=None, timeout=30, sleep=1):
		# set box color
		if box_color is None:
			if box_name in data.Colors:
				box_color = data.Colors[box_name]
			else:
				return False
		# wait for box to appear
		elapsed_time = 0
		while elapsed_time < timeout:
			# wait 1 second
			self.sleep(sleep)
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return False
			# check box color
			location = self.get_box_location(box_name)
			screen = tools.screen_game(location)
			percentage = tools.get_color_percentage(screen, box_color)
			has_appeared = percentage >= 99
			debug_level = DebugLevel.Normal if has_appeared else DebugLevel.High
			self.debug('{} has appeared: {}, percentage: {}%, timeout: {}'.format(box_name, has_appeared, percentage, timeout), debug_level)
			if has_appeared:
				return True
			elapsed_time += 1
		# if box did not appear before timeout
		return False

	def get_box_location(self, box_name):
		if self.game_location:
			game_x, game_y, game_width, game_height = self.game_location
			box_window_width, box_window_height = data.Boxes[box_name]['windowSize']
			x, y = tools.adjust_click_position(data.Boxes[box_name]['x'], data.Boxes[box_name]['y'], box_window_width, box_window_height, game_x, game_y, game_width, game_height)
			width = data.Boxes[box_name]['width']
			height = data.Boxes[box_name]['height']
			return (x, y, width, height)
		else:
			return None

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

	def press_key(self, key):
		# press key
		self.debug('Press key: ' + key, DebugLevel.High)
		tools.press_key(key)

	def hot_click(self, key, coord, double=False):
		tools.key_down(key)
		self.click(coord, double)
		tools.key_up(key)

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

	def monitor_game_screen(self, timeout=10, tolerance=0.0, screen=None, location=None, wait_after_timeout=True):
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
			if wait_after_timeout and elapsed_time == timeout:
				self.pause()
				self.log('Game screen did not change', LogType.Error)

		return False

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
			self.pause()
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
