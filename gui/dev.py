# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from lib import tools
from lib import data
from lib import convert
from .custom import CustomTreeView, CustomComboBox, MenuButton, SpinButton, ButtonBox
from .dialog import CopyTextDialog
from threading import Thread

class DevToolsWidget(Gtk.Table):

	def __init__(self, parent):
		Gtk.Table.__init__(self, 1, 3, True)
		self.set_border_width(5)
		self.parent = parent
		#self.parent.connect('button-press-event', self.on_click)
		## Pixel
		left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		left_box.add(Gtk.Label('<b>Pixel</b>', xalign=0, use_markup=True))
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		left_box.pack_start(hbox, True, True, 0)
		self.attach(left_box, 0, 2, 0, 1)
		# TreeView
		model = Gtk.ListStore(GdkPixbuf.Pixbuf, int, int, int, int, str)
		text_renderer = Gtk.CellRendererText()
		columns = [
			Gtk.TreeViewColumn('', Gtk.CellRendererPixbuf(), pixbuf=0),
			Gtk.TreeViewColumn('X', text_renderer, text=1),
			Gtk.TreeViewColumn('Y', text_renderer, text=2),
			Gtk.TreeViewColumn('Width', text_renderer, text=3),
			Gtk.TreeViewColumn('Height', text_renderer, text=4),
			Gtk.TreeViewColumn('Color', text_renderer, text=5)
		]
		self.tree_view = CustomTreeView(model, columns)
		self.tree_view.connect('button-press-event', self.on_tree_view_double_clicked)
		self.tree_view.connect('selection-changed', self.on_tree_view_selection_changed)
		hbox.pack_start(self.tree_view, True, True, 0)
		# Select
		buttons_box = ButtonBox(orientation=Gtk.Orientation.VERTICAL, centered=True, linked=True)
		hbox.add(buttons_box)
		self.select_pixel_button = Gtk.Button()
		self.select_pixel_button.set_image(Gtk.Image(pixbuf=Gdk.Cursor(Gdk.CursorType.CROSSHAIR).get_image().scale_simple(18, 18, GdkPixbuf.InterpType.BILINEAR)))
		self.select_pixel_button.set_tooltip_text('Select')
		self.select_pixel_button.connect('clicked', self.on_select_pixel_button_clicked)
		buttons_box.add(self.select_pixel_button)
		# Simulate
		self.simulate_click_button = Gtk.Button()
		self.simulate_click_button.set_image(Gtk.Image(pixbuf=Gdk.Cursor(Gdk.CursorType.HAND1).get_image().scale_simple(18, 18, GdkPixbuf.InterpType.BILINEAR)))
		self.simulate_click_button.set_tooltip_text('Simulate Click')
		self.simulate_click_button.set_sensitive(False)
		self.simulate_click_button.connect('clicked', self.on_simulate_click_button_clicked)
		buttons_box.add(self.simulate_click_button)
		# Delete
		self.delete_pixel_button = Gtk.Button()
		self.delete_pixel_button.set_image(Gtk.Image(icon_name='edit-delete-symbolic'))
		self.delete_pixel_button.set_tooltip_text('Delete')
		self.delete_pixel_button.set_sensitive(False)
		self.delete_pixel_button.connect('clicked', self.on_delete_pixel_button_clicked)
		buttons_box.add(self.delete_pixel_button)
		# Separator
		right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		right_box.add(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL, margin=10))
		self.attach(right_box, 2, 3, 0, 1)
		## Key Press
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		right_box.pack_start(vbox, True, True, 0)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		vbox.add(hbox)
		hbox.add(Gtk.Label('<b>Key Press</b>', xalign=0, use_markup=True))
		# Label
		self.keys_label = Gtk.Label()
		hbox.add(self.keys_label)
		# ComboBox
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		vbox.add(hbox)
		self.keys_combo = CustomComboBox(data.KeyboardShortcuts, sort=True)
		self.keys_combo.connect('changed', self.on_keys_combo_changed)
		hbox.pack_start(self.keys_combo, True, True, 0)
		# Simulate
		self.simulate_key_press_button = Gtk.Button()
		self.simulate_key_press_button.set_image(Gtk.Image(icon_name='input-keyboard'))
		self.simulate_key_press_button.set_tooltip_text('Simulate')
		self.simulate_key_press_button.set_sensitive(False)
		self.simulate_key_press_button.connect('clicked', self.on_simulate_key_press_button_clicked)
		hbox.add(self.simulate_key_press_button)
		## Scroll
		vbox.add(Gtk.Label('<b>Scroll</b>', xalign=0, use_markup=True))
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		vbox.add(hbox)
		# Direction
		self.scroll_direction_combo = CustomComboBox(['up', 'down'])
		self.scroll_direction_combo.set_active(1)
		hbox.pack_start(self.scroll_direction_combo, True, True, 0)
		# Value
		self.scroll_menu_button = MenuButton(text='1', position=Gtk.PositionType.TOP)
		self.scroll_spin_button = SpinButton(min=1, max=10)
		self.scroll_spin_button.connect('value-changed', lambda button: self.scroll_menu_button.set_label(str(button.get_value_as_int())))
		self.scroll_menu_button.add(self.scroll_spin_button)
		hbox.add(self.scroll_menu_button)
		# Simulate
		simulate_scroll_button = Gtk.Button()
		simulate_scroll_button.set_image(Gtk.Image(pixbuf=Gdk.Cursor(Gdk.CursorType.SB_V_DOUBLE_ARROW).get_image().scale_simple(18, 18, GdkPixbuf.InterpType.BILINEAR)))
		simulate_scroll_button.set_tooltip_text('Simulate')
		simulate_scroll_button.connect('clicked', self.on_simulate_scroll_button_clicked)
		hbox.add(simulate_scroll_button)

	def on_simulate_scroll_button_clicked(self, button):
		# get scroll value
		direction = self.scroll_direction_combo.get_active_text()
		value = self.scroll_spin_button.get_value_as_int()
		clicks = value if direction == 'up' else -value
		if self.parent.game_area:
			# get game area location
			game_location = tools.get_widget_location(self.parent.game_area)
			# get the center of the game location
			x, y = tools.coordinates_center(game_location)
		else:
			x, y = (None, None)
		# scroll
		self.parent.debug('Scroll: %d' % clicks)
		tools.scroll_to(clicks, x, y)

	def on_keys_combo_changed(self, combo):
		selected = combo.get_active_text()
		self.keys_label.set_text('(' + data.KeyboardShortcuts[selected] + ')')
		if not self.simulate_key_press_button.get_sensitive():
			self.simulate_key_press_button.set_sensitive(True)

	def add_pixel(self, location):
		x, y, width, height = location
		# get pixel color
		pixel = tools.get_pixel(x, y, size=(10, 10))
		pixbuf = convert.image2pixbuf(pixel)
		color = pixel.getpixel((0, 0))
		# append to treeview
		self.tree_view.append_row([pixbuf, x, y, width, height, str(color)])
		self.select_pixel_button.set_sensitive(True)
		self.parent.set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))

	def on_select_pixel_button_clicked(self, button):
		button.set_sensitive(False)
		self.parent.set_cursor(Gdk.Cursor(Gdk.CursorType.CROSSHAIR))
		# wait for click
		game_location = tools.get_widget_location(self.parent.game_area)
		Thread(target=self.parent.wait_for_click, args=(self.add_pixel, game_location)).start()

	def on_simulate_click_button_clicked(self, button):
		# get click coordinates
		selected_row = self.tree_view.get_selected_row()
		x, y, width, height = (selected_row[1], selected_row[2], selected_row[3], selected_row[4])
		#print('x: %d, y: %d, width: %d, height: %d' % (x, y, width, height))
		# adjust for game area
		if self.parent.game_area:
			game_x, game_y, game_width, game_height = tools.get_widget_location(self.parent.game_area)
			#print('game_x: %d, game_y: %d, game_width: %d, game_height: %d' % (game_x, game_y, game_width, game_height))
			click_x, click_y = tools.adjust_click_position(x, y, width, height, game_x, game_y, game_width, game_height)
		else:
			click_x = x
			click_y = y
		# perform click
		self.parent.debug('Click on x: %d, y: %d' % (click_x, click_y))
		tools.perform_click(click_x, click_y)

	def on_delete_pixel_button_clicked(self, button):
		self.tree_view.remove_selected_row()

	def on_simulate_key_press_button_clicked(self, button):
		selected = self.keys_combo.get_active_text()
		key = data.KeyboardShortcuts[selected]
		self.parent.focus_game()
		self.parent.debug('Press key: %s' % key)
		tools.press_key(key)

	def on_click(self, widget, event):
		print('x: %d, y: %d' % (event.x, event.y))

	def on_tree_view_double_clicked(self, widget, event):
		if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
			selected_row = self.tree_view.get_selected_row()
			if selected_row:
				x, y, width, height, color = (selected_row[1], selected_row[2], selected_row[3], selected_row[4], selected_row[5])
				CopyTextDialog(self.parent, "{'x': %d, 'y': %d, 'width': %d, 'height': %d, 'color': %s}" % (x, y, width, height, color))

	def on_tree_view_selection_changed(self, selection):
		model, tree_iter = selection.get_selected()
		if tree_iter is None:
			self.simulate_click_button.set_sensitive(False)
			self.delete_pixel_button.set_sensitive(False)
		else:
			if not self.simulate_click_button.get_sensitive():
				self.simulate_click_button.set_sensitive(True)
			if not self.delete_pixel_button.get_sensitive():
				self.delete_pixel_button.set_sensitive(True)
