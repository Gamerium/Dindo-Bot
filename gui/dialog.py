# coding=utf-8
# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from lib import tools, shared, settings, accounts, maps
from .custom import CustomComboBox, CustomTreeView, ButtonBox, MessageBox, MiniMap

class AboutDialog(Gtk.AboutDialog):

	def __init__(self, transient_for):
		Gtk.AboutDialog.__init__(self, transient_for=transient_for)
		self.set_program_name(shared.__program_name__)
		self.set_version(shared.__version__)
		self.set_comments(shared.__program_desc__)
		self.set_website(shared.__website__)
		self.set_website_label(shared.__website_label__)
		self.set_authors(shared.__authors__)
		logo = GdkPixbuf.Pixbuf.new_from_file_at_size(tools.get_full_path('icons/cover.png'), 64, 64)
		self.set_logo(logo)
		self.connect('response', lambda dialog, response: self.destroy())

class CustomDialog(Gtk.Dialog):

	def __init__(self, title, transient_for=None, destroy_on_response=True):
		Gtk.Dialog.__init__(self, modal=True, transient_for=transient_for, title=title)
		self.set_border_width(10)
		self.set_resizable(False)
		if destroy_on_response:
			self.connect('response', lambda dialog, response: self.destroy())
		# Header Bar
		hb = Gtk.HeaderBar(title=title)
		hb.set_show_close_button(True)
		self.set_titlebar(hb)

class AlertDialog(CustomDialog):

	def __init__(self, transient_for, message):
		CustomDialog.__init__(self, transient_for=transient_for, title='Alert')
		# message
		content_area = self.get_content_area()
		content_area.set_spacing(5)
		content_area.add(Gtk.Label(message, use_markup=True))
		# Ok button
		self.action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)
		ok_button = Gtk.Button('Ok')
		self.add_action_widget(ok_button, Gtk.ResponseType.OK)
		self.show_all()
		self.run()

class CopyTextDialog(CustomDialog):

	def __init__(self, transient_for, text):
		CustomDialog.__init__(self, transient_for=transient_for, title='Copy Text')
		# text entry
		content_area = self.get_content_area()
		content_area.set_spacing(5)
		entry = Gtk.Entry()
		entry.set_text(text)
		entry.set_width_chars(60)
		content_area.add(entry)
		# Close button
		self.action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)
		close_button = Gtk.Button('Close')
		self.add_action_widget(close_button, Gtk.ResponseType.OK)
		self.show_all()
		self.run()

class LoadMapDialog(CustomDialog):

	def __init__(self, transient_for):
		CustomDialog.__init__(self, transient_for=transient_for, title='Load Map', destroy_on_response=False)
		self.parent = transient_for
		self.data = maps.load()
		self.set_size_request(300, -1)
		self.connect('delete-event', lambda dialog, response: self.destroy())
		# Map combobox
		content_area = self.get_content_area()
		content_area.set_spacing(5)
		content_area.add(Gtk.Label('<b>Map</b>', xalign=0, use_markup=True))
		self.maps_combo = CustomComboBox(self.data, sort=True)
		self.maps_combo.set_margin_left(10)
		self.maps_combo.connect('changed', self.on_maps_combo_changed)
		content_area.add(self.maps_combo)
		# Error box
		self.error_box = MessageBox(color='red')
		self.error_box.set_margin_left(10)
		content_area.add(self.error_box)
		# Load button
		self.action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)
		load_button = Gtk.Button('Load')
		load_button.connect('clicked', self.on_load_button_clicked)
		self.add_action_widget(load_button, Gtk.ResponseType.OK)
		self.show_all()
		self.reset()

	def reset(self):
		self.error_box.hide()

	def on_maps_combo_changed(self, combo):
		self.reset()
		if not self.parent.map_data_listbox.is_empty():
			self.error_box.print_message('Your current data will be erased !')

	def on_load_button_clicked(self, button):
		selected = self.maps_combo.get_active_text()
		if selected:
			# clear listbox & view
			self.parent.map_data_listbox.clear()
			self.parent.map_view.clear()
			# append to listbox
			text = maps.to_string(self.data[selected])
			lines = text[1:-1].split('},') # [1:-1] to remove '[]'
			for line in lines:
				text = line.strip()
				if text.startswith('{') and not text.endswith('}'):
					text += '}'
				self.parent.map_data_listbox.append_text(text)
			# append to view
			self.parent.map_view.add_points(self.data[selected], 'Resource', MiniMap.point_colors['Resource'])
			# destroy dialog
			self.destroy()
		else:
			self.error_box.print_message('Please select a map')

