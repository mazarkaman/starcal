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

## Islamic (Hijri) calendar: http://en.wikipedia.org/wiki/Islamic_calendar

import os
from os.path import isfile

from scal3.cal_types import calTypes, jd_to, to_jd
from scal3.cal_types import hijri

from scal3.date_utils import monthPlus
from scal3 import core
from scal3.locale_man import rtl, dateLocale
from scal3.locale_man import tr as _
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.mywidgets.multi_spin.date import DateButton
from scal3.ui_gtk.utils import (
	dialog_add_button,
	toolButtonFromStock,
	set_tooltip,
)
from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk import listener


hijriMode = calTypes.names.index("hijri")


def getCurrentYm():
	y, m, d = ui.todayCell.dates[hijriMode]
	return y * 12 + m - 1


class EditDbDialog(gtk.Dialog):
	def __init__(self, **kwargs):
		gtk.Dialog.__init__(self, **kwargs)
		self.set_title(_("Tune Hijri Monthes"))
		self.connect("delete-event", self.onDeleteEvent)
		############
		self.altMode = 0
		self.altModeDesc = "Gregorian"
		############
		hbox = gtk.HBox()
		self.topLabel = gtk.Label()
		pack(hbox, self.topLabel)
		self.startDateInput = DateButton()
		self.startDateInput.set_editable(False)## FIXME
		self.startDateInput.connect("changed", lambda widget: self.updateEndDates())
		pack(hbox, self.startDateInput)
		pack(self.vbox, hbox)
		############################
		treev = gtk.TreeView()
		trees = gtk.ListStore(
			int,  # ym (hidden)
			str,  # localized year
			str,  # localized month
			int,  # monthLenCombo
			str,  # localized endDate
		)
		treev.set_model(trees)
		#treev.get_selection().connect("changed", self.plugTreevCursorChanged)
		#treev.connect("row-activated", self.plugTreevRActivate)
		#treev.connect("button-press-event", self.plugTreevButtonPress)
		###
		swin = gtk.ScrolledWindow()
		swin.add(treev)
		swin.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
		######
		cell = gtk.CellRendererText()
		col = gtk.TreeViewColumn(_("Year"), cell, text=1)
		treev.append_column(col)
		######
		cell = gtk.CellRendererText()
		col = gtk.TreeViewColumn(_("Month"), cell, text=2)
		treev.append_column(col)
		######
		cell = gtk.CellRendererCombo()
		mLenModel = gtk.ListStore(int)
		mLenModel.append([29])
		mLenModel.append([30])
		cell.set_property("model", mLenModel)
		#cell.set_property("has-entry", False)
		cell.set_property("editable", True)
		cell.set_property("text-column", 0)
		cell.connect("edited", self.monthLenCellEdited)
		col = gtk.TreeViewColumn(_("Month Length"), cell, text=3)
		treev.append_column(col)
		######
		cell = gtk.CellRendererText()
		col = gtk.TreeViewColumn(_("End Date"), cell, text=4)
		treev.append_column(col)
		######
		toolbar = gtk.Toolbar()
		toolbar.set_orientation(gtk.Orientation.VERTICAL)
		size = gtk.IconSize.SMALL_TOOLBAR
		###
		tb = toolButtonFromStock(gtk.STOCK_ADD, size)
		set_tooltip(tb, _("Add"))
		tb.connect("clicked", self.addClicked)
		toolbar.insert(tb, -1)
		###
		tb = toolButtonFromStock(gtk.STOCK_DELETE, size)
		set_tooltip(tb, _("Delete"))
		tb.connect("clicked", self.delClicked)
		toolbar.insert(tb, -1)
		######
		self.treev = treev
		self.trees = trees
		#####
		mainHbox = gtk.HBox()
		pack(mainHbox, swin, 1, 1)
		pack(mainHbox, toolbar)
		pack(self.vbox, mainHbox, 1, 1)
		######
		dialog_add_button(
			self,
			gtk.STOCK_OK,
			_("_OK"),
			gtk.ResponseType.OK,
		)
		dialog_add_button(
			self,
			gtk.STOCK_CANCEL,
			_("_Cancel"),
			gtk.ResponseType.CANCEL,
		)
		##
		resetB = self.add_button(
			gtk.STOCK_UNDO,
			gtk.ResponseType.NONE,
		)
		resetB.set_label(_("_Reset to Defaults"))
		resetB.set_image(gtk.Image.new_from_stock(
			gtk.STOCK_UNDO,
			gtk.IconSize.BUTTON,
		))
		resetB.connect("clicked", self.resetToDefaults)
		##
		self.connect("response", self.onResponse)
		#print(dir(self.get_action_area()))
		#self.get_action_area().set_homogeneous(False)
		######
		self.vbox.show_all()

	def resetToDefaults(self, widget):
		if isfile(hijri.monthDb.userDbPath):
			os.remove(hijri.monthDb.userDbPath)
		hijri.monthDb.load()
		self.updateWidget()
		return True

	def addClicked(self, obj=None):
		last = self.trees[-1]
		# 0 ym
		# 1 yearLocale
		# 2 monthLocale
		# 3 mLen
		# 4 endDate = ""
		ym = last[0] + 1
		mLen = 59 - last[3]
		year, month0 = divmod(ym, 12)
		self.trees.append((
			ym,
			_(year),
			_(hijri.monthName[month0]),
			mLen,
			"",
		))
		self.updateEndDates()
		self.selectLastRow()

	def selectLastRow(self):
		lastPath = (len(self.trees) - 1,)
		self.treev.scroll_to_cell(lastPath)
		self.treev.set_cursor(lastPath)

	def delClicked(self, obj=None):
		if len(self.trees) > 1:
			del self.trees[-1]
		self.selectLastRow()

	def updateWidget(self):
		#for index, module in calTypes.iterIndexModule():
		#	if module.name != "hijri":
		for mode in calTypes.active:
			module, ok = calTypes[mode]
			if not ok:
				raise RuntimeError("cal type %r not found" % mode)
			modeDesc = module.desc
			if "hijri" not in modeDesc.lower():
				self.altMode = mode
				self.altModeDesc = modeDesc
				break
		self.topLabel.set_label(
			_("Start") +
			": " +
			dateLocale(*hijri.monthDb.startDate) +
			" " +
			_("Equals to") +
			" %s" % _(self.altModeDesc)
		)
		self.startDateInput.set_value(jd_to(hijri.monthDb.startJd, self.altMode))
		###########
		selectYm = getCurrentYm() - 1 ## previous month
		selectIndex = None
		self.trees.clear()
		for index, ym, mLen in hijri.monthDb.getMonthLenList():
			if ym == selectYm:
				selectIndex = index
			year, month0 = divmod(ym, 12)
			self.trees.append([
				ym,
				_(year),
				_(hijri.monthName[month0]),
				mLen,
				"",
			])
		self.updateEndDates()
		########
		if selectIndex is not None:
			self.treev.scroll_to_cell(str(selectIndex))
			self.treev.set_cursor(str(selectIndex))

	def updateEndDates(self):
		y, m, d = self.startDateInput.get_value()
		jd0 = to_jd(y, m, d, self.altMode) - 1
		for row in self.trees:
			mLen = row[3]
			jd0 += mLen
			row[4] = dateLocale(*jd_to(jd0, self.altMode))

	def monthLenCellEdited(self, combo, path_string, new_text):
		editIndex = int(path_string)
		mLen = int(new_text)
		if mLen not in (29, 30):
			return
		mLenPrev = self.trees[editIndex][3]
		delta = mLen - mLenPrev
		if delta == 0:
			return
		n = len(self.trees)
		self.trees[editIndex][3] = mLen
		if delta == 1:
			for i in range(editIndex + 1, n):
				if self.trees[i][3] == 30:
					self.trees[i][3] = 29
					break
		elif delta == -1:
			for i in range(editIndex + 1, n):
				if self.trees[i][3] == 29:
					self.trees[i][3] = 30
					break
		self.updateEndDates()

	def updateVars(self):
		y, m, d = self.startDateInput.get_value()
		hijri.monthDb.endJd = hijri.monthDb.startJd = to_jd(y, m, d, self.altMode)
		hijri.monthDb.monthLenByYm = {}
		for row in self.trees:
			ym = row[0]
			mLen = row[3]
			hijri.monthDb.monthLenByYm[ym] = mLen
			hijri.monthDb.endJd += mLen

		hijri.monthDb.expJd = hijri.monthDb.endJd
		hijri.monthDb.save()

	def run(self):
		hijri.monthDb.load()
		self.updateWidget()
		self.treev.grab_focus()
		gtk.Dialog.run(self)

	def onResponse(self, dialog, response_id):
		if response_id == gtk.ResponseType.OK:
			self.updateVars()
			self.destroy()
		elif response_id == gtk.ResponseType.CANCEL:
			self.destroy()
		return True

	def onDeleteEvent(self, dialog, gevent):
		self.destroy()
		return True


