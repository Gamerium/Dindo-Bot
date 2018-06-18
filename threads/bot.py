# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from lib.shared import LogType, DebugLevel
from lib import tools
from lib import parser
from .job import JobThread

class BotThread(JobThread):

	def __init__(self, parent, game_location, start_from_step, repeat_path, connect_disconnect_once):
		JobThread.__init__(self, parent, game_location)
		self.start_from_step = start_from_step
		self.repeat_path = repeat_path
		self.connect_disconnect_once = connect_disconnect_once

	def run(self):
		self.start_timer()
		self.debug('Bot thread started', DebugLevel.Low)

		# get instructions & interpret them
		self.debug('Bot path: %s, repeat: %d' % (self.parent.bot_path, self.repeat_path))
		if self.parent.bot_path:
			instructions = tools.read_file(self.parent.bot_path)
			self.repeat_count = 0
			while self.repeat_count < self.repeat_path:
				# check for pause or suspend
				self.pause_event.wait()
				if self.suspend: break
				# start interpretation
				self.interpret(instructions)
				self.repeat_count += 1

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
				coordinates = (
					int(instruction['x']),
					int(instruction['y']),
					int(instruction['width']),
					int(instruction['height'])
				)
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

			elif instruction['name'] == 'Connect':
				if not self.connect_disconnect_once or self.repeat_count == 0:
					self.connect(int(instruction['account_id']))
				else:
					self.debug('Instruction ignored', DebugLevel.Low)

			elif instruction['name'] == 'Disconnect':
				if not self.connect_disconnect_once or self.repeat_count == self.repeat_path - 1:
					self.disconnect(instruction['value'])
				else:
					self.debug('Instruction ignored', DebugLevel.Low)

			else:
				self.debug('Unknown instruction', DebugLevel.Low)