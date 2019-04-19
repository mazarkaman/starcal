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

from scal3.path import *

from scal3.locale_man import tr as _
from scal3.locale_man import rtl
from scal3.json_utils import saveJsonConf, loadJsonConf
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk.utils import (
	get_menu_width,
	get_menu_height,
	dialog_add_button,
	openWindow,
)

from scal3.ui_gtk.day_cal import DayCal

confPathLive = join(confDir, "ui-daycal-live.json")

confParamsLive = (
	"dcalWinX",
	"dcalWinY",
	"dcalWinWidth",
	"dcalWinHeight",
)

lastLiveConfChangeTime = 0

loadJsonConf(ui, confPathLive)


def saveLiveConf():  # rename to saveConfLive FIXME
	saveJsonConf(ui, confPathLive, confParamsLive)

def saveLiveConfLoop():  # rename to saveConfLiveLoop FIXME
	global lastLiveConfChangeTime
	tm = now()
	if tm - lastLiveConfChangeTime > ui.saveLiveConfDelay:
		saveLiveConf()
		return False  # Finish loop
	return True  # Continue loop

def liveConfChanged():
	global lastLiveConfChangeTime
	tm = now()
	if tm - lastLiveConfChangeTime > ui.saveLiveConfDelay:
		timeout_add(
			int(ui.saveLiveConfDelay * 1000),
			saveLiveConfLoop,
		)
		lastLiveConfChangeTime = tm


class DayCalWindowCustomizeDialog(gtk.Dialog):
	def __init__(self, dayCal: DayCal, **kwargs):
		gtk.Dialog.__init__(self, **kwargs)
		self._widget = dayCal
		##
		self.set_title(_("Customize") + ": " + dayCal.desc)
		self.connect("delete-event", self.close)
		##
		dialog_add_button(
			self,
			"gtk-close",
			_("_Close"),
			0,
			self.close,
		)
		##
		dayCal.optionsWidgetCreate()
		pack(self.vbox, dayCal.optionsWidget)
		##
		# self.vbox.connect("size-allocate", self.vboxSizeRequest)
		self.vbox.show_all()

	# def vboxSizeRequest(self, widget, req):
	# 	self.resize(self.get_size()[0], 1)

	def save(self):
		self._widget.updateVars()
		ui.saveConfCustomize()

	def close(self, button=None, event=None):
		self.save()
		self.hide()
		return True

@registerSignals
class DayCalWindowWidget(DayCal):
	dragAndDropEnable = False
	doubleClickEnable = False
	backgroundColorParam = "dcalWinBackgroundColor"
	heightParam = ""
	typeParamsParam = "dcalWinTypeParams"
	weekdayParamsParam = "dcalWinWeekdayParams"
	buttonsEnableParam = "dcalWinButtonsEnable"
	buttonsParam = "dcalWinButtons"

	def getCell(self):
		return ui.todayCell

	def __init__(self):
		DayCal.__init__(self)
		self.set_size_request(50, 50)
		self.menu = None
		self.customizeDialog = None

	def customizeDialogCreate(self):
		if not self.customizeDialog:
			self.customizeDialog = DayCalWindowCustomizeDialog(self, transient_for=self._window)

	def openCustomize(self, gevent):
		self.customizeDialogCreate()
		x, y = self._window.get_position()
		w, h = self._window.get_size()
		cw, ch = self.customizeDialog.get_size()
		cx = x + w + 5
		cy = y
		if cx + cw > ud.screenW:
			cx = x - cw - 5
		if cy + ch > ud.screenH:
			cy = y + h - ch
		self.customizeDialog.present()
		self.customizeDialog.move(cx, cy)
		# should move() after present()

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
		self.resize(ui.dcalWinWidth, ui.dcalWinHeight)
		self.move(ui.dcalWinX, ui.dcalWinY)
		self.set_skip_taskbar_hint(True)
		self.set_decorated(False)
		self.stick()
		###
		self._widget = DayCalWindowWidget()
		self._widget._window = self

		self.connect("key-press-event", self._widget.keyPress)
		self.connect("delete-event", self.closeClicked)
		self.connect("configure-event", self.configureEvent)

		self.add(self._widget)
		self._widget.show()
		self.appendItem(self._widget)

	def closeClicked(self, arg=None, event=None):
		if ui.mainWin:
			self.hide()
		else:
			gtk.main_quit()
		return True
	
	def configureEvent(self, widget, gevent):
		if not self.get_property("visible"):
			return
		wx, wy = self.get_position()
		ww, wh = self.get_size()
		ui.dcalWinX, ui.dcalWinY = (wx, wy)
		ui.dcalWinWidth = ww
		ui.dcalWinHeight = wh
		liveConfChanged()
		return False