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

from time import time as now
import os
from os.path import join, isabs
from subprocess import Popen

from scal3.utils import myRaise
from scal3.utils import toBytes, toStr
from scal3.json_utils import *
from scal3.path import pixDir, rootDir
from scal3.cal_types import calTypes
from scal3 import core
from scal3.locale_man import tr as _
from scal3 import ui

from gi.repository import GdkPixbuf

from scal3.ui_gtk import *


def hideList(widgets):
	for w in widgets:
		w.hide()


def showList(widgets):
	for w in widgets:
		w.show()


def set_tooltip(widget, text):
	widget.set_tooltip_text(text)


def buffer_get_text(b):
	return b.get_text(
		b.get_start_iter(),
		b.get_end_iter(),
		True,
	)


def setClipboard(text, clipboard=None):
	if not clipboard:
		clipboard = gtk.Clipboard.get(gdk.SELECTION_CLIPBOARD)
	clipboard.set_text(
		toStr(text),
		len(toBytes(text)),
	)
	#clipboard.store() ## ?????? No need!


def imageFromIconName(iconName: str, size: int, nonStock=False) -> gtk.Image:
	# So gtk.Image.new_from_stock is deprecated
	# And the doc says we should use gtk.Image.new_from_icon_name
	# which does NOT have the same functionality!
	# because not all stock items are existing in all themes (even popular themes)
	# and new_from_icon_name does not seem to look in other (non-default) themes!
	# So for now we use new_from_stock, unless it's not a stock item
	# But we do not use either of these two outside this function
	# So that it's easy to switch
	if nonStock:
		return gtk.Image.new_from_icon_name(iconName, size)
	try:
		return gtk.Image.new_from_stock(iconName, size)
	except:
		return gtk.Image.new_from_icon_name(iconName, size)


def imageFromFile(path):## the file must exist
	if not isabs(path):
		path = join(pixDir, path)
	im = gtk.Image()
	try:
		im.set_from_file(path)
	except:
		myRaise()
	return im


def pixbufFromFile(path):## the file may not exist
	if not path:
		return None
	if not isabs(path):
		path = join(pixDir, path)
	try:
		return GdkPixbuf.Pixbuf.new_from_file(path)
	except:
		myRaise()
		return None

def toolButtonFromIcon(iconName, size):
	tb = gtk.ToolButton()
	tb.set_icon_widget(imageFromIconName(iconName, size))
	return tb

def labelIconButton(label, iconName, size):
	button = gtk.Button()
	button.set_label(label)
	button.set_image(imageFromIconName(iconName, size))
	button.set_use_underline(True)
	return button

def toolButtonFromFile(fname):
	tb = gtk.ToolButton()
	tb.set_icon_widget(imageFromFile(fname))
	return tb

def labelIconMenuItem(label, iconName="", func=None, *args):
	item = ImageMenuItem(_(label))
	item.set_use_underline(True)
	if iconName:
		item.set_image(imageFromIconName(iconName, gtk.IconSize.MENU))
	if func:
		item.connect("activate", func, *args)
	return item

def labelImageMenuItem(label, imageName, func=None, *args):
	# FIXME: ImageMenuItem is deprecated since version 3.10: Use Gtk.MenuItem.new() instead.
	item = gtk.ImageMenuItem(label=_(label))
	item.set_use_underline(True)
	if imageName:
		item.set_image(imageFromFile(imageName))
	if func:
		item.connect("activate", func, *args)
	return item


def labelMenuItem(label, func=None, *args):
	item = MenuItem(_(label))
	if func:
		item.connect("activate", func, *args)
	return item


def getStyleColor(widget, state=gtk.StateType.NORMAL):
	return widget.get_style_context().get_color(state)


def modify_bg_all(widget, state, gcolor):
	print(widget.__class__.__name__)
	widget.modify_bg(state, gcolor)
	try:
		children = widget.get_children()
	except AttributeError:
		pass
	else:
		for child in children:
			modify_bg_all(child, state, gcolor)


def rectangleContainsPoint(r, x, y):
	return (
		r.x <= x < r.x + r.width and
		r.y <= y < r.y + r.height
	)


def dialog_add_button(dialog, iconName, label, resId, onClicked=None, tooltip=""):
	b = dialog.add_button(label, resId)
	if ui.autoLocale:
		if label:
			b.set_label(label)
		b.set_image(imageFromIconName(iconName, gtk.IconSize.BUTTON))
	if onClicked:
		b.connect("clicked", onClicked)
	if tooltip:
		set_tooltip(b, tooltip)
	return b


