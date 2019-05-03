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

from scal3.cal_types import calTypes
from scal3 import core
from scal3.locale_man import getMonthName, rtl
from scal3.locale_man import tr as _
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk.utils import (
	set_tooltip,
	setClipboard,
	get_menu_width,
	imageFromIconName,
)
from scal3.ui_gtk.drawing import newTextLayout, setColor
from scal3.ui_gtk.mywidgets.button import ConButton
from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk.color_utils import colorize
from scal3.ui_gtk.customize import CustomizableCalObj


class BaseLabel(gtk.EventBox):
	highlightColor = (176, 176, 176)

	def __init__(self):
		gtk.EventBox.__init__(self)
		##########
		#self.menu.connect("map", lambda obj: self.drag_highlight())
		#self.menu.connect("unmap", lambda obj: self.drag_unhighlight())
		#########
		#self.connect("enter-notify-event", self.highlight)
		#self.connect("leave-notify-event", self.unhighlight)## FIXME

	def highlight(self, widget=None, event=None):
		#self.drag_highlight()
		if self.get_window() is None:
			return
		cr = self.get_window().cairo_create()
		setColor(cr, self.highlightColor)
		#print(tuple(self.get_allocation()), tuple(self.label.get_allocation()))
		w = self.get_allocation().width
		h = self.get_allocation().height
		cr.rectangle(0, 0, w, 1)
		cr.fill()
		cr.rectangle(0, h - 1, w, 1)
		cr.fill()
		cr.rectangle(0, 0, 1, h)
		cr.fill()
		cr.rectangle(w - 1, 0, 1, h)
		cr.fill()
		cr.clip()

	def unhighlight(self, widget=None, event=None):
		#self.drag_unhighlight()
		if self.get_window() is None:
			return
		w = self.get_allocation().width
		h = self.get_allocation().height
		self.get_window().clear_area(0, 0, w, 1)
		self.get_window().clear_area(0, h - 1, w, 1)
		self.get_window().clear_area(0, 0, 1, h)
		self.get_window().clear_area(w - 1, 0, 1, h)


@registerSignals
class MonthLabel(BaseLabel, ud.BaseCalObj):
	def getItemStr(self, i):
		return _(i + 1, fillZero=2)

	def getActiveStr(self, s):
		return colorize(s, ui.labelBoxMenuActiveColor)

	#def getActiveStr(self, s):
	#	return "<b>%s</b>"%s

	def __init__(self, calType, active=0):
		BaseLabel.__init__(self)
		#self.set_border_width(1)#???????????
		self.initVars()
		self.calType = calType
		self.label = gtk.Label()
		self.label.set_use_markup(True)
		self.add(self.label)
		self.menu = gtk.Menu()
		self.menu.set_border_width(0)
		self.menuLabels = []
		self.connect("button-press-event", self.buttonPress)
		self.active = active
		self.setActive(active)

	def createMenuLabels(self):
		if self.menuLabels:
			return
		for i in range(12):
			if ui.monthRMenuNum:
				text = "%s: %s" % (
					self.getItemStr(i),
					_(getMonthName(self.calType, i + 1)),
				)
			else:
				text = _(getMonthName(self.calType, i + 1))
			if i == self.active:
				text = self.getActiveStr(text)
			item = MenuItem()
			label = item.get_child()
			label.set_label(text)
			#label.set_justify(gtk.Justification.LEFT)
			label.set_xalign(0)
			label.set_use_markup(True)
			item.set_right_justified(True) ##?????????
			item.connect("activate", self.itemActivate, i)
			self.menu.append(item)
			self.menuLabels.append(label)
		self.menu.show_all()

	def getMainLabelText(self, active):
		text = getMonthName(self.calType, active + 1)
		if ui.labelBoxMonthColorEnable:
			text = colorize(text, ui.labelBoxMonthColor)
		if ui.boldYmLabel:
			text = "<b>%s</b>" % text
		return text


	def setActive(self, active):
		# (Performance) update menu here, or make menu entirly
		# before popup?
		s = getMonthName(self.calType, active + 1)
		s2 = getMonthName(self.calType, self.active + 1)
		if self.menuLabels:
			if ui.monthRMenuNum:
				self.menuLabels[self.active].set_label(
					"%s: %s" % (
						self.getItemStr(self.active),
						s2,
					)
				)
				self.menuLabels[active].set_label(
					self.getActiveStr("%s: %s" % (
						self.getItemStr(active),
						s,
					)),
				)
			else:
				self.menuLabels[self.active].set_label(s2)
				self.menuLabels[active].set_label(self.getActiveStr(s))
		self.label.set_label(self.getMainLabelText(self.active))
		self.active = active

	def changeCalType(self, calType):
		self.calType = calType
		self.label.set_label(self.getMainLabelText(self.active))
		for i in range(12):
			if ui.monthRMenuNum:
				s = "%s: %s" % (
					self.getItemStr(i),
					getMonthName(self.calType, i + 1),
				)
			else:
				s = getMonthName(self.calType, i + 1)
			if i == self.active:
				s = self.getActiveStr(s)
			self.menuLabels[i].set_label(s)

	def itemActivate(self, item, index):
		y, m, d = ui.cell.dates[self.calType]
		m = index + 1
		ui.changeDate(y, m, d, self.calType)
		self.onDateChange()

	def buttonPress(self, widget, gevent):
		if gevent.button == 3:
			self.createMenuLabels()
			foo, x, y = self.get_window().get_origin()
			## foo == 1 FIXME
			y += self.get_allocation().height
			#if rtl:
			#	x = x - get_menu_width(self.menu) + self.get_allocation().width
			#x -= 7 ## ????????? because of menu padding
			## align menu to center:
			x -= int(
				(
					get_menu_width(self.menu) -
					self.get_allocation().width
				) // 2
			)
			self.menu.popup(
				None,
				None,
				lambda *args: (x, y, True),
				None,
				gevent.button,
				gevent.time,
			)
			ui.updateFocusTime()
			return True
		else:
			return False

	def onDateChange(self, *a, **ka):
		ud.BaseCalObj.onDateChange(self, *a, **ka)
		self.setActive(ui.cell.dates[self.calType][1] - 1)