class DeleteMapDialog(CustomDialog):

	def __init__(self, transient_for):
		CustomDialog.__init__(self, transient_for=transient_for, title='Delete Map', destroy_on_response=False)
		self.parent = transient_for
		self.data = maps.load()
		self.set_size_request(300, -1)
		self.connect('delete-event', lambda dialog, response: self.destroy())
		# Map combobox
		content_area = self.get_content_area()
		content_area.set_spacing(5)
		content_area.add(Gtk.Label('<b>Map</b>', xalign=0, use_markup=True))
		self.maps_combo = CustomComboBox(self.data, sort=True)
		self.maps_combo.set_margin_left(10)
		self.maps_combo.connect('changed', lambda combo: self.reset())
		content_area.add(self.maps_combo)
		# Error box
		self.error_box = MessageBox(color='red', enable_buttons=True)
		self.error_box.set_margin_left(10)
		self.error_box.yes_button.connect('clicked', lambda button: self.delete_data())
		self.error_box.no_button.connect('clicked', lambda button: self.reset())
		content_area.add(self.error_box)
		# Delete button
		self.action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)
		delete_button = Gtk.Button('Delete')
		delete_button.connect('clicked', self.on_delete_button_clicked)
		self.add_action_widget(delete_button, Gtk.ResponseType.OK)
		self.show_all()
		self.reset()

	def reset(self):
		self.error_box.hide()
		self.action_area.show()

	def delete_data(self):
		selected = self.maps_combo.get_active()
		if selected != -1:
			# delete
			map_name = self.maps_combo.get_active_text()
			del self.data[map_name]
			self.maps_combo.remove(selected)
			# save data
			maps.save(self.data)
			# update parent window
			self.parent.collect_map_combo.append_list(self.data, sort=True, clear=True)

	def on_delete_button_clicked(self, button):
		if self.maps_combo.get_active() != -1:
			self.action_area.hide()
			self.error_box.print_message('Confirm delete?', True)
		else:
			self.error_box.print_message('Please select a map')

class SaveMapDialog(CustomDialog):

	def __init__(self, transient_for):
		CustomDialog.__init__(self, transient_for=transient_for, title='Save Map', destroy_on_response=False)
		self.parent = transient_for
		self.data = maps.load()
		self.set_size_request(300, -1)
		self.connect('delete-event', lambda dialog, response: self.destroy())
		# Map Name entry
		content_area = self.get_content_area()
		content_area.set_spacing(5)
		content_area.add(Gtk.Label('<b>Map Name</b>', xalign=0, use_markup=True))
		self.entry = Gtk.Entry()
		self.entry.set_margin_left(10)
		self.entry.connect('focus-in-event', lambda entry, event: self.reset())
		content_area.add(self.entry)
		# Error box
		self.error_box = MessageBox(color='red', enable_buttons=True)
		self.error_box.set_margin_left(10)
		self.error_box.yes_button.connect('clicked', lambda button: self.save_data(self.get_map_name(), self.data))
		self.error_box.no_button.connect('clicked', lambda button: self.reset())
		content_area.add(self.error_box)
		# Save button
		self.action_area.set_layout(Gtk.ButtonBoxStyle.CENTER)
		save_button = Gtk.Button('Save')
		save_button.connect('clicked', self.on_save_button_clicked)
		self.add_action_widget(save_button, Gtk.ResponseType.OK)
		self.show_all()
		self.reset()

	def reset(self):
		self.error_box.hide()
		self.action_area.show()

	def get_map_name(self):
		return self.entry.get_text().strip()

	def save_data(self, name, data):
		# get map data
		map_data = []
		for row in self.parent.map_data_listbox.get_rows():
			text = self.parent.map_data_listbox.get_row_text(row)
			map_data.append(maps.to_array(text))
		data[name] = map_data
		# save data
		maps.save(data)
		# update parent window
		self.parent.collect_map_combo.append_list(data, sort=True, clear=True)
		# destroy dialog
		self.destroy()

	def on_save_button_clicked(self, button):
		# get map name
		name = self.get_map_name()
		# check if empty
		if not name:
			self.error_box.print_message('Please type a name')
		else:
			# check if already exists
			if name in self.data:
				self.action_area.hide()
				self.error_box.print_message('Map name already exists, would you like to override it?', True)
			else:
				self.save_data(name, self.data)

