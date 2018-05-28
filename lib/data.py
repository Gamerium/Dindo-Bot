# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

# Movements
Movements = {
	'UP':    {'x': 200, 'y': 10},
	'LEFT':  {'x': 200, 'y': 10},
	'RIGHT': {'x': 200, 'y': 10},
	'DOWN':  {'x': 200, 'y': 10}
}

# Keyboard shortcuts
KeyboardShortcuts = {
	'Havre-sac':  'h',
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
		'Havre-sac': {'x': 100, 'y': 50},
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
