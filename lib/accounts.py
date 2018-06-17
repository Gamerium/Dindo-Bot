# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import json
from .tools import read_file, save_text_to_file, get_resource_path

def get_filename():
	return get_resource_path('../accounts.json')

def load():
	text = read_file(get_filename())
	if text:
		return json.loads(text)
	else:
		return {}

def save(accounts):
	text = json.dumps(accounts)
	save_text_to_file(text, get_filename())

def get_next_id(accounts, as_str=False):
	if accounts:
		greater_id = 1
		for account_id in accounts:
			id = int(account_id)
			if id > greater_id:
				greater_id = id
		next_id = greater_id + 1
	else:
		next_id = 1
	if as_str:
		return str(next_id)
	else:
		return next_id

def is_duplicate(login):
	accounts = load()
	for id in accounts:
		if accounts[id]['login'] == login:
			return True
	return False

def add(login, pwd):
	# add account
	accounts = load()
	id = get_next_id(accounts, True)
	accounts[id] = {
		'login': login,
		'pwd':   pwd
	}
	# save
	save(accounts)
	return id

def remove(id):
	# remove account
	accounts = load()
	del accounts[str(id)]
	# save
	save(accounts)
