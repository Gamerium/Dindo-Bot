# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from lib import tools
from lib.shared import __version__

class AboutDialog(Gtk.AboutDialog):

	def __init__(self, transient_for):
		Gtk.AboutDialog.__init__(self, transient_for=transient_for)
		self.set_program_name('Dindo Bot')
		self.set_version(__version__)
		self.set_comments('Rearing bot for Dofus game')
		self.set_website('https://github.com/AXeL-dev')
		self.set_website_label('AXeL-dev')
		self.set_authors(['AXeL'])
		logo = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_resource_path('../icons/cover.png'), 64, 64)
		self.set_logo(logo)
		self.connect('response', self.on_response)

	def on_response(self, dialog, response):
		self.destroy()

class MessageDialog(Gtk.MessageDialog):

	def __init__(self, transient_for, message):
		Gtk.MessageDialog.__init__(self, transient_for=transient_for, use_markup=True, text=message, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK)
		self.run()
		self.destroy()
