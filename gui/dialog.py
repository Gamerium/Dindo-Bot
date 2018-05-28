# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from lib import tools
from lib import shared

class AboutDialog(Gtk.AboutDialog):

	def __init__(self, transient_for):
		Gtk.AboutDialog.__init__(self, transient_for=transient_for)
		self.set_program_name(shared.__program_name__)
		self.set_version(shared.__version__)
		self.set_comments(shared.__program_desc__)
		self.set_website(shared.__website__)
		self.set_website_label(shared.__website_label__)
		self.set_authors(shared.__authors__)
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

class TextDialog(Gtk.MessageDialog):

	def __init__(self, transient_for, text):
		Gtk.MessageDialog.__init__(self, transient_for=transient_for, buttons=Gtk.ButtonsType.CLOSE)
		self.set_image(Gtk.Image(stock=Gtk.STOCK_PASTE, icon_size=Gtk.IconSize.DIALOG))
		entry = Gtk.Entry()
		entry.set_text(text)
		entry.set_width_chars(60)
		#entry.set_sensitive(False)
		message_area = self.get_message_area()
		message_area.add(entry)
		self.show_all()
		self.run()
		self.destroy()
