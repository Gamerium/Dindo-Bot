# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from lib.shared import LogType, DebugLevel
from lib import tools, parser, data
from .job import JobThread

class BotThread(JobThread):

	def __init__(self, parent, game_location, start_from_step, repeat_path, account_id, disconnect_after):
		JobThread.__init__(self, parent, game_location)
		self.start_from_step = start_from_step
		self.repeat_path = repeat_path
		self.account_id = account_id
		self.disconnect_after = disconnect_after
		self.exit_game = parent.settings['Account']['ExitGame']

	def run(self):
		self.start_timer()
		self.debug('Bot thread started', DebugLevel.Low)

		# connect to account
		account_connected = False
		if self.account_id is not None:
			self.debug('Connect to account (account_id: %s)' % self.account_id)
			self.connect(self.account_id)
			account_connected = True
			# check for pause
			self.pause_event.wait()

		# get instructions & interpret them
		while True:
			if not self.suspend:
				for bot_path in self.parent.bot_paths:
					self.debug('Bot path: %s, repeat: %d' % (bot_path, self.repeat_path))
					if bot_path:
						instructions = tools.read_file(bot_path)
						repeat_count = 0
						while repeat_count < self.repeat_path:
							# check for pause or suspend
							self.pause_event.wait()
							if self.suspend: break
							# start interpretation
							if self.interpret(instructions):
								self.interpret("GoToBank()")
							repeat_count += 1

						# tell user that we have complete the path
						if not self.suspend:
							self.log('Bot path completed', LogType.Success)

		if not self.suspend:
			# disconnect account
			if account_connected and self.disconnect_after:
				self.debug('Disconnect account')
				self.disconnect(self.exit_game)
			# reset bot window buttons
			self.reset()

		self.debug('Bot thread ended, elapsed time: ' + self.get_elapsed_time(), DebugLevel.Low)

	def interpret(self, instructions, ignore_start_from_step=False):
		# split instructions
		if not isinstance(instructions, list):
			lines = instructions.splitlines()
		else:
			lines = instructions
		# ignore instructions before start step
		if not ignore_start_from_step and self.start_from_step > 1 and self.start_from_step <= len(lines):
			self.debug('Start from step: %d' % self.start_from_step)
			step = self.start_from_step - 1
			lines = lines[step:]

		game_screen = None
		for i, line in enumerate(lines, start=1):
			# check for pause or suspend
			self.pause_event.wait()
			if self.suspend: break

			if self.wait_for_box_appear(box_name='Fight Button Light', timeout=1):
				self.handle_fight()

			# parse instruction
			self.debug('Instruction (%d): %s' % (i, line), DebugLevel.Low)
			instruction = parser.parse_instruction(line)
			self.debug('Parse result: ' + str(instruction), DebugLevel.High)

			# save game screen before those instructions
			if instruction['name'] in ['Click', 'PressKey']:
				game_screen = tools.screen_game(self.game_location)
			elif instruction['name'] != 'MonitorGameScreen':
				game_screen = None

			# begin interpretation
			if instruction['name'] == 'Move':
				self.move(instruction['value'])

			elif instruction['name'] == 'Enclos':
				self.check_enclos(instruction['location'], instruction['type'])

			elif instruction['name'] == 'Zaap':
				self.use_zaap(instruction['from'], instruction['to'])

			elif instruction['name'] == 'Zaapi':
				self.use_zaapi(instruction['from'], instruction['to'])

			elif instruction['name'] == 'Collect':
				if self.collect(instruction['map'], instruction['store_path']):
					# If collect return 1, we need to go to the bank. We forward 1 to the caller
					return 1

			elif instruction['name'] == 'Click':
				coordinates = {
					'x': int(instruction['x']),
					'y': int(instruction['y']),
					'width': int(instruction['width']),
					'height': int(instruction['height'])
				}
				# Handle the case when the click location need to match the stored color
				if 'r' in instruction:
					coordinates['color'] = f"({instruction['r']}, {instruction['g']}, {instruction['b']})"
					while not self.check_location_color(coordinates):
						self.log("Click location has a different color, waiting ...")
						self.pause_event.wait()
						if self.suspend: return
						self.sleep(0.01)

				if 'hotkey' in instruction:
					self.hot_click(instruction['hotkey'], coordinates, instruction['twice'])
				elif instruction['twice'] == 'True':
					self.double_click(coordinates)
				else:
					self.click(coordinates)

			elif instruction['name'] == 'GoToBank':
				self.go_to_bank()
				# Return to skip the end of the ongoing path
				return

			elif instruction['name'] == 'Scroll':
				times = int(instruction['times'])
				value = times if instruction['direction'] == 'up' else -times
				self.scroll(value)

			elif instruction['name'] == 'Pause':
				self.pause()

			elif instruction['name'] == 'MonitorGameScreen':
				self.monitor_game_screen(tolerance=2.5, screen=game_screen)

			elif instruction['name'] == 'Wait':
				duration = int(instruction['value'])
				self.sleep(duration)

			elif instruction['name'] == 'PressKey':
				self.press_key(instruction['value'])

			elif instruction['name'] == 'TypeText':
				self.type_text(instruction['value'])

			elif instruction['name'] == 'Connect':
				if instruction['account_id'].isdigit():
					account_id = int(instruction['account_id'])
				else:
					account_id = instruction['account_id']
				self.connect(account_id)

			elif instruction['name'] == 'Disconnect':
				self.disconnect(instruction['value'])

			else:
				self.debug('Unknown instruction', DebugLevel.Low)

	def go_to_bank(self):
		path_to_bank = data.BankPath
		self.debug(f"Go to Bank (path: {path_to_bank})")
		instructions = tools.read_file(tools.get_full_path(path_to_bank))
		if instructions:
			self.interpret(instructions, ignore_start_from_step=True)
		else:
			self.pause()
			self.log('Error: Could not interpret to go to bank path')
