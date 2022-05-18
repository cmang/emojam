# Emojam
Emojam is a no-frills Emoji picker/keyboard for X-Windows on Unix-like systems.

![emojam-0 7-screenshot](https://user-images.githubusercontent.com/261501/168411763-79b0f9a8-64db-4bc6-a10f-24dd5fdea494.png)

# Requirements
Most Linux systems with X-Windows will probably have these pre-installed:

* Python 3
* PyGTK 3
* Noto Color Emoji Font (from Noto Fonts, Google's free international unicode fonts) - https://fonts.google.com/noto
* A Linux or Unix-like system

# Usage
The easiest way to get an emoji from Emojam into another window is to drag and drop it. You can also right-click the emoji and click "Copy" to copy it to the clipboard. You can also click on it to have it print to standard output, or to add to the "Output:" field, where it can be copied to the clipboard or strung together with other emojis.

In the future I would like to make it send emojis to individual X11 or Wayland windows as key events, like a real keyboard, without the need for drag and drop.

# Why?
When I went looking for an emoji keyboard for Linux, the ones I found all had fatal flaws. Some required a specific package manager, or a specific desktop environment. Some only worked in certain GUI toolkit text fields. Some had hundreds of megabytes of dependencies or large bundled downloads.

I thought I could make something that is flexible, easy to use, and without a bunch of un-necessary dependencies. This should run out-of-the-box on most Linux systems with a GUI, in any window manager, and is just a few hundred kilobytes to download.

# Legal
This program is distributed under the GNU General Public License (GPL) version 3. See LICENSE file for details.

Copyright (c) 2022, Sam Foster All rights reserved.


