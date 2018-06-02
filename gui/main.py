# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
from lib import tools
from lib import logger
from lib import data
from lib import settings
from lib.threads import BotThread
from lib.shared import LogType, DebugLevel, __program_name__
from .dev import DevToolsWidget
from .custom import *
from .dialog import *

class BotWindow(Gtk.ApplicationWindow):

	game_window = None
	game_area = None
	bot_path = None
	bot_thread = None
	args = tools.get_cmd_args()

	def __init__(self, title=__program_name__):
		GObject.threads_init() # allow threads to update GUI
		Gtk.Window.__init__(self, title=title)
		logger.add_separator()
		# Get settings
		self.settings = settings.load()
		# Header Bar
		self.create_header_bar(title)
		# Tables
		self.htable = Gtk.Table(1, 3, True) # horizontal table
		self.vtable = Gtk.Table(4, 1, True) # vertical table
		self.htable.attach(self.vtable, 1, 3, 0, 1)
		self.add(self.htable)
		# Tabs
		self.create_tabs()
		# Window
		self.set_icon_from_file(tools.get_resource_path('../icons/drago.png'))
		self.set_size_request(900, 700)
		self.set_resizable(False)
		self.connect('destroy', Gtk.main_quit)
		self.show_all()
		self.unplug_button.hide()
		if not self.settings['Debug']['Enabled']:
			self.debug_page.hide()

	def _pop(self, text_buffer, max=100):
		start_iter = text_buffer.get_start_iter()
		end_iter = text_buffer.get_end_iter()
		lines = text_buffer.get_text(start_iter, end_iter, True).splitlines()
		if len(lines) >= max:
			new_text = '\n'.join(lines[1:]) + '\n' # [1:] to remove the first line
			text_buffer.set_text(new_text)

	def _log(self, text, type=LogType.Normal):
		# pop first line if we reached the max number of lines
		self._pop(self.log_buf)
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

	def _debug(self, text, level=DebugLevel.Normal):
		# append to text view
		if self.settings['Debug']['Enabled'] and level >= self.settings['Debug']['Level']:
			self._pop(self.debug_buf)
			position = self.debug_buf.get_end_iter()
			self.debug_buf.insert(position, '[' + tools.get_time() + '] ' + text + '\n')
			logger.debug(text)

	def on_settings_button_clicked(self, button):
		self.popover.show_all()

	def on_about_button_clicked(self, button):
		dialog = AboutDialog(transient_for=self)
		dialog.run()

	def on_take_screenshot_button_clicked(self, button):
		if self.game_window:
			screenshot_name = 'screenshot_' + tools.get_date_time()
			screenshot_path = tools.get_resource_path('../' + screenshot_name)
			tools.take_window_screenshot(self.game_window, screenshot_path)
			self._log("Screenshot saved to '%s'" % screenshot_path, LogType.Info)

	def on_debug_check_clicked(self, check):
		value = check.get_active()
		self.debug_level_combo.set_sensitive(value)
		if value:
			self.debug_page.show()
		else:
			self.debug_page.hide()
		settings.update_and_save(self.settings, key='Debug', subkey='Enabled', value=value)

	def create_header_bar(self, title):
		### Header Bar
		hb = Gtk.HeaderBar(title=title)
		hb.set_show_close_button(True)
		self.set_titlebar(hb)
		## Settings button
		self.settings_button = Gtk.Button()
		self.settings_button.set_image(Gtk.Image(stock=Gtk.STOCK_PROPERTIES))
		self.settings_button.connect('clicked', self.on_settings_button_clicked)
		self.popover = Gtk.Popover(relative_to=self.settings_button, position=Gtk.PositionType.BOTTOM)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		self.popover.add(box)
		# Debug
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_top(5)
		hbox.set_margin_right(5)
		self.debug_check = Gtk.CheckButton('Debug')
		self.debug_check.set_active(self.settings['Debug']['Enabled'])
		self.debug_check.connect('clicked', self.on_debug_check_clicked)
		hbox.add(self.debug_check)
		self.debug_level_combo = CustomComboBox(['High', 'Normal', 'Low'])
		self.debug_level_combo.set_active(self.settings['Debug']['Level'])
		self.debug_level_combo.set_sensitive(self.settings['Debug']['Enabled'])
		self.debug_level_combo.connect('changed', 
			lambda combo: settings.update_and_save(self.settings, key='Debug', subkey='Level', value=combo.get_active()))
		hbox.pack_start(self.debug_level_combo, True, True, 0)
		box.add(hbox)
		# Save dragodindes images
		self.save_dragodindes_images_check = Gtk.CheckButton('Save dragodindes image')
		self.save_dragodindes_images_check.set_active(self.settings['SaveDragodindesImages'])
		self.save_dragodindes_images_check.connect('clicked', 
			lambda check: settings.update_and_save(self.settings, 'SaveDragodindesImages', check.get_active()))
		box.add(self.save_dragodindes_images_check)
		# Keep game checkbox
		self.keep_game_on_unplug_check = Gtk.CheckButton('Keep game open when unplug')
		self.keep_game_on_unplug_check.set_active(self.settings['KeepGameOpen'])
		self.keep_game_on_unplug_check.connect('clicked', 
			lambda check: settings.update_and_save(self.settings, 'KeepGameOpen', check.get_active()))
		box.add(self.keep_game_on_unplug_check)
		# Take game screenshot button
		self.take_screenshot_button = Gtk.ModelButton(' Take game screenshot')
		self.take_screenshot_button.set_alignment(0.1, 0.5)
		self.take_screenshot_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_RECORD))
		self.take_screenshot_button.set_sensitive(False)
		self.take_screenshot_button.connect('clicked', self.on_take_screenshot_button_clicked)
		box.add(self.take_screenshot_button)
		# About button
		about_button = Gtk.ModelButton(' About')
		about_button.set_alignment(0.04, 0.5)
		about_button.set_image(Gtk.Image(stock=Gtk.STOCK_ABOUT))
		about_button.connect('clicked', self.on_about_button_clicked)
		box.add(about_button)
		hb.pack_start(Gtk.Image(file=tools.get_resource_path('../icons/drago_24.png')))
		hb.pack_end(self.settings_button)

	def log_view_auto_scroll(self, textview, event):
		adj = textview.get_vadjustment()
		adj.set_value(adj.get_upper() - adj.get_page_size())

	def debug_view_auto_scroll(self, textview, event):
		adj = textview.get_vadjustment()
		adj.set_value(adj.get_upper() - adj.get_page_size())

	def create_tabs(self):
		log_notebook = Gtk.Notebook()
		log_notebook.set_border_width(2)
		self.vtable.attach(log_notebook, 0, 1, 3, 4)
		bot_notebook = Gtk.Notebook()
		bot_notebook.set_border_width(2)
		self.htable.attach(bot_notebook, 0, 1, 0, 1)
		# Log Tab/Page
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
		log_notebook.append_page(log_page, Gtk.Label('Log'))
		# Debug Tab
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
		log_notebook.append_page(self.debug_page, Gtk.Label('Debug'))
		# Dev tools Tab
		if '--enable-dev-env' in self.args:
			dev_tools_page = DevToolsWidget(self)
			log_notebook.append_page(dev_tools_page, Gtk.Label('Dev Tools'))
			log_notebook.show_all()
			log_notebook.set_current_page(2)
		### Bot Tab
		bot_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		bot_page.set_border_width(10)
		bot_notebook.append_page(bot_page, Gtk.Label('Bot'))
		## Game Window
		bot_page.add(Gtk.Label('<b>Game Window</b>', xalign=0, use_markup=True))
		game_window_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		bot_page.add(game_window_box)
		# ComboBox
		self.game_window_combo = Gtk.ComboBoxText()
		self.game_window_combo.set_margin_left(10)
		self.populate_game_window_combo()
		self.game_window_combo.connect('changed', self.on_game_window_combo_changed)
		game_window_box.pack_start(self.game_window_combo, True, True, 0)
		# Refresh
		self.refresh_button = Gtk.Button()
		self.refresh_button.set_image(Gtk.Image(stock=Gtk.STOCK_REFRESH))
		self.refresh_button.set_tooltip_text('Refresh')
		self.refresh_button.connect('clicked', self.on_refresh_button_clicked)
		game_window_box.add(self.refresh_button)
		# Unplug
		self.unplug_button = Gtk.Button()
		self.unplug_button.set_image(Gtk.Image(stock=Gtk.STOCK_LEAVE_FULLSCREEN))
		self.unplug_button.set_tooltip_text('Unplug')
		self.unplug_button.connect('clicked', self.on_unplug_button_clicked)
		game_window_box.add(self.unplug_button)
		# Plug
		if '--enable-dev-env' in self.args:
			self.plug_button = Gtk.Button()
			self.plug_button.set_image(Gtk.Image(stock=Gtk.STOCK_JUMP_TO))
			self.plug_button.set_tooltip_text('Plug')
			self.plug_button.connect('clicked', self.on_plug_button_clicked)
			game_window_box.add(self.plug_button)
		## Bot Path
		bot_page.add(Gtk.Label('<b>Bot Path</b>', xalign=0, use_markup=True))
		self.bot_path_filechooserbutton = Gtk.FileChooserButton(title='Choose bot path')
		self.bot_path_filechooserbutton.set_current_folder(tools.get_resource_path('../paths'))
		pathfilter = Gtk.FileFilter()
		pathfilter.set_name('Bot Path (*.path)')
		pathfilter.add_pattern('*.path')
		self.bot_path_filechooserbutton.add_filter(pathfilter)
		self.bot_path_filechooserbutton.set_margin_left(10)
		self.bot_path_filechooserbutton.connect('file-set', self.on_bot_path_changed)
		bot_page.add(self.bot_path_filechooserbutton)
		## Start From Step
		bot_page.add(Gtk.Label('<b>Start From Step</b>', xalign=0, use_markup=True))
		adjustment = Gtk.Adjustment(value=1, lower=1, upper=10000, step_increment=1, page_increment=5, page_size=0)
		self.step_spin_button = Gtk.SpinButton(adjustment=adjustment)
		self.step_spin_button.set_margin_left(10)
		bot_page.add(self.step_spin_button)
		## Start
		self.start_button = Gtk.Button()
		self.start_button.set_tooltip_text('Start')
		self.start_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
		self.start_button.connect('clicked', self.on_start_button_clicked)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		container_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		hbox.pack_start(container_hbox, True, False, 0)
		container_hbox.add(self.start_button)
		bot_page.pack_end(hbox, False, False, 0)
		## Pause
		self.pause_button = Gtk.Button()
		self.pause_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PAUSE))
		self.pause_button.set_tooltip_text('Pause')
		self.pause_button.set_sensitive(False)
		self.pause_button.connect('clicked', self.on_pause_button_clicked)
		container_hbox.add(self.pause_button)
		## Stop
		self.stop_button = Gtk.Button()
		self.stop_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_STOP))
		self.stop_button.set_tooltip_text('Stop')
		self.stop_button.set_sensitive(False)
		self.stop_button.connect('clicked', self.on_stop_button_clicked)
		container_hbox.add(self.stop_button)
		### Path Tab
		path_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		path_page.set_border_width(10)
		bot_notebook.append_page(path_page, Gtk.Label('Path'))
		## Movement
		path_page.add(Gtk.Label('<b>Movement</b>', xalign=0, use_markup=True))
		# Up
		up_button = Gtk.Button()
		up_button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_UP))
		up_button.connect('clicked', self.on_up_button_clicked)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.pack_start(up_button, True, False, 0)
		path_page.add(hbox)
		# Left
		left_button = Gtk.Button()
		left_button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_BACK))
		left_button.connect('clicked', self.on_left_button_clicked)
		left_right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
		left_right_box.add(left_button)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.pack_start(left_right_box, True, False, 0)
		path_page.add(hbox)
		# Right
		right_button = Gtk.Button()
		right_button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_FORWARD))
		right_button.connect('clicked', self.on_right_button_clicked)
		left_right_box.add(right_button)
		# Down
		down_button = Gtk.Button()
		down_button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_DOWN))
		down_button.connect('clicked', self.on_down_button_clicked)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.pack_start(down_button, True, False, 0)
		path_page.add(hbox)
		## Action
		path_page.add(Gtk.Label('<b>Action</b>', xalign=0, use_markup=True))
		## Enclos
		self.enclos_radio = Gtk.RadioButton('Enclos')
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.set_margin_left(5)
		hbox.add(self.enclos_radio)
		self.enclos_combo = CustomComboBox(data=data.Enclos, sort=True)
		self.enclos_combo.set_margin_left(14)
		self.enclos_combo.connect('changed', lambda combo: self.enclos_radio.set_active(True))
		hbox.pack_start(self.enclos_combo, True, True, 0)
		path_page.add(hbox)
		## Zaap
		self.zaap_radio = Gtk.RadioButton('Zaap', group=self.enclos_radio)
		self.zaap_radio.set_margin_left(5)
		path_page.add(self.zaap_radio)
		# From
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.set_margin_left(40)
		hbox.add(Gtk.Label('<b>From</b>', xalign=0, use_markup=True))
		self.zaap_from_combo = CustomComboBox(data=data.Zaap['From'], sort=True)
		self.zaap_from_combo.set_margin_left(12)
		self.zaap_from_combo.connect('changed', lambda combo: self.zaap_radio.set_active(True))
		hbox.pack_start(self.zaap_from_combo, True, True, 0)
		path_page.add(hbox)
		# To
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.set_margin_left(40)
		hbox.add(Gtk.Label('<b>To</b>', xalign=0, use_markup=True))
		self.zaap_to_combo = CustomComboBox(data=data.Zaap['To'], sort=True)
		self.zaap_to_combo.set_margin_left(30)
		self.zaap_to_combo.connect('changed', lambda combo: self.zaap_radio.set_active(True))
		hbox.pack_start(self.zaap_to_combo, True, True, 0)
		path_page.add(hbox)
		## Zaapi
		self.zaapi_radio = Gtk.RadioButton('Zaapi', group=self.enclos_radio)
		self.zaapi_radio.set_margin_left(5)
		path_page.add(self.zaapi_radio)
		# From
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.set_margin_left(40)
		hbox.add(Gtk.Label('<b>From</b>', xalign=0, use_markup=True))
		self.zaapi_from_combo = CustomComboBox(data=data.Zaapi['From'], sort=True)
		self.zaapi_from_combo.set_margin_left(12)
		self.zaapi_from_combo.connect('changed', lambda combo: self.zaapi_radio.set_active(True))
		hbox.pack_start(self.zaapi_from_combo, True, True, 0)
		path_page.add(hbox)
		# To
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.set_margin_left(40)
		hbox.add(Gtk.Label('<b>To</b>', xalign=0, use_markup=True))
		self.zaapi_to_combo = CustomComboBox(data=data.Zaapi['To'], sort=True)
		self.zaapi_to_combo.set_margin_left(30)
		self.zaapi_to_combo.connect('changed', lambda combo: self.zaapi_radio.set_active(True))
		hbox.pack_start(self.zaapi_to_combo, True, True, 0)
		path_page.add(hbox)
		## Separator
		path_page.add(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, margin=5))
		## Add
		add_action_button = Gtk.Button('Add')
		add_action_button.connect('clicked', self.on_add_action_button_clicked)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		container_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		hbox.pack_start(container_hbox, True, False, 0)
		container_hbox.add(add_action_button)
		## Save
		save_menu_button = Gtk.MenuButton('   Save  |')
		save_menu_button.set_image(Gtk.Arrow(Gtk.ArrowType.DOWN, Gtk.ShadowType.NONE))
		save_menu_button.set_image_position(Gtk.PositionType.RIGHT)
		menu = Gtk.Menu()
		menu.connect('show', self.on_save_menu_show)
		self.save_path = Gtk.MenuItem('Save')
		self.save_path.connect('activate', self.on_save_path_activated)
		menu.append(self.save_path)
		clear_path = Gtk.MenuItem('Clear All')
		clear_path.connect('activate', self.on_clear_path_activated)
		menu.append(clear_path)
		menu.show_all()
		save_menu_button.set_popup(menu)
		container_hbox.add(save_menu_button)
		path_page.add(hbox)
		## Listbox
		frame = Gtk.Frame()
		frame.set_margin_top(5)
		scrolled_window = Gtk.ScrolledWindow()
		self.path_listbox = CustomListBox()
		scrolled_window.add(self.path_listbox)
		frame.add(scrolled_window)
		path_page.pack_end(frame, True, True, 0)

	def on_start_button_clicked(self, button):
		if not self.game_window:
			MessageDialog(self, 'Please select a game window')
		elif not self.bot_path:
			MessageDialog(self, 'Please select a bot path')
		else:
			# start bot thread or resume it
			if not self.bot_thread or not self.bot_thread.isAlive():
				game_location = tools.get_widget_location(self.game_area)
				save_dragodindes_images = self.save_dragodindes_images_check.get_active()
				start_from_step = self.step_spin_button.get_value_as_int()
				self.bot_thread = BotThread(self, game_location, start_from_step, save_dragodindes_images)
				self.bot_thread.start()
				self.unplug_button.set_sensitive(False)
				self.settings_button.set_sensitive(False)
				self.step_spin_button.set_sensitive(False)
				self.bot_path_filechooserbutton.set_sensitive(False)
			else:
				self.bot_thread.resume()
			# enable/disable buttons
			self.start_button.set_image(Gtk.Image(file=tools.get_resource_path('../icons/loader.gif')))
			self.start_button.set_sensitive(False)
			self.pause_button.set_sensitive(True)
			self.stop_button.set_sensitive(True)

	def _disconnected(self, state=None):
		self._log(tools.print_internet_state(state), LogType.Error)
		self.start_button.set_image(Gtk.Image(stock=Gtk.STOCK_NETWORK))

	def _connected(self):
		self.start_button.set_image(Gtk.Image(file=tools.get_resource_path('../icons/loader.gif')))

	def set_buttons_to_paused(self):
		self.start_button.set_tooltip_text('Resume')
		self.start_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
		self.start_button.set_sensitive(True)
		self.pause_button.set_sensitive(False)

	def on_pause_button_clicked(self, button):
		self.bot_thread.pause()
		self.set_buttons_to_paused()

	def reset_buttons(self):
		self.start_button.set_tooltip_text('Start')
		self.start_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
		self.start_button.set_sensitive(True)
		self.stop_button.set_sensitive(False)
		self.pause_button.set_sensitive(False)
		self.unplug_button.set_sensitive(True)
		self.settings_button.set_sensitive(True)
		self.step_spin_button.set_sensitive(True)
		self.bot_path_filechooserbutton.set_sensitive(True)

	def on_stop_button_clicked(self, button):
		self.bot_thread.stop()
		self.reset_buttons()

	def on_save_menu_show(self, menu):
		if self.path_listbox.get_children():
			self.save_path.set_sensitive(True)
		else:
			self.save_path.set_sensitive(False)

	def on_save_path_activated(self, item):
		filechooserdialog = Gtk.FileChooserDialog(title='Save as', transient_for=self, action=Gtk.FileChooserAction.SAVE)
		filechooserdialog.set_current_folder(tools.get_resource_path('../paths'))
		filechooserdialog.set_current_name('path_' + tools.get_date_time() + '.path')
		pathfilter = Gtk.FileFilter()
		pathfilter.set_name('Bot Path (*.path)')
		pathfilter.add_pattern('*.path')
		filechooserdialog.add_filter(pathfilter)
		filechooserdialog.add_button('_Cancel', Gtk.ResponseType.CANCEL)
		filechooserdialog.add_button('_Save', Gtk.ResponseType.OK)
		filechooserdialog.set_default_response(Gtk.ResponseType.OK)
		response = filechooserdialog.run()

		if response == Gtk.ResponseType.OK:
			# get all rows text
			text = ''
			for row in self.path_listbox.get_children():
				text += self.path_listbox.get_row_text(row) + '\n'
			# save it to file
			tools.save_text_to_file(text, filechooserdialog.get_filename())

		filechooserdialog.destroy()

	def on_clear_path_activated(self, item):
		for row in self.path_listbox.get_children():
			self.path_listbox.remove(row)

	def on_up_button_clicked(self, button):
		self.path_listbox.append_text('Move(UP)')

	def on_left_button_clicked(self, button):
		self.path_listbox.append_text('Move(LEFT)')

	def on_right_button_clicked(self, button):
		self.path_listbox.append_text('Move(RIGHT)')

	def on_down_button_clicked(self, button):
		self.path_listbox.append_text('Move(DOWN)')

	def on_add_action_button_clicked(self, button):
		if self.enclos_radio.get_active():
			self.path_listbox.append_text('Enclos(%s)' % self.enclos_combo.get_active_text())
		elif self.zaap_radio.get_active():
			self.path_listbox.append_text('Zaap(from=%s,to=%s)' % (self.zaap_from_combo.get_active_text(), self.zaap_to_combo.get_active_text()))
		elif self.zaapi_radio.get_active():
			self.path_listbox.append_text('Zaapi(from=%s,to=%s)' % (self.zaapi_from_combo.get_active_text(), self.zaapi_to_combo.get_active_text()))

	def on_bot_path_changed(self, filechooserbutton):
		self.bot_path = filechooserbutton.get_filename()

	def populate_game_window_combo(self):
		self.game_window_combo_ignore_change = True
		self.game_window_combo.remove_all()
		self.game_windowList = tools.get_game_window_list()
		self._debug('Populate game window combobox, %s window found' % len(self.game_windowList), DebugLevel.High)
		for window_name in self.game_windowList:
			self.game_window_combo.append_text(window_name)
		self.game_window_combo_ignore_change = False

	def focus_game(self):
		if self.game_area:
			self._debug('Focus game', DebugLevel.High)
			# set keyboard focus
			self.game_area.set_can_focus(True)
			self.game_area.child_focus(Gtk.DirectionType.TAB_BACKWARD)

	def on_plug_added(self, widget):
		self._debug('Game window plugged', DebugLevel.High)

	def on_plug_removed(self, widget):
		self._debug('Game window unplugged', DebugLevel.High)
		# enable/disable widgets
		self.unplug_button.hide()
		self.refresh_button.show()
		if '--enable-dev-env' in self.args:
			self.plug_button.show()
		self.game_window_combo.set_sensitive(True)
		self.populate_game_window_combo()
		self.take_screenshot_button.set_sensitive(False)
		# if game window have been destroyed/closed
		game_window_destroyed = self.game_window and self.game_window.is_destroyed()
		if game_window_destroyed:
			self.game_window = None
		# keep or destroy socket
		if self.keep_game_on_unplug_check.get_active() and not game_window_destroyed:
				return True
		else:
			self.game_area = None

	def plug_game_window(self, window_xid):
		self.game_window = tools.get_game_window(window_xid)
		if self.game_window:
			# create socket if not exist
			if not self.game_area:
				self.game_area = Gtk.Socket()
				self.game_area.connect('plug-added', self.on_plug_added)
				self.game_area.connect('plug-removed', self.on_plug_removed)
				self.game_area.show_all()
				self.vtable.attach(self.game_area, 0, 1, 0, 3)
			# plug game window
			self._debug('Plug game window (id: %s)' % window_xid, DebugLevel.Low)
			self.game_area.add_id(window_xid)
			#self.game_window.reparent(self.game_area.get_window(), 0, 0)
			#self.game_window.show() # force show (when minimized)
			self.focus_game()
			# enable/disable widgets
			self.refresh_button.hide()
			if '--enable-dev-env' in self.args:
				self.plug_button.hide()
			self.unplug_button.show()
			self.game_window_combo.set_sensitive(False)
			self.take_screenshot_button.set_sensitive(True)

	def on_game_window_combo_changed(self, combo):
		if self.game_windowList and not self.game_window_combo_ignore_change:
			# get selected game window
			selected = combo.get_active_text()
			window_xid = self.game_windowList[selected]
			# plug it
			self.plug_game_window(window_xid)

	def unplug_game_window(self):
		if self.game_window and not self.game_window.is_destroyed():
			self._debug('Keep game window open')
			root = Gdk.get_default_root_window()
			self.game_window.reparent(root, 0, 0)

		self.game_window = None

	def on_unplug_button_clicked(self, button):
		self._debug('Unplug game window')
		if self.keep_game_on_unplug_check.get_active():
			self.unplug_game_window()
		else:
			self.game_window.destroy()

	def on_plug_button_clicked(self, button):
		dialog = PlugDialog(self)
		dialog.run()
		dialog.destroy()

	def on_refresh_button_clicked(self, button):
		self.populate_game_window_combo()

	# Override the default handler for the delete-event signal
	def do_delete_event(self, event):
		# Show our message dialog
		dialog = Gtk.MessageDialog(transient_for=self, modal=True, buttons=Gtk.ButtonsType.OK_CANCEL, message_type=Gtk.MessageType.QUESTION)
		dialog.props.text = 'Are you sure you want to quit?'
		response = dialog.run()
		dialog.destroy()

		# We only terminate when the user presses the OK button
		if response == Gtk.ResponseType.OK:
			# keep game window
			if self.keep_game_on_unplug_check.get_active():
				self.unplug_game_window()
			# stop bot thread
			if self.bot_thread and self.bot_thread.isAlive():
				self.bot_thread.stop()
			return False

		# Otherwise we keep the application open
		return True

	def main(self):
		Gtk.main()