@registerSignals
class IntLabel(BaseLabel):
	signals = [
		("changed", [int]),
	]

	def getActiveStr(self, s):
		return colorize(s, ui.labelBoxMenuActiveColor)

	def __init__(self, height=9, active=0):
		BaseLabel.__init__(self)
		#self.set_border_width(1)#???????????
		self.height = height
		#self.delay = delay
		self.label = gtk.Label()
		self.label.set_use_markup(True)
		self.add(self.label)
		self.menu = None
		self.connect("button-press-event", self.buttonPress)
		self.active = active
		self.setActive(active)
		self.start = 0
		self.remain = 0
		self.ymPressTime = 0
		self.etime = 0
		self.step = 0

	def setActive(self, active):
		text = _(active)
		self.label.set_label(text)
		self.active = active

	def createMenu(self):
		if self.menu:
			return
		self.menu = gtk.Menu()
		self.menuLabels = []
		self.menu.connect("scroll-event", self.menuScroll)
		##########
		item = gtk.MenuItem()
		arrow = gtk.Arrow(gtk.ArrowType.UP, gtk.ShadowType.IN)
		item.add(arrow)
		arrow.set_property("height-request", 10)
		#item.set_border_width(0)
		#item.set_property("height-request", 10)
		#print(item.style_get_property("horizontal-padding") ## OK)
		###???????????????????????????????????
		#item.config("horizontal-padding"=0)
		#style = item.get_style()
		#style.set_property("horizontal-padding", 0)
		#item.set_style(style)
		self.menu.append(item)
		item.connect("select", self.arrowSelect, -1)
		item.connect("deselect", self.arrowDeselect)
		item.connect("activate", lambda wid: False)
		##########
		for i in range(self.height):
			item = MenuItem()
			label = item.get_child()
			label.set_use_markup(True)
			item.connect("activate", self.itemActivate, i)
			self.menu.append(item)
			self.menuLabels.append(label)
		##########
		item = gtk.MenuItem()
		arrow = gtk.Arrow(gtk.ArrowType.DOWN, gtk.ShadowType.IN)
		arrow.set_property("height-request", 10)
		item.add(arrow)
		self.menu.append(item)
		item.connect("select", self.arrowSelect, 1)
		item.connect("deselect", self.arrowDeselect)
		##########
		self.menu.show_all()

	def updateMenu(self, start=None):
		self.createMenu()
		if start is None:
			start = self.active - self.height // 2
		self.start = start
		for i in range(self.height):
			if start + i == self.active:
				self.menuLabels[i].set_label(
					self.getActiveStr(_(start + i))
				)
			else:
				self.menuLabels[i].set_label(_(start + i))

	def itemActivate(self, widget, item):
		self.setActive(self.start + item)
		self.emit("changed", self.start + item)

	def buttonPress(self, widget, gevent):
		if gevent.button == 3:
			self.updateMenu()
			foo, x, y = self.get_window().get_origin()
			y += self.get_allocation().height
			x -= 7 ## ????????? because of menu padding
			## align menu to center:
			x -= int(
				(
					get_menu_width(self.menu) -
					self.get_allocation().width
				) // 2
			)
			self.menu.popup(
				None,
				None,
				lambda *args: (x, y, True),
				None,
				gevent.button,
				gevent.time,
			)
			ui.updateFocusTime()
			return True
		else:
			return False

	def arrowSelect(self, item, plus):
		self.remain = plus
		timeout_add(
			int(ui.labelMenuDelay * 1000),
			self.arrowRemain,
			plus,
		)

	def arrowDeselect(self, item):
		self.remain = 0

	def arrowRemain(self, plus):
		t = now()
		#print(t - self.etime)
		if self.remain == plus:
			if t - self.etime < ui.labelMenuDelay - 0.02:
				if self.step > 1:
					self.step = 0
					return False
				else:
					self.step += 1
					self.etime = t  # FIXME
					return True
			else:
				self.updateMenu(self.start + plus)
				self.etime = t
				return True
		else:
			return False

	def menuScroll(self, widget, gevent):
		d = getScrollValue(gevent)
		if d == "up":
			self.updateMenu(self.start - 1)
		elif d == "down":
			self.updateMenu(self.start + 1)
		else:
			return False


