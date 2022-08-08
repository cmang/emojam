#!/usr/bin/env python3

# Emojam - An Emoji keyboard for Linux (Gtk/X11)
# (c) 2022 Sam Foster

# Requires GTK for Python 3
# Requires Google's emoji fonts:
# Noto Color Emoji
# Package for Google's emoji font:
# fonts-noto-color-emoji
# /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf

import gi

import emojam.emojam_emojis as emojam_emojis
import emojam.emojam_config as emojam_config

gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")

from gi.repository import Gtk, Gdk, Notify

class EmojamWindow(Gtk.Window):
    def __init__(self):
        # set up window
        super().__init__(title="Emojam")
        self.set_border_width(10)
        self.set_default_size(740, 400)
        self.set_can_focus(False)
        self.status_bar = None
        self.zoom_control_box = None
        self.group_buttons_dict = {}
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.clipboard_primary = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        # make group for keyboard shortcuts
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)
        # init emoji related stuff, and config
        self.s_active_group = ""
        self.set_css_style()    # for our emoji fonts
        self.init_emojis()  # load emojis
        self.init_config()
        self.s_output_line = ""
        self.current_menu_button = None
        # Initialize composite layout for the window
        box_layout = self.make_larger_layout()
        self.add(box_layout)
        self.show_all()
        self.set_active_group("All")
        self.refresh_statusbar()  # in case the config file overrides default
        self.refresh_zoomer()
        Gtk.Settings.get_default().connect("notify::gtk-theme-name",
                                           self.gtk_theme_changed)
        Notify.init("Emojam")

    def make_larger_layout(self):
        box_layout = Gtk.VBox(spacing=10)
        # make the search entry
        search_box = self.make_search_box()
        # make hamburger menu
        hamburger_menu = self.make_hamburger_menu()
        # make box for search_box and hamburger menu
        search_line_box = Gtk.HBox(spacing=10)
        # make a zoom control
        zoom_control_box = self.make_zoom_control_box()
        self.zoom_control_box = zoom_control_box
        # pack em in proper order
        search_line_box.pack_start(hamburger_menu, expand=False, fill=True,
                                   padding=0)
        search_line_box.pack_start(search_box, expand=True, fill=True,
                                   padding=0)
        search_line_box.pack_start(zoom_control_box, expand=False, fill=True,
                                   padding=0)
        # add search box to the top of the VBox
        box_layout.pack_start(search_line_box, expand=False, fill=True,
                              padding=0)
        # make output line
        self.output_line_box = self.make_output_line()
        box_layout.pack_start(self.output_line_box, expand=False, fill=True,
                              padding=0)
        # make groups buttons area
        groups_button_box = self.make_groups_buttons()
        # add groups buttons just below search box
        box_layout.pack_start(groups_button_box, expand=False, fill=True,
                              padding=0)
        # Make flowbox label, showing which group is selected
        self.selected_group_label = Gtk.Label(label="All")
        self.selected_group_label.props.xalign = 0.0
        self.selected_group_label.show()
        box_layout.pack_start(self.selected_group_label, expand=False,
                              fill=True, padding=0)
        # make the emoji flowbox area
        scrolled_flowbox = self.make_a_scrolled_flowbox_layout()
        # add flowbox to the bottom of the VBox
        box_layout.pack_start(scrolled_flowbox, expand=True, fill=True,
                              padding=0)
        # make a status bar - ugh, it's so big and ugly. why?
        self.status_bar = Gtk.Statusbar()
        context_id = self.status_bar.get_context_id("Statusbar")
        # Bottom of the statusbar stack message:
        i_emoji_count = self.emo.emoji_count()
        statusbar_message = f"{i_emoji_count} emojis loaded"
        self.status_bar.push(context_id, statusbar_message)
        # Try to make this ugly thing smaller:
        self.status_bar.set_margin_top(0)
        self.status_bar.set_margin_bottom(0)
        message_area = self.status_bar.get_message_area()   # a box
        message_area.set_margin_top(0)
        message_area.set_margin_bottom(0)
        box_layout.pack_end(self.status_bar, expand=False, fill=False,
                            padding=0)
        return box_layout

    def make_a_scrolled_flowbox_layout(self):
        # flowbox, for resizable
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(30)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox = flowbox
        self.populate_flowbox_with_emojis(self.flowbox)
        scrolled.add(self.flowbox)
        return scrolled

    def make_hamburger_menu(self):
        # Make button
        menu_button = Gtk.MenuButton()
        menu_icon = Gtk.Image.new_from_icon_name("open-menu-symbolic",
                                                 Gtk.IconSize.MENU)
        menu_icon.show()
        menu_button.add(menu_icon)
        menu_button.set_direction(Gtk.ArrowType.DOWN)
        menu_button.show()

        # give it a keyboard shortcut
        key, mod = Gtk.accelerator_parse("<Alt>f")
        menu_button.add_accelerator("activate", self.accel_group, key, mod,
                                    Gtk.AccelFlags.VISIBLE)
        # Make menu
        menu = Gtk.Menu()
        # make "Go to favorites" menu item
        favorites_menu_item = Gtk.MenuItem(label="Go to _Favorites")
        favorites_menu_item.set_use_underline(True)
        favorites_menu_item.connect("activate", self.jump_to_favorites)
        favorites_menu_item.show()
        # give it a keyboard shortcut
        key, mod = Gtk.accelerator_parse("<Control>f")
        favorites_menu_item.add_accelerator("activate", self.accel_group, key,
                                            mod, Gtk.AccelFlags.VISIBLE)
        menu.append(favorites_menu_item)

        menu_separator = Gtk.SeparatorMenuItem()
        menu_separator.show()
        menu.append(menu_separator)
        # make statusbar checkbox toggle menu item
        self.statusbar_checkbox_menu_item = Gtk.CheckMenuItem(label="Show _Status Bar")
        self.statusbar_checkbox_menu_item.set_use_underline(True)
        self.statusbar_checkbox_menu_item.connect_object('toggled',
                                                         self.toggled_statusbar,
                                                         self.statusbar_checkbox_menu_item)
        self.statusbar_checkbox_menu_item.show()
        menu.append(self.statusbar_checkbox_menu_item)
        # give it a keyboard shortcut
        key, mod = Gtk.accelerator_parse("<Control>s")
        self.statusbar_checkbox_menu_item.add_accelerator("activate",
                                                          self.accel_group,
                                                          key, mod,
                                                          Gtk.AccelFlags.VISIBLE)
        # make zoom checkbox toggle menu item
        self.zoom_checkbox_menu_item = Gtk.CheckMenuItem(label="Show _Zoom Controls")
        self.zoom_checkbox_menu_item.set_use_underline(True)
        self.zoom_checkbox_menu_item.connect_object('toggled',
                                                    self.toggled_zoom_controls,
                                                    self.zoom_checkbox_menu_item)
        self.zoom_checkbox_menu_item.show()
        menu.append(self.zoom_checkbox_menu_item)
        # give it a keyboard shortcut
        key, mod = Gtk.accelerator_parse("<Control>z")
        self.zoom_checkbox_menu_item.add_accelerator("activate", self.accel_group,
                                                     key, mod, Gtk.AccelFlags.VISIBLE)
        # make Auto-Copy checkbox toggle menu item
        self.copy_checkbox_menu_item = Gtk.CheckMenuItem(label="Auto _Copy to Clipboard")
        self.copy_checkbox_menu_item.set_use_underline(True)
        self.copy_checkbox_menu_item.connect_object('toggled', self.toggled_auto_copy,
                                                    self.copy_checkbox_menu_item)
        self.copy_checkbox_menu_item.show()
        menu.append(self.copy_checkbox_menu_item)
        # give it a keyboard shortcut
        key, mod = Gtk.accelerator_parse("<Control>p")
        self.copy_checkbox_menu_item.add_accelerator("activate", self.accel_group,
                                                     key, mod, Gtk.AccelFlags.VISIBLE)
        menu_separator = Gtk.SeparatorMenuItem()
        menu_separator.show()
        menu.append(menu_separator)
        # make exit menu item
        exit_menu_item = Gtk.MenuItem(label="E_xit")
        exit_menu_item.set_use_underline(True)
        exit_menu_item.connect("activate", Gtk.main_quit)
        exit_menu_item.show()
        menu.append(exit_menu_item)
        # give it a keyboard shortcut
        key, mod = Gtk.accelerator_parse("<Control>q")
        exit_menu_item.add_accelerator("activate", self.accel_group, key, mod,
                                       Gtk.AccelFlags.VISIBLE)
        # prepoulate check based on config
        if self.config.statusbar_is_enabled():
            self.statusbar_checkbox_menu_item.set_active(True)
        else:
            self.statusbar_checkbox_menu_item.set_active(False)
        if self.config.zoomer_is_enabled():
            self.zoom_checkbox_menu_item.set_active(True)
        else:
            self.zoom_checkbox_menu_item.set_active(False)
        if self.config.auto_copy_is_enabled():
            self.copy_checkbox_menu_item.set_active(True)
        else:
            self.copy_checkbox_menu_item.set_active(False)
        # add to menu button
        menu_button.set_popup(menu)
        return menu_button

    def toggled_statusbar(self, statusbar_checkbox_menu_item):
        is_checked = statusbar_checkbox_menu_item.get_active()
        if is_checked:
            self.config.enable_statusbar()
        else:
            self.config.disable_statusbar()
        if self.status_bar:  # tricky
            self.refresh_statusbar()
        self.config.save()

    def toggled_zoom_controls(self, checkbox_menu_item):
        is_checked = checkbox_menu_item.get_active()
        if is_checked:
            if self.zoom_control_box:
                self.zoom_control_box.show()
            self.config.enable_zoomer()
        else:
            if self.zoom_control_box:
                self.zoom_control_box.hide()
            self.config.disable_zoomer()
        self.config.save()

    def toggled_auto_copy(self, checkbox_menu_item):
        is_checked = checkbox_menu_item.get_active()
        if is_checked:
            # send notification, "Emojam: Automatic Copy Enabled"
            self.config.enable_auto_copy()
        else:
            # send notification, "Emojam: Automatic Copy Disabled"
            self.config.disable_auto_copy()
        self.config.save()

    def refresh_statusbar(self):
        if self.config.statusbar_is_enabled():
            self.status_bar.show()
        else:
            self.status_bar.hide()

    def refresh_zoomer(self):
        if self.config.zoomer_is_enabled():
            self.zoom_control_box.show()
        else:
            self.zoom_control_box.hide()

    def init_config(self):
        self.config = emojam_config.EmojamConfig()
        self.config.load_config()
        self.update_picker_font_size(self.config.picker_font_size)

    def init_emojis(self):
        self.emo = emojam_emojis.Emojis("emojis.csv")

    def make_output_line(self):
        # make box, put label and Entry in box, side by side, return box
        box_output_line = Gtk.HBox(spacing=10)
        label_output = Gtk.Label(label="Output:")
        label_output.props.xalign = 0.0
        label_output.show()
        box_output_line.pack_start(label_output, expand=False, fill=True,
                                   padding=0)
        self.output_text_field = Gtk.Entry()
        output_text_field_context = self.output_text_field.get_style_context()
        output_text_field_context.add_class("output-field")
        self.output_text_field.show()
        box_output_line.pack_start(self.output_text_field, expand=True,
                                   fill=True, padding=0)
        return box_output_line

    def make_search_box(self):
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.connect("changed", self.search_box_changed,
                                  self.search_entry)
        self.search_entry.show()
        return self.search_entry

    def make_emoji_button_context_menu(self):
        menu = Gtk.Menu()
        favorites_menu_item = Gtk.CheckMenuItem(label="Favorites")
        favorites_menu_item.connect_object('toggled', self.toggled_favorites,
                                           favorites_menu_item)
        menu.append(favorites_menu_item)
        copy_menu_item = Gtk.MenuItem(label="_Copy")
        copy_menu_item.set_use_underline(True)
        copy_menu_item.connect("activate", self.copy_emoji_to_clip)
        copy_menu_item.show()
        menu.append(copy_menu_item)

        favorites_menu_item.show()
        return menu, favorites_menu_item    # I said I'd never love twice.

    def copy_emoji_to_clip(self, widget):
        print(widget)
        if self.current_menu_button:    # tricky
            s_name = self.current_menu_button.get_name()
            s_emoji = self.emo.emoji_from_name(s_name)
            self.clipboard.set_text(s_emoji, -1)
            self.clipboard_primary.set_text(s_emoji, -1)

    def toggled_favorites(self, menu_item):
        is_checked = menu_item.get_active()
        if self.current_menu_button:    # tricky
            emoji_name = self.current_menu_button.get_name()
            if is_checked:
                self.config.add_favorite(emoji_name)
            else:
                self.config.remove_favorite(emoji_name)
            self.config.save()
        # Refresh the favorites page, hopefully
        if self.s_active_group == "Favorites":
            self.flowbox.set_filter_func(self.flowbox_group_filter,
                                         self.s_active_group)

    def make_group_button(self, s_button_name: str):
        s_button_label = self.emo.emoji_from_group(s_button_name)
        button_label = Gtk.Label(label=f" {s_button_label} ")
        button = Gtk.EventBox()
        button.add(button_label)
        button.set_tooltip_text(s_button_name)
        button.set_name(s_button_name)
        # add it to .group-button CSS class
        button_style_context = button.get_style_context()
        button_style_context.add_class("group-button")
        # right click and hover
        button.connect_object("event", self.button_mouse_event, button)
        # map name to widget
        self.group_buttons_dict.update({s_button_name: button})
        return button

    def make_zoom_control_box(self):
        # make buttons, connect them
        zoom_out_event_box = Gtk.EventBox()
        label = Gtk.Label(label='—')    # em dash
        box = Gtk.Box()
        box.pack_start(label, expand=False, fill=True, padding=5)
        zoom_out_event_box.add(box)
        zoom_out_event_box.set_name('-')
        zoom_out_event_box.connect_object("button_press_event",
                                          self.zoom_button_clicked,
                                          zoom_out_event_box)
        zoom_out_event_box.connect_object("event", self.button_mouse_event,
                                          zoom_out_event_box)
        zoom_out_event_box.show()
        zoom_in_event_box = Gtk.EventBox()
        label = Gtk.Label(label='+')
        box = Gtk.Box()
        box.pack_start(label, expand=False, fill=True, padding=5)
        zoom_in_event_box.add(box)
        zoom_in_event_box.set_name('+')
        zoom_in_event_box.connect_object("button_press_event",
                                         self.zoom_button_clicked,
                                         zoom_in_event_box)
        zoom_in_event_box.connect_object("event", self.button_mouse_event,
                                         zoom_in_event_box)
        zoom_in_event_box.show()
        size = self.config.get_picker_font_size()
        zoom_size_event_box = Gtk.EventBox()
        label = Gtk.Label(label=f" {size}% ")
        self.zoom_size_label = label
        zoom_size_event_box.add(label)
        zoom_size_event_box.set_name('size')
        zoom_size_event_box.connect_object("button_press_event",
                                           self.zoom_button_clicked,
                                           zoom_size_event_box)
        zoom_size_event_box.connect_object("event", self.button_mouse_event,
                                           zoom_size_event_box)
        zoom_size_event_box.show()
        # put them in a box, with separators
        zoom_controls_box = Gtk.HBox()
        zoom_controls_box.pack_start(zoom_out_event_box, expand=False,
                                     fill=True, padding=0)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        separator.show()
        zoom_controls_box.pack_start(separator, expand=False, fill=True,
                                     padding=0)
        zoom_controls_box.pack_start(zoom_size_event_box, expand=False,
                                     fill=True, padding=0)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        separator.show()
        zoom_controls_box.pack_start(separator, expand=False, fill=True,
                                     padding=0)
        zoom_controls_box.pack_start(zoom_in_event_box, expand=False,
                                     fill=True, padding=0)
        zoom_controls_box.show()
        return zoom_controls_box

    def zoom_button_clicked(self, event_box, event_button):
        s_button = event_box.get_name()
        old_size = self.config.get_picker_font_size()
        new_size = old_size
        if s_button == '-':
            if old_size >= self.config.picker_min_size:
                if old_size > 1000:
                    new_size = old_size - 50
                else:
                    new_size = old_size - 20
                self.update_picker_font_size(new_size)
        elif s_button == '+':
            if old_size <= self.config.picker_max_size:
                if old_size > 1000:
                    new_size = old_size + 50
                else:
                    new_size = old_size + 20
                self.update_picker_font_size(new_size)
        elif s_button == 'size':
            new_size = 270
            self.update_picker_font_size(new_size)
        self.zoom_size_label.set_label(f" {new_size}% ")
        self.config.save()

    def enter_hover_over_button(self, button):
        s_button_name = button.get_name()
        if self.s_active_group != s_button_name:
            button_style_context = button.get_style_context()
            button_style_context.add_class('hovered-group')
        # update status bar
        if s_button_name == "-":
            s_status_bar_text = "- Zoom Out"
        elif s_button_name == "+":
            s_status_bar_text = "+ Zoom In"
        elif s_button_name == "size":
            s_status_bar_text = "Defaul Size"
        else:   # it's a group button
            s_status_bar_text = f"Category: {s_button_name}"
        context_id = self.status_bar.get_context_id("hovered-group-name")
        self.status_bar.push(context_id, s_status_bar_text)

    def leave_hover_over_button(self, button):
        button_style_context = button.get_style_context()
        button_style_context.remove_class('hovered-group')
        # update status bar
        context_id = self.status_bar.get_context_id("hovered-group-name")
        self.status_bar.pop(context_id)

    def enter_hover_over_emoji_button(self, button):
        s_emoji_name = button.get_name()
        s_emoji = self.emo.emoji_from_name(s_emoji_name)
        # update statusbar:
        d_emoji = self.emo.emoji_dict_from_name(s_emoji_name)
        hex_code = d_emoji['codepoint']
        group = d_emoji['group']
        sub_group = d_emoji['sub_group']
        if self.config.is_in_favorites(button.get_name()):
            fav = "yes"
        else:
            fav = "no"
        s_status_bar_text = f"{s_emoji} {s_emoji_name}, Favorite: {fav}, Hex: {hex_code}, Group: {group}, Sub-group: {sub_group}"
        context_id = self.status_bar.get_context_id("emoji-info")
        self.status_bar.push(context_id, s_status_bar_text)
        button_style_context = button.get_style_context()
        button_style_context.add_class('highlighted')

    def leave_hover_over_emoji_button(self, button):
        context_id = self.status_bar.get_context_id("emoji-info")
        self.status_bar.pop(context_id)
        button_style_context = button.get_style_context()
        button_style_context.remove_class('highlighted')

    def button_mouse_event(self, button, event):
        """ Generic handler for our eventbox buttons - adds hover events for highlighting """
        # print(f"Debug: emoji_button_mouse_event, button: %i" % (event.button.button))
        # print(f"Debug: emoji_button_mouse_event, button: {event}")
        if event.type == Gdk.EventType.ENTER_NOTIFY:
            self.enter_hover_over_button(button)
        elif event.type == Gdk.EventType.LEAVE_NOTIFY:
            self.leave_hover_over_button(button)

    # Mouse event handlers - hovers, clicks, scrolls, etc
    def emoji_button_mouse_event(self, widget, event, button):  # widget = menu
        # print(f"Debug: emoji_button_mouse_event, button: %i" % (event.button.button))
        # print(f"Debug: emoji_button_mouse_event, button: {event}")
        if event.type == Gdk.EventType.ENTER_NOTIFY:
            self.enter_hover_over_emoji_button(button)
        elif event.type == Gdk.EventType.LEAVE_NOTIFY:
            self.leave_hover_over_emoji_button(button)
        elif event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button.button == 3:    # right-click
                # make menu pop up
                self.current_menu_button = button
                widget.popup(None, None, None, None, event.button.button,
                             event.time)
            elif event.button.button == 1:  # left_click-click
                self.clicked_emoji_button(button)

    def make_groups_buttons(self):
        # returns a gtk box containing ze buttons
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        groups_bbox = Gtk.HBox()
        added_groups = []
        # Make "all" (global) button - show all emojis
        button = self.make_group_button("All")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        # Make favorites button
        button = self.make_group_button("Favorites")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        # make recently used button
        button = self.make_group_button("Recently Used")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        # Put smileys-emotion button near the front of the list
        button = self.make_group_button("Smileys-Emotion")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        added_groups.append("Smileys-Emotion")
        # Add People-Body
        button = self.make_group_button("People-Body")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        added_groups.append("People-Body")
        # Add Animals-Nature
        button = self.make_group_button("Animals-Nature")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        added_groups.append("Animals-Nature")
        # Add Food-Drink
        button = self.make_group_button("Food-Drink")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        added_groups.append("Food-Drink")
        # Add Travel-Places
        button = self.make_group_button("Travel-Places")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        added_groups.append("Travel-Places")
        # Add Activities
        button = self.make_group_button("Activities")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        added_groups.append("Activities")
        # Add Objects
        button = self.make_group_button("Objects")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        added_groups.append("Objects")
        # Add Symbols
        button = self.make_group_button("Symbols")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        added_groups.append("Symbols")
        # Add Flags
        button = self.make_group_button("Flags")
        button.connect("button-press-event", self.clicked_group_button)
        groups_bbox.pack_start(button, expand=False, fill=True, padding=0)
        added_groups.append("Flags")

        for s_group in self.emo.d_emojis.keys():
            # For any remaining groups not manually added...
            # Make button for emoji gorup
            # Pack it into groups_bbox
            if s_group not in added_groups:
                button = self.make_group_button(s_group)
                button.connect("button-press-event", self.clicked_group_button)
                groups_bbox.pack_start(button, expand=False, fill=True,
                                       padding=0)
        scrolled.set_propagate_natural_height(True)
        scrolled.add(groups_bbox)
        return scrolled

    def flowbox_group_filter(self, fb_child, s_group):
        """ Filter by group or category """
        if s_group == 'All':
            return True
        elif s_group == "Recently Used":
            for button in fb_child:
                if self.config.is_in_recent_emojis(button.get_name()):
                    return True
                else:
                    return False
        elif s_group == "Favorites":
            for button in fb_child:
                if self.config.is_in_favorites(button.get_name()):
                    return True
                else:
                    return False
        else:
            for button in fb_child:
                if s_group in self.emo.emoji_group_from_name(button.get_name()):
                    return True
                else:
                    return False
        return False    # should never really get here

    def flowbox_search_filter(self, fb_child, text):
        # from example at:
        # https://stackoverflow.com/questions/55828169/how-to-filter-gtk-flowbox-children-with-gtk-entrysearch
        if text == '':
            return True    # empty search
        for button in fb_child:
            if text in button.get_name().lower():
                return True
            elif text in self.emo.emoji_group_from_name(button.get_name()).lower():
                return True
            else:
                return False
        return False    # should never really get here

    def search_box_changed(self, widget, user_data):
        self.set_active_group("All")    # since we're searching all, make it clear..
        search_text = widget.get_text().lower()
        self.flowbox.set_filter_func(self.flowbox_search_filter, search_text)
        pass

    def make_emoji_button(self, s_emoji_name: str):
        s_emoji = self.emo.emoji_from_name(s_emoji_name)
        button = Gtk.EventBox()
        button_label = Gtk.Label(label=s_emoji)
        button.set_name(s_emoji_name)
        button_label.set_name(s_emoji)
        button.add(button_label)
        # add button to .emoji-button CSS class
        button_style_context = button.get_style_context()
        button_style_context.add_class("emoji-button")
        menu, checkbox_menu_item = self.make_emoji_button_context_menu()
        if self.config.is_in_favorites(s_emoji_name):
            # Preopulate favorite checkbox
            checkbox_menu_item.set_active(True)
        else:
            checkbox_menu_item.set_active(False)
        # right-click and hover:
        button.connect_object("event", self.emoji_button_mouse_event, menu,
                              button)
        # enable drag and drop
        button.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [],
                               Gdk.DragAction.COPY)
        button.drag_source_add_text_targets()
        button.connect("drag-data-get", self.emoji_drag_data_get)
        return button

    def emoji_drag_data_get(self, widget, drag_context, data, info, time):
        """ Get data to drop when emoji is drag and dropped """
        TARGET_TEXT_ENTRY = 0
        if info == TARGET_TEXT_ENTRY:
            text = self.emo.emoji_from_name(widget.get_name())
            data.set_text(text, -1)

    def gtk_theme_changed(self, settings, gparam):
        self.set_css_style()

    def set_css_style(self):
        # Get "selected" color from theme, to use as our highlight color
        tv = Gtk.TextView()  # dumb smart way to get theme's selected background color
        selected_bg_color = tv.get_style_context().lookup_color('theme_selected_bg_color')
        s_hilight_color = selected_bg_color.color.to_string()
        selected_bg_color.color.alpha = 0.5
        s_hilight_color_fainter = selected_bg_color.color.to_string()
        # static css - should probably put this in a file...
        css = """
            .emoji-button {
                font-family: Noto Color Emoji;
                font-size: 275%;
            }
            .group-button {
                font-family: Noto Color Emoji;
                font-size: 90%;
            }
            .output-field {
                font-family: Noto Color Emoji;
            }
            """
        # dynamically generated to match theme highlight color
        css += """
            .highlighted {
                border-radius: 10px;
                background-color: %s;
                text-shadow: 1px 1px 3px black;
            }
            .selected-group {
                border-radius: 5px;
                background-color: %s;
                text-shadow: 1px 1px 2px black;
            }
            .hovered-group {
                border-radius: 5px;
                background-color: %s;
                text-shadow: 1px 1px 2px black;
            }
            """ % (s_hilight_color, s_hilight_color, s_hilight_color_fainter)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode())
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def change_picker_size(self, widget, new_size):     # from the menu item
        self.update_picker_font_size(new_size)
        self.config.save()

    def update_picker_font_size(self, new_size):
        css = """
            .emoji-button {
                font-family: Noto Color Emoji;
                font-size: %i%%;
            }
            """ % (new_size)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode())
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.config.set_picker_font_size(new_size)

    def clicked_group_button(self, widget, event):
        s_group: str = widget.get_name()
        self.set_active_group(s_group)
        self.search_entry.set_text("")

    def set_active_group(self, s_group):
        # un-highlight new button
        try:
            button = self.group_buttons_dict[self.s_active_group]
            button_style_context = button.get_style_context()
            button_style_context.remove_class('selected-group')
        except KeyError:    # only happens on startup
            pass
        # change group in data structures
        self.s_active_group = s_group
        self.flowbox.set_filter_func(self.flowbox_group_filter, s_group)
        self.selected_group_label.set_text(s_group)
        # highlight new button
        button = self.group_buttons_dict[s_group]
        button_style_context = button.get_style_context()
        button_style_context.add_class('selected-group')

    def jump_to_favorites(self, widget):    # MenuItem widget
        self.set_active_group("Favorites")

    def add_to_output_line(self, s_emoji):
        self.s_output_line = self.output_text_field.get_text()
        self.s_output_line += s_emoji
        self.output_text_field.set_text(self.s_output_line)

    def clicked_emoji_button(self, widget):
        s_emoji_name: str = widget.get_name()
        s_emoji: str = self.emo.emoji_from_name(s_emoji_name)
        s_emoji_group: str = self.emo.emoji_group_from_name(s_emoji_name)
        self.config.add_recent(s_emoji_name)
        self.config.save()
        # Send emoji wherever! To the terminal:
        print(f"{s_emoji} :{s_emoji_name}: {s_emoji_group}")
        # To self.output_text_field
        self.add_to_output_line(s_emoji)
        # copy to clipboard if auto-copy is enabled
        if self.config.auto_copy:
            self.clipboard.set_text(s_emoji, -1)
            self.clipboard_primary.set_text(s_emoji, -1)
            Notify.Notification.new(f"{s_emoji} copied to clipboard").show()

    def populate_flowbox_with_emojis(self, flowbox):
        # load all emojis:
        for s_group in self.emo.d_emojis.keys():
            label = Gtk.Label(label=s_group)
            label.show()
            for s_emoji_name in self.emo.d_emojis[s_group]:
                button = self.make_emoji_button(s_emoji_name)
                flowbox.add(button)


def main():
    win = EmojamWindow()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCaught interrupt, exiting...")
        exit(0)
