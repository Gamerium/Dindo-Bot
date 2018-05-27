# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from lib import tools
from lib import data
from .custom import CustomComboBox
import pyautogui

class DevToolsWidget(Gtk.Table):

	perform_scroll = False

	def __init__(self, parent):
		Gtk.Table.__init__(self, 1, 3, True)
		self.set_border_width(10)
		self.parent = parent
		#self.parent.connect('button-press-event', self.on_click)
		## Pixel
		left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		left_box.add(parent.create_bold_label('Pixel'))
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		left_box.pack_start(hbox, True, True, 0)
		self.attach(left_box, 0, 2, 0, 1)
		# TreeView
		frame = Gtk.Frame()
		scrolled_window = Gtk.ScrolledWindow()
		self.pixels_list = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str, str, str, str)
		pixbuf = Gdk.Cursor(Gdk.CursorType.ARROW).get_image()
		self.mouse_icon = pixbuf.scale_simple(18, 18, GdkPixbuf.InterpType.BILINEAR)
		tree_view = Gtk.TreeView(self.pixels_list)
		tree_view.append_column(Gtk.TreeViewColumn('', Gtk.CellRendererPixbuf(), pixbuf=0))
		tree_view.append_column(Gtk.TreeViewColumn('X', Gtk.CellRendererText(), text=1))
		tree_view.append_column(Gtk.TreeViewColumn('Y', Gtk.CellRendererText(), text=2))
		tree_view.append_column(Gtk.TreeViewColumn('Width', Gtk.CellRendererText(), text=3))
		tree_view.append_column(Gtk.TreeViewColumn('Height', Gtk.CellRendererText(), text=4))
		tree_view.append_column(Gtk.TreeViewColumn('Color', Gtk.CellRendererText(), text=5))
		tree_view.connect('size-allocate', self.scroll_tree_view)
		self.tree_view_selection = tree_view.get_selection()
		self.tree_view_selection.connect('changed', self.on_selection_changed)
		scrolled_window.add(tree_view)
		frame.add(scrolled_window)
		hbox.pack_start(frame, True, True, 0)
		# Select
		buttons_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		hbox.add(buttons_box)
		select_button = Gtk.Button()
		select_button.set_image(Gtk.Image(pixbuf=Gdk.Cursor(Gdk.CursorType.CROSSHAIR).get_image().scale_simple(18, 18, GdkPixbuf.InterpType.BILINEAR)))
		select_button.set_tooltip_text('Select')
		select_button.connect('clicked', self.on_select_button_clicked)
		buttons_box.add(select_button)
		# Simulate
		self.simulate_click_button = Gtk.Button()
		self.simulate_click_button.set_image(Gtk.Image(pixbuf=Gdk.Cursor(Gdk.CursorType.HAND1).get_image().scale_simple(18, 18, GdkPixbuf.InterpType.BILINEAR)))
		self.simulate_click_button.set_tooltip_text('Simulate Click')
		self.simulate_click_button.set_sensitive(False)
		self.simulate_click_button.connect('clicked', self.on_simulate_click_button_clicked)
		buttons_box.add(self.simulate_click_button)
		# Separator
		right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		right_box.add(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL, margin=10))
		self.attach(right_box, 2, 3, 0, 1)
		## Key Press
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		vbox.add(parent.create_bold_label('Key Press'))
		right_box.pack_start(vbox, True, True, 0)
		# ComboBox
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		self.keys_combo = CustomComboBox(data.KeyboardShortcuts.values())
		hbox.pack_start(self.keys_combo, True, True, 0)
		vbox.add(hbox)
		# Simulate
		simulate_key_press_button = Gtk.Button()
		simulate_key_press_button.set_image(Gtk.Image(icon_name='input-keyboard'))
		simulate_key_press_button.set_tooltip_text('Simulate')
		simulate_key_press_button.connect('clicked', self.on_simulate_key_press_button_clicked)
		hbox.add(simulate_key_press_button)

	def on_select_button_clicked(self, button):
		button.set_sensitive(False)
		# wait for click
		pyautogui.waitForMouseEvent('left_down')
		# get mouse position
		x, y = pyautogui.position()
		# get pixel color
		color = pyautogui.pixel(x, y)
		# get game area allocation (relative to parent)
		game_alloc = self.parent.game_area.get_allocation()
		#print('game_alloc.x: %s, game_alloc.y: %s, game_alloc.width: %s, game_alloc.height: %s' % (game_alloc.x, game_alloc.y, game_alloc.width, game_alloc.height))
		# get game area position (relative to root window)
		game_x, game_y = tools.get_widget_absolute_position(self.parent.game_area)
		#print('x: %s, y: %s, game_x: %s, game_y: %s' % (x, y, game_x, game_y))
		# scale to game area
		if tools.point_is_inside_bounds(x, y, game_x, game_y, game_alloc.width, game_alloc.height):
			# pixel is inside game area, so we fit x & y to it
			x = x - game_x
			y = y - game_y
			width = game_alloc.width
			height = game_alloc.height
		else:
			width, height = pyautogui.size()
		# append to treeview
		self.pixels_list.append([self.mouse_icon, str(x), str(y), str(width), str(height), str(color)])
		self.perform_scroll = True
		button.set_sensitive(True)
		# select last row in treeview
		last_row_index = len(self.pixels_list) - 1
		self.tree_view_selection.select_path(Gtk.TreePath(last_row_index))

	def on_simulate_click_button_clicked(self, button):
		(model, rowlist) = self.tree_view_selection.get_selected_rows()
		for row in rowlist:
			# get click coordinates
			tree_iter = model.get_iter(row)
			x = int(model.get_value(tree_iter, 1))
			y = int(model.get_value(tree_iter, 2))
			width = int(model.get_value(tree_iter, 3))
			height = int(model.get_value(tree_iter, 4))
			#print('x: %s, y: %s, width: %s, height: %s' % (x, y, width, height))
			# scale to screen
			screen_width, screen_height = pyautogui.size()
			if screen_width > width and screen_height > height:
				game_x, game_y = tools.get_widget_absolute_position(self.parent.game_area)
				click_x = x + game_x
				click_y = y + game_y
			else:
				click_x = x
				click_y = y
			#print('click_x: %s, click_y: %s' % (click_x, click_y))
			# perform click
			pyautogui.click(x=click_x, y=click_y)

	def on_simulate_key_press_button_clicked(self, button):
		key = self.keys_combo.get_active_text()
		self.parent.focus_game()
		pyautogui.press(key)

	def on_click(self, widget, event):
		print('x: %s, y: %s' % (event.x, event.y))

	def on_selection_changed(self, selection):
		if not self.simulate_click_button.get_sensitive():
			self.simulate_click_button.set_sensitive(True)

	def scroll_tree_view(self, widget, event):
		if self.perform_scroll:
			adj = widget.get_vadjustment()
			adj.set_value(adj.get_upper() - adj.get_page_size())
			self.perform_scroll = False
