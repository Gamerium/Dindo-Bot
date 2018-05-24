# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from . import tools
from . import logger
from . import data
from .threads import BotThread

class LogType:
	Normal, Info, Success, Error = range(4)

class BotWindow(Gtk.ApplicationWindow):

	game_window = None
	bot_path = None
	bot_thread = None

	def __init__(self, title='Dindo Bot'):
		Gtk.Window.__init__(self, title=title)
		# Header Bar
		self.create_header_bar(title)
		# Tables
		self.htable = Gtk.Table(1, 3, True) # horizontal table
		self.vtable = Gtk.Table(4, 1, True) # vertical table
		self.htable.attach(self.vtable, 1, 3, 0, 1)
		self.add(self.htable)
		# Game Area
		self.game_area = Gtk.DrawingArea()
		self.game_area.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
		#self.game_area.set_sensitive(False)
		#self.game_area.connect('size-allocate', self.on_resize)
		self.vtable.attach(self.game_area, 0, 1, 0, 3)
		# Tabs
		self.create_tabs()
		# Window
		self.set_icon_from_file(tools.get_resource_path('../icons/drago.png'))
		self.set_size_request(900, 700)
		self.set_resizable(False)
		self.connect('destroy', Gtk.main_quit)
		self.show_all()
		self.undo_button.hide()

	def _log(self, text, type=LogType.Normal):
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
		# scroll
		self.log_view.scroll_to_mark(self.log_buf.get_insert(), 0.0, False, 0.5, 0.5)
		# call logger
		if type == LogType.Error:
			logger.error(text)
		else:
			logger.new_entry(text)

	def _debug(self, text):
		position = self.debug_buf.get_end_iter()
		self.debug_buf.insert(position, '[' + tools.get_time() + '] ' + text + '\n')
		self.debug_view.scroll_to_mark(self.debug_buf.get_insert(), 0.0, False, 0.5, 0.5)
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
			self._log("Screenshot saved to '" + screenshot_path + "'", LogType.Info)

	def create_header_bar(self, title):
		### Header Bar
		hb = Gtk.HeaderBar(title=title)
		hb.set_show_close_button(True)
		self.set_titlebar(hb)
		## Settings button
		settings_button = Gtk.Button()
		settings_button.set_image(Gtk.Image(stock=Gtk.STOCK_PROPERTIES))
		settings_button.connect('clicked', self.on_settings_button_clicked)
		self.popover = Gtk.Popover(relative_to=settings_button, position=Gtk.PositionType.BOTTOM)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		self.popover.add(box)
		# Close game checkbox
		self.close_game_checkbox = Gtk.CheckButton('Close game when closing bot')
		#self.close_game_checkbox.set_active(True)
		box.add(self.close_game_checkbox)
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
		hb.pack_end(settings_button)

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
		self.log_buf = self.log_view.get_buffer()
		self.red_text_tag = self.log_buf.create_tag('red', foreground='#FF0000')
		self.green_text_tag = self.log_buf.create_tag('green', foreground='#00FF00')
		self.blue_text_tag = self.log_buf.create_tag('blue', foreground='#0000FF')
		log_page.add(self.log_view)
		log_notebook.append_page(log_page, Gtk.Label('Log'))
		# Debug Tab
		debug_page = Gtk.ScrolledWindow()
		self.debug_view = Gtk.TextView()
		self.debug_view.set_border_width(5)
		self.debug_view.set_editable(False)
		self.debug_view.set_wrap_mode(Gtk.WrapMode.WORD)
		self.debug_view.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('black'))
		self.debug_view.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse('white'))
		self.debug_buf = self.debug_view.get_buffer()
		debug_page.add(self.debug_view)
		log_notebook.append_page(debug_page, Gtk.Label('Debug'))
		### Bot Tab
		bot_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		bot_page.set_border_width(10)
		bot_notebook.append_page(bot_page, Gtk.Label('Bot'))
		## Game Window
		bot_page.add(self.create_bold_label('Game Window'))
		game_window_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
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
		# Undo
		self.undo_button = Gtk.Button()
		self.undo_button.set_image(Gtk.Image(stock=Gtk.STOCK_LEAVE_FULLSCREEN))
		self.undo_button.set_tooltip_text('Undo')
		self.undo_button.connect('clicked', self.on_undo_button_clicked)
		game_window_box.add(self.undo_button)
		bot_page.add(game_window_box)
		## Bot Path
		bot_page.add(self.create_bold_label('Bot Path'))
		filechooserbutton = Gtk.FileChooserButton(title='Choose bot path')
		filechooserbutton.set_current_folder(tools.get_resource_path('../paths'))
		pathfilter = Gtk.FileFilter()
		pathfilter.set_name('Bot Path (*.path)')
		pathfilter.add_pattern('*.path')
		filechooserbutton.add_filter(pathfilter)
		filechooserbutton.set_margin_left(10)
		filechooserbutton.connect('file-set', self.on_bot_path_changed)
		bot_page.add(filechooserbutton)
		## Start
		self.start_button = Gtk.Button(' Start ')
		self.start_button.set_image(self.add_image_margin(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)))
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
		path_page.add(self.create_bold_label('Movement'))
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
		path_page.add(self.create_bold_label('Action'))
		## Enclos
		self.enclos_radio = Gtk.RadioButton('Enclos')
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.set_margin_left(5)
		hbox.add(self.enclos_radio)
		self.enclos_combo = CustomComboBox(data=data.Enclos.keys())
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
		hbox.add(self.create_bold_label('From'))
		self.zaap_from_combo = CustomComboBox(data=data.Zaap['From'].keys())
		self.zaap_from_combo.set_margin_left(12)
		self.zaap_from_combo.connect('changed', lambda combo: self.zaap_radio.set_active(True))
		hbox.pack_start(self.zaap_from_combo, True, True, 0)
		path_page.add(hbox)
		# To
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.set_margin_left(40)
		hbox.add(self.create_bold_label('To'))
		self.zaap_to_combo = CustomComboBox(data=data.Zaap['To'].keys())
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
		hbox.add(self.create_bold_label('From'))
		self.zaapi_from_combo = CustomComboBox(data=data.Zaapi['From'].keys())
		self.zaapi_from_combo.set_margin_left(12)
		self.zaapi_from_combo.connect('changed', lambda combo: self.zaapi_radio.set_active(True))
		hbox.pack_start(self.zaapi_from_combo, True, True, 0)
		path_page.add(hbox)
		# To
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.set_margin_left(40)
		hbox.add(self.create_bold_label('To'))
		self.zaapi_to_combo = CustomComboBox(data=data.Zaapi['To'].keys())
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
		self.save_path.connect("activate", self.on_save_path_activated)
		menu.append(self.save_path)
		clear_path = Gtk.MenuItem('Clear All')
		clear_path.connect("activate", self.on_clear_path_activated)
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
		# start bot thread or resume it
		if self.start_button.get_label() == ' Start ':
			self.bot_thread = BotThread(self)
			self.bot_thread.start()
		else:
			self.bot_thread.resume()
		# enable/disable buttons
		self.start_button.set_image(self.add_image_margin(Gtk.Image(file=tools.get_resource_path('../icons/loader.gif'))))
		self.start_button.set_sensitive(False)
		self.pause_button.set_sensitive(True)
		self.stop_button.set_sensitive(True)

	def on_pause_button_clicked(self, button):
		self.bot_thread.pause()
		self.start_button.set_label(' Resume ')
		self.start_button.set_image(self.add_image_margin(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)))
		self.start_button.set_sensitive(True)
		self.pause_button.set_sensitive(False)

	def reset_buttons(self):
		self.start_button.set_label(' Start ')
		self.start_button.set_image(self.add_image_margin(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY)))
		self.stop_button.set_sensitive(False)
		self.pause_button.set_sensitive(False)
		self.start_button.set_sensitive(True)

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
		filechooserdialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
		filechooserdialog.add_button("_Save", Gtk.ResponseType.OK)
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

	def add_image_margin(self, image, margin=5):
		image.set_margin_left(margin)

		return image

	def create_bold_label(self, text):
		label = Gtk.Label(xalign=0)
		label.set_markup('<b>' + text + '</b>')

		return label

	def populate_game_window_combo(self):
		self.game_window_combo_ignore_change = True
		self.game_window_combo.remove_all()
		self.game_windowList = tools.get_game_window_list()
		self._debug('Populate game window combobox, %s window found' % len(self.game_windowList))
		for window_name in self.game_windowList:
			self.game_window_combo.append_text(window_name)
		self.game_window_combo_ignore_change = False

	def on_game_window_combo_changed(self, combo):
		if not self.game_window_combo_ignore_change:
			if self.game_windowList:
				selected = combo.get_active_text()
				window_xid = self.game_windowList[selected]
				self.game_window = tools.get_game_window(window_xid)
				if self.game_window:
					self.game_window_geometry = self.game_window.get_geometry() # save geometry
					window_to = self.game_area.get_window()
					if window_to:
						# reparent game window
						geo = self.game_window_geometry
						self._debug('Reparent game window, x:%s y:%s width:%s height:%s' % (geo.x, geo.y, geo.width, geo.height))
						self.game_window.reparent(window_to, 0, 0)
						self.game_window.show() # force show (when minimized)
						allocation = self.game_area.get_allocation()
						self.game_window.move_resize(allocation.x, allocation.y, allocation.width, allocation.height)
						# enable/disable controls
						self.take_screenshot_button.set_sensitive(True)
						combo.set_sensitive(False)
						self.refresh_button.hide()
						self.undo_button.show()

	def move_game_window_to_desktop(self):
		if self.game_window:
			self._debug('Move game window to desktop')
			desktop = Gdk.get_default_root_window()
			self.game_window.reparent(desktop, self.game_window_geometry.x, self.game_window_geometry.y)
			self.game_window = None
			self.take_screenshot_button.set_sensitive(False)

	def on_undo_button_clicked(self, button):
		self.move_game_window_to_desktop()
		# enable/disable controls
		self.undo_button.hide()
		self.refresh_button.show()
		self.game_window_combo.set_sensitive(True)
		#self.game_window_combo_ignore_change = True
		#self.game_window_combo.set_active(-1)
		#self.game_window_combo_ignore_change = False
		self.populate_game_window_combo()

	def on_refresh_button_clicked(self, button):
		self.populate_game_window_combo()

	def on_resize(self, widget, size):
		if self.game_window:
			self.game_window.move_resize(size.x, size.y, size.width, size.height)

	# Override the default handler for the delete-event signal
	def do_delete_event(self, event):
		# Show our message dialog
		dialog = Gtk.MessageDialog(transient_for=self, modal=True, buttons=Gtk.ButtonsType.OK_CANCEL, message_type=Gtk.MessageType.QUESTION)
		dialog.props.text = 'Are you sure you want to quit?'
		response = dialog.run()
		dialog.destroy()

		# We only terminate when the user presses the OK button
		if response == Gtk.ResponseType.OK:
			# move game window to desktop
			if not self.close_game_checkbox.get_active():
				self.move_game_window_to_desktop()
			# stop bot thread
			if self.bot_thread and self.bot_thread.isAlive():
				self.bot_thread.stop()
			return False

		# Otherwise we keep the application open
		return True

	def main(self):
		Gtk.main()

