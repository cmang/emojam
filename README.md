# Emojam
Emojam is a no-frills Emoji picker/keyboard for X-Windows (Linux, Unix, X11, etc)

![emojam-0 6-screenshot](https://user-images.githubusercontent.com/261501/167615030-78ec0211-0762-4aec-99e1-a04f1c1f24aa.png)

# Requirements
Most Linux systems with X-Windows will probably have these pre-installed:

* Python 3
* PyGTK 3
* Noto Color Emoji Font (from Noto Fonts, Google's free international unicode fonts) - https://fonts.google.com/noto
* A Linux or Unix-like system

# Usage
Right now it just prints the emoji to an output field, and to standard output. In the future I plan to make it send emojis to individual X11 or Wayland windows, like a real keyboard.

# Why?
When I went looking for an emoji keyboard for Linux, the ones I found all had fatal flaws. Some required a specific package manager, or a specific desktop environment. Some only worked in certain GUI toolkit text fields. Some had hundreds of megabytes of dependencies or large bundled downloads.

I thought I could make something that is flexible, easy to use, and without a bunch of un-necessary dependencies. This should run out-of-the-box on most Linux systems with a GUI, in any window manager, and is just a few hundred kilobytes to download.

# Legal
This program is distributed under the GNU General Public License (GPL) version 3. See LICENSE file for details.

Copyright (c) 2022, Sam Foster All rights reserved.


