# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import json
from .tools import read_file, save_text_to_file, get_resource_path
from .shared import DebugLevel

def get_filename():
	return get_resource_path('../settings.json')

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
	text = read_file(get_filename())
	if text:
		settings = json.loads(text)
	else:
		settings = load_defaults()
	return settings

def save(settings):
	text = json.dumps(settings)
	save_text_to_file(text, get_filename())

def update_and_save(settings, key, value, subkey=None):
	if subkey is not None:
		settings[key][subkey] = value
	else:
		settings[key] = value
	save(settings)
