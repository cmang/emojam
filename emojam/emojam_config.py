#!/urs/bin/env python3

# Set runtime configuration preferences for Emojam
# Save and load config files
# Store favorites and recent lists, so they will preserve when we restart the program
# Some program state lives here and gets saved automatically to emojam.ini
#
# Part of Emojam, (c) 2022 Sam Foster
# See LICENSE file for details


import configparser
import os
import shutil

class EmojamConfig:

    def __init__(self):
        self.s_config_file_name = "emojam.ini"
        self.favorites = []
        self.recently_used_emojis = []
        self.recently_used_max_count = 100
        self.picker_font_size = 275
        self.picker_max_size = 5000
        self.picker_min_size = 30
        self.show_statusbar = False
        self.show_zoomer = False
        self.config = configparser.ConfigParser()

    def add_favorite(self, s_emoji_name: str):
        if s_emoji_name not in self.favorites:
            self.favorites.append(s_emoji_name)

    def remove_favorite(self, s_emoji_name: str):
        if s_emoji_name in self.favorites:
            self.favorites.remove(s_emoji_name)

    def add_recent(self, s_emoji_name: str):
        if s_emoji_name not in self.recently_used_emojis:
            self.recently_used_emojis.insert(0,s_emoji_name)
            # if this puts it over the max count setting, truncate it
            if len(self.recently_used_emojis) > self.recently_used_max_count:
                self.recently_used_emojis.pop() # remove oldest/last item

    def enable_statusbar(self):
        self.show_statusbar = True

    def disable_statusbar(self):
        self.show_statusbar = False

    def enable_zoomer(self):
        self.show_zoomer = True

    def disable_zoomer(self):
        self.show_zoomer = False

    def zoomer_is_enabled(self):
        return self.show_zoomer

    def statusbar_is_enabled(self):
        return self.show_statusbar

    def set_picker_font_size(self, new_size):
        self.picker_font_size = new_size

    def get_picker_font_size(self):
        return self.picker_font_size

    def is_in_recent_emojis(self, s_emoji_name: str):
        """ Returns True if emoji is in the recent list """
        if s_emoji_name in self.recently_used_emojis:
            return True
        else:
            return False

    def is_in_favorites(self, s_emoji_name: str):
        if s_emoji_name in self.favorites:
            return True
        else:
            return False

    def load_config(self):
        # make local config path, if it doesn't exist
        home_path = os.path.expanduser('~')
        config_dir = f'{home_path}/.local/share/emojam'
        full_config_path = f'{config_dir}/{self.s_config_file_name}'
        self.full_config_path = full_config_path
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        # If there is no file in .local/share, see if there's one here. If so, copy it to .local
        if not os.path.exists(full_config_path):
            if os.path.exists(self.s_config_file_name):
                shutil.copyfile(self.s_config_file_name, full_config_path, follow_symlinks=True)
        if os.path.exists(full_config_path):
            self.config.read(full_config_path)
            s_favorites_serialized = self.config['Emojam']['favorites']
            self.favorites = s_favorites_serialized.split(',')
            s_recently_used_serialized = self.config['Emojam']['recently_used']
            self.recently_used_emojis = s_recently_used_serialized.split(',')
            if 'picker_font_size' in self.config['Emojam']:
                self.picker_font_size = int(self.config['Emojam']['picker_font_size'])
            if 'show_statusbar' in self.config['Emojam']:
                if self.config['Emojam']['show_statusbar'] == 'True':
                    self.show_statusbar = True
                else:
                    self.show_statusbar = False
            if 'show_zoomer' in self.config['Emojam']:
                if self.config['Emojam']['show_zoomer'] == 'True':
                    self.show_zoomer = True
                else:
                    self.show_zoomer = False

    def save(self):
        self.config['Emojam'] = {}
        s_favorites_serialized = ','.join(self.favorites)
        self.config['Emojam']['favorites'] = s_favorites_serialized
        #self.config['Emojam']['recently_used_max'] = str(self.recently_used_max_count)
        self.config['Emojam']['picker_font_size'] = str(self.picker_font_size)
        s_recently_used_serialized = ','.join(self.recently_used_emojis)
        self.config['Emojam']['recently_used'] = s_recently_used_serialized
        self.config['Emojam']['show_statusbar'] = str(self.show_statusbar)
        self.config['Emojam']['show_zoomer'] = str(self.show_zoomer)
        with open(self.full_config_path, 'w') as config_file_handle:
            self.config.write(config_file_handle)



