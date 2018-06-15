# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, Pango
from lib.tools import fit_position_to_destination
import math

class CustomComboBox(Gtk.ComboBoxText):

	def __init__(self, data_list=[], sort=False):
		Gtk.ComboBoxText.__init__(self)
		# set max chars width
		for renderer in self.get_cells():
			renderer.props.max_width_chars = 10
			renderer.props.ellipsize = Pango.EllipsizeMode.END
		# append data
		self.append_list(data_list, sort)

	def append_list(self, data_list, sort=False, clear=False):
		# clear combobox
		if clear:
			self.remove_all()
		# sort data
		if sort:
			data_list = sorted(data_list)
		# append data
		for text in data_list:
			self.append_text(text)

	def sync_with_combo(self, combo, use_contains=False):
		if self.get_active() != -1 and combo.get_active() != -1:
			# do not allow same text at same time
			self_text = self.get_active_text()
			combo_text = combo.get_active_text()
			if (use_contains and (self_text in combo_text or combo_text in self_text)) or self_text == combo_text:
				combo.set_active(-1)

class CustomListBox(Gtk.Frame):

	def __init__(self, allow_moving=True):
		Gtk.Frame.__init__(self)
		self.allow_moving = allow_moving
		self.perform_scroll = False
		self.add_callback = None
		self.delete_callback = None
		## ListBox
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.add(vbox)
		self.listbox = Gtk.ListBox()
		self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
		self.listbox.connect('size-allocate', self.on_size_allocate)
		self.listbox.connect('row-activated', self.on_row_activated)
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.add(self.listbox)
		vbox.pack_start(scrolled_window, True, True, 0)
		## ActionBar
		actionbar = Gtk.ActionBar()
		vbox.pack_end(actionbar, False, False, 0)
		default_buttons_box = ButtonBox(linked=True)
		actionbar.pack_start(default_buttons_box)
		if allow_moving:
			# Move up
			self.move_up_button = Gtk.Button()
			self.move_up_button.set_tooltip_text('Move up')
			self.move_up_button.set_image(Gtk.Image(gicon=Gio.ThemedIcon(name='go-up-symbolic')))
			self.move_up_button.connect('clicked', self.on_move_up_button_clicked)
			default_buttons_box.add(self.move_up_button)
			# Move down
			self.move_down_button = Gtk.Button()
			self.move_down_button.set_tooltip_text('Move down')
			self.move_down_button.set_image(Gtk.Image(gicon=Gio.ThemedIcon(name='go-down-symbolic')))
			self.move_down_button.connect('clicked', self.on_move_down_button_clicked)
			default_buttons_box.add(self.move_down_button)
		# Delete
		self.delete_button = Gtk.Button()
		self.delete_button.set_tooltip_text('Delete')
		self.delete_button.set_image(Gtk.Image(stock=Gtk.STOCK_DELETE))
		self.delete_button.connect('clicked', self.on_delete_button_clicked)
		default_buttons_box.add(self.delete_button)
		# Clear all
		self.clear_all_button = Gtk.Button()
		self.clear_all_button.set_tooltip_text('Clear all')
		self.clear_all_button.set_image(Gtk.Image(gicon=Gio.ThemedIcon(name='edit-clear-all-symbolic')))
		self.clear_all_button.connect('clicked', self.on_clear_all_button_clicked)
		default_buttons_box.add(self.clear_all_button)
		# Initialise default buttons status
		self.reset_buttons()
		# Buttons box
		self.buttons_box = ButtonBox(linked=True)
		actionbar.pack_end(self.buttons_box)

	def on_add(self, callback):
		self.add_callback = callback

	def on_delete(self, callback):
		self.delete_callback = callback

	def on_row_activated(self, listbox, row):
		if self.allow_moving:
			rows_count = len(self.get_rows())
			index = row.get_index()
			# Move up
			enable_move_up = True if index > 0 else False
			self.move_up_button.set_sensitive(enable_move_up)
			# Move down
			enable_move_down = True if index < rows_count - 1 else False
			self.move_down_button.set_sensitive(enable_move_down)
		# Delete
		self.delete_button.set_sensitive(True)
		# Clear all
		self.clear_all_button.set_sensitive(True)

	def on_size_allocate(self, listbox, event):
		if self.perform_scroll:
			adj = listbox.get_adjustment()
			adj.set_value(adj.get_upper() - adj.get_page_size())
			self.perform_scroll = False

	def add_button(self, button):
		self.buttons_box.add(button)

	def append_text(self, text):
		# add new row
		row = Gtk.ListBoxRow()
		label = Gtk.Label(text, xalign=0, margin=5)
		row.add(label)
		self.listbox.add(row)
		self.listbox.show_all()
		self.perform_scroll = True
		self.select_row(row)
		if self.add_callback is not None:
			self.add_callback()

	def select_row(self, row):
		self.listbox.select_row(row)
		self.on_row_activated(self.listbox, row)

	def get_rows(self):
		return self.listbox.get_children()

	def is_empty(self):
		return len(self.get_rows()) == 0

	def get_row_text(self, row):
		label = row.get_children()[0]
		return label.get_text()

	def reset_buttons(self):
		if self.allow_moving:
			self.move_up_button.set_sensitive(False)
			self.move_down_button.set_sensitive(False)
		self.delete_button.set_sensitive(False)
		if self.is_empty():
			self.clear_all_button.set_sensitive(False)

	def remove_row(self, row, reset=True):
		row_index = row.get_index()
		self.listbox.remove(row)
		if reset:
			self.reset_buttons()
		if self.delete_callback is not None:
			self.delete_callback(row_index)

	def on_delete_button_clicked(self, button):
		row = self.listbox.get_selected_row()
		self.remove_row(row)

	def move_row(self, row, new_index):
		self.listbox.select_row(None) # remove selection
		self.listbox.remove(row)
		self.listbox.insert(row, new_index)
		self.select_row(row)

	def on_move_up_button_clicked(self, button):
		row = self.listbox.get_selected_row()
		if row:
			index = row.get_index()
			self.move_row(row, index - 1)

	def on_move_down_button_clicked(self, button):
		row = self.listbox.get_selected_row()
		if row:
			index = row.get_index()
			self.move_row(row, index + 1)

	def clear(self):
		for row in self.get_rows():
			self.remove_row(row, False)
		self.reset_buttons()

	def on_clear_all_button_clicked(self, button):
		self.clear()

