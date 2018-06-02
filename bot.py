# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

'''
	Rearing bot for Dofus game
'''

from gui.main import BotWindow
from lib.tools import print_internet_state
from lib.shared import DebugLevel

bot = BotWindow()
bot._log('Bot window loaded')
bot._debug(print_internet_state(), DebugLevel.High)
bot.main()
