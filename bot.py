# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

'''
	Rearing bot for Dofus game
'''

from lib.ui import BotWindow
from lib.tools import internet_on

bot = BotWindow()
bot._log('Bot window loaded')
bot._debug('Internet is ' + ('on' if internet_on() else 'off'))
bot.main()