class CustomScaleButton(Gtk.Button):

	def __init__(self, value=0, min=0, max=100, step=1):
		Gtk.Button.__init__(self, value)
		self.connect('clicked', self.on_clicked)
		# scale
		adjustment = Gtk.Adjustment(value=value, lower=min, upper=max, step_increment=step, page_increment=step, page_size=0)
		self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment, digits=0)
		self.scale.set_size_request(100, -1)
		self.scale.connect('value-changed', self.on_value_changed)
		# popover
		self.popover = Gtk.Popover(relative_to=self, position=Gtk.PositionType.TOP)
		self.popover.add(self.scale)

	def on_clicked(self, button):
		self.popover.show_all()

	def on_value_changed(self, button):
		value = int(self.scale.get_value())
		self.set_label(str(value))

	def get_value(self):
		return int(self.get_label())

class CustomSpinButton(Gtk.Button):

	def __init__(self, min=0, max=100, value=0, step=1):
		text = min if value < min else value
		Gtk.Button.__init__(self, text)
		self.connect('clicked', self.on_clicked)
		# spin button
		self.spin_button = SpinButton(min=min, max=max, value=value, step=step, page_step=step)
		self.spin_button.connect('value-changed', self.on_value_changed)
		# popover
		self.popover = Gtk.Popover(relative_to=self, position=Gtk.PositionType.TOP)
		self.popover.set_border_width(2)
		self.popover.add(self.spin_button)

	def on_clicked(self, button):
		self.popover.show_all()

	def on_value_changed(self, button):
		value = self.spin_button.get_value_as_int()
		self.set_label(str(value))

	def get_value(self):
		return int(self.get_label())

class SpinButton(Gtk.SpinButton):

	def __init__(self, min=0, max=100, value=0, step=1, page_step=5):
		adjustment = Gtk.Adjustment(value=value, lower=min, upper=max, step_increment=step, page_increment=page_step, page_size=0)
		Gtk.SpinButton.__init__(self, adjustment=adjustment)

class ImageLabel(Gtk.Box):

	def __init__(self, image, text, padding=0):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
		self.set_border_width(padding)
		self.add(image)
		self.label = Gtk.Label(text, ellipsize=Pango.EllipsizeMode.END)
		self.add(self.label)

	def get_text(self):
		return self.label.get_text()

