# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

def parse_instruction(line):
	result = {}
	# extract name
	instruction = line.split('(')
	name = instruction[0]
	result['name'] = name
	# extract value/parameters
	if len(instruction) > 1:
		value = instruction[1][:-1] # [:-1] will remove the last character ')'
		if not ',' in value or (value.startswith('[') and value.endswith(']')): # do not split map position(s)
			result['value'] = value.strip()
		else:
			if '],' in value:
				parameters = value.replace('],', '];').split(';') # for instructions like Zaap(from=[10,-20], to=[-13,15])
			else:
				parameters = value.split(',')
			for i, parameter in enumerate(parameters):
				split_parameter = parameter.split('=')
				if len(split_parameter) > 1:
					key = split_parameter[0].strip()
					value = split_parameter[1]
				else:
					key = i
					value = split_parameter[0]
				result[key] = value.strip()

	return result

def parse_data(data, key, subkeys=[]):
	if key in data:
		if subkeys:
			count = len(subkeys)
			many = {} # dict to store subkeys data if there are more than 1
			for subkey in subkeys:
				if subkey in data[key]:
					if count == 1:
						return data[key][subkey]
					else:
						many[subkey] = data[key][subkey]
				else:
					if count == 1:
						return None
					else:
						many[subkey] = None
			return many
		else:
			return data[key]

	return None
