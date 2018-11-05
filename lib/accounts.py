# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import json
from .tools import read_file, save_text_to_file, get_full_path

def get_filename():
	return get_full_path('accounts.json')

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
	position = id - 1
	accounts.append({
		'id':       id,
		'login':    login,
		'pwd':      pwd,
		'position': position
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
			break
	# save
	save(accounts)
	return accounts

def get(id):
	accounts = load()
	for account in accounts:
		if account['id'] == id:
			return account
	return None

def swap(id1, id2):
	accounts = load()
	account1_index, account2_index = (None, None)
	# get accounts indexes by id
	for i, account in enumerate(accounts):
		if account['id'] == id1 and account1_index is None:
			account1_index = i
			if account2_index is not None: # if we have the 2 indexes, break
				break
		elif account['id'] == id2 and account2_index is None:
			account2_index = i
			if account1_index is not None: # if we have the 2 indexes, break
				break
	# swap positions
	if account1_index is not None and account2_index is not None:
		account1_position = accounts[account1_index]['position']
		accounts[account1_index]['position'] = accounts[account2_index]['position']
		accounts[account2_index]['position'] = account1_position
		# save
		save(accounts)
	return accounts