class StackListBox(Gtk.Box):

	def __init__(self):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.count = 0
		frame = Gtk.Frame()
		scrolled_window = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
		self.listbox = Gtk.ListBox()
		self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
		self.listbox.connect('row-activated', self.on_row_activated)
		scrolled_window.add(self.listbox)
		frame.add(scrolled_window)
		self.pack_start(frame, True, True, 0)
		self.stack = Gtk.Stack()
		self.pack_end(self.stack, False, False, 0)

	def on_row_activated(self, listbox, row):
		name = row.get_children()[0].get_text()
		self.stack.set_visible_child_name(name)

	def append(self, label, widget):
		self.listbox.add(label)
		if self.count == 0: # select first row
			self.listbox.select_row(self.listbox.get_row_at_index(self.count))
		self.stack.add_named(widget, label.get_text())
		self.count += 1

class ButtonBox(Gtk.Box):

	def __init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=5, centered=False, linked=False):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
		self.buttons_container = Gtk.Box(orientation=orientation)
		self.orientation = orientation
		self.linked = linked
		# set centered
		if centered:
			self.pack_start(self.buttons_container, True, False, 0)
		else:
			self.pack_start(self.buttons_container, False, False, 0)
		# set linked
		if linked:
			Gtk.StyleContext.add_class(self.buttons_container.get_style_context(), Gtk.STYLE_CLASS_LINKED)
		else:
			self.buttons_container.set_spacing(spacing)

	def add(self, button):
		if self.orientation == Gtk.Orientation.VERTICAL and not self.linked:
			hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
			hbox.pack_start(button, True, False, 0)
			self.buttons_container.add(hbox)
		else:
			self.buttons_container.add(button)

class MessageBox(Gtk.Box):

	def __init__(self, text=None, color='black', enable_buttons=False):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.enable_buttons = enable_buttons
		# label
		self.label = Gtk.Label(text)
		self.label.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse(color))
		self.add(self.label)
		# question buttons
		if enable_buttons:
			self.button_box = ButtonBox(linked=True)
			self.pack_end(self.button_box, False, False, 0)
			# yes
			self.yes_button = Gtk.Button()
			self.yes_button.set_tooltip_text('Yes')
			self.yes_button.set_image(Gtk.Image(stock=Gtk.STOCK_YES))
			self.button_box.add(self.yes_button)
			# no
			self.no_button = Gtk.Button()
			self.no_button.set_tooltip_text('No')
			self.no_button.set_image(Gtk.Image(stock=Gtk.STOCK_NO))
			self.button_box.add(self.no_button)

	def print_message(self, text, is_question=False):
		self.label.set_text(text)
		if self.enable_buttons:
			if is_question:
				self.button_box.show()
			else:
				self.button_box.hide()
		self.show()

class MenuButton(Gtk.Button):

	def __init__(self, text=None, position=Gtk.PositionType.TOP, padding=2):
		Gtk.Button.__init__(self, text)
		# popover
		self.popover = Gtk.Popover(relative_to=self, position=position)
		self.popover.set_border_width(padding)
		self.connect('clicked', self.on_clicked)

	def on_clicked(self, button):
		self.popover.show_all()

	def add(self, widget):
		self.popover.add(widget)

