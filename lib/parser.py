# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

from .convert import rgb2hex

# Replace given string index by substitute
def replace_at_index(string, index, substitute, length=1):
	return string[:index] + substitute + string[index+length:]

# Replace all occurrences of needle in text with substitute only if needle is surrounded by starts_with & ends_with
def replace_all_between(text, needle, substitute, starts_with, ends_with):
	# TODO: use regex
	result = text
	cursor_position = 0
	proceed = needle != substitute
	while proceed: # while True:
		#print('text: "%s", cursor: %d' % (text, cursor_position))
		if len(text) == 0:
			break
		# try to find needle & his surroundings
		start = text.find(starts_with)
		needle_position = text.find(needle)
		end = text.find(ends_with)
		# if needle is surrounded
		if start != -1 and end != -1 and start < needle_position < end:
			result = replace_at_index(result, cursor_position+needle_position, substitute, len(needle))
			cursor_position += end+1-len(needle)+len(substitute)
			text = text[end+1:]
			#print('replaced')
		# else if not surrounded
		elif needle_position != -1:
			cursor_position += needle_position+1
			text = text[needle_position+1:]
			#print('not surrounded')
		# else if not find
		else:
			#print('break')
			break
	return result

# Parse instruction string, e.: 'Move(UP)', 'Enclos([-20,10])'
def parse_instruction(line, separator=','):
	result = {}
	# extract name
	instruction = line.split('(')
	name = instruction[0]
	result['name'] = name
	# extract value/parameters
	if len(instruction) > 1:
		if instruction[1].endswith(')'):
			origin_value = instruction[1][:-1].strip() # [:-1] will remove the last character ')'
		else:
			origin_value = instruction[1].strip()
		if not origin_value:
			result['value'] = None
		else:
			value = replace_all_between(origin_value, ',', ';', '[', ']') # avoid splitting map position(s)
			parameters = value.split(separator)
			# if single parameter + without name, return it as instruction value
			if len(parameters) == 1 and '=' not in parameters[0]:
				result['value'] = replace_all_between(value, ';', ',', '[', ']') # value & parameters[0] are the same in this case
			else:
				# return parameter(s) name/index & their value(s)
				for i, parameter in enumerate(parameters):
					split_parameter = parameter.split('=')
					if len(split_parameter) > 1:
						key = split_parameter[0].strip()
						value = split_parameter[1]
					else:
						key = i
						value = split_parameter[0]
					result[key] = replace_all_between(value.strip(), ';', ',', '[', ']')
	else:
		result['value'] = None

	return result

# Parse data dictionary, e.: {'x': 200, 'y': 10}, {'Zaap Bonta': {'x': 100, 'y': 50}}
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

# Parse key string, e.: 'a', 'ctrl+c'
def parse_key(key):
	result = []

	keys = key.split('+')

	for part in keys:
		result.append(part.strip())

	return result

def parse_color(color, as_hex=False):
	'''
	Parse color string and returns a tuple
		Examples:
			RGB: '(255, 255, 255)'
			Hex: #F424BE
	'''
	# To avoid problems if color was already decoded
	if isinstance(color, tuple):
		return color
	# check if RGB
	if color.startswith('(') and color.endswith(')'):
		values = color[1:-1].split(',') # [1:-1] will remove the first & last parentheses '(' ')'
		if len(values) == 3:
			rgb = (int(values[0]), int(values[1]), int(values[2]))
			if as_hex:
				return rgb2hex(rgb)
			else:
				return rgb
		else:
			return None
	# check if HEX
	elif color.startswith('#') and len(color) in (4, 7): # '#xxx' or '#xxxxxx'
		return color
	else:
		return None
