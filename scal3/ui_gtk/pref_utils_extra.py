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

from os.path import join, isabs

from scal3.path import *
from scal3.cal_types import calTypes
from scal3 import core
from scal3 import locale_man
from scal3.locale_man import langDict, rtl
from scal3.locale_man import tr as _
from scal3 import startup
from scal3 import ui

from gi.repository import GdkPixbuf

from scal3.ui_gtk import *
from scal3.ui_gtk.utils import (
	set_tooltip,
	toolButtonFromIcon,
	imageFromIconName,
)


from scal3.ui_gtk.pref_utils import PrefItem

def newBox(vertical: bool, homogeneous: False):
	if vertical:
		box = VBox()
	else:
		box = HBox()
	box.set_homogeneous(homogeneous)
	return box

class WeekDayCheckListPrefItem(PrefItem):
	def __init__(
		self,
		module,
		varName,
		vertical=False,
		homogeneous=True,
		abbreviateNames=True,
		twoRows=False
	):
		self.module = module
		self.varName = varName
		self.vertical = vertical
		self.homogeneous = homogeneous
		self.twoRows = twoRows
		self.start = core.firstWeekDay
		self.buttons = [
			gtk.ToggleButton(label=name)
			for name in \
				(core.weekDayNameAb if abbreviateNames else core.weekDayName)
		]
		if self.twoRows:
			self._widget = newBox(not self.vertical, self.homogeneous)
		else:
			self._widget = newBox(self.vertical, homo)
		self.updateBoxChildren()

	def updateBoxChildren(self):
		buttons = self.buttons
		start = self.start
		mainBox = self._widget
		for child in mainBox.get_children():
			mainBox.remove(child)
			for child2 in child.get_children():
				child.remove(child2)
		if self.twoRows:
			box1 = newBox(self.vertical, self.homogeneous)
			box2 = newBox(self.vertical, self.homogeneous)
			pack(mainBox, box1)
			pack(mainBox, box2)
			for i in range(4):
				pack(box1, buttons[(start + i) % 7], 1, 1)
			for i in range(4, 7):
				pack(box2, buttons[(start + i) % 7], 1, 1)
		else:
			for i in range(7):
				pack(mainBox, buttons[(start + i) % 7], 1, 1)
		mainBox.show_all()

	def setStart(self, start):
		self.start = start
		self.updateBoxChildren()

	def get(self):
		return [
			index
			for index, button in enumerate(self.buttons)
			if button.get_active()
		]

	def set(self, value):
		buttons = self.buttons
		for button in buttons:
			button.set_active(False)
		for index in value:
			buttons[index].set_active(True)


"""
class ToolbarIconSizePrefItem(PrefItem):
	def __init__(self, module, varName):
		self.module = module
		self.varName = varName
		####
		self._widget = gtk.ComboBoxText()
		for item in ud.iconSizeList:
			self._widget.append_text(item[0])

	def get(self):
		return ud.iconSizeList[self._widget.get_active()][0]

	def set(self, value):
		for (i, item) in enumerate(ud.iconSizeList):
			if item[0] == value:
				self._widget.set_active(i)
				return
"""

############################################################


class LangPrefItem(PrefItem):
	def __init__(self):
		self.module = locale_man
		self.varName = "lang"
		###
		ls = gtk.ListStore(GdkPixbuf.Pixbuf, str)
		combo = gtk.ComboBox()
		combo.set_model(ls)
		###
		cell = gtk.CellRendererPixbuf()
		pack(combo, cell, False)
		combo.add_attribute(cell, "pixbuf", 0)
		###
		cell = gtk.CellRendererText()
		pack(combo, cell, True)
		combo.add_attribute(cell, "text", 1)
		###
		self._widget = combo
		self.ls = ls
		self.append(join(pixDir, "computer.png"), _("System Setting"))
		for (key, data) in langDict.items():
			self.append(data.flag, data.name)

	def append(self, imPath, label):
		if imPath == "":
			pix = None
		else:
			if not isabs(imPath):
				imPath = join(pixDir, imPath)
			pix = GdkPixbuf.Pixbuf.new_from_file(imPath)
		self.ls.append([pix, label])

	def get(self):
		i = self._widget.get_active()
		if i == 0:
			return ""
		else:
			return langDict.keyList[i - 1]

	def set(self, value):
		if value == "":
			self._widget.set_active(0)
		else:
			try:
				i = langDict.keyList.index(value)
			except ValueError:
				print("language %s in not in list!" % value)
				self._widget.set_active(0)
			else:
				self._widget.set_active(i + 1)

	#def updateVar(self):
	#	lang =


