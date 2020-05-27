# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

__program_name__  = 'Dindo Bot'
__program_desc__  = 'Farming bot for Dofus game'
__website__       = 'https://github.com/AXeL-dev'
__website_label__ = 'AXeL-dev'
__version__       = '3.0.0-alpha'
__authors__       = ['AXeL']

class LogType:
	Normal, Info, Success, Error = range(4)

class DebugLevel:
	'''
	High: The highest level (for text with too much details)
	Normal: Medium level (for text to show when the debug level is normal or high)
	Low: The lowest level (for text to always show when debug is enabled)
	'''
	High, Normal, Low = range(3)

class GameVersion:
    Retro, Two = 1, 2
