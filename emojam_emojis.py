#!/usr/bin/env python3

# Library for loading, containing and manging the Emoji database
# Part of Emojam, (c) 2022 Sam Foster
# See LICENSE file for details

import csv

class Emojis:
    """ Load, contain and manage an emoji database """
    def __init__(self, s_db_filename: str):
        self.s_db_filename = s_db_filename
        self.load_emojis_from_csv_file(s_db_filename)
 
    def load_emojis_from_csv_file(self, s_db_filename: str):
        self.d_emojis = {} # our DB of emojis.
        self.i_emoji_count = 0 
        # { group {name: represenation}}
        with open(s_db_filename, mode='r') as f_db_csv:
            self.csv_reader = csv.DictReader(f_db_csv)
            for row in self.csv_reader:
                #self.d_emojis.update({row['Group'], row})
                # Add the category if it isn't already there
                if row['Group'] not in self.d_emojis:
                    self.d_emojis[row['Group']] = {}
                # Make metadata dict for emoji
                d_emoji_metadata = {"name": row['Name'], "emoji": row['Representation'], \
                    "group": row['Group'], "sub_group": row['Subgroup'], "codepoint": row['CodePoint'], "favorite": False}
                # Add the emoji to its given group
                #self.d_emojis[row['Group']].update({row['Name']: row['Representation']})
                self.d_emojis[row['Group']].update({row['Name']: d_emoji_metadata})
                self.i_emoji_count += 1

    def emoji_count(self):
        return self.i_emoji_count

    def emoji_from_name(self, s_emoji_name: str):
        """ Takes in an emoji name, returno the emoji """
        for group in self.d_emojis:
            if s_emoji_name in self.d_emojis[group]:
                #return(self.d_emojis[group][s_emoji_name])
                return(self.d_emojis[group][s_emoji_name]['emoji'])

    def emoji_from_group(self, s_emoji_name: str):
        """ Takes in a group name, returns an emoji to represent that group """
        if s_emoji_name == "Smileys-Emotion":
            return self.emoji_from_name("slightly smiling face")
        elif s_emoji_name == "Activities":
            return self.emoji_from_name("rugby football")
        elif s_emoji_name == "Animals-Nature":
            return self.emoji_from_name("herb")
        elif s_emoji_name == "Component":
            return self.emoji_from_name("medium skin tone")
        elif s_emoji_name == "Flags":
            return self.emoji_from_name("white flag")
        elif s_emoji_name == "Food-Drink":
            return self.emoji_from_name("fork and knife")
        elif s_emoji_name == "Objects":
            return self.emoji_from_name("light bulb")
        elif s_emoji_name == "People-Body":
            return self.emoji_from_name("person shrugging")
        elif s_emoji_name == "Symbols":
            return self.emoji_from_name("heavy dollar sign")
        elif s_emoji_name == "Travel-Places":
            return self.emoji_from_name("airplane")
        elif s_emoji_name == "Favorites":
            return self.emoji_from_name("red heart")
        elif s_emoji_name == "Recently Used":
            return self.emoji_from_name("two oclock")
        elif s_emoji_name == "All":
            return self.emoji_from_name("globe with meridians")
        else:
            # Couldn't find a nice preset icon, so just return the original name
            return s_emoji_name

    def emoji_dict_from_name(self, s_emoji_name: str):
        """ Take an emoji name, return the dict entry """
        for group in self.d_emojis:
            if s_emoji_name in self.d_emojis[group]:
                return(self.d_emojis[group][s_emoji_name])

    def emoji_group_from_name(self, s_emoji_name: str):
        """ Take an emoji name, return the group name """
        for group in self.d_emojis:
            if s_emoji_name in self.d_emojis[group]:
                return(group)



                
