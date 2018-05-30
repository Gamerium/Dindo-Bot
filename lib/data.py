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
	'Workshops Menu':        {'x': 218, 'y': 78, 'width': 642, 'height': 483},
	'SH Menu':               {'x': 299, 'y': 81, 'width': 642, 'height': 483},
	'Various Menu':          {'x': 382, 'y': 78, 'width': 642, 'height': 483},
	'Select From Enclos':    {'x': 154, 'y': 314, 'width': 642, 'height': 483},
	'Select From Inventory': {'x': 485, 'y': 176, 'width': 642, 'height': 483}
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
	'[-37,-56]': {'x': 386, 'y': 162, 'width': 642, 'height': 483, 'type': EnclosType.Amour},
	'[-38,-56]': {'x': 409, 'y': 132, 'width': 642, 'height': 483, 'type': EnclosType.Endurance},
	'[-38,-57]': {'x': 217, 'y': 161, 'width': 642, 'height': 483, 'type': EnclosType.NegativeSerenity},
	'[-37,-57]': {'x': 468, 'y': 191, 'width': 642, 'height': 483, 'type': EnclosType.PositiveSerenity},
	'[-37,-58]': {'x': 384, 'y': 263, 'width': 642, 'height': 483, 'type': EnclosType.Energy},
	'[-36,-57]': {'x': 219, 'y': 255, 'width': 642, 'height': 483, 'type': EnclosType.Maturity},
	# Brakmar
	'[-30,37]':  {'x': 197, 'y': 112, 'width': 642, 'height': 483, 'type': EnclosType.Amour},
	'[-31,38]':  {'x': 432, 'y': 99, 'width': 642, 'height': 483, 'type': EnclosType.Endurance},
	'[-32,38]':  {'x': 393, 'y': 143, 'width': 642, 'height': 483, 'type': EnclosType.NegativeSerenity},
	'[-30,38]':  {'x': 236, 'y': 128, 'width': 642, 'height': 483, 'type': EnclosType.PositiveSerenity},
	'[-32,37]':  {'x': 272, 'y': 224, 'width': 642, 'height': 483, 'type': EnclosType.Energy},
	'[-31,37]':  {'x': 177, 'y': 112, 'width': 642, 'height': 483, 'type': EnclosType.Maturity}
}

# Zaap
Zaap = {
	'From': {
		'Havenbag':  {'x': 140, 'y': 177, 'width': 642, 'height': 483},
		'Bonta':     {'x': 286, 'y': 150, 'width': 642, 'height': 483},
		'Brakmar':   {'x': 348, 'y': 116, 'width': 642, 'height': 483}
	},
	'To': {
		'Bonta':     {'x': 213, 'y': 227, 'width': 642, 'height': 483, 'scroll': -2},
		'Brakmar':   {'x': 216, 'y': 249, 'width': 642, 'height': 483, 'scroll': -2}
	}
}

# Zaapi
Zaapi = {
	'From': {
		'Zaap Bonta':        {'x': 96, 'y': 73, 'width': 642, 'height': 483},
		'Zaap Brakmar':      {'x': 465, 'y': 173, 'width': 642, 'height': 483},
		'Animal SH Bonta':   {'x': 211, 'y': 48, 'width': 642, 'height': 483},
		'Animal SH Brakmar': {'x': 471, 'y': 68, 'width': 642, 'height': 483},
		'Bank Bonta':        {'x': 492, 'y': 264, 'width': 642, 'height': 483},
		'Bank Brakmar':      {'x': 193, 'y': 43, 'width': 642, 'height': 483}
	},
	'To': {
		'Zaap':              {'x': 206, 'y': 312, 'width': 642, 'height': 483, 'scroll': -2},
		'Animal SH':         {'x': 282, 'y': 184, 'width': 642, 'height': 483},
		'Bank':              {'x': 212, 'y': 163, 'width': 642, 'height': 483}
	}
}
