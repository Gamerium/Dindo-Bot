# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import threading
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from .shared import LogType, DebugLevel
from . import tools
from . import parser
from . import data
from . import imgcompare

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

	def __init__(self, parent, game_location, start_from_step, repeat_path, save_dragodindes_images):
		TimerThread.__init__(self)
		self.parent = parent
		self.game_location = game_location
		self.start_from_step = start_from_step
		self.repeat_path = repeat_path
		self.save_dragodindes_images = save_dragodindes_images
		self.pause_event = threading.Event()
		self.pause_event.set()
		self.suspend = False

	def run(self):
		self.start_timer()
		self.debug('Bot thread started', DebugLevel.Low)

		# get instructions & interpret them
		self.debug('Bot path: %s, repeat: %d' % (self.parent.bot_path, self.repeat_path))
		if self.parent.bot_path:
			instructions = tools.read_file(self.parent.bot_path)
			repeat_count = 0
			while repeat_count < self.repeat_path:
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: break
				# start interpretation
				self.interpret(instructions)
				repeat_count += 1

			# tell user that we have complete the path
			if not self.suspend:
				self.log('Bot path completed', LogType.Success)

		# reset bot window buttons
		if not self.suspend:
			self.reset()

		self.debug('Bot thread ended, elapsed time: ' + self.get_elapsed_time(), DebugLevel.Low)

	def interpret(self, instructions):
		# split instructions
		lines = instructions.splitlines()
		# ignore instructions before start step
		if self.start_from_step > 1 and self.start_from_step <= len(lines):
			self.debug('Start from step: %d' % self.start_from_step)
			step = self.start_from_step - 1
			lines = lines[step:]

		for i, line in enumerate(lines, start=1):
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: break

			# parse instruction
			self.debug('Instruction (%d): %s' % (i, line), DebugLevel.Low)
			instruction = parser.parse_instruction(line)
			self.debug('Parse result: ' + str(instruction), DebugLevel.High)

			# begin interpretation
			if instruction['name'] == 'Move':
				self.move(instruction['value'])

			elif instruction['name'] == 'Enclos':
				self.check_enclos(instruction['value'])

			elif instruction['name'] == 'Zaap':
				self.use_zaap(instruction['from'], instruction['to'])

			elif instruction['name'] == 'Zaapi':
				self.use_zaapi(instruction['from'], instruction['to'])

			elif instruction['name'] == 'Click':
				coordinates = (instruction['x'], instruction['y'], instruction['width'], instruction['height'])
				if instruction['twice'] == 'True':
					self.double_click(coordinates)
				else:
					self.click(coordinates)

			elif instruction['name'] == 'Wait':
				duration = instruction['value']
				if duration.isdigit():
					self.sleep(int(duration))

			elif instruction['name'] == 'PressKey':
				self.press_key(instruction['value'])

			elif instruction['name'] == 'TypeText':
				self.type_text(instruction['value'])

			else:
				self.debug('Unknown instruction')

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

	def move(self, direction):
		# get coordinates
		coordinates = parser.parse_data(data.Movements, direction)
		if coordinates:
			# click
			self.click(coordinates)
			# wait for map to change
			self.wait_for_map_change()

	def press_key(self, key):
		# press key
		self.debug('Press key: ' + key, DebugLevel.High)
		tools.press_key(key)

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

	def monitor_game_screen(self, timeout=10, tolerance=0.0, screen=None, location=None, await_after_timeout=True):
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
			if await_after_timeout and elapsed_time == timeout:
				self.await()
				self.log('Game screen don\'t change', LogType.Error)

		return False

	def wait_for_map_change(self, timeout=30, tolerance=2.5, screen=None):
		# wait for map to change
		self.debug('Waiting for map to change')
		if self.monitor_game_screen(timeout=timeout, tolerance=tolerance, screen=screen):
			# wait for map to load
			self.debug('Waiting for map to load')
			self.sleep(3)

	def use_zaap(self, zaap_from, zaap_to):
		# get coordinates
		zaap_from_coordinates = parser.parse_data(data.Zaap['From'], zaap_from)
		zaap_to_coordinates = parser.parse_data(data.Zaap['To'], zaap_to)
		if zaap_from_coordinates and zaap_to_coordinates:
			# if a keyboard shortcut is set (like for Havenbag)
			if 'keyboard_shortcut' in zaap_from_coordinates:
				# press key
				self.press_key(zaap_from_coordinates['keyboard_shortcut'])
				# wait for map to change
				self.wait_for_map_change()
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
			# click on zaap from
			screen = tools.screen_game(self.game_location)
			self.click(zaap_from_coordinates)
			# wait for zaap list to show
			self.debug('Waiting for zaap list to show')
			self.monitor_game_screen(tolerance=2.5, screen=screen)
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# if we need to scroll zaap list
			if 'scroll' in zaap_to_coordinates:
				# scroll
				self.scroll(zaap_to_coordinates['scroll'])
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: return
			# double click on zaap to
			screen = tools.screen_game(self.game_location)
			self.double_click(zaap_to_coordinates)
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

	def get_dragodinde_spec(self, name, dragodinde_screen):
		# crop dragodinde image
		location = data.Locations[name]
		x, y, w, h = (location['x'], location['y'], location['width'], location['height'])
		image = dragodinde_screen.crop((x, y, w+x, h+y))
		# get specification percentage & state
		state = data.DragodindeStats.Full
		percentage = tools.get_color_percentage(image, data.Colors['Full'])
		if percentage == 0:
			state = data.DragodindeStats.InProgress
			percentage = tools.get_color_percentage(image, data.Colors['In Progress'])
			if percentage == 0:
				state = data.DragodindeStats.Empty

		return [percentage, state]

	def get_dragodinde_stats(self, dragodinde_image):
		if dragodinde_image:
			# get dragodinde specifications (percent & state)
			energy = self.get_dragodinde_spec('Dragodinde Energy', dragodinde_image)
			amour = self.get_dragodinde_spec('Dragodinde Amour', dragodinde_image)
			maturity = self.get_dragodinde_spec('Dragodinde Maturity', dragodinde_image)
			endurance = self.get_dragodinde_spec('Dragodinde Endurance', dragodinde_image)
			serenity = self.get_dragodinde_spec('Dragodinde Serenity', dragodinde_image)
			# correct energy state
			if energy[1] == data.DragodindeStats.Full and energy[0] < data.DragodindeEnergy.Max:
				energy[1] = data.DragodindeStats.InProgress
			# set serenity state
			if serenity[0] >= data.DragodindeSenerity.MaxMedium:
				serenity[1] = data.DragodindeSenerity.Positive
			elif serenity[1] == data.DragodindeStats.Full:
				serenity[1] = data.DragodindeSenerity.Medium
			else:
				serenity[1] = data.DragodindeSenerity.Negative
			# return dragodinde stats
			stats = (energy, amour, maturity, endurance, serenity)
			self.debug('Energy: {0[0][0]}% ({0[0][1]}), Amour: {0[1][0]}% ({0[1][1]}), Maturity: {0[2][0]}% ({0[2][1]}), Endurance: {0[3][0]}% ({0[3][1]}), Serenity: {0[4][0]}% ({0[4][1]})'.format(stats))
			return stats
		else:
			return None

	def take_dragodinde_image(self, name, location=None):
		# get location
		if location is None:
			location = self.get_location('Dragodinde Card')
		# take dragodinde image
		if location:
			if self.save_dragodindes_images:
				# create directory(s) to store dragodindes images
				directory = tools.get_resource_path('../dragodindes') + '/' + tools.get_date()
				tools.create_directory(directory)
				save_to = directory + '/' + name
			else:
				save_to = None
			return tools.screen_game(location, save_to)
		else:
			return None

	def get_location(self, location):
		if self.game_location:
			game_x, game_y, game_width, game_height = self.game_location
			x = data.Locations[location]['x'] + game_x
			y = data.Locations[location]['y'] + game_y
			width = data.Locations[location]['width']
			height = data.Locations[location]['height']
			return (x, y, width, height)
		else:
			return None

	def move_dragodinde(self, action, dragodinde_image=None, dragodinde_location=None):
		if dragodinde_location is None:
			dragodinde_location = self.get_location('Dragodinde Card')
		if dragodinde_image is None:
			dragodinde_image = tools.screen_game(dragodinde_location)
		self.press_key(data.KeyboardShortcuts[action])
		self.monitor_game_screen(screen=dragodinde_image, location=dragodinde_location)

	def move_dragodinde_to_inventory(self, dragodinde_image=None, dragodinde_location=None):
		self.debug('Moving dragodinde to inventory')
		self.move_dragodinde('Exchange', dragodinde_image)
		return True

	def move_dragodinde_to_enclos(self, dragodinde_image=None, dragodinde_location=None):
		self.debug('Moving dragodinde to enclos')
		self.move_dragodinde('Elevate', dragodinde_image)
		return True

	def move_dragodinde_to_cowshed(self, dragodinde_image=None, dragodinde_location=None):
		self.debug('Moving dragodinde to cowshed')
		self.move_dragodinde('Store', dragodinde_image)
		return True

	def enclos_is_empty(self):
		location = self.get_location('Enclos First Place')
		screen = tools.screen_game(location)
		empty_percentage = tools.get_color_percentage(screen, data.Colors['Enclos Empty'])
		selected_percentage = tools.get_color_percentage(screen, data.Colors['Row Selected'])
		is_empty = empty_percentage >= 99 or selected_percentage >= 99
		debug_level = DebugLevel.Normal if is_empty else DebugLevel.High
		self.debug('Enclos is empty: {}, empty percentage: {}%, selected percentage: {}%'.format(is_empty, empty_percentage, selected_percentage), debug_level)
		return is_empty

	def get_dragodinde_name(self):
		return 'dd_%d' % tools.get_timestamp()

	def manage_enclos(self, enclos_type):
		# select dragodinde from enclos
		self.debug('Select dragodinde from enclos')
		screen = tools.screen_game(self.game_location)
		self.click(data.Locations['Select From Enclos'])
		# wait for dragodinde card to show
		self.debug('Waiting for dragodinde card to show')
		self.monitor_game_screen(tolerance=2.5, screen=screen)
		# manage dragodinde(s)
		dragodinde_number = 0
		moved_dragodinde_number = 0
		dragodinde_location = self.get_location('Dragodinde Card')
		while dragodinde_number < 10:
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return 0
			# break if enclos is empty
			if self.enclos_is_empty():
				break
			# take dragodinde image
			dragodinde_name = self.get_dragodinde_name()
			dragodinde_image = self.take_dragodinde_image(dragodinde_name, dragodinde_location)
			# increase dragodindes number
			dragodinde_number += 1
			# get dragodinde stats
			if self.save_dragodindes_images:
				self.debug("Get dragodinde '%s' stats" % dragodinde_name)
			else:
				self.debug('Get dragodinde stats')
			stats = self.get_dragodinde_stats(dragodinde_image)
			if stats:
				Stats = data.DragodindeStats
				Serenity = data.DragodindeSenerity
				# move dragodinde
				dragodinde_moved = False
				energy, amour, maturity, endurance, serenity = stats
				energy_percent, energy_state = energy
				amour_percent, amour_state = amour
				maturity_percent, maturity_state = maturity
				endurance_percent, endurance_state = endurance
				serenity_percent, serenity_state = serenity
				# get dragodinde needs
				need_energy = energy_state in (Stats.Empty, Stats.InProgress)
				need_amour = amour_state in (Stats.Empty, Stats.InProgress)
				need_maturity = maturity_state in (Stats.Empty, Stats.InProgress)
				need_endurance = endurance_state in (Stats.Empty, Stats.InProgress)
				self.debug('Need Energy: %s, Amour: %s, Maturity: %s, Endurance: %s' % (need_energy, need_amour, need_maturity, need_endurance), DebugLevel.High)
				# enclos 'Amour'
				if enclos_type == data.EnclosType.Amour:
					if amour_state == Stats.Full:
						dragodinde_moved = self.move_dragodinde_to_inventory(dragodinde_image, dragodinde_location)
				# enclos 'Endurance'
				elif enclos_type == data.EnclosType.Endurance:
					if endurance_state == Stats.Full:
						dragodinde_moved = self.move_dragodinde_to_inventory(dragodinde_image, dragodinde_location)
				# enclos 'NegativeSerenity'
				elif enclos_type == data.EnclosType.NegativeSerenity:
					if serenity_state == Serenity.Negative or (serenity_state == Serenity.Medium and need_maturity):
						dragodinde_moved = self.move_dragodinde_to_inventory(dragodinde_image, dragodinde_location)
				# enclos 'PositiveSerenity'
				elif enclos_type == data.EnclosType.PositiveSerenity:
					if serenity_state == Serenity.Positive or (serenity_state == Serenity.Medium and need_maturity):
						dragodinde_moved = self.move_dragodinde_to_inventory(dragodinde_image, dragodinde_location)
				# enclos 'Energy'
				elif enclos_type == data.EnclosType.Energy:
					if all(state == Stats.Full for state in (energy_state, amour_state, maturity_state, endurance_state)):
						dragodinde_moved = self.move_dragodinde_to_cowshed(dragodinde_image, dragodinde_location)
					elif energy_state == Stats.Full:
						dragodinde_moved = self.move_dragodinde_to_inventory(dragodinde_image, dragodinde_location)
				# enclos 'Maturity'
				elif enclos_type == data.EnclosType.Maturity:
					if maturity_state == Stats.Full or not serenity_state == Serenity.Medium:
						dragodinde_moved = self.move_dragodinde_to_inventory(dragodinde_image, dragodinde_location)
				# Nothing to do
				if not dragodinde_moved:
					self.debug('Nothing to do')
				else:
					moved_dragodinde_number += 1
					continue
				# break if managed dragodinde number equal 10
				if dragodinde_number == 10:
					break
			else:
				continue
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return 0
			# check next dragodinde
			self.debug('Check next dragodinde')
			self.press_key(data.KeyboardShortcuts['Down'])
			# break if there is no more dragodinde
			if not self.monitor_game_screen(tolerance=0.01, screen=dragodinde_image, location=dragodinde_location, await_after_timeout=False):
				if not self.suspend:
					self.debug('No more dragodinde')
					break
				else:
					return

		# print managed dragodindes number when break from loop
		free_places = 10 - (dragodinde_number - moved_dragodinde_number)
		self.debug('(Enclos) Managed dragodindes: %d, Moved dragodindes: %d, Free places: %d' % (dragodinde_number, moved_dragodinde_number, free_places), DebugLevel.Low)

		# return enclos free places number
		return free_places

	def inventory_is_empty(self):
		location = self.get_location('Inventory First Place')
		screen = tools.screen_game(location)
		percentage = tools.get_color_percentage(screen, data.Colors['Inventory Empty'])
		is_empty = percentage >= 99
		debug_level = DebugLevel.Normal if is_empty else DebugLevel.High
		self.debug('Inventory is empty: {}, percentage: {}%'.format(is_empty, percentage), debug_level)
		return is_empty

	def manage_inventory(self, enclos_type, enclos_free_places):
		# select dragodinde from inventory
		self.debug('Select dragodinde from inventory')
		screen = tools.screen_game(self.game_location)
		self.click(data.Locations['Select From Inventory'])
		# wait for dragodinde card to show
		self.debug('Waiting for dragodinde card to show')
		self.monitor_game_screen(tolerance=0.1, screen=screen)
		# manage dragodinde(s)
		dragodinde_number = 0
		moved_dragodinde_number = 0
		dragodinde_location = self.get_location('Dragodinde Card')
		while moved_dragodinde_number < enclos_free_places:
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# break if inventory empty
			if self.inventory_is_empty():
				break
			# take dragodinde image
			dragodinde_name = self.get_dragodinde_name()
			dragodinde_image = self.take_dragodinde_image(dragodinde_name, dragodinde_location)
			# increase dragodindes number
			dragodinde_number += 1
			# get dragodinde stats
			if self.save_dragodindes_images:
				self.debug("Get dragodinde '%s' stats" % dragodinde_name)
			else:
				self.debug('Get dragodinde stats')
			stats = self.get_dragodinde_stats(dragodinde_image)
			if stats:
				Stats = data.DragodindeStats
				Serenity = data.DragodindeSenerity
				# move dragodinde
				dragodinde_moved = False
				energy, amour, maturity, endurance, serenity = stats
				energy_percent, energy_state = energy
				amour_percent, amour_state = amour
				maturity_percent, maturity_state = maturity
				endurance_percent, endurance_state = endurance
				serenity_percent, serenity_state = serenity
				# get dragodinde needs
				need_energy = energy_state in (Stats.Empty, Stats.InProgress)
				need_amour = amour_state in (Stats.Empty, Stats.InProgress)
				need_maturity = maturity_state in (Stats.Empty, Stats.InProgress)
				need_endurance = endurance_state in (Stats.Empty, Stats.InProgress)
				self.debug('Need Energy: %s, Amour: %s, Maturity: %s, Endurance: %s' % (need_energy, need_amour, need_maturity, need_endurance), DebugLevel.High)
				# enclos 'Amour'
				if enclos_type == data.EnclosType.Amour:
					if need_amour and serenity_state == Serenity.Positive:
						dragodinde_moved = self.move_dragodinde_to_enclos(dragodinde_image, dragodinde_location)
				# enclos 'Endurance'
				elif enclos_type == data.EnclosType.Endurance:
					if need_endurance and serenity_state == Serenity.Negative:
						dragodinde_moved = self.move_dragodinde_to_enclos(dragodinde_image, dragodinde_location)
				# enclos 'NegativeSerenity'
				elif enclos_type == data.EnclosType.NegativeSerenity:
					if ((need_maturity or (need_endurance and not need_amour)) and serenity_state == Serenity.Positive)  or (need_endurance and serenity_state == Serenity.Medium and maturity_state == Stats.Full):
						dragodinde_moved = self.move_dragodinde_to_enclos(dragodinde_image, dragodinde_location)
				# enclos 'PositiveSerenity'
				elif enclos_type == data.EnclosType.PositiveSerenity:
					if ((need_maturity or (need_amour and not need_endurance)) and serenity_state == Serenity.Negative) or (need_amour and serenity_state == Serenity.Medium and maturity_state == Stats.Full):
						dragodinde_moved = self.move_dragodinde_to_enclos(dragodinde_image, dragodinde_location)
				# enclos 'Energy'
				elif enclos_type == data.EnclosType.Energy:
					if need_energy and all(state == Stats.Full for state in (amour_state, maturity_state, endurance_state)):
						dragodinde_moved = self.move_dragodinde_to_enclos(dragodinde_image, dragodinde_location)
				# enclos 'Maturity'
				elif enclos_type == data.EnclosType.Maturity:
					if need_maturity and serenity_state == Serenity.Medium:
						dragodinde_moved = self.move_dragodinde_to_enclos(dragodinde_image, dragodinde_location)
				# Nothing to do
				if not dragodinde_moved:
					self.debug('Nothing to do')
				else:
					moved_dragodinde_number += 1
					continue
			else:
				continue
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# check next dragodinde
			self.debug('Check next dragodinde')
			self.press_key(data.KeyboardShortcuts['Down'])
			# break if there is no more dragodinde
			if not self.monitor_game_screen(tolerance=0.01, screen=dragodinde_image, location=dragodinde_location, await_after_timeout=False):
				if not self.suspend:
					self.debug('No more dragodinde')
					break
				else:
					return

		# print managed dragodindes number when break from loop
		self.debug('(Inventory) Managed dragodindes: %d, Moved dragodindes: %d' % (dragodinde_number, moved_dragodinde_number), DebugLevel.Low)

	def check_enclos(self, enclos_name):
		# get enclos coordinates
		enclos = parser.parse_data(data.Enclos, enclos_name)
		if enclos:
			self.debug('Check enclos %s (%s)' % (enclos_name, enclos['type']))
			# click on enclos
			self.click(enclos)
			# wait for enclos to open
			self.debug('Waiting for enclos to open')
			if self.monitor_game_screen(tolerance=2.5):
				# wait for enclos to load
				self.sleep(1)
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# check enclos
			enclos_free_places = 0
			if not self.enclos_is_empty():
				enclos_free_places = self.manage_enclos(enclos['type'])
			else:
				enclos_free_places = 10
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# check inventory
			if enclos_free_places > 0 and not self.inventory_is_empty():
				self.manage_inventory(enclos['type'], enclos_free_places)
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: return
			# close enclos
			self.debug('Closing enclos')
			screen = tools.screen_game(self.game_location)
			self.press_key(data.KeyboardShortcuts['Esc'])
			# wait for enclos to close
			self.debug('Waiting for enclos to close')
			self.monitor_game_screen(tolerance=2.5, screen=screen)

	def slow_down(self):
		time.sleep(0.1) # reduce thread speed

	def log(self, text, type=LogType.Normal):
		GObject.idle_add(self.parent.log, text, type)
		self.slow_down()

	def debug(self, text, level=DebugLevel.Normal):
		GObject.idle_add(self.parent.debug, text, level)
		self.slow_down()

	def reset(self):
		GObject.idle_add(self.parent.reset_buttons)

	def await(self):
		self.pause()
		GObject.idle_add(self.parent.set_buttons_to_paused)

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
			self.await()
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

	def pause(self):
		self.pause_timer()
		self.pause_event.clear()
		self.debug('Bot thread paused', DebugLevel.Low)

	def resume(self, game_location):
		self.game_location = game_location
		self.resume_timer()
		self.pause_event.set()
		self.debug('Bot thread resumed', DebugLevel.Low)

	def stop(self):
		self.stop_timer()
		self.suspend = True
		self.pause_event.set() # ensure that thread is resumed (if ever paused)
		self.join() # wait for thread to exit
		self.debug('Bot thread stopped', DebugLevel.Low)
