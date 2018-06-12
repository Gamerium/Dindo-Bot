# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
from lib import tools
from lib import logger
from lib import data
from lib import parser
from lib import settings
from lib.threads import BotThread
from lib.shared import LogType, DebugLevel, __program_name__
from .dev import DevToolsWidget
from .custom import *
from .dialog import *
from threading import Thread

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
		self.connect('key-press-event', self.on_key_press)
		self.connect('configure-event', self.on_resize_or_move)
		self.connect('window-state-event', self.on_minimize)
		self.connect('destroy', Gtk.main_quit)
		self.show_all()
		self.unplug_button.hide()
		if not self.settings['Debug']['Enabled']:
			self.debug_page.hide()

	def on_key_press(self, widget, event):
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

	def on_take_screenshot_button_clicked(self, button):
		if self.game_window:
			screenshot_name = 'screenshot_' + tools.get_date_time()
			screenshot_path = tools.get_resource_path('../' + screenshot_name)
			tools.take_window_screenshot(self.game_window, screenshot_path)
			self.log("Screenshot saved to '%s'" % screenshot_path, LogType.Info)

	def create_header_bar(self, title):
		### Header Bar
		hb = Gtk.HeaderBar(title=title)
		hb.pack_start(Gtk.Image(file=tools.get_resource_path('../icons/drago_24.png')))
		hb.set_show_close_button(True)
		self.set_titlebar(hb)
		## Settings button
		self.settings_button = Gtk.Button()
		self.settings_button.set_image(Gtk.Image(stock=Gtk.STOCK_PROPERTIES))
		self.settings_button.connect('clicked', lambda button: self.popover.show_all())
		hb.pack_end(self.settings_button)
		self.popover = Gtk.Popover(relative_to=self.settings_button, position=Gtk.PositionType.BOTTOM)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		self.popover.add(box)
		# Preferences button
		preferences_button = Gtk.ModelButton(' Preferences')
		preferences_button.set_alignment(0, 0.5)
		preferences_button.set_image(Gtk.Image(stock=Gtk.STOCK_PREFERENCES))
		preferences_button.connect('clicked', self.on_preferences_button_clicked)
		box.add(preferences_button)
		# Take game screenshot button
		self.take_screenshot_button = Gtk.ModelButton(' Take game screenshot')
		self.take_screenshot_button.set_alignment(0, 0.5)
		self.take_screenshot_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_RECORD))
		self.take_screenshot_button.set_sensitive(False)
		self.take_screenshot_button.connect('clicked', self.on_take_screenshot_button_clicked)
		box.add(self.take_screenshot_button)
		# Open log file button
		open_log_button = Gtk.ModelButton(' Open log file')
		open_log_button.set_alignment(0, 0.5)
		open_log_button.set_image(Gtk.Image(stock=Gtk.STOCK_FILE))
		open_log_button.connect('clicked', lambda button: tools.open_file_in_editor(logger.get_filename()))
		box.add(open_log_button)
		# About button
		about_button = Gtk.ModelButton(' About')
		about_button.set_alignment(0, 0.5)
		about_button.set_image(Gtk.Image(stock=Gtk.STOCK_ABOUT))
		about_button.connect('clicked', self.on_about_button_clicked)
		box.add(about_button)

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
		self.bot_widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		bot_page.add(self.bot_widgets)
		## Game Window
		self.bot_widgets.add(Gtk.Label('<b>Game Window</b>', xalign=0, use_markup=True))
		game_window_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.bot_widgets.add(game_window_box)
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
			self.plug_button.set_image(Gtk.Image(stock=Gtk.STOCK_FIND))
			self.plug_button.set_tooltip_text('Plug')
			self.plug_button.connect('clicked', self.on_plug_button_clicked)
			game_window_box.add(self.plug_button)
		## Bot Path
		self.bot_widgets.add(Gtk.Label('<b>Bot Path</b>', xalign=0, use_markup=True))
		bot_path_filechooserbutton = Gtk.FileChooserButton(title='Choose bot path')
		bot_path_filechooserbutton.set_current_folder(tools.get_resource_path('../paths'))
		pathfilter = Gtk.FileFilter()
		pathfilter.set_name('Bot Path (*.path)')
		pathfilter.add_pattern('*.path')
		bot_path_filechooserbutton.add_filter(pathfilter)
		bot_path_filechooserbutton.set_margin_left(10)
		bot_path_filechooserbutton.connect('file-set', self.on_bot_path_changed)
		self.bot_widgets.add(bot_path_filechooserbutton)
		## Start From Step
		self.bot_widgets.add(Gtk.Label('<b>Start From Step</b>', xalign=0, use_markup=True))
		self.step_spin_button = SpinButton(min=1, max=10000)
		self.step_spin_button.set_margin_left(10)
		self.bot_widgets.add(self.step_spin_button)
		## Repeat Path
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.add(Gtk.Label('<b>Repeat Path</b>', xalign=0, use_markup=True))
		self.bot_widgets.add(hbox)
		# Switch
		self.repeat_switch = Gtk.Switch()
		self.repeat_switch.connect('notify::active', lambda switch, pspec: self.repeat_spin_button.set_sensitive(switch.get_active()))
		hbox.pack_end(self.repeat_switch, False, False, 0)
		# Spin button
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		self.bot_widgets.add(hbox)
		hbox.add(Gtk.Label('Number of times'))
		self.repeat_spin_button = SpinButton(min=2, max=1000)
		self.repeat_spin_button.set_sensitive(False)
		hbox.pack_end(self.repeat_spin_button, False, False, 0)
		## Start
		button_box = ButtonBox(centered=True, linked=True)
		bot_page.pack_end(button_box, False, False, 0)
		self.start_button = Gtk.Button()
		self.start_button.set_tooltip_text('Start')
		self.start_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
		self.start_button.connect('clicked', self.on_start_button_clicked)
		button_box.add(self.start_button)
		## Pause
		self.pause_button = Gtk.Button()
		self.pause_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PAUSE))
		self.pause_button.set_tooltip_text('Pause')
		self.pause_button.set_sensitive(False)
		self.pause_button.connect('clicked', self.on_pause_button_clicked)
		button_box.add(self.pause_button)
		## Stop
		self.stop_button = Gtk.Button()
		self.stop_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_STOP))
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
		up_button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_UP))
		up_button.connect('clicked', lambda button: self.path_listbox.append_text('Move(UP)'))
		button_box.add(up_button)
		# Left
		left_button = Gtk.Button()
		left_button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_BACK))
		left_button.connect('clicked', lambda button: self.path_listbox.append_text('Move(LEFT)'))
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
		hbox.add(left_button)
		button_box.add(hbox)
		# Right
		right_button = Gtk.Button()
		right_button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_FORWARD))
		right_button.connect('clicked', lambda buton: self.path_listbox.append_text('Move(RIGHT)'))
		hbox.add(right_button)
		# Down
		down_button = Gtk.Button()
		down_button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_DOWN))
		down_button.connect('clicked', lambda button: self.path_listbox.append_text('Move(DOWN)'))
		button_box.add(down_button)
		## Action
		path_page.add(Gtk.Label('<b>Action</b>', xalign=0, use_markup=True))
		stack_listbox = StackListBox()
		path_page.add(stack_listbox)
		## Enclos
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_resource_path('../icons/enclos.png'), 24, 24)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Enclos')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Location
		widget.add(Gtk.Label('<b>Location</b>', xalign=0, use_markup=True))
		self.enclos_combo = CustomComboBox(data=data.Enclos, sort=True)
		self.enclos_combo.set_margin_left(10)
		widget.add(self.enclos_combo)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Enclos(%s)' % self.enclos_combo.get_active_text()))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.pack_end(button_box, False, False, 0)
		## Zaap
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_resource_path('../icons/zaap.png'), 24, 24)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Zaap')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# From
		widget.add(Gtk.Label('<b>From</b>', xalign=0, use_markup=True))
		self.zaap_from_combo = CustomComboBox(data=data.Zaap['From'], sort=True)
		self.zaap_from_combo.set_margin_left(10)
		widget.add(self.zaap_from_combo)
		# To
		widget.add(Gtk.Label('<b>To</b>', xalign=0, use_markup=True))
		self.zaap_to_combo = CustomComboBox(data=data.Zaap['To'], sort=True)
		self.zaap_to_combo.set_margin_left(10)
		widget.add(self.zaap_to_combo)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Zaap(from=%s,to=%s)' % (self.zaap_from_combo.get_active_text(), self.zaap_to_combo.get_active_text())))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.pack_end(button_box, False, False, 0)
		## Zaapi
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_resource_path('../icons/destination.png'), 24, 24)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Zaapi')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# From
		widget.add(Gtk.Label('<b>From</b>', xalign=0, use_markup=True))
		self.zaapi_from_combo = CustomComboBox(data=data.Zaapi['From'], sort=True)
		self.zaapi_from_combo.set_margin_left(10)
		widget.add(self.zaapi_from_combo)
		# To
		widget.add(Gtk.Label('<b>To</b>', xalign=0, use_markup=True))
		self.zaapi_to_combo = CustomComboBox(data=data.Zaapi['To'], sort=True)
		self.zaapi_to_combo.set_margin_left(10)
		widget.add(self.zaapi_to_combo)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Zaapi(from=%s,to=%s)' % (self.zaapi_from_combo.get_active_text(), self.zaapi_to_combo.get_active_text())))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.pack_end(button_box, False, False, 0)
		## Click
		pixbuf = Gdk.Cursor(Gdk.CursorType.ARROW).get_image().scale_simple(24, 24, GdkPixbuf.InterpType.BILINEAR)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Click')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Twice
		widget.add(Gtk.Label('<b>Twice</b>', xalign=0, use_markup=True))
		self.click_twice_yes_radio = Gtk.RadioButton('Yes')
		click_twice_no_radio = Gtk.RadioButton('No', group=self.click_twice_yes_radio)
		click_twice_no_radio.set_active(True)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		hbox.add(self.click_twice_yes_radio)
		hbox.add(click_twice_no_radio)
		widget.add(hbox)
		# Location
		widget.add(Gtk.Label('<b>Location</b>', xalign=0, use_markup=True))
		cursor_pixbuf = Gdk.Cursor(Gdk.CursorType.CROSSHAIR).get_image().scale_simple(16, 16, GdkPixbuf.InterpType.BILINEAR)
		self.select_button = Gtk.Button('Select')
		self.select_button.set_image(Gtk.Image(pixbuf=cursor_pixbuf))
		self.select_button.connect('clicked', self.on_select_button_clicked)
		button_box = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL, layout_style=Gtk.ButtonBoxStyle.CENTER)
		button_box.add(self.select_button)
		widget.add(button_box)
		## Wait
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_resource_path('../icons/hourglass.png'), 24, 24)
		image = Gtk.Image(pixbuf=pixbuf)
		label = ImageLabel(image, 'Wait')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Duration
		widget.add(Gtk.Label('<b>Duration</b>', xalign=0, use_markup=True))
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		self.duration_spin_button = SpinButton(min=1, max=60)
		hbox.pack_start(self.duration_spin_button, True, True, 0)
		hbox.add(Gtk.Label('second(s)'))
		widget.add(hbox)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', lambda button: self.path_listbox.append_text('Wait(%d)' % self.duration_spin_button.get_value_as_int()))
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.pack_end(button_box, False, False, 0)
		## Keyboard
		image = Gtk.Image(icon_name='input-keyboard', margin=2, pixel_size=20)
		label = ImageLabel(image, 'Keyboard')
		widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack_listbox.append(label, widget)
		# Press key
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.press_key_radio = Gtk.RadioButton()
		self.press_key_radio.add(Gtk.Label('<b>Press key</b>', xalign=0, use_markup=True))
		hbox.add(self.press_key_radio)
		self.key_label = Gtk.Label()
		hbox.add(self.key_label)
		widget.add(hbox)
		self.keys_combo = CustomComboBox(data.KeyboardShortcuts, True)
		self.keys_combo.set_margin_left(10)
		self.keys_combo.connect('changed', lambda combo: (
				self.key_label.set_text('(' + data.KeyboardShortcuts[combo.get_active_text()] + ')'),
				self.press_key_radio.set_active(True)
			)
		)
		widget.add(self.keys_combo)
		# Type text
		self.type_text_radio = Gtk.RadioButton(group=self.press_key_radio)
		self.type_text_radio.add(Gtk.Label('<b>Type text</b>', xalign=0, use_markup=True))
		widget.add(self.type_text_radio)
		self.type_text_entry = Gtk.Entry(placeholder_text='text')
		self.type_text_entry.set_margin_left(10)
		self.type_text_entry.set_width_chars(10)
		self.type_text_entry.connect('focus-in-event', lambda entry, event: self.type_text_radio.set_active(True))
		widget.add(self.type_text_entry)
		# Add
		add_button = Gtk.Button('Add')
		add_button.connect('clicked', self.on_keyboard_add_button_clicked)
		button_box = ButtonBox(centered=True)
		button_box.add(add_button)
		widget.pack_end(button_box, False, False, 0)
		## Separator
		path_page.add(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, margin=5))
		## Listbox
		self.path_listbox = CustomListBox()
		path_page.pack_end(self.path_listbox, True, True, 0)
		# Load
		load_path_button = Gtk.Button()
		load_path_button.set_tooltip_text('Load')
		load_path_button.set_image(Gtk.Image(stock=Gtk.STOCK_OPEN))
		load_path_button.connect('clicked', self.on_load_path_button_clicked)
		self.path_listbox.add_button(load_path_button)
		# Save
		self.save_path_button = Gtk.Button()
		self.save_path_button.set_tooltip_text('Save')
		self.save_path_button.set_sensitive(False)
		self.save_path_button.set_image(Gtk.Image(stock=Gtk.STOCK_SAVE_AS))
		self.save_path_button.connect('clicked', self.on_save_path_button_clicked)
		self.path_listbox.add_button(self.save_path_button)
		self.path_listbox.on_add(self.on_path_listbox_add)
		self.path_listbox.on_delete(self.on_path_listbox_delete)
		### Map Tab
		map_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		map_page.set_border_width(10)
		bot_notebook.append_page(map_page, Gtk.Label('Map'))
		## Stack & Stack switcher
		stack = Gtk.Stack()
		stack.set_margin_top(5)
		stack_switcher = Gtk.StackSwitcher()
		stack_switcher.set_stack(stack)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.pack_start(stack_switcher, True, False, 0)
		map_page.add(hbox)
		map_page.pack_start(stack, True, True, 0)
		## Data
		self.map_data_listbox = CustomListBox(allow_moving=False)
		stack.add_titled(self.map_data_listbox, 'data', 'Data')
		# Select
		self.select_resource_button = Gtk.Button()
		self.select_resource_button.set_tooltip_text('Select resource')
		self.select_resource_button.set_image(Gtk.Image(pixbuf=cursor_pixbuf))
		self.select_resource_button.connect('clicked', self.on_select_resource_button_clicked)
		self.map_data_listbox.add_button(self.select_resource_button)
		# Load
		load_map_button = Gtk.Button()
		load_map_button.set_tooltip_text('Load')
		load_map_button.set_image(Gtk.Image(stock=Gtk.STOCK_OPEN))
		load_map_button.connect('clicked', self.on_load_map_button_clicked)
		self.map_data_listbox.add_button(load_map_button)
		# Save
		self.save_map_button = Gtk.Button()
		self.save_map_button.set_tooltip_text('Save')
		self.save_map_button.set_sensitive(False)
		self.save_map_button.set_image(Gtk.Image(stock=Gtk.STOCK_SAVE_AS))
		self.save_map_button.connect('clicked', self.on_save_map_button_clicked)
		self.map_data_listbox.add_button(self.save_map_button)
		self.map_data_listbox.on_add(self.on_map_data_listbox_add)
		self.map_data_listbox.on_delete(self.on_map_data_listbox_delete)
		## View
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack.add_titled(box, 'view', 'View')

	def on_load_map_button_clicked(self, button):
		dialog = LoadMapDialog(self)
		dialog.run()

	def on_save_map_button_clicked(self, button):
		dialog = SaveMapDialog(self)
		dialog.run()

	def add_map_data(self, location):
		x, y, width, height = location
		# get pixel color
		color = tools.get_pixel_color(x, y)
		# append to listbox
		self.map_data_listbox.append_text('{"x": "%d", "y": "%d", "width": "%d", "height": "%d", "color": "%s"}' % (x, y, width, height, color))
		self.select_resource_button.set_sensitive(True)
		self.set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))

	def on_select_resource_button_clicked(self, button):
		button.set_sensitive(False)
		self.set_cursor(Gdk.Cursor(Gdk.CursorType.CROSSHAIR))
		game_location = tools.get_widget_location(self.game_area)
		Thread(target=self.wait_for_click, args=(self.add_map_data, game_location)).start()

	def on_map_data_listbox_add(self):
		if not self.save_map_button.get_sensitive():
			self.save_map_button.set_sensitive(True)

	def on_map_data_listbox_delete(self):
		if self.map_data_listbox.is_empty():
			self.save_map_button.set_sensitive(False)

	def on_path_listbox_add(self):
		if not self.save_path_button.get_sensitive():
			self.save_path_button.set_sensitive(True)

	def on_path_listbox_delete(self):
		if self.path_listbox.is_empty():
			self.save_path_button.set_sensitive(False)

	def on_load_path_button_clicked(self, button):
		dialog = OpenFileDialog('Load Path', self, ('Bot Path', '*.path'))
		dialog.set_current_folder(tools.get_resource_path('../paths'))
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
		dialog.set_current_folder(tools.get_resource_path('../paths'))
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
		GObject.idle_add(callback, (x, y, width, height))

	def add_click(self, location):
		x, y, width, height = location
		twice = self.click_twice_yes_radio.get_active()
		self.path_listbox.append_text('Click(x=%d,y=%d,width=%d,height=%d,twice=%s)' % (x, y, width, height, twice))
		self.select_button.set_sensitive(True)
		self.set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))

	def set_cursor(self, cursor):
		window = self.get_window() # Gdk.get_default_root_window()
		window.set_cursor(cursor)

	def on_select_button_clicked(self, button):
		button.set_sensitive(False)
		self.set_cursor(Gdk.Cursor(Gdk.CursorType.CROSSHAIR))
		game_location = tools.get_widget_location(self.game_area)
		Thread(target=self.wait_for_click, args=(self.add_click, game_location)).start()

	def on_start_button_clicked(self, button):
		if not self.game_window:
			MessageDialog(self, 'Please select a game window')
		elif not self.bot_path:
			MessageDialog(self, 'Please select a bot path')
		else:
			# get game location
			game_location = tools.get_widget_location(self.game_area)
			# start bot thread or resume it
			if not self.bot_thread or not self.bot_thread.isAlive():
				start_from_step = self.step_spin_button.get_value_as_int()
				repeat_path = self.repeat_spin_button.get_value_as_int() if self.repeat_switch.get_active() else 1
				self.bot_thread = BotThread(self, game_location, start_from_step, repeat_path, self.settings['SaveDragodindesImages'])
				self.bot_thread.start()
				self.settings_button.set_sensitive(False)
				self.bot_widgets.set_sensitive(False)
			else:
				self.bot_thread.resume(game_location)
			# enable/disable buttons
			self.start_button.set_image(Gtk.Image(file=tools.get_resource_path('../icons/loader.gif')))
			self.start_button.set_sensitive(False)
			self.pause_button.set_sensitive(True)
			self.stop_button.set_sensitive(True)

	def set_internet_state(self, state):
		if state:
			self.start_button.set_image(Gtk.Image(file=tools.get_resource_path('../icons/loader.gif')))
		else:
			self.log(tools.print_internet_state(state), LogType.Error)
			self.start_button.set_image(Gtk.Image(stock=Gtk.STOCK_NETWORK))

	def set_buttons_to_paused(self):
		self.start_button.set_tooltip_text('Resume')
		self.start_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
		self.start_button.set_sensitive(True)
		self.pause_button.set_sensitive(False)

	def pause_bot(self):
		if self.bot_thread and self.bot_thread.isAlive() and self.bot_thread.pause_event.isSet():
			self.bot_thread.pause()
			self.set_buttons_to_paused()

	def on_pause_button_clicked(self, button):
		self.pause_bot()

	def reset_buttons(self):
		self.start_button.set_tooltip_text('Start')
		self.start_button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
		self.start_button.set_sensitive(True)
		self.stop_button.set_sensitive(False)
		self.pause_button.set_sensitive(False)
		self.settings_button.set_sensitive(True)
		self.bot_widgets.set_sensitive(True)

	def on_stop_button_clicked(self, button):
		self.bot_thread.stop()
		self.reset_buttons()

	def on_bot_path_changed(self, filechooserbutton):
		self.bot_path = filechooserbutton.get_filename()

	def populate_game_window_combo(self):
		self.game_window_combo_ignore_change = True
		self.game_window_combo.remove_all()
		self.game_windowList = tools.get_game_window_list()
		self.debug('Populate game window combobox, %d window found' % len(self.game_windowList), DebugLevel.High)
		for window_name in self.game_windowList:
			self.game_window_combo.append_text(window_name)
		self.game_window_combo_ignore_change = False

	def focus_game(self):
		if self.game_area:
			self.debug('Focus game', DebugLevel.High)
			# set keyboard focus
			self.game_area.child_focus(Gtk.DirectionType.TAB_BACKWARD)

	def on_plug_added(self, widget):
		self.debug('Game window plugged')

	def on_plug_removed(self, widget):
		self.debug('Game window unplugged')
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
		if self.settings['KeepGameOpen'] and not game_window_destroyed:
			return True
		else:
			self.game_area = None

	def plug_game_window(self, window_xid):
		self.game_window = tools.get_game_window(window_xid)
		if self.game_window:
			# create socket if not exist
			if not self.game_area:
				self.game_area = Gtk.Socket()
				#self.game_area.set_can_focus(True)
				self.game_area.connect('plug-added', self.on_plug_added)
				self.game_area.connect('plug-removed', self.on_plug_removed)
				self.game_area.show_all()
				self.vtable.attach(self.game_area, 0, 1, 0, 3)
			# plug game window
			self.debug('Plug game window (id: %d)' % window_xid, DebugLevel.Low)
			self.game_area.add_id(window_xid)
			#self.game_window.reparent(self.game_area.get_window(), 0, 0)
			#self.game_window.show() # force show (when minimized)
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
			self.debug('Keep game window open')
			root = Gdk.get_default_root_window()
			self.game_window.reparent(root, 0, 0)

		self.game_window = None

	def on_unplug_button_clicked(self, button):
		self.debug('Unplug game window')
		if self.settings['KeepGameOpen']:
			self.unplug_game_window()
		else:
			self.game_window.destroy()

	def on_plug_button_clicked(self, button):
		dialog = PlugDialog(self)
		dialog.run()

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
			# keep game window
			if self.settings['KeepGameOpen']:
				self.unplug_game_window()
			# stop bot thread
			if self.bot_thread and self.bot_thread.isAlive():
				self.bot_thread.stop()
			return False

		# Otherwise we keep the application open
		return True

	def main(self):
		Gtk.main()