class OpenFileDialog(Gtk.FileChooserDialog):

	def __init__(self, title, transient_for=None, filter=None):
		Gtk.FileChooserDialog.__init__(self, title=title, transient_for=transient_for, action=Gtk.FileChooserAction.OPEN)
		if filter is not None and len(filter) > 1:
			name, pattern = filter
			file_filter = Gtk.FileFilter()
			file_filter.set_name('%s (%s)' % (name, pattern))
			file_filter.add_pattern(pattern)
			self.add_filter(file_filter)
		self.add_button('_Cancel', Gtk.ResponseType.CANCEL)
		self.add_button('_Open', Gtk.ResponseType.OK)
		self.set_default_response(Gtk.ResponseType.OK)

class SaveFileDialog(Gtk.FileChooserDialog):

	def __init__(self, title, transient_for=None, filter=None):
		Gtk.FileChooserDialog.__init__(self, title=title, transient_for=transient_for, action=Gtk.FileChooserAction.SAVE)
		if filter is not None and len(filter) > 1:
			name, pattern = filter
			file_filter = Gtk.FileFilter()
			file_filter.set_name('%s (%s)' % (name, pattern))
			file_filter.add_pattern(pattern)
			self.add_filter(file_filter)
		self.add_button('_Cancel', Gtk.ResponseType.CANCEL)
		self.add_button('_Save', Gtk.ResponseType.OK)
		self.set_default_response(Gtk.ResponseType.OK)