def confirm(msg, parent=None):
	win = gtk.MessageDialog(
		parent=parent,
		flags=0,
		type=gtk.MessageType.INFO,
		buttons=gtk.ButtonsType.NONE,
		message_format=msg,
	)
	dialog_add_button(
		win,
		"gtk-cancel",
		_("_Cancel"),
		gtk.ResponseType.CANCEL,
	)
	dialog_add_button(
		win,
		"gtk-ok",
		_("_OK"),
		gtk.ResponseType.OK,
	)
	ok = win.run() == gtk.ResponseType.OK
	win.destroy()
	return ok


def showMsg(msg, parent, msg_type):
	win = gtk.MessageDialog(
		parent=parent,
		flags=0,
		type=msg_type,
		buttons=gtk.ButtonsType.NONE,
		message_format=msg,
	)
	dialog_add_button(
		win,
		"gtk-close",
		_("_Close"),
		gtk.ResponseType.OK,
	)
	win.run()
	win.destroy()


def showError(msg, parent=None):
	showMsg(msg, parent, gtk.MessageType.ERROR)


def showInfo(msg, parent=None):
	showMsg(msg, parent, gtk.MessageType.INFO)


def openWindow(win):
	win.set_keep_above(ui.winKeepAbove)
	win.present()


def get_menu_width(menu):
	"""
	#print(menu.has_screen())
	#menu.show_all()
	#menu.realize()
	print(
		menu.get_border_width(),
		max_item_width,
		menu.get_allocation().width,
		menu.size_request().width,
		menu.get_size_request()[0],
		menu.get_preferred_width(),
		#menu.do_get_preferred_width(),
		menu.get_preferred_size()[0].width,
		menu.get_preferred_size()[1].width,
		)
	"""
	w = menu.get_allocation().width
	if w > 1:
		#print(w-max(item.size_request().width for item in menu.get_children()))
		return w
	items = menu.get_children()
	if items:
		mw = max(item.size_request().width for item in items)
		return mw + 56 ## FIXME
	return 0

def get_menu_height(menu):
	h = menu.get_allocation().height
	if h > 1:
		# print("menu height from before:", h)
		return h
	items = menu.get_children()
	if not items:
		return 0
	h = sum(item.size_request().height for item in items)
	# FIXME: does not work, all items are zero
	# print("menu height from sum:", h)
	# print([item.size_request().height for item in items])
	return h

def get_pixbuf_hash(pbuf):
	import hashlib
	md5 = hashlib.md5()

	def save_func(chunkBytes, size, unknown):
		# len(chunkBytes) == size
		md5.update(chunkBytes)
		return True

	pbuf.save_to_callbackv(
		save_func,
		None,  # user_data
		"bmp",  # type, name of file format
		[],  # option_keys
		[],  # option_values
	)
	return md5.hexdigest()


def window_set_size_aspect(win, min_aspect, max_aspect=None):
	if max_aspect is None:
		max_aspect = min_aspect
	geom = gdk.Geometry()
	geom.min_aspect = min_aspect
	geom.max_aspect = max_aspect
	win.set_geometry_hints(
		None,  # widget, ignored since Gtk 3.20
		geom,  # geometry
		gdk.WindowHints.ASPECT,  # geom_mask
	)
	win.resize(1, 1)


def newHSep():
	return gtk.Separator(orientation=gtk.Orientation.HORIZONTAL)


def newAlignLabel(sgroup=None, label=""):
	label = gtk.Label(label=label)
	label.set_xalign(0)
	if sgroup:
		sgroup.add_widget(label)
	return label


class IdComboBox(gtk.ComboBox):
	def set_active(self, _id):
		ls = self.get_model()
		for i in range(len(ls)):
			if ls[i][0] == _id:
				gtk.ComboBox.set_active(self, i)
				return

	def get_active(self):
		i = gtk.ComboBox.get_active(self)
		if i is None:
			return
		try:
			return self.get_model()[i][0]
		except IndexError:
			return


class CopyLabelMenuItem(MenuItem):
	def __init__(self, label):
		MenuItem.__init__(self)
		self.set_label(label)
		self.connect("activate", self.on_activate)

	def on_activate(self, item):
		setClipboard(self.get_property("label"))


if __name__ == "__main__":
	diolog = gtk.Dialog(parent=None)
	w = TimeZoneComboBoxEntry()
	pack(diolog.vbox, w)
	diolog.vbox.show_all()
	diolog.run()
