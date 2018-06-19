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
		return []

def save(accounts):
	text = json.dumps(accounts)
	save_text_to_file(text, get_filename())

def get_next_id(accounts):
	if accounts:
		greater_id = 1
		for account in accounts:
			if account['id'] > greater_id:
				greater_id = account['id']
		next_id = greater_id + 1
	else:
		next_id = 1
	return next_id

def is_duplicate(login):
	accounts = load()
	for account in accounts:
		if account['login'] == login:
			return True
	return False

def add(login, pwd):
	# add account
	accounts = load()
	id = get_next_id(accounts)
	accounts.append({
		'id':    id,
		'login': login,
		'pwd':   pwd
	})
	# save
	save(accounts)
	return (id, accounts)

def remove(id):
	# remove account
	accounts = load()
	for i, account in enumerate(accounts):
		if account['id'] == id:
			del accounts[i]
	# save
	save(accounts)
	return accounts

def get(id):
	accounts = load()
	for account in accounts:
		if account['id'] == id:
			return account
	return None

def swap(id, with_id):
	accounts = load()
	id_index, with_id_index = (None, None)
	# get first & second accounts by id
	for i, account in enumerate(accounts):
		if account['id'] == id and id_index is None:
			id_index = i
			if with_id_index is not None: # if we have the 2 indexes, break
				break
		elif account['id'] == with_id and with_id_index is None:
			with_id_index = i
			if id_index is not None: # if we have the 2 indexes, break
				break
	# swap ids
	if id_index is not None and with_id_index is not None:
		accounts[id_index]['id'] = with_id
		accounts[with_id_index]['id'] = id
		# save
		save(accounts)
	return accounts