class PreferencesDialog(CustomDialog):

	def __init__(self, transient_for, title='Preferences'):
		CustomDialog.__init__(self, transient_for=transient_for, title=title)
		self.parent = transient_for
		# Stack & Stack switcher
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		content_area = self.get_content_area()
		content_area.add(vbox)
		stack = Gtk.Stack()
		stack.set_margin_top(5)
		#stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
		#stack.set_transition_duration(1000)
		stack_switcher = Gtk.StackSwitcher()
		stack_switcher.set_stack(stack)
		vbox.pack_start(stack_switcher, True, True, 0)
		vbox.pack_start(stack, True, True, 0)
		### General
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack.add_titled(box, 'general', 'General')
		## Debug
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		box.add(hbox)
		hbox.add(Gtk.Label('<b>Debug</b>', xalign=0, use_markup=True))
		debug_switch = Gtk.Switch()
		debug_switch.set_active(self.parent.settings['Debug']['Enabled'])
		debug_switch.connect('notify::active', self.on_debug_switch_activated)
		hbox.pack_end(debug_switch, False, False, 0)
		# Level
		self.debug_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.debug_box.set_margin_left(10)
		self.debug_box.set_sensitive(self.parent.settings['Debug']['Enabled'])
		box.add(self.debug_box)
		self.debug_box.add(Gtk.Label('Level'))
		debug_level_combo = CustomComboBox(['High', 'Normal', 'Low'])
		debug_level_combo.set_active(self.parent.settings['Debug']['Level'])
		debug_level_combo.connect('changed', 
			lambda combo: settings.update_and_save(self.parent.settings, key='Debug', subkey='Level', value=combo.get_active()))
		self.debug_box.pack_end(debug_level_combo, False, False, 0)
		## Game
		box.add(Gtk.Label('<b>Game</b>', xalign=0, use_markup=True))
		# Keep game checkbox
		keep_game_on_unplug_check = Gtk.CheckButton('Keep game open when unbind')
		keep_game_on_unplug_check.set_margin_left(10)
		keep_game_on_unplug_check.set_active(self.parent.settings['Game']['KeepOpen'])
		keep_game_on_unplug_check.connect('clicked', 
			lambda check: settings.update_and_save(self.parent.settings, key='Game', subkey='KeepOpen', value=check.get_active()))
		box.add(keep_game_on_unplug_check)
		## Account
		box.add(Gtk.Label('<b>Account</b>', xalign=0, use_markup=True))
		# Exit game checkbox
		exit_game_on_disconnect_check = Gtk.CheckButton('Exit game when disconnect')
		exit_game_on_disconnect_check.set_margin_left(10)
		exit_game_on_disconnect_check.set_active(self.parent.settings['Account']['ExitGame'])
		exit_game_on_disconnect_check.connect('clicked', 
			lambda check: settings.update_and_save(self.parent.settings, key='Account', subkey='ExitGame', value=check.get_active()))
		box.add(exit_game_on_disconnect_check)
		### Bot
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack.add_titled(box, 'bot', 'Bot')
		## State
		box.add(Gtk.Label('<b>State</b>', xalign=0, use_markup=True))
		# PodBar
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		hbox.add(Gtk.Label('PodBar'))
		podbar_switch = Gtk.Switch()
		podbar_switch.set_active(self.parent.settings['State']['EnablePodBar'])
		podbar_switch.connect('notify::active', self.on_podbar_switch_activated)
		hbox.pack_end(podbar_switch, False, False, 0)
		box.add(hbox)
		# MiniMap
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		hbox.set_margin_left(10)
		hbox.add(Gtk.Label('MiniMap'))
		minimap_switch = Gtk.Switch()
		minimap_switch.set_active(self.parent.settings['State']['EnableMiniMap'])
		minimap_switch.connect('notify::active', self.on_minimap_switch_activated)
		hbox.pack_end(minimap_switch, False, False, 0)
		box.add(hbox)
		## Farming
		box.add(Gtk.Label('<b>Farming</b>', xalign=0, use_markup=True))
		# Save dragodindes images
		save_dragodindes_images_check = Gtk.CheckButton('Save dragodindes image')
		save_dragodindes_images_check.set_margin_left(10)
		save_dragodindes_images_check.set_active(self.parent.settings['Farming']['SaveDragodindesImages'])
		save_dragodindes_images_check.connect('clicked', 
			lambda check: settings.update_and_save(self.parent.settings, key='Farming', subkey='SaveDragodindesImages', value=check.get_active()))
		box.add(save_dragodindes_images_check)
		### Shortcuts
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		stack.add_titled(box, 'shortcuts', 'Shortcuts')
		## Keyboard Shortcuts
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.add(Gtk.Label('<b>Keyboard Shortcuts</b>', xalign=0, use_markup=True))
		box.add(hbox)
		# Switch
		shortcuts_switch = Gtk.Switch()
		shortcuts_switch.set_active(self.parent.settings['EnableShortcuts'])
		shortcuts_switch.connect('notify::active', self.on_shortcuts_switch_activated)
		hbox.pack_end(shortcuts_switch, False, False, 0)
		# TreeView
		model = Gtk.ListStore(str, str)
		text_renderer = Gtk.CellRendererText()
		columns = [
			Gtk.TreeViewColumn('Action', text_renderer, text=0),
			Gtk.TreeViewColumn('Shortcut', text_renderer, text=1)
		]
		self.shortcuts_tree_view = CustomTreeView(model, columns)
		self.shortcuts_tree_view.vbox.set_sensitive(self.parent.settings['EnableShortcuts'])
		self.shortcuts_tree_view.connect('button-press-event', self.on_shortcuts_tree_view_double_clicked)
		self.shortcuts_tree_view.connect('selection-changed', self.on_shortcuts_tree_view_selection_changed)
		# fill treeview
		for action in sorted(self.parent.settings['Shortcuts']):
			shortcut = self.parent.settings['Shortcuts'][action]
			self.shortcuts_tree_view.append_row([action, shortcut], select=False, scroll_to=False)
		box.pack_start(self.shortcuts_tree_view, True, True, 0)
		# ActionBar
		actionbar = Gtk.ActionBar()
		self.shortcuts_edit_button = Gtk.Button()
		self.shortcuts_edit_button.set_tooltip_text('Edit')
		self.shortcuts_edit_button.set_image(Gtk.Image(icon_name='document-edit-symbolic'))
		self.shortcuts_edit_button.set_sensitive(False)
		self.shortcuts_edit_button.connect('clicked', self.on_shortcuts_edit_button_clicked)
		actionbar.add(self.shortcuts_edit_button)
		self.shortcuts_tree_view.vbox.pack_end(actionbar, False, False, 0)
		self.show_all()

	def on_shortcuts_switch_activated(self, switch, pspec):
		value = switch.get_active()
		self.shortcuts_tree_view.vbox.set_sensitive(value)
		settings.update_and_save(self.parent.settings, 'EnableShortcuts', value)

	def show_shortcuts_dialog(self):
		selected_row = self.shortcuts_tree_view.get_selected_row()
		if selected_row:
			dialog = ShortcutsDialog(self, selected_row[0])
			dialog.run()

	def on_shortcuts_edit_button_clicked(self, button):
		self.show_shortcuts_dialog()

	def on_shortcuts_tree_view_double_clicked(self, widget, event):
		if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
			self.show_shortcuts_dialog()

	def on_shortcuts_tree_view_selection_changed(self, selection):
		if not self.shortcuts_edit_button.get_sensitive():
			self.shortcuts_edit_button.set_sensitive(True)

	def on_podbar_switch_activated(self, switch, pspec):
		value = switch.get_active()
		if value:
			self.parent.podbar_box.show()
		else:
			self.parent.podbar_box.hide()
		settings.update_and_save(self.parent.settings, key='State', subkey='EnablePodBar', value=value)

	def on_minimap_switch_activated(self, switch, pspec):
		value = switch.get_active()
		if value:
			self.parent.minimap_box.show()
		else:
			self.parent.minimap_box.hide()
		settings.update_and_save(self.parent.settings, key='State', subkey='EnableMiniMap', value=value)

	def on_debug_switch_activated(self, switch, pspec):
		value = switch.get_active()
		self.debug_box.set_sensitive(value)
		if value:
			self.parent.debug_page.show()
		else:
			self.parent.debug_page.hide()
		settings.update_and_save(self.parent.settings, key='Debug', subkey='Enabled', value=value)

