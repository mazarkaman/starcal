#!/usr/bin/env python3
from scal3 import core
from scal3.locale_man import tr as _
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk.toolbar import ToolbarItem, CustomizableToolbar


@registerSignals
class CalObj(CustomizableToolbar):
	defaultItems = [
		ToolbarItem(
			"today",
			"gtk-home",
			"goToday",
			"Select Today",
			"Today",
		),
		ToolbarItem(
			"date",
			"gtk-index",
			"selectDateShow",
			"Select Date...",
			"Date",
		),
		ToolbarItem(
			"customize",
			"gtk-edit",
			"customizeShow",
		),
		ToolbarItem(
			"preferences",
			"gtk-preferences",
			"prefShow",
		),
		ToolbarItem(
			"add",
			"gtk-add",
			"eventManShow",
			"Event Manager",
			"Event",
		),
		ToolbarItem(
			"export",
			"gtk-convert",
			"onExportClick",
			_("Export to {format}").format(format="HTML"),
			"Export",
		),
		ToolbarItem(
			"about",
			"gtk-about",
			"aboutShow",
			_("About ") + core.APP_DESC,
			"About",
		),
		ToolbarItem(
			"quit",
			"gtk-quit",
			"quit",
		),
	]
	defaultItemsDict = {
		item._name: item
		for item in defaultItems
	}

	def __init__(self):
		CustomizableToolbar.__init__(
			self,
			ui.mainWin,
			vertical=False,
			continuousClick=False,
		)
		if not ud.mainToolbarData["items"]:
			ud.mainToolbarData["items"] = [
				(item._name, True) for item in self.defaultItems
			]
		self.setData(ud.mainToolbarData)
		if ui.mainWin:
			self.connect("button-press-event", ui.mainWin.childButtonPress)

	def updateVars(self):
		CustomizableToolbar.updateVars(self)
		ud.mainToolbarData = self.getData()