@registerSignals
class YearLabel(IntLabel, ud.BaseCalObj):
	signals = ud.BaseCalObj.signals

	def __init__(self, calType, **kwargs):
		IntLabel.__init__(self, **kwargs)
		self.initVars()
		self.calType = calType
		self.connect("changed", self.onChanged)

	def onChanged(self, label, item):
		calType = self.calType
		y, m, d = ui.cell.dates[calType]
		ui.changeDate(item, m, d, calType)
		self.onDateChange()

	def changeCalType(self, calType):
		self.calType = calType
		#self.onDateChange()

	def onDateChange(self, *a, **ka):
		ud.BaseCalObj.onDateChange(self, *a, **ka)
		self.setActive(ui.cell.dates[self.calType][0])

	def setActive(self, active):
		text = _(active)
		if ui.labelBoxYearColorEnable:
			text = colorize(text, ui.labelBoxYearColor)
		if ui.boldYmLabel:
			text = "<b>%s</b>" % text
		self.label.set_label(text)
		self.active = active


def newSmallNoFocusButton(iconName, func, tooltip=""):
	arrow = ConButton()
	arrow.set_relief(2)
	arrow.set_can_focus(False)
	arrow.set_image(imageFromIconName(
		iconName,
		gtk.IconSize.SMALL_TOOLBAR,
	))
	arrow.connect("con-clicked", func)
	if tooltip:
		set_tooltip(arrow, tooltip)
	return arrow


class YearLabelButtonBox(gtk.Box, ud.BaseCalObj):
	def __init__(self, calType, **kwargs):
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		self.initVars()
		###
		pack(
			self,
			newSmallNoFocusButton(
				"gtk-remove",
				self.prevClicked,
				_("Previous Year"),
			),
			0,
			0,
			0,
		)
		###
		self.label = YearLabel(calType, **kwargs)
		pack(self, self.label)
		###
		pack(
			self,
			newSmallNoFocusButton(
				"gtk-add",
				self.nextClicked,
				_("Next Year"),
			),
			0,
			0,
			0,
		)

	def prevClicked(self, button):
		ui.yearPlus(-1)
		self.label.onDateChange()

	def nextClicked(self, button):
		ui.yearPlus(1)
		self.label.onDateChange()

	def changeCalType(self, calType):
		return self.label.changeCalType(calType)


class MonthLabelButtonBox(gtk.Box, ud.BaseCalObj):
	def __init__(self, calType, **kwargs):
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		self.initVars()
		###
		pack(
			self,
			newSmallNoFocusButton(
				"gtk-remove",
				self.prevClicked,
				_("Previous Month"),
			),
			0,
			0,
			0,
		)
		###
		self.label = MonthLabel(calType, **kwargs)
		pack(self, self.label)
		###
		pack(
			self,
			newSmallNoFocusButton(
				"gtk-add",
				self.nextClicked,
				_("Next Month"),
			),
			0,
			0,
			0,
		)

	def prevClicked(self, button):
		ui.monthPlus(-1)
		self.label.onDateChange()

	def nextClicked(self, button):
		ui.monthPlus(1)
		self.label.onDateChange()

	def changeCalType(self, calType):
		return self.label.changeCalType(calType)


