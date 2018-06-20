# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from lib.shared import DebugLevel
from lib import data
from lib import tools
from lib import parser
from .travel import TravelThread

class FarmingThread(TravelThread):

	def __init__(self, parent, game_location):
		TravelThread.__init__(self, parent, game_location)
		self.save_dragodindes_images = parent.settings['Farming']['SaveDragodindesImages']

	def get_dragodinde_spec(self, name, dragodinde_image):
		# crop dragodinde image
		box = data.Boxes[name]
		x, y, w, h = (box['x'], box['y'], box['width'], box['height'])
		image = dragodinde_image.crop((x, y, w+x, h+y))
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
			location = self.get_box_location('Dragodinde Card')
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

	def move_dragodinde(self, action, dragodinde_image=None, dragodinde_location=None):
		if dragodinde_location is None:
			dragodinde_location = self.get_box_location('Dragodinde Card')
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
		location = self.get_box_location('Enclos First Place')
		screen = tools.screen_game(location)
		empty_percentage = tools.get_color_percentage(screen, data.Colors['Empty Enclos'])
		selected_percentage = tools.get_color_percentage(screen, data.Colors['Selected Row'])
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
		dragodinde_location = self.get_box_location('Dragodinde Card')
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
		location = self.get_box_location('Inventory First Place')
		screen = tools.screen_game(location)
		percentage = tools.get_color_percentage(screen, data.Colors['Empty Inventory'])
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
		dragodinde_location = self.get_box_location('Dragodinde Card')
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
			if self.monitor_game_screen(timeout=30, tolerance=2.5):
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
