# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, Pango

class CustomComboBox(Gtk.ComboBoxText):

	def __init__(self, data=[], sort=False):
		Gtk.ComboBoxText.__init__(self)
		if sort:
			data = sorted(data)
		for text in data:
			self.append_text(text)

class CustomListBox(Gtk.Frame):

	perform_scroll = False
	add_callback = None
	delete_callback = None

	def __init__(self, allow_moving=True):
		Gtk.Frame.__init__(self)
		self.allow_moving = allow_moving
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

	def remove_row(self, row):
		self.listbox.remove(row)
		self.reset_buttons()
		if self.delete_callback is not None:
			self.delete_callback()

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

	def clear_all(self):
		for row in self.get_rows():
			self.listbox.remove(row)
		self.reset_buttons()
		if self.delete_callback is not None:
			self.delete_callback()

	def on_clear_all_button_clicked(self, button):
		self.clear_all()

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

	count = 0

	def __init__(self):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
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