class MiniMap(Gtk.Frame):

	point_colors = {
		'Monster': 'red',
		'Resource': 'green',
		'NPC': 'blue',
		'None': 'black'
	}

	def __init__(self, background_color='#CECECE', show_grid=True, grid_color='#DDDDDD', grid_size=(15, 15), point_radius=3):
		Gtk.Frame.__init__(self)
		self.points = []
		self.point_opacity = 0.7
		self.point_radius = point_radius
		self.show_grid = show_grid
		self.grid_color = grid_color
		self.grid_size = grid_size
		self.background_color = background_color
		self.drawing_area = Gtk.DrawingArea()
		self.drawing_area.set_has_tooltip(True)
		self.drawing_area.connect('draw', self.on_draw)
		self.drawing_area.connect('query-tooltip', self.on_query_tooltip)
		self.add(self.drawing_area)

	def add_point(self, point, name=None, color=None, redraw=True):
		# set point coordinates
		new_point = {
			'x': int(point['x']),
			'y': int(point['y']),
			'width': int(point['width']),
			'height': int(point['height'])
		}
		# set point name
		if name is not None:
			new_point['name'] = name
		elif 'name' in point:
			new_point['name'] = point['name']
		else:
			new_point['name'] = None
		# set point color
		if color is not None:
			new_point['color'] = color
		elif 'color' in point:
			new_point['color'] = point['color']
		else:
			new_point['color'] = None
		# add point
		self.points.append(new_point)
		if redraw:
			self.drawing_area.queue_draw()

	def add_points(self, points, name=None, color=None):
		for point in points:
			self.add_point(point, name, color, False)
		self.drawing_area.queue_draw()

	def remove_point(self, index):
		if 0 <= index < len(self.points):
			del self.points[index]
			self.drawing_area.queue_draw()

	def clear(self):
		if self.points:
			self.points = []
			self.drawing_area.queue_draw()

	def on_draw(self, widget, cr):
		drawing_area = widget.get_allocation()
		square_width, square_height = self.grid_size
		cr.set_line_width(1)
		# set color function
		def set_color(value, opacity=1.0):
			color = Gdk.color_parse(value)
			cr.set_source_rgba(float(color.red) / 65535, float(color.green) / 65535, float(color.blue) / 65535, opacity)
		# fill background with color
		if self.background_color:
			cr.rectangle(0, 0, drawing_area.width, drawing_area.height)
			set_color(self.background_color)
			cr.fill()
		# draw grid lines
		if self.show_grid:
			set_color(self.grid_color)
			# draw vertical lines
			for x in range(square_width, drawing_area.width, square_width + 1): # +1 for line width
				cr.move_to(x + 0.5, 0) # +0.5 for smooth line
				cr.line_to(x + 0.5, drawing_area.height)
			# draw horizontal lines
			for y in range(square_height, drawing_area.height, square_height + 1):
				cr.move_to(0, y + 0.5)
				cr.line_to(drawing_area.width, y + 0.5)
			cr.stroke()
		# draw points
		for point in self.points:
			# fit point to drawing area (should keep here, because it's useful when drawing area get resized)
			x, y = fit_position_to_destination(point['x'], point['y'], point['width'], point['height'], drawing_area.width, drawing_area.height)
			#set_color('black')
			cr.arc(x, y, self.point_radius, 0, 2*math.pi)
			#cr.stroke_preserve()
			color = self.point_colors['None'] if point['color'] is None else point['color']
			set_color(color, self.point_opacity)
			cr.fill()

	def get_tooltip_widget(self, point):
		# on draw function
		def on_draw(widget, cr):
			cr.set_line_width(1)
			# draw point
			color = Gdk.color_parse(point['color'])
			cr.set_source_rgba(float(color.red) / 65535, float(color.green) / 65535, float(color.blue) / 65535, self.point_opacity)
			cr.arc(self.point_radius, self.point_radius, self.point_radius, 0, 2*math.pi)
			cr.fill()
		# tooltip widget
		if point['name'] is not None:
			widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
			if point['color'] is not None:
				drawing_area = Gtk.DrawingArea()
				point_diameter = self.point_radius*2
				drawing_area.set_size_request(point_diameter, point_diameter)
				drawing_area.connect('draw', on_draw)
				box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
				box.pack_start(drawing_area, True, False, 0)
				widget.add(box)
			widget.add(Gtk.Label(point['name']))
			widget.show_all()
		else:
			widget = None
		return widget

	def on_query_tooltip(self, widget, x, y, keyboard_mode, tooltip):
		drawing_area = self.drawing_area.get_allocation()
		tooltip_widget = None
		# check if a point is hovered
		for point in self.points:
			# fit point to drawing area
			point_x, point_y = fit_position_to_destination(point['x'], point['y'], point['width'], point['height'], drawing_area.width, drawing_area.height)
			# TODO: the check below should be circular, not rectangular
			if point_x - self.point_radius <= x <= point_x + self.point_radius and point_y - self.point_radius <= y <= point_y + self.point_radius:
				tooltip_widget = self.get_tooltip_widget(point)
				break
		# if so
		if tooltip_widget is not None:
			# set tooltip widget
			tooltip.set_custom(tooltip_widget)
			# show the tooltip
			return True
		else:
			return False
