# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from .tools import save_text_to_file, get_resource_path, get_date, get_time

def new_entry(text):
	new_text = '[' + get_time() + '] ' + text + '\n'
	save_text_to_file(new_text, get_resource_path('../logs/' + get_date() + '.log'), 'a')

def debug(text):
	new_entry('DEBUG::' + text)

def error(text):
	new_entry('ERROR::' + text)
