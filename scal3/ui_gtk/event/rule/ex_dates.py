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

from scal3 import core
from scal3.date_utils import dateEncode, dateDecode
from scal3.locale_man import tr as _
from scal3.locale_man import textNumEncode, textNumDecode
from scal3 import event_lib
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.utils import (
	toolButtonFromIcon,
	set_tooltip,
	imageFromIconName,
)


def encode(d):
	return textNumEncode(dateEncode(d))


def decode(s):
	return dateDecode(textNumDecode(s))


def validate(s):
	return encode(decode(s))


class WidgetClass(gtk.Box):
	def __init__(self, rule):
		self.rule = rule
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		###
		self.countLabel = gtk.Label()
		pack(self, self.countLabel)
		###
		self.trees = gtk.ListStore(str)
		self.dialog = None
		###
		self.editButton = gtk.Button(label=_("Edit"))
		self.editButton.set_image(imageFromIconName(
			"gtk-edit",
			gtk.IconSize.BUTTON,
		))
		self.editButton.connect("clicked", self.showDialog)
		pack(self, self.editButton)

	def updateCountLabel(self):
		self.countLabel.set_label(
			" " * 2 +
			_("{count} items").format(count=_(len(self.trees))) +
			" " * 2
		)

	def createDialog(self):
		if self.dialog:
			return
		log.debug("----- toplevel: {self.get_toplevel()}")
		self.dialog = gtk.Dialog(
			title=self.rule.desc,
			transient_for=self.get_toplevel(),
		)
		###
		self.treev = gtk.TreeView()
		self.treev.set_headers_visible(True)
		self.treev.set_model(self.trees)
		##
		cell = gtk.CellRendererText()
		cell.set_property("editable", True)
		cell.connect("edited", self.dateCellEdited)
		col = gtk.TreeViewColumn(title=_("Date"), cell_renderer=cell, text=0)
		# col.set_title
		self.treev.append_column(col)
		##
		toolbar = gtk.Toolbar()
		toolbar.set_orientation(gtk.Orientation.VERTICAL)
		size = gtk.IconSize.SMALL_TOOLBAR
		##
		tb = toolButtonFromIcon("gtk-add", size)
		set_tooltip(tb, _("Add"))
		tb.connect("clicked", self.onAddClick)
		toolbar.insert(tb, -1)
		#self.buttonAdd = tb
		##
		tb = toolButtonFromIcon("gtk-delete", size)
		set_tooltip(tb, _("Delete"))
		tb.connect("clicked", self.onDeleteClick)
		toolbar.insert(tb, -1)
		#self.buttonDel = tb
		##
		tb = toolButtonFromIcon("gtk-go-up", size)
		set_tooltip(tb, _("Move up"))
		tb.connect("clicked", self.onMoveUpClick)
		toolbar.insert(tb, -1)
		##
		tb = toolButtonFromIcon("gtk-go-down", size)
		set_tooltip(tb, _("Move down"))
		tb.connect("clicked", self.onMoveDownClick)
		toolbar.insert(tb, -1)
		##
		dialogHbox = HBox()
		pack(dialogHbox, self.treev, 1, 1)
		pack(dialogHbox, toolbar)
		pack(self.dialog.vbox, dialogHbox, 1, 1)
		self.dialog.vbox.show_all()
		self.dialog.resize(200, 300)
		self.dialog.connect("response", lambda w, e: self.dialog.hide())
		##
		okButton = self.dialog.add_button("gtk-ok", gtk.ResponseType.CANCEL)
		if ui.autoLocale:
			okButton.set_label(_("_OK"))
			okButton.set_image(imageFromIconName(
				"gtk-ok",
				gtk.IconSize.BUTTON,
			))

	def showDialog(self, w=None):
		self.createDialog()
		self.dialog.run()
		self.updateCountLabel()

	def dateCellEdited(self, cell, path, newText):
		index = int(path)
		self.trees[index][0] = validate(newText)

	def getSelectedIndex(self):
		cur = self.treev.get_cursor()
		try:
			path, col = cur
			index = path[0]
			return index
		except (ValueError, IndexError):
			return None

	def onAddClick(self, button):
		index = self.getSelectedIndex()
		calType = self.rule.getCalType()## FIXME
		row = [encode(core.getSysDate(calType))]
		if index is None:
			newIter = self.trees.append(row)
		else:
			newIter = self.trees.insert(index + 1, row)
		self.treev.set_cursor(self.trees.get_path(newIter))
		#col = self.treev.get_column(0)
		#cell = col.get_cell_renderers()[0]
		#cell.start_editing(...) ## FIXME

	def onDeleteClick(self, button):
		index = self.getSelectedIndex()
		if index is None:
			return
		del self.trees[index]

	def onMoveUpClick(self, button):
		index = self.getSelectedIndex()
		if index is None:
			return
		t = self.trees
		if index <= 0 or index >= len(t):
			gdk.beep()
			return
		t.swap(
			t.get_iter(index - 1),
			t.get_iter(index),
		)
		self.treev.set_cursor(index - 1)

	def onMoveDownClick(self, button):
		index = self.getSelectedIndex()
		if index is None:
			return
		t = self.trees
		if index < 0 or index >= len(t) - 1:
			gdk.beep()
			return
		t.swap(
			t.get_iter(index),
			t.get_iter(index + 1),
		)
		self.treev.set_cursor(index + 1)

	def updateWidget(self):
		for date in self.rule.dates:
			self.trees.append([encode(date)])
		self.updateCountLabel()

	def updateVars(self):
		dates = []
		for row in self.trees:
			dates.append(decode(row[0]))
		self.rule.setDates(dates)
