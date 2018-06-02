# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import json
from .tools import read_file, save_text_to_file
from .shared import DebugLevel

def load_defaults():
	settings = {
		'Debug': {
			'Enabled': True,
			'Level':   DebugLevel.Low
		},
		'SaveDragodindesImages': False,
		'KeepGameOpen':          False
	}
	return settings

def load():
	text = read_file('settings.json')
	if text:
		settings = json.loads(text)
	else:
		settings = load_defaults()
	return settings

def save(settings):
	text = json.dumps(settings)
	save_text_to_file(text, 'settings.json')

def update_and_save(settings, key, value, subkey=None):
	if subkey:
		settings[key][subkey] = value
	else:
		settings[key] = value
	save(settings)
