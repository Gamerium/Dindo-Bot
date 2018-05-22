# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from datetime import datetime
from .tools import get_resource_path

def new_entry(text):
	# get date & time
	date_time = datetime.now()
	date = date_time.strftime('%d-%m-%y')
	time = date_time.strftime('%H:%M:%S')
	# write to file
	file = open(get_resource_path('../logs/' + date + '.txt'), 'a')
	file.write('[' + time + '] ' + text + '\n')
	file.close()

def debug(text):
	new_entry('DEBUG::' + text)

def error(text):
	new_entry('ERROR::' + text)
