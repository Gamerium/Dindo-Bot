# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from lib import tools
from lib import shared
from lib import settings
from .custom import CustomComboBox

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
		self.connect('response', lambda dialog, response: self.destroy())

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
		# Window id entry
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		hbox.set_border_width(10)
		hbox.add(Gtk.Label('Window id'))
		self.entry = Gtk.Entry()
		hbox.add(self.entry)
		content_area = self.get_content_area()
		content_area.add(hbox)
		# Plug button
		self.action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)
		plug_button = Gtk.Button('Plug')
		plug_button.connect('clicked', self.on_plug_button_clicked)
		self.add_action_widget(plug_button, Gtk.ResponseType.OK)
		self.show_all()

	def on_plug_button_clicked(self, button):
		window_xid = self.entry.get_text().strip()
		if window_xid.startswith('0x') or window_xid.isdigit():
			self.parent.plug_game_window(int(window_xid, 0))

class PreferencesDialog(Gtk.Dialog):

	def __init__(self, transient_for, title='Preferences'):
		Gtk.Dialog.__init__(self, transient_for=transient_for, title=title)
		self.parent = transient_for
		self.set_resizable(False)
		self.connect('response', lambda dialog, response: self.destroy())
		# Header Bar
		hb = Gtk.HeaderBar(title=title)
		hb.set_show_close_button(True)
		self.set_titlebar(hb)
		# Grid, Stack & Stack switcher
		grid = Gtk.Grid()
		grid.set_border_width(10)
		content_area = self.get_content_area()
		content_area.add(grid)
		stack = Gtk.Stack()
		grid.attach(stack, 0, 1, 1, 1)
		stackswitcher = Gtk.StackSwitcher()
		stackswitcher.set_stack(stack)
		grid.attach(stackswitcher, 0, 0, 1, 1)
		### General
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		box.set_margin_top(10)
		stack.add_titled(box, 'general', 'General')
		## Debug
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		box.add(hbox)
		hbox.add(Gtk.Label('<b>Debug</b>', xalign=0, use_markup=True))
		debug_switch = Gtk.Switch()
		debug_switch.set_active(self.parent.settings['Debug']['Enabled'])
		debug_switch.connect('notify::active', self.on_debug_switch_activated)
		hbox.pack_end(debug_switch, False, False, 0)
		# Level
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		box.add(hbox)
		hbox.add(Gtk.Label('Level'))
		self.debug_level_combo = CustomComboBox(['High', 'Normal', 'Low'])
		self.debug_level_combo.set_active(self.parent.settings['Debug']['Level'])
		self.debug_level_combo.set_sensitive(self.parent.settings['Debug']['Enabled'])
		self.debug_level_combo.connect('changed', 
			lambda combo: settings.update_and_save(self.parent.settings, key='Debug', subkey='Level', value=combo.get_active()))
		hbox.pack_end(self.debug_level_combo, False, False, 0)
		## Game
		box.add(Gtk.Label('<b>Game</b>', xalign=0, use_markup=True))
		# Keep game checkbox
		keep_game_on_unplug_check = Gtk.CheckButton('Keep game open when unplug')
		keep_game_on_unplug_check.set_margin_left(10)
		keep_game_on_unplug_check.set_active(self.parent.settings['KeepGameOpen'])
		keep_game_on_unplug_check.connect('clicked', 
			lambda check: settings.update_and_save(self.parent.settings, 'KeepGameOpen', check.get_active()))
		box.add(keep_game_on_unplug_check)
		### Farming
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		box.set_margin_top(10)
		stack.add_titled(box, 'farming', 'Farming')
		# Save dragodindes images
		save_dragodindes_images_check = Gtk.CheckButton('Save dragodindes image')
		save_dragodindes_images_check.set_active(self.parent.settings['SaveDragodindesImages'])
		save_dragodindes_images_check.connect('clicked', 
			lambda check: settings.update_and_save(self.parent.settings, 'SaveDragodindesImages', check.get_active()))
		box.add(save_dragodindes_images_check)
		self.show_all()

	def on_debug_switch_activated(self, switch, pspec):
		value = switch.get_active()
		self.debug_level_combo.set_sensitive(value)
		if value:
			self.parent.debug_page.show()
		else:
			self.parent.debug_page.hide()
		settings.update_and_save(self.parent.settings, key='Debug', subkey='Enabled', value=value)
