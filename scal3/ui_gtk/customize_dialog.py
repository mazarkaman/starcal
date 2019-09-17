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

from typing import Tuple

from scal3.path import *
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
	pixbufFromFile,
)
from scal3.ui_gtk.tree_utils import tree_path_split
from scal3.ui_gtk.stack import MyStack, StackPage
from scal3.ui_gtk.customize import newSubPageButton
from scal3.ui_gtk.pref_utils import CheckPrefItem


class CustomizeDialog(gtk.Dialog):
	def __init__(self, item: "CustomizableCalObj", scrolled=True, **kwargs):
		gtk.Dialog.__init__(self, **kwargs)
		self.vbox.set_border_width(10)
		##
		self.stack = MyStack(
			headerSpacing=10,
			iconSize=ui.stackIconSize,
			iconSizeGtk=ud.stackIconSizeGtk,
		)
		pack(self.vbox, self.stack, 1, 1)
		##
		self.set_title(_("Customize"))
		#self.set_has_separator(False)## not in gtk3
		self.connect("delete-event", self.onSaveClick)
		dialog_add_button(
			self,
			"gtk-save",
			_("_Save"),
			0,
			self.onSaveClick,
		)
		# should we save on Escape? or when clicking the X (close) button?
		###
		self.rootItem = item
		###
		rootPageName = "mainWin"
		rootPage = StackPage()
		rootPage.pageName = rootPageName
		rootPage.pageWidget = item.getOptionsButtonBox()
		rootPage.pageExpand = True
		rootPage.pageExpand = True
		rootPage.pageItem = item
		self.stack.addPage(rootPage)

		for page in item.getSubPages():
			if page.pageItem is None:
				raise ValueError(f"pageItem=None, pageName={page.pageName}")
			page.pageParent = rootPageName
			page.pageName = rootPageName + "." + page.pageName
			self.addPageObj(page)
		###
		self.vbox.connect("size-allocate", self.vboxSizeRequest)
		self.vbox.show_all()
		###
		if scrolled:
			# self.resize does not work
			self.vbox.set_size_request(300, 450)

	def itemPixbuf(self, item):
		if not item.enable:
			return None
		if item.hasOptions or (item.itemListCustomizable and item.items):
			return pixbufFromFile("document-edit.svg", ui.treeIconSize)
		return None

	def newItemList(
		self, pageName: str,
		parentItem: "CustomizableCalObj",
		scrolled=False,
	) -> Tuple[gtk.TreeView, gtk.Box]:
		# column 0: bool: enable
		# column 1: str: unique pageName (dot separated)
		# column 2: str: desc
		# column 3: Pixbuf: settings icon
		model = gtk.ListStore(bool, str, str, GdkPixbuf.Pixbuf)
		treev = gtk.TreeView(model=model)
		treev.scalItem = parentItem
		if parentItem.itemsPageEnable:
			treev.pageName = pageName + ".items"
		else:
			treev.pageName = pageName
		##
		treev.set_headers_visible(False)
		treev.connect("button-press-event", self.onTreeviewButtonPress)
		treev.connect("row-activated", self.rowActivated)
		######
		cell = gtk.CellRendererToggle()
		col = gtk.TreeViewColumn(title="", cell_renderer=cell, active=0)
		col.set_property("expand", False)
		cell.connect("toggled", self.enableCellToggled, treev)
		treev.append_column(col)
		#####
		col = gtk.TreeViewColumn(
			title="Widget",
			cell_renderer=gtk.CellRendererText(),
			text=2,
		)
		col.set_property("expand", True)
		treev.append_column(col)
		#####
		col = gtk.TreeViewColumn(
			title="S",
			cell_renderer=gtk.CellRendererPixbuf(),
			pixbuf=3,
		)
		col.set_property("expand", False)
		treev.append_column(col)
		#####
		anyItemHasOptions = False
		for item in parentItem.items:
			if not item.customizable:
				continue
			if item.hasOptions:
				anyItemHasOptions = True
			if not item._name:
				raise ValueError(f"item._name = {item._name}")
			pageName = parentItem._name + "." + item._name
			model.append([
				item.enable,
				pageName,
				item.desc,
				self.itemPixbuf(item),
			])
		###
		hbox = HBox()
		vbox_l = VBox()
		if scrolled:
			swin = gtk.ScrolledWindow()
			swin.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
			swin.add(treev)
			pack(vbox_l, swin, 1, 1)
		else:
			pack(vbox_l, treev, 1, 1)
		pack(hbox, vbox_l, 1, 1)
		###
		toolbar = gtk.Toolbar()
		toolbar.set_orientation(gtk.Orientation.VERTICAL)
		size = gtk.IconSize.SMALL_TOOLBAR
		toolbar.set_icon_size(size)
		# argument2 to image_new_from_stock does not affect
		###
		tb = toolButtonFromIcon("gtk-go-up", size)
		set_tooltip(tb, _("Move up"))
		tb.connect("clicked", self.onUpClick, treev)
		toolbar.insert(tb, -1)
		###
		tb = toolButtonFromIcon("gtk-go-down", size)
		set_tooltip(tb, _("Move down"))
		tb.connect("clicked", self.onDownClick, treev)
		toolbar.insert(tb, -1)
		###
		pack(hbox, toolbar)
		###
		vbox = VBox(spacing=10)
		if anyItemHasOptions:
			label = gtk.Label(
				label=(
					"<span font_size=\"xx-small\">" +
					_("Double-click on each row to see its settings") +
					"</span>"
				),
			)
			label.set_use_markup(True)
			pack(vbox, label)
		pack(vbox, hbox, 1, 1)
		###
		return treev, vbox

	def vboxSizeRequest(self, widget, req):
		self.resize(self.get_size()[0], 1)

	def onUpClick(self, button, treev):
		item = treev.scalItem
		model = treev.get_model()
		index_list = treev.get_cursor()[0]
		if not index_list:
			return
		i = index_list[-1]

		if len(index_list) != 1:
			raise RuntimeError(f"unexpected index_list = {index_list!r}")

		if i <= 0 or i >= len(model):
			gdk.beep()
			return
		###
		item.moveItemUp(i)
		model.swap(model.get_iter(i - 1), model.get_iter(i))
		treev.set_cursor(i - 1)

	def onDownClick(self, button, treev):
		item = treev.scalItem
		model = treev.get_model()
		index_list = treev.get_cursor()[0]
		if not index_list:
			return
		i = index_list[-1]

		if len(index_list) != 1:
			raise RuntimeError(f"unexpected index_list = {index_list!r}")

		if i < 0 or i >= len(model) - 1:
			gdk.beep()
			return
		###
		item.moveItemUp(i + 1)
		model.swap(model.get_iter(i), model.get_iter(i + 1))
		treev.set_cursor(i + 1)

	def addPageObj(self, page):
		pageName = page.pageName
		parentPageName = page.pageParent
		title = page.pageTitle
		item = page.pageItem
		log.debug(f"addPageObj: pageName={page.pageName}, parent={page.pageParent}, item._name={item._name}")

		if self.stack.hasPage(pageName):
			return

		if item.enableParam:
			hbox = HBox(spacing=10)
			prefItem = CheckPrefItem(
				ui,
				item.enableParam,
				_("Enable"),
				live=True,
				onChangeFunc=item.onEnableCheckClick,
			)
			pack(hbox, prefItem.getWidget())
			pack(page.pageWidget, hbox, 0, 0)

		###
		if item.itemListCustomizable and item.items:
			childrenBox = self.newItemList(pageName, item, scrolled=True)[1]
			childrenBox.show_all()
			if item.itemsPageEnable:
				itemsPageName = pageName + ".items"
				itemsPage = StackPage()
				itemsPage.pageWidget = childrenBox
				itemsPage.pageParent = pageName
				itemsPage.pageName = itemsPageName
				itemsPage.pageTitle = item.itemsPageTitle + " - " + title
				itemsPage.pageLabel = item.itemsPageTitle
				itemsPage.pageExpand = True
				self.stack.addPage(itemsPage)
				pack(page.pageWidget, newSubPageButton(
					item,
					itemsPage,
					borderWidth=item.itemsPageButtonBorder,
				))
			else:
				pack(page.pageWidget, childrenBox, 1, 1)
		if item.hasOptions:
			optionsWidget = item.getOptionsWidget()
			if optionsWidget is None:
				raise ValueError(f"hasOptions={item.hasOptions} but getOptionsWidget returned {optionsWidget}")
			pack(page.pageWidget, optionsWidget, 0, 0)

		log.debug(f"adding page {page.pageName} to stack, pageWidget={page.pageWidget} (parent={page.pageWidget.get_parent()})")
		self.stack.addPage(page) # FIXME: crashes here

		for page in item.getSubPages():
			page.pageParent = pageName
			page.pageName = pageName + "." + page.pageName
			page.pageTitle = title + " - " + page.pageTitle
			self.stack.addPage(page)
		item.connect("goto-page", self.gotoPageCallback)

	def addPage(
		self,
		pageName: str,
		parentPageName: str,
		parentItem: "CustomizableCalObj",
		itemIndex: int,
	):
		item = parentItem.items[itemIndex]

		title = item.desc
		if parentItem._name != "mainWin":
			title = title + " - " + parentItem.desc

		page = StackPage()
		page.pageName = pageName
		page.pageParent = parentPageName
		page.pageWidget = VBox(spacing=item.optionsPageSpacing)
		page.pageTitle = title
		page.pageExpand = True
		page.pageExpand = True
		page.pageItem = item

		self.addPageObj(page)

	def gotoPageCallback(self, item, pageName):
		self.stack.gotoPage(pageName)

	def onTreeviewButtonPress(self, treev, gevent):
		if gevent.button != 1:
			return False
		pos_t = treev.get_path_at_pos(int(gevent.x), int(gevent.y))
		if not pos_t:
			return False
		# pos_t == path, col, xRel, yRel
		path = pos_t[0]
		col = pos_t[1]
		cell = col.get_cells()[0]
		if isinstance(cell, gtk.CellRendererPixbuf):
			self.rowActivated(treev, path, col)
		return False

	def rowActivated(
		self,
		treev: gtk.TreeView,
		path: gtk.TreePath,
		col: gtk.TreeViewColumn,
	):
		parentItem = treev.scalItem
		model = treev.get_model()
		itemIter = model.get_iter(path)
		pageName = model.get_value(itemIter, 1)
		itemIndex = tree_path_split(path)[0]
		item = parentItem.items[itemIndex]
		if not item.enable:
			msg = _(
				"{item} is disabled.\n"
				"Check the checkbox if you want to enable it."
			).format(item=item.desc)
			showInfo(msg, transient_for=self)
			return
		parentPageName = treev.pageName
		log.debug(f"rowActivated: pageName={pageName}, itemIndex={itemIndex}, parentPageName={parentPageName}")
		if parentItem.isWrapper:
			parentItem = parentItem.getWidget()
		self.addPage(pageName, parentPageName, parentItem, itemIndex)
		self.stack.gotoPage(pageName)

	def loadItem(self, parentItem, itemIndex):
		item = parentItem.items[itemIndex]
		if not item.loaded:
			item = item.getLoadedObj()
			if item is None:
				return
			parentItem.replaceItem(itemIndex, item)
			parentItem.insertItemWidget(itemIndex)
		item.onConfigChange()
		item.onDateChange()
		return item

	def enableCellToggled(self, cell, path, treev):
		model = treev.get_model()
		active = not cell.get_active()
		itr = model.get_iter(path)
		model.set_value(itr, 0, active)
		parentItem = treev.scalItem
		itemIndex = tree_path_split(path)[0]
		item = parentItem.items[itemIndex]
		assert parentItem.items[itemIndex] == item
		###
		if active:
			item = self.loadItem(parentItem, itemIndex)
			if item is None:
				return
		item.enable = active
		model.set_value(itr, 3, self.itemPixbuf(item))
		item.showHide()
		item.onConfigChange()

	def updateTreeEnableChecks(self):
		pass
		# FIXME: called from MainWin
		#treev = self.treev_root
		#model = treev.get_model()
		#for i, item in enumerate(self.mainPanelItem.items):
		#	model.set_value(
		#		model.get_iter((i,)),
		#		0,
		#		item.enable,
		#	)

	def save(self):
		item = self.rootItem
		item.updateVars()
		ui.ud__wcalToolbarData = ud.wcalToolbarData
		ui.ud__mainToolbarData = ud.mainToolbarData
		ui.saveConfCustomize()
		#data = item.getData()## remove? FIXME

	def onSaveClick(self, button=None, event=None):
		self.save()
		self.hide()
		return True
