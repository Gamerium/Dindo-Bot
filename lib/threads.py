# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import threading
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from .shared import LogType
from . import tools
from . import parser
from . import data
from . import imgcompare
import pyautogui

'''
	TimerThread is a quick implementation of thread class with a timer (not really powerful, but it do the job)
'''
class TimerThread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.start_time = 0
		self.elapsed_time = 0

	def start_timer(self):
		self.elapsed_time = 0
		self.start_time = time.time()

	def pause_timer(self):
		if self.start_time > 0: # if timer started
			self.elapsed_time += time.time() - self.start_time # save elapsed time
			self.start_time = 0 # pause timer

	def resume_timer(self):
		if self.start_time == 0: # if timer paused or even not started
			self.start_time = time.time() # restart timer

	def stop_timer(self):
		self.pause_timer()

	def get_elapsed_time(self):
		if self.start_time > 0: # if timer started
			self.elapsed_time += time.time() - self.start_time # save elapsed time
			self.start_time = time.time() # restart timer

		return time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time))

class BotThread(TimerThread):

	def __init__(self, parent, game_geometry):
		TimerThread.__init__(self)
		self.parent = parent
		self.game_geometry = game_geometry
		self.pause_event = threading.Event()
		self.pause_event.set()
		self.suspend = False

	def run(self):
		self.start_timer()
		self.debug('Bot thread started')

		# get instructions & interpret them
		self.debug('Bot path: %s' % self.parent.bot_path)
		if self.parent.bot_path:
			instructions = tools.read_file(self.parent.bot_path)
			self.interpret(instructions)

			# tell user that we have complete the path
			if not self.suspend:
				self.log('Bot path completed', LogType.Success)

		# reset bot window buttons
		self.reset()

		self.debug('Bot thread ended, elapsed time: ' + self.get_elapsed_time())

	def interpret(self, instructions):
		# split instructions
		lines = instructions.splitlines()

		for line in lines:
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: break

			# parse instruction
			self.debug('Instruction: ' + line)
			instruction = parser.parse_instruction(line)
			self.debug('Parse result: ' + str(instruction))

			# begin interpretation
			if instruction['name'] == 'Move':
				self.move(instruction['value'])

			elif instruction['name'] == 'Enclos':
				enclos_pos = parser.parse_data(data.Enclos, instruction['value'], ['x', 'y'])
				enclos_type = parser.parse_data(data.Enclos, instruction['value'], ['type'])
				print(str(enclos_pos) + ', type: ' + str(enclos_type))

			elif instruction['name'] == 'Zaap':
				zaap_from = parser.parse_data(data.Zaap['From'], instruction['from'])
				zaap_to = parser.parse_data(data.Zaap['To'], instruction['to'])
				print(str(zaap_from) + ' - ' + str(zaap_to))

			elif instruction['name'] == 'Zaapi':
				zaapi_from = parser.parse_data(data.Zaapi['From'], instruction['from'])
				zaapi_to = parser.parse_data(data.Zaapi['To'], instruction['to'])
				print(str(zaapi_from) + ' - ' + str(zaapi_to))

			else:
				self.debug('Unknown instruction')

	def click(self, coord):
		# adjust coordinates
		if self.game_geometry:
			game_x, game_y, game_width, game_height = self.game_geometry
			#print('game_x: %s, game_y: %s, game_width: %s, game_height: %s' % (game_x, game_y, game_width, game_height))
			x, y = tools.adjust_click_position(coord['x'], coord['y'], coord['width'], coord['height'], game_x, game_y, game_width, game_height)
		else:
			x, y = (coord['x'], coord['y'])
		# click
		self.debug('Click on x: %s, y: %s' % (x, y))
		tools.perform_click(x, y)

	def monitor_game_screen(self, timeout=30, tolerance=0.0):
		if self.game_geometry:
			# screen game
			prev_screen = tools.screen_game(self.game_geometry)
			elapsed_time = 0
			# wait for game screen to change
			while elapsed_time < timeout:
				# wait 1 second
				time.sleep(1)
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: break
				# take a new screen & compare it with the previous one
				screen = tools.screen_game(self.game_geometry)
				if screen.size != prev_screen.size:
					self.debug('Screen size has changed, retry')
				else:
					diff_percent = round(imgcompare.image_diff_percent(prev_screen, screen), 2)
					has_changed = diff_percent > tolerance
					self.debug('Game screen has changed: {}, diff: {}%, tolerance: {}, timeout: {}'.format(has_changed, diff_percent, tolerance, timeout))
					if has_changed:
						return True
				prev_screen = screen
				elapsed_time += 1
			# if game screen hasn't change before timeout
			if elapsed_time == timeout:
				self.await()
				self.log('Game screen don\'t change', LogType.Error)
				self.debug(tools.print_internet_state())

		return False

	def move(self, direction):
		# get coordinates
		coordinates = parser.parse_data(data.Movements, direction)
		if coordinates:
			# click
			self.click(coordinates)
			# wait for map to change
			self.debug('Waiting for map to change')
			if self.monitor_game_screen(tolerance=2.5):
				# wait for map to load
				self.debug('Waiting for map to load')
				time.sleep(3)

	def update_game_geometry(self, game_geometry):
		self.game_geometry = game_geometry

	def slow_down(self):
		# reduce thread speed
		time.sleep(0.15)

	def log(self, text, type=LogType.Normal):
		GObject.idle_add(self.parent._log, text, type)
		self.slow_down()

	def debug(self, text):
		GObject.idle_add(self.parent._debug, text)
		self.slow_down()

	def reset(self):
		GObject.idle_add(self.parent.reset_buttons)

	def await(self):
		self.pause()
		GObject.idle_add(self.parent.set_buttons_to_paused)

	def pause(self):
		self.pause_timer()
		self.pause_event.clear()
		self.debug('Bot thread paused')

	def resume(self):
		self.resume_timer()
		self.pause_event.set()
		self.debug('Bot thread resumed')

	def stop(self):
		self.stop_timer()
		self.suspend = True
		self.pause_event.set() # ensure that thread is resumed (if ever paused)
		self.join() # wait for thread to exit
		self.debug('Bot thread stopped')