def tuneHijriMonthes(widget=None):
	dialog = EditDbDialog(parent=ui.prefDialog)
	dialog.resize(400, 400)
	dialog.run()


def dbIsExpired() -> bool:
	if not hijri.hijriUseDB:
		return False
	expJd = hijri.monthDb.expJd
	if expJd is None:
		print("checkDbExpired: hijri.monthDb.expJd = None")
		return False
	if ui.todayCell.jd >= expJd:
		return True
	return False

class HijriMonthsExpirationDialog(gtk.Dialog):
	message = _("""Hijri months are expired.
Please update StarCalendar.
Otherwise, Hijri dates and Iranian official holidays would be incorrect.""")
	def __init__(self, **kwargs):
		gtk.Dialog.__init__(self, **kwargs)
		self.set_title(_("Hijri months expired"))
		self.connect("response", self.onResponse)
		###
		pack(self.vbox, gtk.Label(self.message + "\n\n"), 1, 1)
		###
		hbox = gtk.HBox()
		checkb = gtk.CheckButton(_("Don't show this again"))
		pack(hbox, checkb)
		pack(self.vbox, hbox)
		self.noShowCheckb = checkb
		###
		dialog_add_button(
			self,
			gtk.STOCK_CLOSE,
			_("_Close"),
			gtk.ResponseType.OK,
		)
		###
		self.vbox.show_all()

	def onResponse(self, dialog, response_id):
		if self.noShowCheckb.get_active():
			open(hijri.monthDbExpiredIgnoreFile, "w").write("")
		self.destroy()
		return True


def checkHijriMonthsExpiration():
	if not dbIsExpired():
		# not expired
		return
	if isfile(hijri.monthDbExpiredIgnoreFile):
		# user previously checked "Don't show this again" checkbox
		return
	dialog = HijriMonthsExpirationDialog(parent=ui.mainWin)
	dialog.run()

class HijriMonthsExpirationListener():
	def onCurrentDateChange(self, gdate):
		checkHijriMonthsExpiration()



if __name__ == "__main__":
	tuneHijriMonthes()