class CheckStartupPrefItem(PrefItem):  # FIXME
	def __init__(self):
		w = gtk.CheckButton(label=_("Run on session startup"))
		set_tooltip(
			w,
			"Run on startup of Gnome, KDE, Xfce, LXDE, ...\nFile: %s"
			% startup.comDesk
		)
		self._widget = w

	def get(self):
		return self._widget.get_active()

	def set(self, value):
		self._widget.set_active(value)

	def updateVar(self):
		if self.get():
			if not startup.addStartup():
				self.set(False)
		else:
			try:
				startup.removeStartup()
			except:
				pass

	def updateWidget(self):
		self.set(
			startup.checkStartup()
		)


class AICalsTreeview(gtk.TreeView):
	def __init__(self):
		gtk.TreeView.__init__(self)
		self.set_headers_clickable(False)
		self.set_model(gtk.ListStore(str, str))
		###
		self.enable_model_drag_source(
			gdk.ModifierType.BUTTON1_MASK,
			[
				("row", gtk.TargetFlags.SAME_APP, self.dragId),
			],
			gdk.DragAction.MOVE,
		)
		self.enable_model_drag_dest(
			[
				("row", gtk.TargetFlags.SAME_APP, self.dragId),
			],
			gdk.DragAction.MOVE,
		)
		self.connect("drag-data-get", self.dragDataGet)
		self.connect("drag_data_received", self.dragDataReceived)
		####
		cell = gtk.CellRendererText()
		col = gtk.TreeViewColumn(self.title, cell, text=1)
		col.set_resizable(True)
		self.append_column(col)
		self.set_search_column(1)

	def dragDataGet(self, treev, context, selection, dragId, etime):
		path, col = treev.get_cursor()
		if path is None:
			return
		self.dragPath = path
		return True

	def dragDataReceived(self, treev, context, x, y, selection, dragId, etime):
		srcTreev = gtk.drag_get_source_widget(context)
		if not isinstance(srcTreev, AICalsTreeview):
			return
		srcDragId = srcTreev.dragId
		model = treev.get_model()
		dest = treev.get_dest_row_at_pos(x, y)
		if srcDragId == self.dragId:
			path, col = treev.get_cursor()
			if path is None:
				return
			i = path[0]
			if dest is None:
				model.move_after(
					model.get_iter(i),
					model.get_iter(len(model) - 1),
				)
			elif dest[1] in (
				gtk.TreeViewDropPosition.BEFORE,
				gtk.TreeViewDropPosition.INTO_OR_BEFORE,
			):
				model.move_before(
					model.get_iter(i),
					model.get_iter(dest[0][0]),
				)
			else:
				model.move_after(
					model.get_iter(i),
					model.get_iter(dest[0][0]),
				)
		else:
			smodel = srcTreev.get_model()
			sIter = smodel.get_iter(srcTreev.dragPath)
			row = [
				smodel.get(sIter, j)[0]
				for j in range(2)
			]
			smodel.remove(sIter)
			if dest is None:
				model.append(row)
			elif dest[1] in (
				gtk.TreeViewDropPosition.BEFORE,
				gtk.TreeViewDropPosition.INTO_OR_BEFORE,
			):
				model.insert_before(
					model.get_iter(dest[0]),
					row,
				)
			else:
				model.insert_after(
					model.get_iter(dest[0]),
					row,
				)

	def makeSwin(self):
		swin = gtk.ScrolledWindow()
		swin.add(self)
		swin.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
		swin.set_property("width-request", 200)
		return swin


class ActiveCalsTreeView(AICalsTreeview):
	isActive = True
	title = _("Active")
	dragId = 100


class InactiveCalsTreeView(AICalsTreeview):
	isActive = False
	title = _("Inactive")
	dragId = 101


