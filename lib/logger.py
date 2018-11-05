# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from .tools import save_text_to_file, get_full_path, get_date, get_time

def get_filename():
	return get_full_path('logs/' + get_date() + '.log')

def new_entry(text):
	filename = get_filename()
	new_text = '[' + get_time() + '] ' + text + '\n'
	save_text_to_file(new_text, filename, 'a')

def debug(text):
	new_entry('DEBUG::' + text)

def error(text):
	new_entry('ERROR::' + text)

def add_separator(bold=False):
	filename = get_filename()
	separator = '=' if bold else '-'
	line = separator*50 + '\n'
	save_text_to_file(line, filename, 'a')
