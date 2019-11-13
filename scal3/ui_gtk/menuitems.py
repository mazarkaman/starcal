#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) Saeed Rasooli <saeed.gnu@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/gpl.txt>.
# Also avalable in /usr/share/common-licenses/GPL on Debian systems
# or /usr/share/licenses/common/GPL3/license.txt on ArchLinux

from scal3 import logger
log = logger.get()

from typing import Optional, Tuple, Union, Callable

from gi.repository import GdkPixbuf

from scal3 import ui
from scal3.ui_gtk import *
from scal3.ui_gtk.utils import imageFromFile, imageFromIconName


def labelIconMenuItem(
	label: str,
	iconName: str = "",
	func: Optional[Callable] = None,
	args: Optional[Tuple] = None,
):
	image = None
	if iconName:
		image = imageFromIconName(iconName, gtk.IconSize.MENU)
	return labelImageObjMenuItem(
		label,
		image=image,
		func=func,
		args=args,
	)


def labelImageMenuItem(
	label: str,
	imageName: str = "",
	pixbuf: Optional[GdkPixbuf.Pixbuf] = None,
	spacing: int = 3,
	func: Optional[Callable] = None,
	args: Optional[Tuple] = None,
):
	image = None
	if imageName:
		image = imageFromFile(imageName, ui.menuIconSize, resize=True)
	elif pixbuf:
		image = gtk.Image()
		image.set_from_pixbuf(pixbuf)
	return labelImageObjMenuItem(
		label,
		image=image,
		spacing=spacing,
		func=func,
		args=args,
	)


def labelImageObjMenuItem(
	label: str,
	image: Optional[gtk.Image] = None,
	spacing=3,
	func=None,
	args=None,
):
	if args is not None and not isinstance(args, tuple):
		raise TypeError("args must be None or tuple")
	item = gtk.ImageMenuItem()
	"""
	Documentation says:
		Gtk.ImageMenuItem has been deprecated since GTK+ 3.10. If you want to
		display an icon in a menu item, you should use Gtk.MenuItem and pack a
		Gtk.Box with a Gtk.Image and a Gtk.Label instead. You should also consider
		using Gtk.Builder and the XML Gio.Menu description for creating menus, by
		following the ‘GMenu guide [https://developer.gnome.org/GMenu/]’.
		You should consider using icons in menu items only sparingly, and for
		“objects” (or “nouns”) elements only, like bookmarks, files, and links;
		“actions” (or “verbs”) should not have icons.

	The problem is, using a Box does not get along with gtk.CheckMenuItem
	"""
	if image:
		item.set_label(label)
		item.set_image(image)
		# hbox = HBox(spacing=spacing)
		# pack(hbox, image)
		# pack(hbox, gtk.Label(label=label))
		# item.add(hbox)
	else:
		item.set_label(label)
	item.set_use_underline(True)
	if func:
		if args is None:
			args = ()
		item.connect("activate", func, *args)
	return item


def labelMenuItem(label, func=None, *args):
	item = MenuItem(_(label))
	if func:
		item.connect("activate", func, *args)
	return item

