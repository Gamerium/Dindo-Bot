# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from . import tools
from . import logger
from datetime import datetime

class LogType:
	Normal, Info, Success, Error = range(4)

class BotWindow(Gtk.ApplicationWindow):

	game_window = None

	def __init__(self, title='Dindo Bot'):
		Gtk.Window.__init__(self, title=title)
		# Header Bar
		hb = Gtk.HeaderBar(title=title)
		hb.set_show_close_button(True)
		self.set_titlebar(hb)
		#menu_button = Gtk.Button()
		#menu_button.add(Gtk.Image(file=tools.get_resource_path('../icons/drago_24.png')))
		settings_button = Gtk.Button()
		settings_button.add(Gtk.Image(stock=Gtk.STOCK_PROPERTIES))
		settings_button.connect('clicked', self.on_settings_button_clicked)
		self.popover = Gtk.Popover(relative_to=settings_button, position=Gtk.PositionType.BOTTOM)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		self.popover.add(box)
		self.close_game_window_checkbox = Gtk.CheckButton('Close game window when closing bot')
		self.close_game_window_checkbox.set_active(True)
		box.add(self.close_game_window_checkbox)
		about_button = Gtk.ModelButton(' About')
		#about_button.set_alignment(0, 0.5)
		about_button.set_image(Gtk.Image(stock=Gtk.STOCK_ABOUT))
		about_button.connect('clicked', self.on_about_button_clicked)
		box.add(about_button)
		#hb.pack_start(menu_button)
		hb.pack_end(settings_button)
		# Table
		self.table = Gtk.Table(4, 3, True)
		self.add(self.table)
		# Game Area
		self.game_area = Gtk.DrawingArea()
		self.game_area.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
		self.game_area.connect('size-allocate', self.on_resize)
		self.table.attach(self.game_area, 0, 2, 0, 3)
		# Log Section
		self.create_log_section()
		# Bot Section
		self.create_bot_section()
		# Window
		self.set_icon_from_file(tools.get_resource_path('../icons/drago.png'))
		self.set_size_request(900, 700)
		self.connect('destroy', Gtk.main_quit)
		self.show_all()
		self.undoButton.hide()
		self._log('Bot window loaded')

	def _log(self, text, type=LogType.Normal):
		# get time
		time = datetime.now().strftime('%H:%M:%S')
		position = self.log_buf.get_end_iter()
		new_text = '[' + time + '] ' + text + '\n'
		# append to text view
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
		time = datetime.now().strftime('%H:%M:%S')
		position = self.debug_buf.get_end_iter()
		self.debug_buf.insert(position, '[' + time + '] ' + text + '\n')
		self.debug_view.scroll_to_mark(self.debug_buf.get_insert(), 0.0, False, 0.5, 0.5)
		logger.debug(text)

	def on_settings_button_clicked(self, button):
		self.popover.show_all()

	def on_about_button_clicked(self, button):
		dialog = AboutDialog(transient_for=self)
		dialog.run()

	def create_log_section(self):
		notebook = Gtk.Notebook()
		notebook.set_border_width(2)
		# Log Tab
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
		notebook.append_page(log_page, Gtk.Label('Log'))
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
		notebook.append_page(debug_page, Gtk.Label('Debug'))
		self.table.attach(notebook, 0, 2, 3, 4)

	def create_bot_section(self):
		notebook = Gtk.Notebook()
		notebook.set_border_width(2)
		### Bot Tab
		bot_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		bot_page.set_border_width(10)
		## Game Window
		bot_page.add(self.create_bold_label('Game Window'))
		game_window_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		# ComboBox
		self.game_window_combo = Gtk.ComboBoxText()
		self.game_window_combo.set_entry_text_column(0)
		self.game_window_combo.set_margin_left(10)
		self.populate_game_window_combo()
		self.game_window_combo.connect('changed', self.on_game_window_combo_changed)
		game_window_box.pack_start(self.game_window_combo, True, True, 0)
		# Refresh
		self.refreshButton = Gtk.Button()
		self.refreshButton.set_image(Gtk.Image(stock=Gtk.STOCK_REFRESH))
		self.refreshButton.set_tooltip_text('Refresh')
		self.refreshButton.connect('clicked', self.on_refresh_button_clicked)
		game_window_box.add(self.refreshButton)
		# Undo
		self.undoButton = Gtk.Button()
		self.undoButton.set_image(Gtk.Image(stock=Gtk.STOCK_LEAVE_FULLSCREEN))
		self.undoButton.set_tooltip_text('Undo')
		self.undoButton.connect('clicked', self.on_undo_button_clicked)
		game_window_box.add(self.undoButton)
		bot_page.add(game_window_box)
		notebook.append_page(bot_page, Gtk.Label('Bot'))
		self.table.attach(notebook, 2, 3, 0, 4)

	def create_bold_label(self, text):
		label = Gtk.Label()
		label.set_markup('<b>' + text + '</b>')
		label.set_alignment(0, 0.5)

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
						combo.set_sensitive(False)
						self.refreshButton.hide()
						self.undoButton.show()

	def move_game_window_to_desktop(self):
		if self.game_window:
			self._debug('Move game window to desktop')
			desktop = Gdk.get_default_root_window()
			self.game_window.reparent(desktop, self.game_window_geometry.x, self.game_window_geometry.y)
			self.game_window = None

	def on_undo_button_clicked(self, button):
		self.move_game_window_to_desktop()
		# enable/disable controls
		self.undoButton.hide()
		self.refreshButton.show()
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
			if not self.close_game_window_checkbox.get_active():
				self.move_game_window_to_desktop()
			return False

		# Otherwise we keep the application open
		return True

	def main(self):
		Gtk.main()

class AboutDialog(Gtk.AboutDialog):

	def __init__(self, transient_for):
		Gtk.AboutDialog.__init__(self, transient_for=transient_for)
		self.set_program_name("Dindo Bot")
		self.set_version("1.0.0")
		self.set_comments("DD Management dedicated bot for Dofus game")
		self.set_website("https://github.com/AXeL-dev")
		self.set_website_label("AXeL-dev")
		self.set_authors(["AXeL"])
		logo = GdkPixbuf.Pixbuf.new_from_file(tools.get_resource_path("../icons/dragox2.png"))
		self.set_logo(logo)
		self.connect("response", self.on_response)

	def on_response(self, dialog, response):
		self.destroy()