@registerSignals
class CalObj(gtk.Box, CustomizableCalObj):
	_name = "labelBox"
	desc = _("Year & Month Labels")
	itemListCustomizable = False
	hasOptions = True

	def __init__(self):
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		self.initVars()
		#self.set_border_width(2)

	def onConfigChange(self, *a, **kw):
		CustomizableCalObj.onConfigChange(self, *a, **kw)
		#####
		for child in self.get_children():
			child.destroy()
		###
		monthLabels = []
		calType = calTypes.primary
		##
		box = YearLabelButtonBox(calType)
		pack(self, box)
		self.appendItem(box.label)
		##
		pack(self, gtk.VSeparator(), 1, 1)
		##
		box = MonthLabelButtonBox(calType)
		pack(self, box)
		self.appendItem(box.label)
		monthLabels.append(box.label)
		####
		for i, calType in list(enumerate(calTypes.active))[1:]:
			pack(self, gtk.VSeparator(), 1, 1)
			label = YearLabel(calType)
			pack(self, label)
			self.appendItem(label)
			###############
			label = gtk.Label()
			label.set_property("width-request", 5)
			pack(self, label)
			###############
			label = MonthLabel(calType)
			pack(self, label)
			monthLabels.append(label)
			self.appendItem(label)
		####
		## updateTextWidth
		lay = newTextLayout(self)
		for label in monthLabels:
			wm = 0
			for m in range(12):
				name = getMonthName(label.calType, m)
				if ui.boldYmLabel:
					lay.set_markup("<b>%s</b>" % name)
				else:
					lay.set_text(name)  # OR lay.set_markup
				w = lay.get_pixel_size()[0]
				if w > wm:
					wm = w
			label.set_property("width-request", wm)
		#####
		self.show_all()
		#####
		self.onDateChange()

	def getOptionsWidget(self):
		from scal3.ui_gtk.pref_utils import LiveColorPrefItem, LiveCheckPrefItem, \
			CheckPrefItem, ColorPrefItem, LiveCheckColorPrefItem
		if self.optionsWidget:
			return self.optionsWidget
		####
		optionsWidget = VBox(spacing=10)
		####
		hbox = HBox(spacing=5)
		pack(hbox, gtk.Label(label=_("Active menu item color")))
		prefItem = LiveColorPrefItem(
			ui,
			"labelBoxMenuActiveColor",
			onChangeFunc=self.onConfigChange,
		)
		pack(hbox, prefItem.getWidget())
		pack(optionsWidget, hbox)
		###
		checkSizeGroup = gtk.SizeGroup(mode=gtk.SizeGroupMode.HORIZONTAL)
		###
		prefItem = LiveCheckColorPrefItem(
			CheckPrefItem(ui, "labelBoxYearColorEnable", _("Year Color")),
			ColorPrefItem(ui, "labelBoxYearColor", True),
			onChangeFunc=self.onDateChange,
			checkSizeGroup=checkSizeGroup,
		)
		pack(optionsWidget, prefItem.getWidget())
		###
		prefItem = LiveCheckColorPrefItem(
			CheckPrefItem(ui, "labelBoxMonthColorEnable", _("Month Color")),
			ColorPrefItem(ui, "labelBoxMonthColor", True),
			onChangeFunc=self.onDateChange,
			checkSizeGroup=checkSizeGroup,
		)
		pack(optionsWidget, prefItem.getWidget())
		###
		optionsWidget.show_all()
		self.optionsWidget = optionsWidget
		return self.optionsWidget


if __name__ == "__main__":
	win = gtk.Dialog(parent=None)
	box = CalObj()
	win.add_events(
		gdk.EventMask.POINTER_MOTION_MASK |
		gdk.EventMask.FOCUS_CHANGE_MASK |
		gdk.EventMask.BUTTON_MOTION_MASK |
		gdk.EventMask.BUTTON_PRESS_MASK |
		gdk.EventMask.BUTTON_RELEASE_MASK |
		gdk.EventMask.SCROLL_MASK |
		gdk.EventMask.KEY_PRESS_MASK |
		gdk.EventMask.VISIBILITY_NOTIFY_MASK |
		gdk.EventMask.EXPOSURE_MASK
	)
	pack(win.vbox, box, 1, 1)
	win.vbox.show_all()
	win.resize(600, 50)
	win.set_title(box.desc)
	box.onConfigChange()
	win.run()
