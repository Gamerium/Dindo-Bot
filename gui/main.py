# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
from lib import tools, logger, data, parser, settings, accounts, maps
from threads.bot import BotThread
from lib.shared import LogType, DebugLevel, __program_name__, GameVersion
from .dev import DevToolsWidget
from .custom import *
from .dialog import *
from threading import Thread

class BotWindow(Gtk.ApplicationWindow):

	def __init__(self, title=__program_name__):
		GObject.threads_init() # allow threads to update GUI
		Gtk.Window.__init__(self, title=title)
		logger.add_separator()
		# Initialise class attributes
		self.game_window = None
		self.game_window_location = None
		self.bot_paths = []
		self.bot_thread = None
		self.args = tools.get_cmd_args()
		# Get settings
		self.settings = settings.load()
		# Header Bar
		self.create_header_bar(title)
		# Tabs
		self.create_tabs()
		# Window
		self.set_icon_from_file(tools.get_full_path('icons/logo.png'))
		#self.set_size_request(350, 700)
		self.set_default_size(350, 700)
		self.set_resizable(False)
		self.connect('key-press-event', self.on_key_press)
		#self.connect('configure-event', self.on_resize_or_move)
		#self.connect('window-state-event', self.on_minimize)
		self.connect('destroy', Gtk.main_quit)
		self.show_all()
		self.unbind_button.hide()
		if not self.settings['Debug']['Enabled']:
			self.debug_page.hide()
		if not self.settings['State']['EnablePodBar']:
			self.podbar_box.hide()
		if not self.settings['State']['EnableMiniMap']:
			self.minimap_box.hide()

	def on_key_press(self, widget, event):
		if self.settings['EnableShortcuts']:
			# get keyname
			keyname = Gdk.keyval_name(event.keyval)
			ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
			alt = (event.state & Gdk.ModifierType.MOD1_MASK)
			shift = (event.state & Gdk.ModifierType.SHIFT_MASK)
			# handle shortcuts
			for action in self.settings['Shortcuts']:
				value = self.settings['Shortcuts'][action]
				if value is not None:
					keys = value.split('+')
					if (len(keys) == 1 and keys[0] == keyname) or (len(keys) == 2 and ((keys[0] == 'Ctrl' and ctrl) or (keys[0] == 'Alt' and alt) or (keys[0] == 'Shift' and shift)) and keys[1] == keyname):
						# run actions
						if action == 'Start':
							self.start_button.emit('clicked')
						elif action == 'Pause':
							self.pause_button.emit('clicked')
						elif action == 'Stop':
							self.stop_button.emit('clicked')
						elif action == 'Minimize':
							self.iconify()
						elif action == 'Take Game Screenshot':
							self.take_screenshot_button.emit('clicked')
						elif action == 'Focus Game':
							self.focus_game()
						# stop event propagation
						return True
		# focus game
		if self.bot_thread and self.bot_thread.isAlive():
			self.focus_game()

	def on_minimize(self, widget, event):
		if event.window.get_state() == Gdk.WindowState.ICONIFIED:
			self.pause_bot()

	def on_resize_or_move(self, widget, event):
		self.pause_bot()

	def pop(self, text_buffer, max=100):
		start_iter = text_buffer.get_start_iter()
		end_iter = text_buffer.get_end_iter()
		lines = text_buffer.get_text(start_iter, end_iter, True).splitlines()
		if len(lines) >= max:
			new_text = '\n'.join(lines[1:]) + '\n' # [1:] to remove the first line
			text_buffer.set_text(new_text)

	def log(self, text, type=LogType.Normal):
		# pop first line if we reached the max number of lines
		self.pop(self.log_buf)
		# append to text view
		position = self.log_buf.get_end_iter()
		new_text = '[' + tools.get_time() + '] ' + text + '\n'
		if type == LogType.Success:
			self.log_buf.insert_with_tags(position, new_text, self.green_text_tag)
		elif type == LogType.Error:
			self.log_buf.insert_with_tags(position, new_text, self.red_text_tag)
		elif type == LogType.Info:
			self.log_buf.insert_with_tags(position, new_text, self.blue_text_tag)
		else:
			self.log_buf.insert(position, new_text)
		# call logger
		if type == LogType.Error:
			logger.error(text)
		else:
			logger.new_entry(text)

	def debug(self, text, level=DebugLevel.Normal):
		# append to text view
		if self.settings['Debug']['Enabled'] and level >= self.settings['Debug']['Level']:
			self.pop(self.debug_buf)
			position = self.debug_buf.get_end_iter()
			self.debug_buf.insert(position, '[' + tools.get_time() + '] ' + text + '\n')
			logger.debug(text)

	def on_about_button_clicked(self, button):
		dialog = AboutDialog(transient_for=self)
		dialog.run()

	def on_preferences_button_clicked(self, button):
		dialog = PreferencesDialog(transient_for=self)
		dialog.run()

	def on_accounts_button_clicked(self, button):
		dialog = AccountsDialog(transient_for=self)
		dialog.run()

	def on_take_screenshot_button_clicked(self, button):
		if self.game_window and not self.game_window.is_destroyed():
			screenshot_name = 'screenshot_' + tools.get_date_time()
			screenshot_path = tools.get_full_path(screenshot_name)
			tools.take_window_screenshot(self.game_window, screenshot_path)
			self.log("Screenshot saved to '%s'" % screenshot_path, LogType.Info)

	def create_header_bar(self, title):
		### Header Bar
		hb = Gtk.HeaderBar(title=title)
		logo = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/logo.png'), 24, 24)
		hb.pack_start(Gtk.Image(pixbuf=logo))
		hb.set_show_close_button(True)
		self.set_titlebar(hb)
		## Settings button
		self.settings_button = Gtk.Button()
		self.settings_button.set_image(Gtk.Image(icon_name='open-menu-symbolic'))
		self.settings_button.connect('clicked', lambda button: self.popover.show_all())
		hb.pack_end(self.settings_button)
		self.popover = Gtk.Popover(relative_to=self.settings_button, position=Gtk.PositionType.BOTTOM)
		self.popover.set_border_width(2)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		self.popover.add(box)
		# Preferences button
		preferences_button = Gtk.ModelButton(' Preferences')
		preferences_button.set_alignment(0, 0.5)
		preferences_button.set_image(Gtk.Image(icon_name='preferences-desktop'))
		preferences_button.connect('clicked', self.on_preferences_button_clicked)
		box.add(preferences_button)
		# Accounts button
		accounts_button = Gtk.ModelButton(' Accounts')
		accounts_button.set_alignment(0, 0.5)
		accounts_button.set_image(Gtk.Image(icon_name='dialog-password'))
		accounts_button.connect('clicked', self.on_accounts_button_clicked)
		box.add(accounts_button)
		# Take Game Screenshot button
		self.take_screenshot_button = Gtk.ModelButton(' Take Game Screenshot')
		self.take_screenshot_button.set_alignment(0, 0.5)
		self.take_screenshot_button.set_image(Gtk.Image(icon_name='camera-photo'))
		self.take_screenshot_button.set_sensitive(False)
		self.take_screenshot_button.connect('clicked', self.on_take_screenshot_button_clicked)
		box.add(self.take_screenshot_button)
		# Open Log File button
		open_log_button = Gtk.ModelButton(' Open Log File')
		open_log_button.set_alignment(0, 0.5)
		open_log_button.set_image(Gtk.Image(icon_name='text-x-generic'))
		open_log_button.connect('clicked', lambda button: tools.open_file_in_editor(logger.get_filename()))
		box.add(open_log_button)
		# About button
		about_button = Gtk.ModelButton(' About')
		about_button.set_alignment(0, 0.5)
		about_button.set_image(Gtk.Image(icon_name='help-about'))
		about_button.connect('clicked', self.on_about_button_clicked)
		box.add(about_button)

	def log_view_auto_scroll(self, textview, event):
		adj = textview.get_vadjustment()
		adj.set_value(adj.get_upper() - adj.get_page_size())

	def debug_view_auto_scroll(self, textview, event):
		adj = textview.get_vadjustment()
		adj.set_value(adj.get_upper() - adj.get_page_size())

	def create_tabs(self):
		bot_notebook = Gtk.Notebook()
		bot_notebook.set_border_width(2)
		self.add(bot_notebook)
		self.config_notebook = Gtk.Notebook()
		self.log_notebook = Gtk.Notebook()
		self.log_notebook.set_size_request(-1, 200)
		## Log Tab
		log_page = Gtk.ScrolledWindow()
		self.log_view = Gtk.TextView()
		self.log_view.set_border_width(5)
		self.log_view.set_editable(False)
		self.log_view.set_wrap_mode(Gtk.WrapMode.WORD)
		self.log_view.connect('size-allocate', self.log_view_auto_scroll)
		self.log_buf = self.log_view.get_buffer()
		self.red_text_tag = self.log_buf.create_tag('red', foreground='#dc3545')
		self.green_text_tag = self.log_buf.create_tag('green', foreground='#28a745')
		self.blue_text_tag = self.log_buf.create_tag('blue', foreground='#007bff')
		log_page.add(self.log_view)
		self.log_notebook.append_page(log_page, Gtk.Label('Log'))
		## Debug Tab
		self.debug_page = Gtk.ScrolledWindow()
		self.debug_view = Gtk.TextView()
		self.debug_view.set_border_width(5)
		self.debug_view.set_editable(False)
		self.debug_view.set_wrap_mode(Gtk.WrapMode.WORD)
		self.debug_view.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('black'))
		self.debug_view.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse('white'))
		self.debug_view.connect('size-allocate', self.debug_view_auto_scroll)
		self.debug_buf = self.debug_view.get_buffer()
		self.debug_page.add(self.debug_view)
		self.log_notebook.append_page(self.debug_page, Gtk.Label('Debug'))
		### Bot Tab
		bot_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		bot_page.set_border_width(2)
		bot_page.add(self.config_notebook)
		bot_page.pack_start(self.log_notebook, True, True, 0)
		bot_notebook.append_page(bot_page, Gtk.Label('Bot'))
		## Config Tab
		self.bot_config_widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		self.bot_config_widgets.set_border_width(10)
		self.config_notebook.append_page(self.bot_config_widgets, Gtk.Label('Config'))
		## Game Window
		self.bot_config_widgets.add(Gtk.Label('<b>Game Window</b>', xalign=0, use_markup=True))
		game_window_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.bot_config_widgets.add(game_window_box)
		# ComboBox
		self.game_window_combo = Gtk.ComboBoxText()
		self.game_window_combo.set_margin_left(10)
		self.populate_game_window_combo()
		self.game_window_combo.connect('changed', self.on_game_window_combo_changed)
		game_window_box.pack_start(self.game_window_combo, True, True, 0)
		# Refresh
		self.refresh_button = Gtk.Button()
		self.refresh_button.set_image(Gtk.Image(icon_name='view-refresh'))
		self.refresh_button.set_tooltip_text('Refresh')
		self.refresh_button.connect('clicked', self.on_refresh_button_clicked)
		game_window_box.add(self.refresh_button)
		# Unbind
		self.unbind_button = Gtk.Button()
		self.unbind_button.set_image(Gtk.Image(icon_name='view-restore'))
		self.unbind_button.set_tooltip_text('Unbind')
		self.unbind_button.connect('clicked', self.on_unbind_button_clicked)
		game_window_box.add(self.unbind_button)
		## Bot Path
		self.bot_config_widgets.add(Gtk.Label('<b>Bot Path</b>', xalign=0, use_markup=True))
		# To do multiple paths, the user can load a .paths file which contains many .path
		bot_path_filechooserbutton = FileChooserButton(title='Choose bot path', filter=('Bot Path', '*.path*'))
		bot_path_filechooserbutton.set_margin_left(10)
		bot_path_filechooserbutton.set_current_folder(tools.get_full_path('paths'))
		bot_path_filechooserbutton.connect('file-set', self.on_bot_path_changed)
		self.bot_config_widgets.add(bot_path_filechooserbutton)
		## Start From Step
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		self.bot_config_widgets.add(hbox)
		hbox.add(Gtk.Label('Start From Step'))
		self.step_spin_button = SpinButton(min=1, max=1000)
		self.step_spin_button.set_margin_left(10)
		hbox.pack_end(self.step_spin_button, False, False, 0)
		## Repeat Path
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		hbox.add(Gtk.Label('Repeat Path'))
		self.bot_config_widgets.add(hbox)
		# Switch
		self.repeat_switch = Gtk.Switch()
		self.repeat_switch.connect('notify::active', lambda switch, pspec: self.repeat_spin_button.set_sensitive(switch.get_active()))
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		vbox.pack_start(self.repeat_switch, True, False, 0)
		hbox.add(vbox)
		# SpinButton
		self.repeat_spin_button = SpinButton(min=2, max=1000)
		self.repeat_spin_button.set_tooltip_text('Number of times')
		self.repeat_spin_button.set_sensitive(False)
		hbox.pack_end(self.repeat_spin_button, False, False, 0)
		## Connect To Account
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('<b>Connect To Account</b>', xalign=0, use_markup=True))
		self.bot_config_widgets.add(hbox)
		# Switch
		self.connect_to_account_switch = Gtk.Switch()
		self.connect_to_account_switch.connect('notify::active', lambda switch, pspec: self.connect_to_account_box.set_sensitive(switch.get_active()))
		hbox.pack_end(self.connect_to_account_switch, False, False, 0)
		# Box
		self.connect_to_account_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		self.connect_to_account_box.set_margin_left(10)
		self.connect_to_account_box.set_sensitive(False)
		self.bot_config_widgets.add(self.connect_to_account_box)
		# Account
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('Account'))
		self.connect_to_account_box.add(hbox)
		# Combo
		accounts_list = accounts.load()
		self.accounts_combo = TextValueComboBox(accounts_list, model=Gtk.ListStore(str, int), text_key='login', value_key='id', sort_key='position')
		self.accounts_combo.set_size_request(120, -1)
		hbox.pack_end(self.accounts_combo, False, False, 0)
		# Disconnect after
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('Disconnect after'))
		self.connect_to_account_box.add(hbox)
		# Switch
		self.disconnect_after_switch = Gtk.Switch()
		hbox.pack_end(self.disconnect_after_switch, False, False, 0)
		## State Tab
		bot_state_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		bot_state_page.set_border_width(10)
		self.config_notebook.append_page(bot_state_page, Gtk.Label('State'))
		# Pod
		self.podbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		bot_state_page.add(self.podbar_box)
		self.podbar_box.add(Gtk.Label('<b>Pod</b>', xalign=0, use_markup=True))
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.podbar_box.pack_start(vbox, True, True, 0)
		self.podbar = Gtk.ProgressBar()
		vbox.pack_start(self.podbar, True, False, 0)
		# MiniMap
		self.minimap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		bot_state_page.add(self.minimap_box)
		self.minimap_box.add(Gtk.Label('<b>MiniMap</b>', xalign=0, use_markup=True))
		self.minimap = MiniMap(grid_size=(14, 14))
		self.minimap.set_size_request(-1, 240)
		self.minimap_box.add(self.minimap)
		## Dev tools Tab
		if '--dev' in self.args:
			dev_tools_page = DevToolsWidget(self)
			self.config_notebook.append_page(dev_tools_page, Gtk.Label('Dev Tools'))
			#self.config_notebook.show_all()
			#self.config_notebook.set_current_page(2)
		## Start
		button_box = ButtonBox(centered=True, linked=True)
		bot_page.pack_end(button_box, False, False, 0)
		self.start_button = Gtk.Button()
		self.start_button.set_tooltip_text('Start')
		self.start_button.set_image(Gtk.Image(icon_name='media-playback-start'))
		self.start_button.connect('clicked', self.on_start_button_clicked)
		button_box.add(self.start_button)
		## Pause
		self.pause_button = Gtk.Button()
		self.pause_button.set_image(Gtk.Image(icon_name='media-playback-pause'))
		self.pause_button.set_tooltip_text('Pause')
		self.pause_button.set_sensitive(False)
		self.pause_button.connect('clicked', self.on_pause_button_clicked)
		button_box.add(self.pause_button)
		## Stop
		self.stop_button = Gtk.Button()
		self.stop_button.set_image(Gtk.Image(icon_name='media-playback-stop'))
		self.stop_button.set_tooltip_text('Stop')
		self.stop_button.set_sensitive(False)
		self.stop_button.connect('clicked', self.on_stop_button_clicked)
		button_box.add(self.stop_button)
		### Path Tab
		path_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		path_page.set_border_width(10)
		bot_notebook.append_page(path_page, Gtk.Label('Path'))
		## Movement
		path_page.add(Gtk.Label('<b>Movement</b>', xalign=0, use_markup=True))
		button_box = ButtonBox(orientation=Gtk.Orientation.VERTICAL, centered=True)
		path_page.add(button_box)
		# Up
		up_button = Gtk.Button()
		up_button.set_image(Gtk.Image(icon_name='go-up'))
		up_button.connect('clicked', lambda button: self.path_listbox.append_text('Move(UP)'))
		button_box.add(up_button)
		# Left
		left_button = Gtk.Button()
		left_button.set_image(Gtk.Image(icon_name='go-previous'))
		left_button.connect('clicked', lambda button: self.path_listbox.append_text('Move(LEFT)'))
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
		hbox.add(left_button)
		button_box.add(hbox)
		# Right
		right_button = Gtk.Button()
		right_button.set_image(Gtk.Image(icon_name='go-next'))
		right_button.connect('clicked', lambda buton: self.path_listbox.append_text('Move(RIGHT)'))
		hbox.add(right_button)
		# Down
		down_button = Gtk.Button()
		down_button.set_image(Gtk.Image(icon_name='go-down'))
		down_button.connect('clicked', lambda button: self.path_listbox.append_text('Move(DOWN)'))
		button_box.add(down_button)
		## Action
		path_page.add(Gtk.Label('<b>Action</b>', xalign=0, use_markup=True))
		stack_listbox = StackListBox()
		path_page.add(stack_listbox)
		## Enclos
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/enclos.png'), 24, 24)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Enclos')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Location
		widget.add(Gtk.Label('<b>Location</b>', xalign=0, use_markup=True))
		self.enclos_location_combo = CustomComboBox(data.Enclos, sort=True)
		self.enclos_location_combo.set_margin_left(10)
		widget.add(self.enclos_location_combo)
		# Type
		widget.add(Gtk.Label('<b>Type</b>', xalign=0, use_markup=True))
		self.enclos_type_combo = CustomComboBox(data.EnclosType, sort=True)
		self.enclos_type_combo.set_margin_left(10)
		widget.add(self.enclos_type_combo)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Enclos(location=%s,type=%s)' % (self.enclos_location_combo.get_active_text(), self.enclos_type_combo.get_active_text())))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.add(button_box)
		## Zaap
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/zaap.png'), 24, 24)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Zaap')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# From
		widget.add(Gtk.Label('<b>From</b>', xalign=0, use_markup=True))
		self.zaap_from_combo = CustomComboBox(['Havenbag'], sort=True)
		self.zaap_from_combo.set_margin_left(10)
		self.zaap_from_combo.connect('changed', lambda combo:
			combo.sync_with_combo(self.zaap_to_combo)
		)
		widget.add(self.zaap_from_combo)
		# To
		widget.add(Gtk.Label('<b>To</b>', xalign=0, use_markup=True))
		self.zaap_to_combo = CustomComboBox(data.Zaap['To'], sort=True)
		self.zaap_to_combo.set_margin_left(10)
		self.zaap_to_combo.connect('changed', lambda combo:
			combo.sync_with_combo(self.zaap_from_combo)
		)
		widget.add(self.zaap_to_combo)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Zaap(from=%s,to=%s)' % (self.zaap_from_combo.get_active_text(), self.zaap_to_combo.get_active_text())))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.add(button_box)
		## Zaapi
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/destination.png'), 24, 24)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Zaapi')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# From
		widget.add(Gtk.Label('<b>From</b>', xalign=0, use_markup=True))
		self.zaapi_from_combo = CustomComboBox(data.Zaapi['From'], sort=True)
		self.zaapi_from_combo.set_margin_left(10)
		self.zaapi_from_combo.connect('changed', lambda combo:
			combo.sync_with_combo(self.zaapi_to_combo, use_contains=True)
		)
		widget.add(self.zaapi_from_combo)
		# To
		widget.add(Gtk.Label('<b>To</b>', xalign=0, use_markup=True))
		self.zaapi_to_combo = CustomComboBox(data.Zaapi['To'], sort=True)
		self.zaapi_to_combo.set_margin_left(10)
		self.zaapi_to_combo.connect('changed', lambda combo:
			combo.sync_with_combo(self.zaapi_from_combo, use_contains=True)
		)
		widget.add(self.zaapi_to_combo)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Zaapi(from=%s,to=%s)' % (self.zaapi_from_combo.get_active_text(), self.zaapi_to_combo.get_active_text())))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.add(button_box)
		## Collect
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/miner.png'), 24, 24)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Collect')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Map
		widget.add(Gtk.Label('<b>Map</b>', xalign=0, use_markup=True))
		self.collect_map_combo = CustomComboBox(maps.load(), sort=True)
		self.collect_map_combo.set_margin_left(10)
		widget.add(self.collect_map_combo)
		# Store Path
		widget.add(Gtk.Label('<b>Store Path</b>', xalign=0, use_markup=True))
		# Combo
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		self.collect_sp_combo_radio = Gtk.RadioButton()
		self.collect_sp_combo_radio.set_active(True)
		hbox.add(self.collect_sp_combo_radio)
		self.collect_sp_combo = CustomComboBox(data.BankPath, sort=True)
		self.collect_sp_combo.connect('changed', lambda combo: self.collect_sp_combo_radio.set_active(True))
		hbox.pack_start(self.collect_sp_combo, True, True, 0)
		widget.add(hbox)
		# FileChooserButton
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		self.collect_sp_filechooser_radio = Gtk.RadioButton(group=self.collect_sp_combo_radio)
		hbox.add(self.collect_sp_filechooser_radio)
		self.collect_sp_filechooserbutton = FileChooserButton(title='Choose store path', filter=('Store Path', '*.path'))
		self.collect_sp_filechooserbutton.set_current_folder(tools.get_full_path('paths'))
		self.collect_sp_filechooserbutton.get_children()[0].get_children()[0].get_children()[1].set_max_width_chars(12)
		self.collect_sp_filechooserbutton.connect('file-set', lambda filechooserbutton: self.collect_sp_filechooser_radio.set_active(True))
		hbox.pack_start(self.collect_sp_filechooserbutton, True, True, 0)
		widget.add(hbox)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Collect(map=%s,store_path=%s)' % (self.collect_map_combo.get_active_text(), self.collect_sp_combo.get_active_text() if self.collect_sp_combo_radio.get_active() else (self.collect_sp_filechooserbutton.get_filename() or 'None').replace(tools.get_full_path('') + '/', ''))))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.add(button_box)
		## Click
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/arrow.png'), 24, 24)
		#pixbuf = Gdk.Cursor(Gdk.CursorType.ARROW).get_image().scale_simple(24, 24, GdkPixbuf.InterpType.BILINEAR)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Click')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Twice
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('<b>Twice</b>', xalign=0, use_markup=True))
		self.click_twice_switch = Gtk.Switch()
		hbox.pack_end(self.click_twice_switch, False, False, 0)
		widget.add(hbox)
		# Color sentitive
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('<b>Color Sensitive</b>', xalign=0, use_markup=True))
		self.click_color_sensitive = Gtk.Switch()
		hbox.pack_end(self.click_color_sensitive, False, False, 0)
		widget.add(hbox)
		# Hot key to be pressed before click (ex : ctrl + click)
		self.hot_keys_combo = CustomComboBox(data.KeyboardShortcuts, sort=True)
		self.hot_keys_combo.set_margin_left(10)
		widget.add(self.hot_keys_combo)
		# Location
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('<b>Location</b>', xalign=0, use_markup=True))
		cursor_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/crosshair.png'), 16, 16)
		#cursor_pixbuf = Gdk.Cursor(Gdk.CursorType.CROSSHAIR).get_image().scale_simple(18, 18, GdkPixbuf.InterpType.BILINEAR)
		self.select_button = Gtk.Button()
		self.select_button.set_size_request(40, -1)
		self.select_button.set_tooltip_text('Select')
		self.select_button.set_image(Gtk.Image(pixbuf=cursor_pixbuf))
		self.select_button.connect('clicked', self.on_select_button_clicked)
		hbox.pack_end(self.select_button, False, False, 0)
		widget.add(hbox)
		## Scroll
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/scroll.png'), 24, 24)
		#pixbuf = Gdk.Cursor(Gdk.CursorType.SB_V_DOUBLE_ARROW).get_image().scale_simple(18, 18, GdkPixbuf.InterpType.BILINEAR)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Scroll')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Direction
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('<b>Direction</b>', xalign=0, use_markup=True))
		self.scroll_direction_combo = CustomComboBox(['up', 'down'])
		self.scroll_direction_combo.set_active(1)
		hbox.pack_end(self.scroll_direction_combo, False, False, 0)
		widget.add(hbox)
		# Times
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('<b>Times</b>', xalign=0, use_markup=True))
		self.scroll_spin_button = SpinButton(min=1, max=10)
		hbox.pack_end(self.scroll_spin_button, False, False, 0)
		widget.add(hbox)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Scroll(direction=%s,times=%s)' % (self.scroll_direction_combo.get_active_text(), self.scroll_spin_button.get_value_as_int())))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.add(button_box)
		## Wait
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/hourglass.png'), 24, 24)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Wait')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Duration
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		label = Gtk.Label('<b>Duration</b>', xalign=0, use_markup=True)
		label.set_tooltip_text('(in seconds)')
		self.duration_radio = Gtk.RadioButton()
		self.duration_radio.add(label)
		hbox.add(self.duration_radio)
		self.duration_spin_button = SpinButton(min=1, max=60)
		self.duration_spin_button.connect('value-changed', lambda button: self.duration_radio.set_active(True))
		hbox.pack_end(self.duration_spin_button, False, False, 0)
		widget.add(hbox)
		# Pause Bot
		self.pause_bot_radio = Gtk.RadioButton(group=self.duration_radio)
		self.pause_bot_radio.add(Gtk.Label('<b>Pause Bot</b>', xalign=0, use_markup=True))
		widget.add(self.pause_bot_radio)
		# Monitor Game Screen
		self.monitor_game_screen_radio = Gtk.RadioButton(group=self.duration_radio)
		self.monitor_game_screen_radio.add(Gtk.Label('<b>Until map/screen changes</b>', xalign=0, use_markup=True))
		widget.add(self.monitor_game_screen_radio)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', self.on_wait_add_button_clicked)
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.add(button_box)
		## Keyboard
		image = Gtk.Image(icon_name='input-keyboard', icon_size=Gtk.IconSize.LARGE_TOOLBAR)
		label = ImageLabel(image, 'Keyboard')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Press Key
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.press_key_radio = Gtk.RadioButton()
		self.press_key_radio.add(Gtk.Label('<b>Press Key</b>', xalign=0, use_markup=True))
		hbox.add(self.press_key_radio)
		self.key_label = Gtk.Label()
		hbox.add(self.key_label)
		widget.add(hbox)
		self.keys_combo = CustomComboBox(data.KeyboardShortcuts, sort=True)
		self.keys_combo.set_margin_left(10)
		self.keys_combo.connect('changed', lambda combo: (
				self.key_label.set_text('(' + data.KeyboardShortcuts[combo.get_active_text()] + ')'),
				self.press_key_radio.set_active(True)
			)
		)
		widget.add(self.keys_combo)
		# Type Text
		self.type_text_radio = Gtk.RadioButton(group=self.press_key_radio)
		self.type_text_radio.add(Gtk.Label('<b>Type Text</b>', xalign=0, use_markup=True))
		widget.add(self.type_text_radio)
		self.type_text_entry = Gtk.Entry(placeholder_text='Text')
		self.type_text_entry.set_margin_left(10)
		self.type_text_entry.set_width_chars(10)
		self.type_text_entry.connect('focus-in-event', lambda entry, event: self.type_text_radio.set_active(True))
		widget.add(self.type_text_entry)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', self.on_keyboard_add_button_clicked)
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.add(button_box)
		## Connect
		image = Gtk.Image(icon_name='network-wired', icon_size=Gtk.IconSize.LARGE_TOOLBAR)
		label = ImageLabel(image, 'Connect')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Account
		widget.add(Gtk.Label('<b>Account</b>', xalign=0, use_markup=True))
		self.connect_accounts_combo = TextValueComboBox(accounts_list, model=Gtk.ListStore(str, int), text_key='login', value_key='id', sort_key='position')
		self.connect_accounts_combo.set_margin_left(10)
		widget.add(self.connect_accounts_combo)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Connect(account_id=%s)' % self.connect_accounts_combo.get_active_value()))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.add(button_box)
		## Disconnect
		image = Gtk.Image(icon_name='network-idle', icon_size=Gtk.IconSize.LARGE_TOOLBAR)
		label = ImageLabel(image, 'Disconnect')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Exit Game
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		widget.add(hbox)
		hbox.add(Gtk.Label('<b>Exit Game</b>', xalign=0, use_markup=True))
		self.exit_game_switch = Gtk.Switch()
		hbox.pack_end(self.exit_game_switch, False, False, 0)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Disconnect(%s)' % self.exit_game_switch.get_active()))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.add(button_box)
		## Separator
		path_page.add(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, margin=5))
		## Listbox
		self.path_listbox = CustomListBox(parent=self)
		path_page.pack_end(self.path_listbox, True, True, 0)
		# Load
		load_path_button = Gtk.Button()
		load_path_button.set_tooltip_text('Load')
		load_path_button.set_image(Gtk.Image(icon_name='document-open'))
		load_path_button.connect('clicked', self.on_load_path_button_clicked)
		self.path_listbox.add_button(load_path_button)
		# Save
		self.save_path_button = Gtk.Button()
		self.save_path_button.set_tooltip_text('Save')
		self.save_path_button.set_sensitive(False)
		self.save_path_button.set_image(Gtk.Image(icon_name='document-save-as'))
		self.save_path_button.connect('clicked', self.on_save_path_button_clicked)
		self.path_listbox.add_button(self.save_path_button)
		self.path_listbox.on_add(self.on_path_listbox_add)
		self.path_listbox.on_delete(self.on_path_listbox_delete)
		### Map Tab
		map_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		map_page.set_border_width(10)
		bot_notebook.append_page(map_page, Gtk.Label('Map'))
		## View
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('<b>View</b>', xalign=0, use_markup=True))
		map_page.add(hbox)
		# Options
		menu_image = MenuImage()
		hbox.add(menu_image)
		options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		menu_image.set_widget(options_box)
		# Use data colors
		use_data_colors_check = Gtk.CheckButton('Use data colors')
		use_data_colors_check.connect('clicked', lambda button: self.map_view.set_use_origin_colors(button.get_active()))
		options_box.add(use_data_colors_check)
		# Add borders
		add_borders_check = Gtk.CheckButton('Add borders')
		add_borders_check.connect('clicked', lambda button: self.map_view.set_add_borders(button.get_active()))
		options_box.add(add_borders_check)
		# Show selected data only
		self.show_selected_data_only_check = Gtk.CheckButton('Show selected data only')
		self.show_selected_data_only_check.connect('clicked', self.on_show_selected_data_only_check_clicked)
		options_box.add(self.show_selected_data_only_check)
		# Map View
		self.map_view = MiniMap()
		map_page.pack_start(self.map_view, True, True, 0)
		## Data
		map_page.add(Gtk.Label('<b>Data</b>', xalign=0, use_markup=True))
		self.map_data_listbox = CustomListBox(parent=self, allow_moving=False)
		map_page.pack_start(self.map_data_listbox, True, True, 0)
		# Select
		self.select_resource_button = Gtk.Button()
		self.select_resource_button.set_tooltip_text('Select resource')
		self.select_resource_button.set_image(Gtk.Image(pixbuf=cursor_pixbuf))
		self.select_resource_button.connect('clicked', self.on_select_resource_button_clicked)
		self.map_data_listbox.add_button(self.select_resource_button)
		# Simulate click
		self.simulate_resource_click_button = Gtk.Button()
		self.simulate_resource_click_button.set_tooltip_text('Simulate click')
		self.simulate_resource_click_button.set_sensitive(False)
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/hand.png'), 16, 16)
		self.simulate_resource_click_button.set_image(Gtk.Image(pixbuf=pixbuf))
		self.simulate_resource_click_button.connect('clicked', self.on_simulate_resource_click_button_clicked)
		self.map_data_listbox.add_button(self.simulate_resource_click_button)
		# Edit
		edit_map_button = MenuButton(icon_name='document-edit-symbolic')
		edit_map_button.set_tooltip_text('Edit')
		self.map_data_listbox.add_button(edit_map_button)
		button_box = ButtonBox(linked=True)
		edit_map_button.add(button_box)
		# Load
		load_map_button = Gtk.Button()
		load_map_button.set_tooltip_text('Load')
		load_map_button.set_image(Gtk.Image(icon_name='document-open'))
		load_map_button.connect('clicked', self.on_load_map_button_clicked)
		button_box.add(load_map_button)
		# Delete
		delete_map_button = Gtk.Button()
		delete_map_button.set_tooltip_text('Delete')
		delete_map_button.set_image(Gtk.Image(icon_name='edit-delete'))
		delete_map_button.connect('clicked', self.on_delete_map_button_clicked)
		button_box.add(delete_map_button)
		# Save
		self.save_map_button = Gtk.Button()
		self.save_map_button.set_tooltip_text('Save')
		self.save_map_button.set_sensitive(False)
		self.save_map_button.set_image(Gtk.Image(icon_name='document-save-as'))
		self.save_map_button.connect('clicked', self.on_save_map_button_clicked)
		self.map_data_listbox.add_button(self.save_map_button)
		self.map_data_listbox.on_add(self.on_map_data_listbox_add)
		self.map_data_listbox.on_delete(self.on_map_data_listbox_delete)
		self.map_data_listbox.on_activate(self.on_map_data_listbox_activate)

	def on_show_selected_data_only_check_clicked(self, button):
		self.map_view.clear()
		if button.get_active():
			selected_row = self.map_data_listbox.listbox.get_selected_row()
			if selected_row:
				text = self.map_data_listbox.get_row_text(selected_row)
				point = maps.to_array(text)
				self.map_view.add_point(point, 'Resource', MiniMap.point_colors['Resource'])
		else:
			points = []
			for row in self.map_data_listbox.get_rows():
				text = self.map_data_listbox.get_row_text(row)
				point = maps.to_array(text)
				points.append(point)
			self.map_view.add_points(points, 'Resource', MiniMap.point_colors['Resource'])

	def on_simulate_resource_click_button_clicked(self, button):
		selected_row = self.map_data_listbox.listbox.get_selected_row()
		if selected_row:
			text = self.map_data_listbox.get_row_text(selected_row)
			data = maps.to_array(text)
			x, y, width, height, color = (data['x'], data['y'], data['width'], data['height'], data['color'])
			#print('x: %d, y: %d, width: %d, height: %d' % (x, y, width, height))
			# adjust for game area
			if self.game_window and not self.game_window.is_destroyed() and self.game_window_location:
				game_x, game_y, game_width, game_height = self.game_window_location
				#print('game_x: %d, game_y: %d, game_width: %d, game_height: %d' % (game_x, game_y, game_width, game_height))
				click_x, click_y = tools.adjust_click_position(x, y, width, height, game_x, game_y, game_width, game_height)
			else:
				click_x = x
				click_y = y
			# perform click
			self.debug('Simulate click on x: %d, y: %d' % (click_x, click_y))
			tools.perform_click(click_x, click_y)

	def on_load_map_button_clicked(self, button):
		dialog = LoadMapDialog(self)
		dialog.run()

	def on_delete_map_button_clicked(self, button):
		dialog = DeleteMapDialog(self)
		dialog.run()

	def on_save_map_button_clicked(self, button):
		dialog = SaveMapDialog(self)
		dialog.run()

	def add_map_data(self, location):
		# append to listbox
		text = '{"x": %d, "y": %d, "width": %d, "height": %d, "color": "%s"}' % location
		self.map_data_listbox.append_text(text)
		# append to view
		point = maps.to_array(text)
		self.map_view.add_point(point, 'Resource', MiniMap.point_colors['Resource'])
		self.select_resource_button.set_sensitive(True)
		self.set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))

	def on_select_resource_button_clicked(self, button):
		button.set_sensitive(False)
		self.set_cursor(Gdk.Cursor(Gdk.CursorType.CROSSHAIR))
		Thread(target=self.wait_for_click, args=(self.add_map_data, self.game_window_location)).start()

	def on_map_data_listbox_add(self):
		if not self.save_map_button.get_sensitive():
			self.save_map_button.set_sensitive(True)
		if not self.simulate_resource_click_button.get_sensitive():
			self.simulate_resource_click_button.set_sensitive(True)

	def on_map_data_listbox_delete(self, row_index):
		if self.show_selected_data_only_check.get_active():
			self.map_view.clear()
		else:
			self.map_view.remove_point(row_index)
		self.simulate_resource_click_button.set_sensitive(False)
		if self.map_data_listbox.is_empty():
			self.save_map_button.set_sensitive(False)

	def on_map_data_listbox_activate(self):
		if not self.simulate_resource_click_button.get_sensitive():
			self.simulate_resource_click_button.set_sensitive(True)
		if self.show_selected_data_only_check.get_active():
			self.on_show_selected_data_only_check_clicked(self.show_selected_data_only_check)

	def on_path_listbox_add(self):
		if not self.save_path_button.get_sensitive():
			self.save_path_button.set_sensitive(True)

	def on_path_listbox_delete(self, row_index):
		if self.path_listbox.is_empty():
			self.save_path_button.set_sensitive(False)

	def on_load_path_button_clicked(self, button):
		dialog = OpenFileDialog('Load Path', self, ('Bot Path', '*.path'))
		dialog.set_current_folder(tools.get_full_path('paths'))
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			# read file
			path = tools.read_file(dialog.get_filename())
			# append to path listbox
			for line in path.splitlines():
				self.path_listbox.append_text(line)

		dialog.destroy()

	def on_save_path_button_clicked(self, button):
		dialog = SaveFileDialog('Save as', self, ('Bot Path', '*.path'))
		dialog.set_current_folder(tools.get_full_path('paths'))
		dialog.set_current_name('path_' + tools.get_date_time() + '.path')
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			# get all rows text
			text = ''
			for row in self.path_listbox.get_rows():
				text += self.path_listbox.get_row_text(row) + '\n'
			# save it to file
			tools.save_text_to_file(text, dialog.get_filename())

		dialog.destroy()

	def on_wait_add_button_clicked(self, button):
		if self.pause_bot_radio.get_active():
			self.path_listbox.append_text('Pause()')
		elif self.monitor_game_screen_radio.get_active():
			self.path_listbox.append_text('MonitorGameScreen()')
		else:
			self.path_listbox.append_text('Wait(%s)' % self.duration_spin_button.get_value_as_int())

	def on_keyboard_add_button_clicked(self, button):
		if self.press_key_radio.get_active():
			selected = self.keys_combo.get_active_text()
			self.path_listbox.append_text('PressKey(%s)' % parser.parse_data(data.KeyboardShortcuts, selected))
		else:
			self.path_listbox.append_text('TypeText(%s)' % self.type_text_entry.get_text())

	def wait_for_click(self, callback, game_location=None):
		# wait for click
		tools.wait_for_mouse_event('left_down')
		# get mouse position & screen size
		x, y = tools.get_mouse_position()
		width, height = tools.get_screen_size()
		# get pixel color
		color = tools.get_pixel_color(x, y)
		# adjust location to game window
		if game_location is not None:
			# get game area location
			game_x, game_y, game_width, game_height = game_location
			#print('x: %d, y: %d, game_x: %d, game_y: %d, game_width: %d, game_height: %d' % (x, y, game_x, game_y, game_width, game_height))
			# scale to game area
			if tools.position_is_inside_bounds(x, y, game_x, game_y, game_width, game_height):
				# position is inside game area, so we fit x & y to it
				x = x - game_x
				y = y - game_y
				width = game_width
				height = game_height
		# execute callback
		GObject.idle_add(callback, (x, y, width, height, color))

	def add_click(self, location):
		x, y, width, height, color = location
		twice = self.click_twice_switch.get_active()
		color_sensitive = self.click_color_sensitive.get_active()
		hot_key = self.hot_keys_combo.get_active_text()
		instruction = ""
		if color_sensitive:
			instruction = f"Click(x={x},y={y},width={width},height={height},twice={twice},hotkey={hot_key}, r={color[0]}, g={color[1]}, b={color[2]})"
		else:
			instruction = f"Click(x={x},y={y},width={width},height={height},twice={twice},hotkey={hot_key})"
		self.path_listbox.append_text(instruction)
		self.select_button.set_sensitive(True)
		self.set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))

	def set_cursor(self, cursor):
		window = self.get_window() # Gdk.get_default_root_window()
		window.set_cursor(cursor)

	def on_select_button_clicked(self, button):
		button.set_sensitive(False)
		self.set_cursor(Gdk.Cursor(Gdk.CursorType.CROSSHAIR))
		Thread(target=self.wait_for_click, args=(self.add_click, self.game_window_location)).start()

	def on_start_button_clicked(self, button):
		if self.game_window is None:
			AlertDialog(self, 'Please select a game window')
		elif self.game_window.is_destroyed():
			AlertDialog(self, 'Chosen game window was destroyed')
		elif not self.bot_paths:
			AlertDialog(self, 'Please select a bot path')
		else:
			# ensure that game window is in the right place
			self.move_resize_game_window(self.game_window_location)
			# start bot thread
			if self.bot_thread is None or not self.bot_thread.isAlive():
				# get thread parameters
				start_from_step = self.step_spin_button.get_value_as_int()
				repeat_path = self.repeat_spin_button.get_value_as_int() if self.repeat_switch.get_active() else 1
				if self.connect_to_account_switch.get_active():
					account_id = self.accounts_combo.get_active_value()
					disconnect_after = self.disconnect_after_switch.get_active()
				else:
					account_id = None
					disconnect_after = False
				# run thread
				self.bot_thread = BotThread(self, self.game_window_location, start_from_step, repeat_path, account_id, disconnect_after)
				self.bot_thread.start()
				self.settings_button.set_sensitive(False)
				self.bot_config_widgets.set_sensitive(False)
			# resume bot thread if paused
			else:
				self.bot_thread.resume(self.game_window_location)
			# show bot state & debug tabs
			self.log_notebook.set_current_page(1)
			if self.settings['Debug']['Enabled']:
				self.config_notebook.set_current_page(1)
			# enable/disable buttons
			self.start_button.set_image(Gtk.Image(file=tools.get_full_path('icons/loader.gif')))
			self.start_button.set_sensitive(False)
			self.pause_button.set_sensitive(True)
			self.stop_button.set_sensitive(True)

	def set_internet_state(self, state):
		if state:
			self.start_button.set_image(Gtk.Image(file=tools.get_full_path('icons/loader.gif')))
		else:
			self.log(tools.print_internet_state(state), LogType.Error)
			self.start_button.set_image(Gtk.Image(icon_name='network-error'))

	def set_buttons_to_paused(self):
		self.start_button.set_tooltip_text('Resume')
		self.start_button.set_image(Gtk.Image(icon_name='media-skip-forward'))
		self.start_button.set_sensitive(True)
		self.pause_button.set_sensitive(False)

	def pause_bot(self):
		if self.bot_thread and self.bot_thread.isAlive() and self.bot_thread.pause_event.isSet():
			self.bot_thread.pause()

	def on_pause_button_clicked(self, button):
		self.pause_bot()

	def reset_buttons(self):
		self.start_button.set_tooltip_text('Start')
		self.start_button.set_image(Gtk.Image(icon_name='media-playback-start'))
		self.start_button.set_sensitive(True)
		self.stop_button.set_sensitive(False)
		self.pause_button.set_sensitive(False)
		self.settings_button.set_sensitive(True)
		self.bot_config_widgets.set_sensitive(True)

	def on_stop_button_clicked(self, button):
		if self.bot_thread and self.bot_thread.isAlive():
			self.bot_thread.stop()
			self.reset_buttons()

	def on_bot_path_changed(self, filechooserbutton):
		'''
		This function populates the self.bot_paths attribute
		with the paths specified. The chosen file can either be
		single path or a list of paths provided in a .paths file.
		'''
		path_filename = filechooserbutton.get_filename()
		_, ext = os.path.splitext(path_filename)
		if ext == ".paths":
			with open(path_filename, "r") as f:
				for path in f:
					self.bot_paths.append(tools.get_full_path("paths/"+path.splitlines()[0]))
		else:
			self.bot_paths = [path_filename]

	def populate_game_window_combo(self):
		self.game_window_combo_ignore_change = True
		self.game_window_combo.remove_all()
		self.game_windowList = tools.get_game_window_list()
		count = len(self.game_windowList)
		if count == 0:
			self.debug('Populate game window combobox, no window found', DebugLevel.High)
		else:
			self.debug('Populate game window combobox, %d window found' % count, DebugLevel.High)
		for window_name in self.game_windowList:
			self.game_window_combo.append_text(window_name)
		self.game_window_combo_ignore_change = False

	def focus_game(self):
		if self.game_window and not self.game_window.is_destroyed():
			#self.debug('Focus game', DebugLevel.High)
			# activate & focus game window
			tools.activate_window(self.game_window)
			#self.game_window.focus(0)

	def move_resize_game_window(self, location):
		if self.game_window and not self.game_window.is_destroyed() and location:
			x, y, width, height = location
			self.debug('Move & resize game window (x: %d, y: %d, width: %d, height: %d)' % (x, y, width, height), DebugLevel.Low)
			self.game_window.unmaximize()
			self.game_window.move_resize(x, y, width, height)
			self.game_window.show() # force show (when minimized)
			tools.activate_window(self.game_window)

	def bind_game_window(self, window_xid):
		self.debug('Bind game window (id: %d)' % window_xid, DebugLevel.Low)
		self.game_window = tools.get_game_window(window_xid)
		if self.game_window:
			bot_width, bot_height = self.get_size()
			bot_decoration_height = self.get_titlebar().get_allocated_height()
			screen_width, screen_height = tools.get_screen_size()
			game_window_left_margin = 1
			game_window_decoration_height = self.settings['Game']['WindowDecorationHeight'] if self.settings['Game']['UseCustomWindowDecorationHeight'] else tools.get_game_window_decoration_height(window_xid)
			game_window_width = screen_width - bot_width - game_window_left_margin
			game_window_height = bot_height if self.settings['Game']['UseCustomWindowDecorationHeight'] else bot_height + bot_decoration_height - game_window_decoration_height
			if game_window_width > 900:
				game_window_width = 900
			bot_x_position = screen_width / 2 - (bot_width + game_window_width) / 2
			bot_y_position = screen_height / 2 - bot_height / 2
			game_window_x_position = bot_x_position + bot_width + game_window_left_margin
			game_window_y_position = bot_y_position + game_window_decoration_height
			# save game window location
			self.game_window_location = (int(game_window_x_position), int(game_window_y_position), int(game_window_width), int(game_window_height))
			# move bot & game window
			self.move(bot_x_position, bot_y_position)
			self.move_resize_game_window(self.game_window_location)
			# enable/disable widgets
			self.refresh_button.hide()
			self.unbind_button.show()
			self.game_window_combo.set_sensitive(False)
			self.take_screenshot_button.set_sensitive(True)

	def on_game_window_combo_changed(self, combo):
		if self.game_windowList and not self.game_window_combo_ignore_change:
			# get selected game window
			selected = combo.get_active_text()
			window_xid = self.game_windowList[selected]
			# bind it
			self.bind_game_window(window_xid)

	def unbind_game_window(self):
		self.debug('Unbind game window')
		if self.settings['Game']['KeepOpen']:
			self.debug('Keep game window open')
		elif self.game_window and not self.game_window.is_destroyed():
			self.game_window.destroy()
		self.game_window = None
		self.game_window_location = None
		self.debug('Game window unbinded')
		# enable/disable widgets
		self.unbind_button.hide()
		self.refresh_button.show()
		self.game_window_combo.set_sensitive(True)
		self.populate_game_window_combo()
		self.take_screenshot_button.set_sensitive(False)

	def on_unbind_button_clicked(self, button):
		self.unbind_game_window()

	def on_refresh_button_clicked(self, button):
		self.populate_game_window_combo()

	# Override the default handler for the delete-event signal
	def do_delete_event(self, event):
		# Show our message dialog
		dialog = Gtk.MessageDialog(text='Are you sure you want to quit?', transient_for=self, buttons=Gtk.ButtonsType.OK_CANCEL, message_type=Gtk.MessageType.QUESTION)
		response = dialog.run()
		dialog.destroy()

		# We only terminate when the user presses the OK button
		if response == Gtk.ResponseType.OK:
			# stop bot thread
			if self.bot_thread and self.bot_thread.isAlive():
				self.bot_thread.stop()
			return False

		# Otherwise we keep the application open
		return True

	def main(self):
		Gtk.main()