class ShortcutsDialog(CustomDialog):

	def __init__(self, transient_for, action_name):
		title = '%s Shortcut' % action_name
		CustomDialog.__init__(self, transient_for=transient_for, title=title, destroy_on_response=False)
		self.parent = transient_for
		self.action_name = action_name
		self.connect('key-press-event', self.on_key_press)
		self.connect('response', self.on_response)
		# Action
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		content_area = self.get_content_area()
		content_area.add(vbox)
		action_label = Gtk.Label(xalign=0)
		action_label.set_line_wrap(True)
		action_label.set_max_width_chars(40)
		action_label.set_markup('Press keys on keyboard that you want to use to trigger « <b>%s</b> » action' % action_name)
		vbox.add(action_label)
		# Shortcut
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		vbox.add(hbox)
		hbox.add(Gtk.Label('Shortcut:', xalign=0))
		self.shortcut_label = Gtk.Label()
		shortcut = self.parent.parent.settings['Shortcuts'][action_name]
		if shortcut is not None:
			self.shortcut_label.set_markup('<b>%s</b>' % shortcut)
		hbox.add(self.shortcut_label)
		# Error box
		self.error_box = MessageBox(color='red')
		vbox.add(self.error_box)
		# Clear
		self.action_area.set_margin_top(10)
		clear_button = Gtk.Button('Clear')
		clear_button.set_image(Gtk.Image(icon_name='edit-clear'))
		self.add_action_widget(clear_button, Gtk.ResponseType.CANCEL)
		# Save
		save_button = Gtk.Button('Save')
		save_button.set_image(Gtk.Image(icon_name='document-save'))
		self.add_action_widget(save_button, Gtk.ResponseType.OK)
		self.show_all()
		self.error_box.hide()

	def on_key_press(self, widget, event):
		# get keyname
		keyname = Gdk.keyval_name(event.keyval)
		# check combinations
		if event.state & Gdk.ModifierType.CONTROL_MASK:
			shortcut = 'Ctrl+%s' % keyname
		elif event.state & Gdk.ModifierType.MOD1_MASK:
			shortcut = 'Alt+%s' % keyname
		elif event.state & Gdk.ModifierType.SHIFT_MASK:
			shortcut = 'Shift+%s' % keyname
		else:
			shortcut = keyname
		# show shortcut
		self.shortcut_label.set_markup('<b>%s</b>' % shortcut)
		# hide error box
		self.error_box.hide()
		# stop event propagation
		return True

	def on_response(self, dialog, response):
		# Save
		if response == Gtk.ResponseType.OK:
			# get shortcut
			shortcut = self.shortcut_label.get_text()
			if shortcut:
				# check if duplicated
				for action in self.parent.parent.settings['Shortcuts']:
					value = self.parent.parent.settings['Shortcuts'][action]
					if shortcut == value and action != self.action_name:
						self.error_box.print_message('Duplicate shortcut, please choose another one')
						return
			else:
				shortcut = None
			# save shortcut
			settings.update_and_save(self.parent.parent.settings, key='Shortcuts', subkey=self.action_name, value=shortcut)
			# apply to treeview
			for row in self.parent.shortcuts_tree_view.model:
				if row[0] == self.action_name:
					row[1] = shortcut
					break
		# Clear
		elif response == Gtk.ResponseType.CANCEL:
			# clear shortcut label
			self.shortcut_label.set_text('')
			# hide error box
			self.error_box.hide()
			return
		# Close
		self.destroy()

