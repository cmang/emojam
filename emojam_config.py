#!/urs/bin/env python3

# Set runtime configuration preferences for Emojam
# Save and load config files
# Store favorites and recent lists, so they will preserve when we restart the program
# Some program state lives here and gets saved automatically to emojam.ini
#
# Part of Emojam, (c) 2022 Sam Foster
# See LICENSE file for details


import configparser
import os.path
from os import path

class EmojamConfig:

    def __init__(self):
        self.s_config_file_name = "emojam.ini"
        self.favorites = []
        self.recently_used_emojis = []
        self.recently_used_max_count = 100
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
        if path.exists(self.s_config_file_name):
            self.config.read(self.s_config_file_name)
            s_favorites_serialized = self.config['Emojam']['favorites']
            self.favorites = s_favorites_serialized.split(',')
            s_recently_used_serialized = self.config['Emojam']['recently_used']
            self.recently_used_emojis = s_recently_used_serialized.split(',')

    def save(self):
        self.config['Emojam'] = {}
        s_favorites_serialized = ','.join(self.favorites)
        self.config['Emojam']['favorites'] = s_favorites_serialized
        self.config['Emojam']['recently_used_max'] = str(self.recently_used_max_count)
        s_recently_used_serialized = ','.join(self.recently_used_emojis)
        self.config['Emojam']['recently_used'] = s_recently_used_serialized
        with open(self.s_config_file_name, 'w') as config_file_handle:
            self.config.write(config_file_handle)



