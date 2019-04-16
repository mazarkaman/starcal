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

from time import localtime
from time import time as now

import sys
import os
from math import sqrt

from scal3.utils import myRaise
from scal3.cal_types import calTypes
from scal3 import core
from scal3.core import log
from scal3.locale_man import rtl, rtlSgn
from scal3.locale_man import tr as _
from scal3 import ui
from scal3.monthcal import getCurrentMonthStatus

from gi.repository import GdkPixbuf

from scal3.ui_gtk import *
from scal3.ui_gtk.drawing import *
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk.customize import CustomizableCalObj
from scal3.ui_gtk.cal_base import CalBase


class DayCal(gtk.DrawingArea, CalBase):
	_name = "dayCal"
	desc = _("Day Calendar")
	heightParam = ""
	typeParamsParam = ""
	buttonsEnableParam = ""
	buttonsParam = ""

	myKeys = CalBase.myKeys + (
		"up", "down",
		"right", "left",
		"page_up",
		"k", "p",
		"page_down",
		"j", "n",
		#"end",
		"f10", "m",
	)

	def heightUpdate(self, emit=True):
		if not self.heightParam:
			return
		self.set_property("height-request", getattr(ui, self.heightParam))
		if emit:
			self.onDateChange() # just to resize the main window when decreasing height

	def getTypeParams(self):
		return getattr(ui, self.typeParamsParam)

	def getButtonsEnable(self):
		return getattr(ui, self.buttonsEnableParam)

	def getButtons(self):
		return [
			Button(
				d.get("imageName", ""),
				getattr(self, d["onClick"]),
				d["x"],
				d["y"],
				autoDir=d["autoDir"],
				iconName=d.get("iconName", ""),
				iconSize=d.get("iconSize", 16),
			)
			for d in getattr(ui, self.buttonsParam)
		]

	def startMove(self, gevent):
		win = self.getWindow()
		if not win:
			return
		win.begin_move_drag(
			1,
			int(gevent.x_root),
			int(gevent.y_root),
			gevent.time,
		)

	def startResize(self, gevent):
		win = self.getWindow()
		if not win:
			return
		win.begin_resize_drag(
			gdk.WindowEdge.SOUTH_EAST,
			gevent.button,
			int(gevent.x_root),
			int(gevent.y_root),
			gevent.time,
		)

	def openCustomize(self, gevent):
		if ui.mainWin:
			ui.mainWin.customizeShow()

	def updateTypeParamsWidget(self):
		from scal3.ui_gtk.cal_type_params import CalTypeParamBox
		if not self.typeParamsParam:
			return
		typeParams = self.getTypeParams()
		try:
			vbox = self.typeParamsVbox
		except AttributeError:
			return
		for child in vbox.get_children():
			child.destroy()
		###
		n = len(calTypes.active)
		while len(typeParams) < n:
			typeParams.append({
				"pos": (0, 0),
				"font": ui.getFont(3.0),
				"color": ui.textColor,
			})
		sgroupLabel = gtk.SizeGroup(mode=gtk.SizeGroupMode.HORIZONTAL)
		sgroupFont = gtk.SizeGroup(mode=gtk.SizeGroupMode.HORIZONTAL)
		for i, calType in enumerate(calTypes.active):
			#try:
			params = typeParams[i]
			#except IndexError:
			##
			hbox = CalTypeParamBox(
				self.typeParamsParam,
				self,
				i,
				calType,
				params,
				sgroupLabel,
				hasEnable=(i > 0),
				hasAlign=True,
			)
			pack(vbox, hbox)
		###
		vbox.show_all()

	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self._window = None
		self.add_events(gdk.EventMask.ALL_EVENTS_MASK)
		self.initCal()
		self.heightUpdate(emit=False)
		######################
		#self.kTime = 0
		######################
		self.connect("draw", self.drawAll)
		self.connect("button-press-event", self.buttonPress)
		#self.connect("screen-changed", self.screenChanged)
		self.connect("scroll-event", self.scroll)

	def getWindow(self):
		return self._window

	def optionsWidgetCreate(self):
		from scal3.ui_gtk.pref_utils import LiveLabelSpinPrefItem, SpinPrefItem, \
			CheckPrefItem, ColorPrefItem, LiveCheckPrefItem
		if self.optionsWidget:
			return
		self.optionsWidget = gtk.VBox()
		####
		if self.heightParam:
			prefItem = LiveLabelSpinPrefItem(
				_("Height"),
				SpinPrefItem(ui, self.heightParam, 1, 9999, digits=0),
				self.heightUpdate,
			)
			pack(self.optionsWidget, prefItem.getWidget())
		####
		prefItem = LiveCheckPrefItem(
			ui,
			self.buttonsEnableParam,
			label=_("Show buttons"),
			onChangeFunc=self.queue_draw,
		)
		pack(self.optionsWidget, prefItem.getWidget())
		########
		frame = gtk.Frame()
		frame.set_label(_("Calendars"))
		self.typeParamsVbox = gtk.VBox()
		frame.add(self.typeParamsVbox)
		frame.show_all()
		pack(self.optionsWidget, frame)
		self.optionsWidget.show_all()
		self.updateTypeParamsWidget()## FIXME

	def getRenderPos(self, params, x0, y0, w, h, fontw, fonth):
		xalign = params.get("xalign")
		yalign = params.get("yalign")

		if not xalign or xalign == "center":
			x = x0 + w / 2 - fontw / 2 + params["pos"][0]
		elif xalign == "left":
			x = x0 + params["pos"][0]
		elif xalign == "right":
			x = x0 + w - fontw - params["pos"][0]
		else:
			x = x0 + w / 2 - fontw / 2 + params["pos"][0]
			print("invalid xalign = %r" % xalign)

		if not yalign or yalign == "center":
			y = y0 + h / 2 - fonth / 2 + params["pos"][1]
		elif yalign == "top":
			y = y0 + params["pos"][1]
		elif yalign == "buttom":
			y = y0 + h - fonth - params["pos"][1]
		else:
			y = y0 + h / 2 - fonth / 2 + params["pos"][1]
			print("invalid yalign = %r" % yalign)

		return (x, y)

	def getCell(self):
		return ui.cell

	def drawAll(self, widget=None, cr=None, cursor=True):
		#gevent = gtk.get_current_event()
		w = self.get_allocation().width
		h = self.get_allocation().height
		if not cr:
			cr = self.get_window().cairo_create()
			#cr.set_line_width(0)#??????????????
			#cr.scale(0.5, 0.5)
		cr.rectangle(0, 0, w, h)
		fillColor(cr, ui.bgColor)
		#####
		c = self.getCell()
		x0 = 0
		y0 = 0
		########
		iconList = c.getDayEventIcons()
		if iconList:
			iconsN = len(iconList)
			scaleFact = 3.0 / sqrt(iconsN)
			fromRight = 0
			for index, icon in enumerate(iconList):
				## if len(iconList) > 1 ## FIXME
				try:
					pix = GdkPixbuf.Pixbuf.new_from_file(icon)
				except:
					myRaise(__file__)
					continue
				pix_w = pix.get_width()
				pix_h = pix.get_height()
				## right buttom corner ?????????????????????
				x1 = (x0 + w) / scaleFact - fromRight - pix_w # right side
				y1 = (y0 + h / 2) / scaleFact - pix_h / 2 # middle
				cr.scale(scaleFact, scaleFact)
				gdk.cairo_set_source_pixbuf(cr, pix, x1, y1)
				cr.rectangle(x1, y1, pix_w, pix_h)
				cr.fill()
				cr.scale(1 / scaleFact, 1 / scaleFact)
				fromRight += pix_w
		#### Drawing numbers inside every cell
		#cr.rectangle(
		#	x0-w/2.0+1,
		#	y0-h/2.0+1,
		#	w-1,
		#	h-1,
		#)
		calType = calTypes.primary
		params = self.getTypeParams()[0]
		daynum = newTextLayout(
			self,
			_(c.dates[calType][2], calType),
			params["font"],
		)
		fontw, fonth = daynum.get_pixel_size()
		if c.holiday:
			setColor(cr, ui.holidayColor)
		else:
			setColor(cr, params["color"])

		font_x, font_y = self.getRenderPos(params, x0, y0, w, h, fontw, fonth)
		cr.move_to(font_x, font_y)
		show_layout(cr, daynum)
		####
		activeTypeParams = list(zip(
			calTypes.active,
			self.getTypeParams(),
		))
		for calType, params in activeTypeParams[1:]:
			if not params.get("enable", True):
				continue
			daynum = newTextLayout(self, _(c.dates[calType][2], calType), params["font"])
			fontw, fonth = daynum.get_pixel_size()
			setColor(cr, params["color"])
			font_x, font_y = self.getRenderPos(params, x0, y0, w, h, fontw, fonth)
			cr.move_to(font_x, font_y)
			show_layout(cr, daynum)

		if self.getButtonsEnable():
			for button in self.getButtons():
				button.draw(cr, w, h)

	def buttonPress(self, obj, gevent):
		b = gevent.button
		x, y = gevent.x, gevent.y
		###
		if gevent.type == TWO_BUTTON_PRESS:
			self.emit("2button-press")
		if b == 1 and self.getButtonsEnable():
			w = self.get_allocation().width
			h = self.get_allocation().height
			for button in self.getButtons():
				if button.contains(x, y, w, h):
					button.func(gevent)
					return True
		if b == 3:
			self.emit("popup-cell-menu", gevent.time, x, y)
		return True

	def jdPlus(self, p):
		ui.jdPlus(p)
		self.onDateChange()

	def keyPress(self, arg, gevent):
		if CalBase.keyPress(self, arg, gevent):
			return True
		kname = gdk.keyval_name(gevent.keyval).lower()
		#if kname.startswith("alt"):
		#	return True
		## How to disable Alt+Space of metacity ?????????????????????
		if kname == "up":
			self.jdPlus(-1)
		elif kname == "down":
			self.jdPlus(1)
		elif kname == "right":
			if rtl:
				self.jdPlus(-1)
			else:
				self.jdPlus(1)
		elif kname == "left":
			if rtl:
				self.jdPlus(1)
			else:
				self.jdPlus(-1)
		elif kname in ("page_up", "k", "p"):
			self.jdPlus(-1)  # FIXME
		elif kname in ("page_down", "j", "n"):
			self.jdPlus(1)  # FIXME
		#elif kname in ("f10", "m"):  # FIXME
		#	if gevent.get_state() & gdk.ModifierType.SHIFT_MASK:
		#		# Simulate right click (key beside Right-Ctrl)
		#		self.emit("popup-cell-menu", gevent.time, *self.getCellPos())
		#	else:
		#		self.emit("popup-main-menu", gevent.time, *self.getMainMenuPos())
		else:
			return False
		return True

	def scroll(self, widget, gevent):
		d = getScrollValue(gevent)
		if d == "up":
			self.jdPlus(-1)
		elif d == "down":
			self.jdPlus(1)
		else:
			return False

	def onDateChange(self, *a, **kw):
		CustomizableCalObj.onDateChange(self, *a, **kw)
		self.queue_draw()

	def onConfigChange(self, *a, **kw):
		CustomizableCalObj.onConfigChange(self, *a, **kw)
		self.updateTypeParamsWidget()
