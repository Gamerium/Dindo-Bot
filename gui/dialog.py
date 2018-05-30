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

class PlugDialog(Gtk.Dialog):

	def __init__(self, transient_for):
		Gtk.Dialog.__init__(self, transient_for=transient_for, title='Plug Game Window')
		self.parent = transient_for
		self.set_resizable(False)
		content_area = self.get_content_area()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		hbox.set_border_width(10)
		hbox.add(Gtk.Label('Window id'))
		self.entry = Gtk.Entry()
		hbox.add(self.entry)
		content_area.add(hbox)
		self.action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)
		plug_button = Gtk.Button('Plug')
		plug_button.connect('clicked', self.on_plug_button_clicked)
		self.add_action_widget(plug_button, Gtk.ResponseType.OK)
		self.show_all()

	def on_plug_button_clicked(self, button):
		window_xid = self.entry.get_text().strip()
		if window_xid.startswith('0x') or window_xid.isdigit():
			self.parent.plug_game_window(int(window_xid, 0))
