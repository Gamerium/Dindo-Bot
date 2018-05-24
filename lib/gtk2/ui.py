# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gtk
import tools

VERSION = '1.0.0'

class BotWindow(gtk.Window):

	gameWindow = None
	logTextView = None
	debugTextView = None

	def __init__(self, title='Dindo Bot'):
		gtk.Window.__init__(self)
		# Table
		self.table = gtk.Table(4, 3, True)
		self.add(self.table)
		# Game Area
		self.gameArea = gtk.DrawingArea()
		self.gameArea.set_events(gtk.gdk.ALL_EVENTS_MASK)
		self.gameArea.set_flags(gtk.CAN_FOCUS)
		self.table.attach(self.gameArea, 0, 2, 0, 3)
		# Log Section
		self.create_log_section()
		# Bot Section
		self.create_bot_section()
		# Window
		self.set_title(title)
		self.set_icon_from_file(tools.get_resource_path('../icons/drago.png'))
		self.set_size_request(900, 700)
		self.connect('destroy', gtk.main_quit)
		self.show_all()

	def create_log_section(self):
		notebook = gtk.Notebook()
		notebook.set_border_width(2)
		# Log Tab
		logPage = gtk.ScrolledWindow()
		self.logTextView = gtk.TextView()
		self.logTextView.set_border_width(6)
		self.logTextView.set_editable(False)
		self.logTextView.set_wrap_mode(gtk.WRAP_WORD)
		logPage.add(self.logTextView)
		notebook.append_page(logPage, gtk.Label('Log'))
		# Debug Tab
		debugPage = gtk.ScrolledWindow()
		self.debugTextView = gtk.TextView()
		self.debugTextView.set_border_width(6)
		self.debugTextView.set_editable(False)
		self.debugTextView.set_wrap_mode(gtk.WRAP_WORD)
		self.debugTextView.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
		self.debugTextView.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
		debugPage.add(self.debugTextView)
		notebook.append_page(debugPage, gtk.Label('Debug'))
		self.table.attach(notebook, 0, 2, 3, 4)

	def create_bot_section(self):
		notebook = gtk.Notebook()
		notebook.set_border_width(2)
		### Bot Tab
		botPage = gtk.VBox(spacing=6)
		botPage.set_border_width(10)
		## Game Window
		botPage.pack_start(self.create_bold_label('Game Window'), False)
		halign = gtk.Alignment(0, 0, 0, 0)
		halign.set_padding(0, 0, 10, 0)
		self.gameWindowBox = gtk.HBox(spacing=6)
		# ComboBox
		self.gameWindowCombo = gtk.combo_box_new_text()
		#self.gameWindowCombo.set_entry_text_column(0)
		self.populate_gamewindow_combo()
		self.gameWindowCombo.connect('changed', self.on_gamewindow_combo_changed)
		self.gameWindowBox.pack_start(self.gameWindowCombo, True)
		# Refresh
		self.refreshButton = gtk.Button()
		self.refreshButton.set_image(self.image_from_stock(gtk.STOCK_REFRESH))
		self.refreshButton.set_tooltip_text('Refresh')
		self.refreshButton.connect('clicked', self.on_refresh_button_clicked)
		self.gameWindowBox.pack_start(self.refreshButton, False)
		# Undo
		self.undoButton = gtk.Button()
		self.undoButton.set_image(self.image_from_stock(gtk.STOCK_UNDO))
		self.refreshButton.set_tooltip_text('Undo')
		self.undoButton.connect('clicked', self.on_undo_button_clicked)
		#self.gameWindowBox.pack_start(self.undoButton, False)
		halign.add(self.gameWindowBox)
		botPage.pack_start(halign)
		notebook.append_page(botPage, gtk.Label('Bot'))
		self.table.attach(notebook, 2, 3, 0, 4)

	def image_from_stock(self, icon, size=gtk.ICON_SIZE_BUTTON):
		image = gtk.Image()
		image.set_from_stock(icon, size)

		return image

	def create_bold_label(self, text):
		label = gtk.Label()
		label.set_markup('<b>' + text + '</b>')
		label.set_alignment(0, 0.5)

		return label

	def populate_gamewindow_combo(self):
		self.gamewindow_combo_ignore_change = True
		model = self.gameWindowCombo.get_model()
		model.clear()
		self.gameWindowsList = tools.get_active_game_windows()
		for window_name in self.gameWindowsList:
			self.gameWindowCombo.append_text(window_name)
		self.gamewindow_combo_ignore_change = False

	def on_gamewindow_combo_changed(self, combo):
		if not self.gamewindow_combo_ignore_change:
			if self.gameWindowsList:
				selected = combo.get_active_text()
				self.gameWindow = self.gameWindowsList[selected]
				# reparent game window
				self.gameWindow.reparent(self.gameArea.window, 0, 0)
				# enable/disable controls
				combo.set_sensitive(False)
				self.gameWindowBox.remove(self.refreshButton)
				self.gameWindowBox.add(self.undoButton)

	def on_undo_button_clicked(self, button):
		if self.gameWindow:
			root = gtk.gdk.get_default_root_window()
			self.gameWindow.reparent(root, 0, 0)

	def on_refresh_button_clicked(self, button):
		self.populate_gamewindow_combo()

	# Override the default handler for the delete-event signal
	def do_delete_event(self, event):
		# Show our message dialog
		dialog = gtk.MessageDialog(transient_for=self, modal=True, buttons=gtk.ButtonsType.OK_CANCEL, message_type=gtk.MessageType.QUESTION)
		dialog.props.text = 'Are you sure you want to quit?'
		response = dialog.run()
		dialog.destroy()

		# We only terminate when the user presses the OK button
		if response == gtk.ResponseType.OK:
			return False

		# Otherwise we keep the application open
		return True

	def main(self):
		gtk.main()
