# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import json
from .tools import read_file, save_text_to_file, get_full_path
from .shared import DebugLevel, GameVersion

def get_filename():
	return get_full_path('settings.json')

def load_defaults():
	settings = {
		'Debug': {
			'Enabled': True,
			'Level':   DebugLevel.Low
		},
		'Shortcuts': {
			'Start':                None,
			'Pause':                None,
			'Stop':                 None,
			'Minimize':             'Alt_L',
			'Focus Game':           'Ctrl+g',
			'Take Game Screenshot': 'Ctrl+Print'
		},
		'Game': {
			'Version': GameVersion.Two,
			'UseCustomWindowDecorationHeight': False,
			'WindowDecorationHeight': 36,
			'KeepOpen': True
		},
		'Account': {
			'ExitGame': False
		},
		'State': {
			'EnablePodBar':  True,
			'GoToBankPodPercentage': 80,
			'EnableMiniMap': True
		},
		'Farming': {
			'SaveDragodindesImages': False,
			'CheckResourcesColor': True,
			'AutoClosePopups': True,
			'CollectionTime': 0,
			'FirstResourceAdditionalCollectionTime': 3,
			'RatioCollectionMap':True,
			'NameRatioCollectionMap': "Ratio/RatioCollectMap.txt"
		},
		'Fighting': {
			'SaveScreenshots': False
		},
		'EnableShortcuts': False
	}
	return settings

def load():
	text = read_file(get_filename())
	defaults = load_defaults()
	if text:
		# load settings
		settings = json.loads(text)
		# check if all settings are there
		for key in defaults:
			# check keys
			if not key in settings:
				settings[key] = defaults[key]
			# check subkeys
			elif isinstance(defaults[key], dict):
				for subkey in defaults[key]:
					if not subkey in settings[key]:
						settings[key][subkey] = defaults[key][subkey]
		return settings
	else:
		return defaults

def save(settings):
	text = json.dumps(settings)
	save_text_to_file(text, get_filename())

def update_and_save(settings, key, value, subkey=None):
	if subkey is not None:
		settings[key][subkey] = value
	else:
		settings[key] = value
	save(settings)

def get(settings, key, subkey=None):
	if key in settings:
		if subkey is not None:
			if subkey in settings[key]:
				return settings[key][subkey]
			else:
				defaults = load_defaults()
				if key in defaults and subkey in defaults[key]:
					return defaults[key][subkey]
				else:
					return None
		else:
			return settings[key]
	else:
		defaults = load_defaults()
		if key in defaults:
			if subkey is not None:
				if subkey in defaults[key]:
					return defaults[key][subkey]
				else:
					return None
			else:
				return defaults[key]
		else:
			return None