class CustomComboBox(Gtk.ComboBoxText):

	def __init__(self, data=[]):
		Gtk.ComboBoxText.__init__(self)
		for text in data:
			self.append_text(text)

class CustomListBox(Gtk.ListBox):

	perform_scroll = False

	def __init__(self):
		Gtk.ListBox.__init__(self)
		self.set_selection_mode(Gtk.SelectionMode.NONE)
		self.connect('size-allocate', self.on_size_allocate)

	def on_size_allocate(self, widget, event):
		if self.perform_scroll:
			adj = widget.get_adjustment()
			adj.set_value(adj.get_upper() - adj.get_page_size())
			self.perform_scroll = False

	def append_text(self, text):
		# add new row with text & delete button
		row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
		row.add(hbox)
		label = Gtk.Label(text, xalign=0)
		label.set_margin_left(5)
		delete_button = Gtk.ModelButton()
		delete_button.set_image(Gtk.Image(stock=Gtk.STOCK_DELETE))
		delete_button.set_tooltip_text('Delete')
		delete_button.connect('clicked', self.on_delete_button_clicked)
		hbox.pack_start(label, True, True, 0)
		hbox.pack_start(delete_button, False, True, 0)
		self.add(row)
		self.show_all()
		self.perform_scroll = True

	def get_row_text(self, row):
		label = row.get_children()[0].get_children()[0]
		return label.get_text()

	def on_delete_button_clicked(self, button):
		row = button.get_parent().get_parent()
		self.remove(row)

class AboutDialog(Gtk.AboutDialog):

	def __init__(self, transient_for):
		Gtk.AboutDialog.__init__(self, transient_for=transient_for)
		self.set_program_name("Dindo Bot")
		self.set_version("1.0.0")
		self.set_comments("Rearing bot for Dofus game")
		self.set_website("https://github.com/AXeL-dev")
		self.set_website_label("AXeL-dev")
		self.set_authors(["AXeL"])
		logo = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_resource_path("../icons/cover.png"), 64, 64)
		self.set_logo(logo)
		self.connect("response", self.on_response)

	def on_response(self, dialog, response):
		self.destroy()
