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
	'Select From Inventory': {'x': 450, 'y': 165, 'width': 566, 'height': 456},
	'Disconnect Button':     {'x': 282, 'y': 218, 'width': 566, 'height': 456},
	'Exit Button':           {'x': 282, 'y': 236, 'width': 566, 'height': 456},
	'Login Input':           {'x': 270, 'y': 146, 'width': 566, 'height': 456},
	'Password Input':        {'x': 270, 'y': 174, 'width': 566, 'height': 456}
}

# Boxes
Boxes = {
	'Dragodinde Card':       {'x': 207, 'y': 42, 'width': 159, 'height': 320, 'windowSize': (566, 456)},
	'Dragodinde Energy':     {'x': 75, 'y': 136, 'width': 69, 'height': 1, 'windowSize': (566, 456)},
	#'Dragodinde Experience': {'x': 75, 'y': 148, 'width': 69, 'height': 1, 'windowSize': (566, 456)},
	#'Dragodinde Tiredness':  {'x': 75, 'y': 159, 'width': 69, 'height': 1, 'windowSize': (566, 456)},
	'Dragodinde Amour':      {'x': 75, 'y': 218, 'width': 69, 'height': 1, 'windowSize': (566, 456)},
	'Dragodinde Maturity':   {'x': 75, 'y': 229, 'width': 69, 'height': 1, 'windowSize': (566, 456)},
	'Dragodinde Endurance':  {'x': 75, 'y': 240, 'width': 69, 'height': 1, 'windowSize': (566, 456)},
	'Dragodinde Serenity':   {'x': 26, 'y': 274, 'width': 106, 'height': 1, 'windowSize': (566, 456)},
	'Enclos First Place':    {'x': 28, 'y': 295, 'width': 167, 'height': 1, 'windowSize': (566, 456)},
	'Inventory First Place': {'x': 377, 'y': 165, 'width': 168, 'height': 1, 'windowSize': (566, 456)},
	'Play Button':           {'x': 341, 'y': 362, 'width': 96, 'height': 1, 'windowSize': (566, 456)},
	'PodBar':                {'x': 658, 'y': 564, 'width': 81, 'height': 1, 'windowSize': (900, 700)}
	# TODO: update all boxes coordinates to (900, 700) window size
}

# DragodindeSerenity
class DragodindeSerenity:
	Negative, Medium, Positive = ('Negative', 'Medium', 'Positive')
	MaxMedium = 57.55

# DragodindeEnergy
class DragodindeEnergy:
	Max = 98.55

# DragodindeStats
class DragodindeStats:
	Empty, InProgress, Full = ('Empty', 'In Progress', 'Full')

# Colors
Colors = {
	'Full':            (204, 246, 0),
	'In Progress':     (255, 106, 61),
	#'Experience':      (108, 240, 229),
	#'Tiredness':       (252, 200, 0),
	'Empty Enclos':    (56, 56, 49),
	'Selected Row':    (83, 83, 77),
	'Empty Inventory': (53, 53, 45),
	'Play Button':     (215, 247, 0),
	'Empty PodBar':    (67, 70, 68)
}

# Keyboard shortcuts
KeyboardShortcuts = {
	'Havenbag':  'h',
	'Inventory': 'i',
	'Store':     '&',
	'Equip':     '"',
	'Elevate':   '2',
	'Exchange':  '\'',
	'Up':        'up',
	'Down':      'down',
	'Left':      'left',
	'Right':     'right',
	'Backspace': 'backspace',
	'Enter':     'enter',
	'Tab':       'tab',
	'Esc':       'esc'
	#'Copy':      'ctrl+c',
	#'Cut':       'ctrl+x',
	#'Paste':     'ctrl+v'
}

# Enclos
EnclosType = [
	'Amour',
	'Energy',
	'Endurance',
	'Maturity',
	'NegativeSerenity',
	'PositiveSerenity'
]

Enclos = {
	# Bonta
	'[-37,-56]': {'x': 354, 'y': 144, 'width': 566, 'height': 456},
	# Brakmar
	'[-32,37]':  {'x': 234, 'y': 202, 'width': 566, 'height': 456}
}

# Zaap
Zaap = {
	'From': {
		'Havenbag':  {'x': 110, 'y': 162, 'width': 566, 'height': 456, 'keyboard_shortcut': KeyboardShortcuts['Havenbag']},
		'Bonta':     {'x': 248, 'y': 140, 'width': 566, 'height': 456},
		'Brakmar':   {'x': 305, 'y': 106, 'width': 566, 'height': 456}
	},
	'To': {
		'Bonta':     {'x': 177, 'y': 274, 'width': 566, 'height': 456, 'scroll': -1},
		'Brakmar':   {'x': 182, 'y': 295, 'width': 566, 'height': 456, 'scroll': -1}
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
		'Animal SH':         {'x': 203, 'y': 175, 'width': 566, 'height': 456, 'location': Locations['SH Menu']},
		'Bank':              {'x': 183, 'y': 153, 'width': 566, 'height': 456, 'location': Locations['Various Menu']}
	}
}

# BankPath
BankPath = {
	# Bonta
	'Bank Bonta': [
		'Zaap(from=Havenbag,to=Bonta)',
		'Zaapi(from=Zaap Bonta,to=Bank)'
		# TODO: complete this path...
	],
	# Brakmar
	'Bank Brakmar': [
		'Zaap(from=Havenbag,to=Brakmar)',
		'Zaapi(from=Zaap Brakmar,to=Bank)'
		# TODO: complete this path...
	]
}
