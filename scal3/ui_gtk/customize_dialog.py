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

from typing import Tuple

from scal3.path import *
from scal3.utils import myRaise
from scal3 import core
from scal3.locale_man import tr as _
from scal3.locale_man import rtl
from scal3 import ui

from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk import *
from scal3.ui_gtk.utils import (
	toolButtonFromIcon,
	set_tooltip,
	dialog_add_button,
	showInfo,
)
from scal3.ui_gtk.tree_utils import tree_path_split
from scal3.ui_gtk.stack import MyStack


class CustomizeDialog(gtk.Dialog):
	def __init__(self, widget: "CustomizableCalObj", **kwargs):
		gtk.Dialog.__init__(self, **kwargs)
		self.vbox.set_border_width(10)
		##
		self.stack = MyStack(rtl=rtl, vboxSpacing=10)
		pack(self.vbox, self.stack, 1, 1)
		##
		self.set_title(_("Customize"))
		#self.set_has_separator(False)## not in gtk3
		self.connect("delete-event", self.close)
		dialog_add_button(
			self,
			"gtk-close",
			_("_Close"),
			0,
			self.close,
		)
		###
		treev, childrenBox = self.newItemList("mainWin", widget)
		self.treev_root = treev
		self.stack.addPage("mainWin", "", childrenBox)
		###
		self.vbox.connect("size-allocate", self.vboxSizeRequest)
		self.vbox.show_all()

	def newItemList(self, pageName: str, parentItem: "CustomizableCalObj") -> Tuple[gtk.TreeView, gtk.Box]:
		# column 0: bool: enable
		# column 1: str: unique pageName (dot separated)
		# column 2: str: desc
		model = gtk.ListStore(bool, str, str)
		treev = gtk.TreeView(model=model)
		treev.scalItem = parentItem
		treev.pageName = pageName
		##
		treev.set_enable_tree_lines(True)
		treev.set_headers_visible(False)
		treev.connect("row-activated", self.rowActivated, parentItem)
		##
		col = gtk.TreeViewColumn("Widget")
		##
		cell = gtk.CellRendererToggle()
		cell.connect("toggled", self.enableCellToggled, treev)
		pack(col, cell)
		col.add_attribute(cell, "active", 0)
		col.set_property("expand", False)
		##
		treev.append_column(col)
		col = gtk.TreeViewColumn("Widget")
		col.set_property("expand", False)
		##
		cell = gtk.CellRendererText()
		pack(col, cell)
		col.add_attribute(cell, "text", 2)
		col.set_property("expand", True)
		##
		treev.append_column(col)
		###
		for item in parentItem.items:
			pageName = parentItem._name + "." + item._name
			if item.customizable:
				itemIter = model.append(None)
				model.set(
					itemIter,
					0, item.enable,
					1, pageName,
					2, item.desc,
				)
		###
		hbox = gtk.HBox()
		vbox_l = gtk.VBox()
		pack(vbox_l, treev, 1, 1)
		pack(hbox, vbox_l, 1, 1)
		###
		toolbar = gtk.Toolbar()
		toolbar.set_orientation(gtk.Orientation.VERTICAL)
		size = gtk.IconSize.SMALL_TOOLBAR
		toolbar.set_icon_size(size)
		## argument2 to image_new_from_stock does not affect
		###
		tb = toolButtonFromIcon("gtk-go-up", size)
		set_tooltip(tb, _("Move up"))
		tb.connect("clicked", self.upClicked, treev)
		toolbar.insert(tb, -1)
		###
		tb = toolButtonFromIcon("gtk-go-down", size)
		set_tooltip(tb, _("Move down"))
		tb.connect("clicked", self.downClicked, treev)
		toolbar.insert(tb, -1)
		###
		pack(hbox, toolbar)
		###
		vbox = gtk.VBox(spacing=10)
		label = gtk.Label(
			label="<span font_size=\"xx-small\">" +
				_("Double-click on each row to see it's settings") +
				"</span>"
		)
		label.set_use_markup(True)
		pack(vbox, label)
		pack(vbox, hbox, 1, 1)
		###
		return treev, vbox

	def vboxSizeRequest(self, widget, req):
		self.resize(self.get_size()[0], 1)

	def upClicked(self, button, treev):
		item = treev.scalItem
		model = treev.get_model()
		index_list = treev.get_cursor()[0]
		if not index_list:
			return
		i = index_list[-1]
		
		if len(index_list) != 1:
			raise RuntimeError("unexpected index_list = %r" % index_list)

		if i <= 0 or i >= len(model):
			gdk.beep()
			return
		###
		item.moveItemUp(i)
		model.swap(model.get_iter(i - 1), model.get_iter(i))
		treev.set_cursor(i - 1)
			

	def downClicked(self, button, treev):
		item = treev.scalItem
		model = treev.get_model()
		index_list = treev.get_cursor()[0]
		if not index_list:
			return
		i = index_list[-1]

		if len(index_list) != 1:
			raise RuntimeError("unexpected index_list = %r" % index_list)

		if i < 0 or i >= len(model) - 1:
			gdk.beep()
			return
		###
		item.moveItemUp(i + 1)
		model.swap(model.get_iter(i), model.get_iter(i + 1))
		treev.set_cursor(i + 1)

	def addPage(self, pageName: str, parentPageName: str, parentItem: "CustomizableCalObj", itemIndex: int):
		if self.stack.hasPage(pageName):
			return
		item = parentItem.items[itemIndex]
		###
		if item.customizable and not item.optionsWidget:
			item.optionsWidgetCreate()
		vbox = gtk.VBox()
		showChildList = False
		for child in item.items:
			if child.customizable:
				showChildList = True
				break
		# print("customizable=%s, len(items)=%s, showChildList=%s" % (item.customizable, len(item.items), showChildList))
		if showChildList:
			treev, childrenBox = self.newItemList(pageName, item)
			childrenBox.show_all()
			pack(vbox, childrenBox)
		if item.optionsWidget:
			pack(vbox, item.optionsWidget, 0, 0)
		self.stack.addPage(pageName, parentPageName, vbox, desc=item.desc)

	def rowActivated(
		self,
		treev: gtk.TreeView,
		path: gtk.TreePath,
		col: gtk.TreeViewColumn,
		parentItem: "CustomizableCalObj",
	):
		model = treev.get_model()
		itemIter = model.get_iter(path)
		pageName = model.get_value(itemIter, 1)
		itemIndex = tree_path_split(path)[0]
		item = parentItem.items[itemIndex]
		if not item.enable:
			showInfo(
				_("%s is disabled.\nCheck the checkbox if you want to enable it.") % item.desc,
				parent=self,
			)
			return
		print("rowActivated: pageName = %r" % pageName)
		parentPageName = treev.pageName
		self.addPage(pageName, parentPageName, parentItem, itemIndex)
		self.stack.gotoPage(pageName)

	def enableCellToggled(self, cell, path, treev):
		model = treev.get_model()
		active = not cell.get_active()
		model.set_value(
			model.get_iter(path),
			0,
			active,
		)  # or set(...)
		parentItem = treev.scalItem
		itemIndex = tree_path_split(path)[0]
		item = parentItem.items[itemIndex]
		assert parentItem.items[itemIndex] == item
		###
		if active:
			if not item.loaded:
				item = item.getLoadedObj()
				parentItem.replaceItem(itemIndex, item)
				parentItem.insertItemWidget(itemIndex)
			item.onConfigChange()
			item.onDateChange()
		item.enable = active
		item.showHide()

	def updateTreeEnableChecks(self):
		treev = self.treev_root
		model = treev.get_model()
		for i, item in enumerate(treev.scalItem.items):
			model.set_value(
				model.get_iter((i,)),
				0,
				item.enable,
			)

	def save(self):
		item = self.treev_root.scalItem
		item.updateVars()
		ui.ud__wcalToolbarData = ud.wcalToolbarData
		ui.ud__mainToolbarData = ud.mainToolbarData
		ui.saveConfCustomize()
		#data = item.getData()## remove? FIXME

	def close(self, button=None, event=None):
		self.save()
		self.hide()
		return True
