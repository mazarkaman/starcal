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

import os

from scal3.locale_man import tr as _
from scal3.locale_man import rtl


from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk.utils import get_menu_width, get_menu_height

from scal3.ui_gtk.day_cal import DayCal

@registerSignals
class DayCalWindowWidget(DayCal):
	dragAndDropEnable = False
	doubleClickEnable = False
	heightParam = ""
	typeParamsParam = "dcalWinTypeParams"
	buttonsEnableParam = "dcalWinButtonsEnable"
	buttonsParam = "dcalWinButtons"

	def getCell(self):
		return ui.todayCell

	def __init__(self):
		DayCal.__init__(self)
		self.menu = None

	def buttonPress(self, obj, gevent):
		b = gevent.button
		if b == 1 and self.getButtonsEnable():
			x, y = gevent.x, gevent.y
			w = self.get_allocation().width
			h = self.get_allocation().height
			for button in self.getButtons():
				if button.contains(x, y, w, h):
					button.func(gevent)
					return True
			if ui.mainWin:
				ui.mainWin.statusIconClicked()
				return True
		elif b == 3:
			self.popupMenu(obj, gevent)
		return True

	def popupMenu(self, obj, gevent):
		reverse = gevent.y_root > ud.screenH / 2.0

		menu = self.menu
		if menu is None:
			menu = gtk.Menu()
			if os.sep == "\\":
				from scal3.ui_gtk.windows import setupMenuHideOnLeave
				setupMenuHideOnLeave(menu)
			items = ui.mainWin.getStatusIconPopupItems()
			if reverse:
				items.reverse()
			for item in items:
				menu.add(item)
			self.menu = menu

		menu.show_all()
		menu.popup(
			None,
			None,
			lambda *args: (
				gevent.x_root - get_menu_width(menu) if rtl else gevent.x_root,
				gevent.y_root - get_menu_height(menu) if reverse else gevent.y_root,
				True,
			),
			self,
			gevent.button,
			gevent.time,
		)
		ui.updateFocusTime()


@registerSignals
class DayCalWindow(gtk.Window, ud.BaseCalObj):
	_name = "dayCalWin"
	desc = _("Day Calendar Window")

	def __init__(self):
		gtk.Window.__init__(self)
		self.initVars()
		ud.windowList.appendItem(self)
		###
		self.resize(180, 180)
		self.move(0, 0)
		self.set_title(self.desc)
		self.set_decorated(False)
		###
		self._widget = DayCalWindowWidget()
		self._widget._window = self

		self.connect("key-press-event", self._widget.keyPress)
		self.connect("delete-event", self.closeClicked)
		# self.connect("button-press-event", self._widget.buttonPress)

		self.add(self._widget)
		self._widget.show()
		self.appendItem(self._widget)

	def closeClicked(self, arg=None, event=None):
		if ui.mainWin:
			self.hide()
		else:
			gtk.main_quit()
		return True
	
	# TODO: capture resize (configure) event
	# and save width and height