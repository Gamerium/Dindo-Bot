# coding=utf-8
# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

# Movements
Movements = {
	'UP':    {'x': 266, 'y': 4, 'width': 566, 'height': 456},
	'LEFT':  {'x': 5, 'y': 224, 'width': 566, 'height': 456},
	'RIGHT': {'x': 561, 'y': 225, 'width': 566, 'height': 456},
	'DOWN':  {'x': 263, 'y': 397, 'width': 566, 'height': 456}
}

# Locations
Locations = {
	'Workshops Menu':        {'x': 187, 'y': 75, 'width': 566, 'height': 456},
	'SH Menu':               {'x': 261, 'y': 75, 'width': 566, 'height': 456},
	'Various Menu':          {'x': 342, 'y': 75, 'width': 566, 'height': 456},
	'Select From Enclos':    {'x': 105, 'y': 297, 'width': 566, 'height': 456},
	'Select From Inventory': {'x': 450, 'y': 165, 'width': 566, 'height': 456}
}

# Keyboard shortcuts
KeyboardShortcuts = {
	'Havenbag':  'h',
	'Inventory': 'i',
	'Store':     '&',
	'Equip':     '"',
	'Elevate':   'é',
	'Exchange':  '\'',
	'Up':        'up',
	'Down':      'down',
	'Left':      'left',
	'Right':     'right',
	'Backspace': 'backspace',
	'Tab':       'tab',
	'Esc':       'esc'
	#'Copy':      'ctrl+c',
	#'Cut':       'ctrl+x',
	#'Paste':     'ctrl+v'
}

# Enclos
class EnclosType:
	Endurance, Maturity, Amour, Energy, NegativeSerenity, PositiveSerenity = range(6)

Enclos = {
	# Bonta
	'[-37,-56]': {'x': 354, 'y': 144, 'width': 566, 'height': 456, 'type': EnclosType.Amour},
	'[-38,-56]': {'x': 375, 'y': 118, 'width': 566, 'height': 456, 'type': EnclosType.Endurance},
	'[-38,-57]': {'x': 179, 'y': 155, 'width': 566, 'height': 456, 'type': EnclosType.NegativeSerenity},
	'[-37,-57]': {'x': 433, 'y': 187, 'width': 566, 'height': 456, 'type': EnclosType.PositiveSerenity},
	'[-37,-58]': {'x': 355, 'y': 247, 'width': 566, 'height': 456, 'type': EnclosType.Energy},
	'[-36,-57]': {'x': 174, 'y': 233, 'width': 566, 'height': 456, 'type': EnclosType.Maturity},
	# Brakmar
	'[-30,37]':  {'x': 157, 'y': 102, 'width': 566, 'height': 456, 'type': EnclosType.Amour},
	'[-31,38]':  {'x': 394, 'y': 89, 'width': 566, 'height': 456, 'type': EnclosType.Endurance},
	'[-32,38]':  {'x': 353, 'y': 129, 'width': 566, 'height': 456, 'type': EnclosType.NegativeSerenity},
	'[-30,38]':  {'x': 199, 'y': 125, 'width': 566, 'height': 456, 'type': EnclosType.PositiveSerenity},
	'[-32,37]':  {'x': 234, 'y': 202, 'width': 566, 'height': 456, 'type': EnclosType.Energy},
	'[-31,37]':  {'x': 140, 'y': 93, 'width': 566, 'height': 456, 'type': EnclosType.Maturity}
}

# Zaap
Zaap = {
	'From': {
		'Havenbag':  {'x': 110, 'y': 162, 'width': 566, 'height': 456, 'keyboard_shortcut': KeyboardShortcuts['Havenbag']},
		'Bonta':     {'x': 248, 'y': 140, 'width': 566, 'height': 456},
		'Brakmar':   {'x': 305, 'y': 106, 'width': 566, 'height': 456}
	},
	'To': {
		'Bonta':     {'x': 178, 'y': 214, 'width': 566, 'height': 456, 'scroll': -2},
		'Brakmar':   {'x': 184, 'y': 234, 'width': 566, 'height': 456, 'scroll': -2}
	}
}

# Zaapi
Zaapi = {
	'From': {
		# Bonta
		'Zaap Bonta':        {'x': 58, 'y': 67, 'width': 566, 'height': 456},
		'Bank Bonta':        {'x': 450, 'y': 242, 'width': 566, 'height': 456},
		'Animal SH Bonta':   {'x': 178, 'y': 48, 'width': 566, 'height': 456},
		# Brakmar
		'Zaap Brakmar':      {'x': 435, 'y': 161, 'width': 566, 'height': 456},
		'Bank Brakmar':      {'x': 154, 'y': 45, 'width': 566, 'height': 456},
		'Animal SH Brakmar': {'x': 434, 'y': 62, 'width': 566, 'height': 456}
	},
	'To': {
		'Zaap':              {'x': 176, 'y': 298, 'width': 566, 'height': 456, 'scroll': -2, 'location': Locations['Various Menu']},
		'Animal SH':         {'x': 205, 'y': 173, 'width': 566, 'height': 456, 'location': Locations['SH Menu']},
		'Bank':              {'x': 183, 'y': 153, 'width': 566, 'height': 456, 'location': Locations['Various Menu']}
	}
}
