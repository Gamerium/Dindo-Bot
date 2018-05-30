# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

# Movements
Movements = {
	'UP':    {'x': 266, 'y': 4, 'width': 566, 'height': 456},
	'LEFT':  {'x': 5, 'y': 224, 'width': 566, 'height': 456},
	'RIGHT': {'x': 561, 'y': 225, 'width': 566, 'height': 456},
	'DOWN':  {'x': 263, 'y': 397, 'width': 566, 'height': 456}
}

# Keyboard shortcuts
KeyboardShortcuts = {
	'Havenbag':  'h',
	'Inventory':  'i'
	#'Up':         'up',
	#'Down':       'down',
	#'Left':       'left',
	#'Right':      'right',
	#'Backspace':  'backspace',
	#'Tab':        'tab',
	#'Copy':       'ctrl+c',
	#'Cut':        'ctrl+x',
	#'Paste':      'ctrl+v'
}

# Enclos
class EnclosType:
	Endurance, Maturity, Amour, Energy, NegativeSerenity, PositiveSerenity = range(6)

Enclos = {
	'[-20,11]': {'x': 200, 'y': 10, 'type': EnclosType.Endurance},
	'[-20,12]': {'x': 200, 'y': 10, 'type': EnclosType.Amour}
}

# Zaap
Zaap = {
	'From': {
		'Havenbag': {'x': 100, 'y': 50},
		'Bonta':     {'x': 100, 'y': 50},
		'Brakmar':   {'x': 100, 'y': 50},
		'Astrub':    {'x': 100, 'y': 50}
	},
	'To': {
		'Bonta':     {'x': 100, 'y': 50},
		'Brakmar':   {'x': 100, 'y': 50},
		'Astrub':    {'x': 100, 'y': 50}
	}
}

# Zaapi
Zaapi = {
	'From': {
		'Zaap Bonta':   {'x': 100, 'y': 50},
		'Zaap Brakmar': {'x': 100, 'y': 50},
		'HDV Animaux':  {'x': 100, 'y': 50},
		'Banque':       {'x': 100, 'y': 50}
	},
	'To': {
		'Zaap Bonta':   {'x': 100, 'y': 50},
		'Zaap Brakmar': {'x': 100, 'y': 50},
		'HDV Animaux':  {'x': 100, 'y': 50},
		'Banque':       {'x': 100, 'y': 50}
	}
}