class AccountsDialog(CustomDialog):

	def __init__(self, transient_for, title='Accounts'):
		CustomDialog.__init__(self, transient_for=transient_for, title=title)
		self.parent = transient_for
		### New
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		content_area = self.get_content_area()
		content_area.add(vbox)
		vbox.add(Gtk.Label('<b>New</b>', xalign=0, use_markup=True))
		new_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		vbox.add(new_hbox)
		new_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		new_hbox.pack_start(new_vbox, True, False, 0)
		## Login
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		new_vbox.add(hbox)
		hbox.add(Gtk.Label('Login'))
		# Entry
		self.login_entry = Gtk.Entry()
		self.login_entry.connect('focus-in-event', lambda entry, event: self.error_box.hide())
		hbox.pack_end(self.login_entry, False, False, 0)
		## Password
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		new_vbox.add(hbox)
		hbox.add(Gtk.Label('Password'))
		# Show password
		show_password_button = Gtk.Button()
		show_password_button.set_tooltip_text('Show password')
		show_password_button.set_image(Gtk.Image(icon_name='channel-insecure-symbolic'))
		show_password_button.set_relief(Gtk.ReliefStyle.NONE)
		show_password_button.connect('clicked', self.on_show_password_button_clicked)
		hbox.add(show_password_button)
		# Entry
		self.password_entry = Gtk.Entry(visibility=False)
		self.password_entry.connect('focus-in-event', lambda entry, event: self.error_box.hide())
		hbox.pack_end(self.password_entry, False, False, 0)
		## Error box
		self.error_box = MessageBox(color='red')
		new_vbox.add(self.error_box)
		## Add
		add_button = Gtk.Button('Add')
		add_button.set_image(Gtk.Image(icon_name='list-add-symbolic'))
		add_button.connect('clicked', self.on_add_button_clicked)
		button_box = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL, layout_style=Gtk.ButtonBoxStyle.CENTER)
		button_box.add(add_button)
		new_vbox.add(button_box)
		### Accounts
		vbox.add(Gtk.Label('<b>Accounts</b>', xalign=0, use_markup=True))
		## TreeView
		model = Gtk.ListStore(int, str, str)
		text_renderer = Gtk.CellRendererText()
		columns = [
			Gtk.TreeViewColumn('ID', text_renderer, text=0),
			Gtk.TreeViewColumn('Login', text_renderer, text=1),
			Gtk.TreeViewColumn('Password', text_renderer, text=2)
		]
		self.tree_view = CustomTreeView(model, columns)
		self.tree_view.set_size_request(400, 160)
		self.tree_view.connect('selection-changed', self.on_tree_view_selection_changed)
		vbox.pack_start(self.tree_view, True, True, 0)
		# fill treeview
		for account in sorted(accounts.load(), key=lambda item: item['position']):
			pwd = '*' * len(account['pwd'])
			self.tree_view.append_row([account['id'], account['login'], pwd], select=False)
		## ActionBar
		actionbar = Gtk.ActionBar()
		self.tree_view.vbox.pack_end(actionbar, False, False, 0)
		buttons_box = ButtonBox(linked=True)
		actionbar.add(buttons_box)
		# Move up
		self.move_up_button = Gtk.Button()
		self.move_up_button.set_tooltip_text('Move up')
		self.move_up_button.set_image(Gtk.Image(icon_name='go-up-symbolic'))
		self.move_up_button.set_sensitive(False)
		self.move_up_button.connect('clicked', self.on_move_up_button_clicked)
		buttons_box.add(self.move_up_button)
		# Move down
		self.move_down_button = Gtk.Button()
		self.move_down_button.set_tooltip_text('Move down')
		self.move_down_button.set_image(Gtk.Image(icon_name='go-down-symbolic'))
		self.move_down_button.set_sensitive(False)
		self.move_down_button.connect('clicked', self.on_move_down_button_clicked)
		buttons_box.add(self.move_down_button)
		# Delete
		self.delete_button = Gtk.Button()
		self.delete_button.set_tooltip_text('Delete')
		self.delete_button.set_image(Gtk.Image(icon_name='edit-delete-symbolic'))
		self.delete_button.set_sensitive(False)
		self.delete_button.connect('clicked', self.on_delete_button_clicked)
		buttons_box.add(self.delete_button)
		self.show_all()
		self.error_box.hide()

	def update_parent_window(self, accounts_list):
		self.parent.accounts_combo.append_list(accounts_list, text_key='login', value_key='id', sort_key='position', clear=True)
		self.parent.connect_accounts_combo.append_list(accounts_list, text_key='login', value_key='id', sort_key='position', clear=True)

	def on_add_button_clicked(self, button):
		login = self.login_entry.get_text()
		password = self.password_entry.get_text()
		if not login:
			self.error_box.print_message('Please type a login')
		elif not password:
			self.error_box.print_message('Please type a password')
		elif accounts.is_duplicate(login):
			self.error_box.print_message('Duplicate login, please choose another one')
		else:
			# hide error box
			self.error_box.hide()
			# add account
			id, accounts_list = accounts.add(login, password)
			# append to treeview
			pwd = '*' * len(password)
			self.tree_view.append_row([id, login, pwd])
			# update parent window
			self.update_parent_window(accounts_list)

	def swap_accounts(self, old_index, new_index):
		# get accounts ids
		account1_id = self.tree_view.model[old_index][0]
		account2_id = self.tree_view.model[new_index][0]
		# swap accounts positions
		accounts_list = accounts.swap(account1_id, account2_id)
		# update parent window
		self.update_parent_window(accounts_list)
		# set move buttons sensitivity
		self.set_move_buttons_sensitivity(new_index)

	def on_move_up_button_clicked(self, button):
		model, tree_iter = self.tree_view.selection.get_selected()
		if tree_iter:
			previous_iter = model.iter_previous(tree_iter)
			if previous_iter is not None:
				# get row index
				index = self.tree_view.get_row_index(tree_iter)
				# move up
				model.move_before(tree_iter, previous_iter)
				# swap accounts
				self.swap_accounts(index, index - 1)

	def on_move_down_button_clicked(self, button):
		model, tree_iter = self.tree_view.selection.get_selected()
		if tree_iter:
			next_iter = model.iter_next(tree_iter)
			if next_iter is not None:
				# get row index
				index = self.tree_view.get_row_index(tree_iter)
				# move down
				model.move_after(tree_iter, next_iter)
				# swap accounts
				self.swap_accounts(index, index + 1)

	def on_delete_button_clicked(self, button):
		# remove selected account
		id = self.tree_view.get_selected_row()[0]
		accounts_list = accounts.remove(id)
		# remove from treeview also
		self.tree_view.remove_selected_row()
		# update parent window
		self.update_parent_window(accounts_list)

	def on_show_password_button_clicked(self, button):
		if self.password_entry.get_visibility():
			self.password_entry.set_visibility(False)
			button.set_image(Gtk.Image(icon_name='channel-insecure-symbolic'))
			button.set_tooltip_text('Show password')
		else:
			self.password_entry.set_visibility(True)
			button.set_image(Gtk.Image(icon_name='channel-secure-symbolic'))
			button.set_tooltip_text('Hide password')

	def set_move_buttons_sensitivity(self, index):
		# Move up
		if index <= 0:
			self.move_up_button.set_sensitive(False)
		elif not self.move_up_button.get_sensitive():
			self.move_up_button.set_sensitive(True)
		# Move down
		rows_count = self.tree_view.get_rows_count()
		if index >= rows_count - 1:
			self.move_down_button.set_sensitive(False)
		elif not self.move_down_button.get_sensitive():
			self.move_down_button.set_sensitive(True)

	def on_tree_view_selection_changed(self, selection):
		model, tree_iter = selection.get_selected()
		if tree_iter is None:
			self.move_up_button.set_sensitive(False)
			self.move_down_button.set_sensitive(False)
			self.delete_button.set_sensitive(False)
		else:
			# Move buttons
			index = self.tree_view.get_row_index(tree_iter)
			self.set_move_buttons_sensitivity(index)
			# Delete button
			if not self.delete_button.get_sensitive():
				self.delete_button.set_sensitive(True)
