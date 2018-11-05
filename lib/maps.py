# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import json
from .tools import read_file, save_text_to_file, get_full_path

def get_filename():
	return get_full_path('maps.data')

def to_string(data):
	return json.dumps(data)

def to_array(text, jsonify=True):
	if jsonify:
		json_text = text.replace('\'', '"')
	else:
		json_text = text
	return json.loads(json_text)

def load():
	text = read_file(get_filename())
	if text:
		data = to_array(text, False)
	else:
		data = {}
	return data

def save(data):
	text = to_string(data)
	save_text_to_file(text, get_filename())
