# coding=utf-8
# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

# Movements
Movements = {
	'UP':    {'x': 266, 'y': 1, 'width': 566, 'height': 456},
	'LEFT':  {'x': 5, 'y': 224, 'width': 566, 'height': 456},
	'RIGHT': {'x': 561, 'y': 225, 'width': 566, 'height': 456},
	'DOWN':  {'x': 263, 'y': 397, 'width': 566, 'height': 456},
	# TODO: rename 'width' & 'height' to 'windowSize' (this may impact many parts of code)
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
	'Exit Defeat Message':   {'x': 556, 'y': 503, 'width': 900, 'height': 712},
	'Login Input':           {'x': 270, 'y': 146, 'width': 566, 'height': 456},
	'Password Input':        {'x': 270, 'y': 174, 'width': 566, 'height': 456},
	# TODO: rename 'width' & 'height' to 'windowSize' (this may impact many parts of code)
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
	'Login Button':          {'x': 400, 'y': 385, 'width': 96, 'height': 1, 'windowSize': (900, 700)}, # not accurate
	'PodBar':                {'x': 364, 'y': 692, 'width': 322, 'height': 1, 'windowSize': (900, 704)},
	'Fight Button Light':    {'x': 720, 'y': 661, 'width': 1, 'height': 1, 'windowSize': (900, 712)},
	'Fight Button Dark':     {'x': 720, 'y': 661, 'width': 1, 'height': 1, 'windowSize': (900, 712)},
    'Victory':               {'x': 492, 'y': 479, 'width': 3, 'height': 3, 'windowSize': (900, 704)},
	'NewVictory':            {'x': 101, 'y': 205, 'width': 3, 'height': 3, 'windowSize': (900, 704)},
    'Defeat':                {'x': 494, 'y': 487, 'width': 3, 'height': 3, 'windowSize': (900, 712)},
	'Job Level Up Popup':    {'x': 249, 'y': 397, 'width': 11, 'height': 1, 'windowSize': (900, 713)}
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
	'Full':               (204, 246, 0),
	'In Progress':        (255, 106, 61),
	#'Experience':         (108, 240, 229),
	#'Tiredness':          (252, 200, 0),
	'Empty Enclos':       (56, 56, 49),
	'Selected Row':       (83, 83, 77),
	'Empty Inventory':    (53, 53, 45),
	'Play Button':        (215, 247, 0),
	'Login Button':       (214, 246, 0),
	'Empty PodBar':       (0, 0, 0),
	'Fight Button Light': (206, 240, 0),
	'Fight Button Dark':  (123,143,0),
	'Job Level Up Popup': (229, 249, 0),
	'Victory':            (206,150,20),
	'NewVictory':         (255,235,165),
	'Defeat':             (161,75,67)
}

# Keyboard shortcuts
KeyboardShortcuts = {
	'None':      '',
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
	'Esc':       'esc',
	'Ctrl':      'crtl',
	'arakne':    '-',
	'epee':      '(',
	'EndTurn':   ','
	#'Copy':      'ctrl+c',
	#'Cut':       'ctrl+x',
	#'Paste':     'ctrl+v',
}

# Enclos
EnclosType = [
	'Amour',
	'Energy',
	'Endurance',
	'Maturity',
	'NegativeSerenity',
	'PositiveSerenity',
]

Enclos = {
	# Bonta
	'[-37,-56]': {'x': 354, 'y': 144, 'width': 566, 'height': 456},
	# Brakmar
	'[-32,37]':  {'x': 234, 'y': 202, 'width': 566, 'height': 456},
	# TODO: rename 'width' & 'height' to 'windowSize' (this may impact many parts of code)
}

# Zaap
Zaap = {
	'To': ['Bonta',
            'Rocky Roads',
            'Tailena',
            'Astrub City',
            'Madrestam',
            'Lousy Big',
            'Frigost Island',
            'Rocky Plains',
            'Gobball Corner'],
	'SearchBar': {'x': 497, 'y': 136, 'width': 900, 'height': 704},
	'FirstDestination': {'x': 470, 'y': 194, 'width': 900, 'height': 704},
	'ZaapItself': {'x': 180, 'y': 241, 'width': 900, 'height': 704}
	# TODO: rename 'width' & 'height' to 'windowSize' (this may impact many parts of code)
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
		'Animal SH Brakmar': {'x': 434, 'y': 62, 'width': 566, 'height': 456},
	},
	'To': {
		'Zaap':              {'x': 176, 'y': 298, 'width': 566, 'height': 456, 'scroll': -2, 'location': Locations['Various Menu']},
		'Animal SH':         {'x': 203, 'y': 175, 'width': 566, 'height': 456, 'location': Locations['SH Menu']},
		'Bank':              {'x': 183, 'y': 153, 'width': 566, 'height': 456, 'location': Locations['Various Menu']},
	}
	# TODO: rename 'width' & 'height' to 'windowSize' (this may impact many parts of code)
}

BankPath = "./paths/path-to-bank.path"
