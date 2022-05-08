![emojam-screenshot](https://user-images.githubusercontent.com/261501/167248068-0d346c64-5123-4bcd-b62f-a4cfb62e19d7.png)

# Emojam
Emojam is a no-frills Emoji picker/keyboard for Linux/X11.

# Requirements
Most Linux systems with X-Windows will probably have these pre-installed:

* Python 3
* PyGTK
* Noto Color Emoji Font (from Noto Fonts, Google's free international unicode fonts) - https://fonts.google.com/noto

# Usage
Right now it just prints the emoji to standard output, so run it from a terminal. In the future I plan to make it send emojis to individual X11 or Wayland windows.

# Why?
When I went looking for an emoji keyboard for Linux, the ones I found all had fatal flaws. Some required a specific package manager, or a specific desktop environment. Some had hundreds of megabytes of dependencies or large bundled downloads.

I thought I could make something that is relatively small, easy to use, and without a bunch of un-necessary dependencies. This should run on most Linux systems with a GUI out-of-the-box, and is just a few hundred kilobytes.

# Legal
This program is distributed under the GNU General Public License (GPL) version 3. See LICENSE file for details.

Copyright (c) 2022, Sam Foster All rights reserved.


