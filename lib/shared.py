# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

__program_name__  = 'Dindo Bot'
__program_desc__  = 'Rearing bot for Dofus game'
__website__       = 'https://github.com/AXeL-dev'
__website_label__ = 'AXeL-dev'
__version__       = '1.0.0-beta'
__authors__       = ['AXeL']

class LogType:
	Normal, Info, Success, Error = range(4)

class DebugLevel:
	'''
	High: The highest level (for debug text with too much details)
	Normal: Medium level (for normal debug text)
	Low: The lowest level (for text without real interest)
	'''
	High, Normal, Low = range(3)