class AICalsPrefItem(PrefItem):
	def __init__(self):
		self._widget = HBox()
		size = gtk.IconSize.SMALL_TOOLBAR
		######
		toolbar = gtk.Toolbar()
		toolbar.set_orientation(gtk.Orientation.VERTICAL)
		########
		treev = ActiveCalsTreeView()
		treev.connect("row-activated", self.activeTreevRActivate)
		treev.connect("focus-in-event", self.activeTreevFocus)
		treev.get_selection().connect(
			"changed",
			self.activeTreevSelectionChanged,
		)
		###
		pack(self._widget, treev.makeSwin())
		####
		self.activeTreev = treev
		self.activeTrees = treev.get_model()
		########
		toolbar = gtk.Toolbar()
		toolbar.set_orientation(gtk.Orientation.VERTICAL)
		####
		tb = gtk.ToolButton()
		tb.set_direction(gtk.TextDirection.LTR)
		tb.action = ""
		self.leftRightButton = tb
		set_tooltip(tb, _("Activate/Inactivate"))
		tb.connect("clicked", self.leftRightClicked)
		toolbar.insert(tb, -1)
		####
		tb = toolButtonFromIcon("gtk-go-up", size)
		set_tooltip(tb, _("Move up"))
		tb.connect("clicked", self.upClicked)
		toolbar.insert(tb, -1)
		##
		tb = toolButtonFromIcon("gtk-go-down", size)
		set_tooltip(tb, _("Move down"))
		tb.connect("clicked", self.downClicked)
		toolbar.insert(tb, -1)
		##
		pack(self._widget, toolbar)
		########
		treev = InactiveCalsTreeView()
		treev.connect("row-activated", self.inactiveTreevRActivate)
		treev.connect("focus-in-event", self.inactiveTreevFocus)
		treev.get_selection().connect(
			"changed",
			self.inactiveTreevSelectionChanged,
		)
		###
		pack(self._widget, treev.makeSwin())
		####
		self.inactiveTreev = treev
		self.inactiveTrees = treev.get_model()
		########

	def setLeftRight(self, isRight):
		tb = self.leftRightButton
		if isRight is None:
			tb.set_label_widget(None)
			tb.action = ""
		else:
			tb.set_label_widget(
				imageFromIconName(
					(
						"gtk-go-forward" if isRight ^ rtl
						else "gtk-go-back"
					),
					gtk.IconSize.SMALL_TOOLBAR,
				)
			)
			tb.action = "inactivate" if isRight else "activate"
		tb.show_all()

	def activeTreevFocus(self, treev, gevent=None):
		self.setLeftRight(True)

	def inactiveTreevFocus(self, treev, gevent=None):
		self.setLeftRight(False)

	def leftRightClicked(self, obj=None):
		tb = self.leftRightButton
		if tb.action == "activate":
			path, col = self.inactiveTreev.get_cursor()
			if path:
				self.activateIndex(path[0])
		elif tb.action == "inactivate":
			if len(self.activeTrees) > 1:
				path, col = self.activeTreev.get_cursor()
				if path:
					self.inactivateIndex(path[0])

	def getCurrentTreeview(self):
		tb = self.leftRightButton
		if tb.action == "inactivate":
			return self.activeTreev
		elif tb.action == "activate":
			return self.inactiveTreev
		else:
			return

	def upClicked(self, obj=None):
		treev = self.getCurrentTreeview()
		if not treev:
			return
		path, col = treev.get_cursor()
		if path:
			i = path[0]
			s = treev.get_model()
			if i > 0:
				s.swap(
					s.get_iter(i - 1),
					s.get_iter(i),
				)
				treev.set_cursor(i - 1)

	def downClicked(self, obj=None):
		treev = self.getCurrentTreeview()
		if not treev:
			return
		path, col = treev.get_cursor()
		if path:
			i = path[0]
			s = treev.get_model()
			if i < len(s) - 1:
				s.swap(
					s.get_iter(i),
					s.get_iter(i + 1),
				)
				treev.set_cursor(i + 1)

	def inactivateIndex(self, index):
		self.inactiveTrees.prepend(list(self.activeTrees[index]))
		del self.activeTrees[index]
		self.inactiveTreev.set_cursor(0)
		try:
			self.activeTreev.set_cursor(min(
				index,
				len(self.activeTrees) - 1
			))
		except:
			pass
		self.inactiveTreev.grab_focus()  # FIXME

	def activateIndex(self, index):
		self.activeTrees.append(list(self.inactiveTrees[index]))
		del self.inactiveTrees[index]
		self.activeTreev.set_cursor(len(self.activeTrees) - 1)  # FIXME
		try:
			self.inactiveTreev.set_cursor(min(
				index,
				len(self.inactiveTrees) - 1,
			))
		except:
			pass
		self.activeTreev.grab_focus()  # FIXME

	def activeTreevSelectionChanged(self, selection):
		if selection.count_selected_rows() > 0:
			self.setLeftRight(True)
		else:
			self.setLeftRight(None)

	def inactiveTreevSelectionChanged(self, selection):
		if selection.count_selected_rows() > 0:
			self.setLeftRight(False)
		else:
			self.setLeftRight(None)

	def activeTreevRActivate(self, treev, path, col):
		self.inactivateIndex(path[0])

	def inactiveTreevRActivate(self, treev, path, col):
		self.activateIndex(path[0])

	def updateVar(self):
		calTypes.activeNames = [row[0] for row in self.activeTrees]
		calTypes.inactiveNames = [row[0] for row in self.inactiveTrees]
		calTypes.update()

	def updateWidget(self):
		self.activeTrees.clear()
		self.inactiveTrees.clear()
		##
		for calType in calTypes.active:
			module, ok = calTypes[calType]
			if not ok:
				raise RuntimeError("cal type %r not found" % calType)
			self.activeTrees.append([module.name, _(module.desc)])
		##
		for calType in calTypes.inactive:
			module, ok = calTypes[calType]
			if not ok:
				raise RuntimeError("cal type %r not found" % calType)
			self.inactiveTrees.append([module.name, _(module.desc)])
