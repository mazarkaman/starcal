#!/usr/bin/env python3
from scal3 import core
from scal3.locale_man import tr as _
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk.toolbox import (
	ToolBoxItem,
	CustomizableToolBox,
)



@registerSignals
class CalObj(CustomizableToolBox):
	defaultItems = [
		ToolBoxItem(
			"today",
			"gtk-home",
			"goToday",
			"Select Today",
			"Today",
			continuousClick=False,
		),
		ToolBoxItem(
			"date",
			"gtk-index",
			"selectDateShow",
			"Select Date...",
			"Date",
			continuousClick=False,
		),
		ToolBoxItem(
			"customize",
			"gtk-edit",
			"customizeShow",
			continuousClick=False,
		),
		ToolBoxItem(
			"preferences",
			"gtk-preferences",
			"prefShow",
			continuousClick=False,
		),
		ToolBoxItem(
			"add",
			"gtk-add",
			"eventManShow",
			"Event Manager",
			"Event",
			continuousClick=False,
		),
		ToolBoxItem(
			"export",
			"gtk-convert",
			"onExportClick",
			_("Export to {format}").format(format="HTML"),
			"Export",
			continuousClick=False,
		),
		ToolBoxItem(
			"about",
			"gtk-about",
			"aboutShow",
			_("About ") + core.APP_DESC,
			"About",
			continuousClick=False,
		),
		ToolBoxItem(
			"quit",
			"gtk-quit",
			"quit",
			continuousClick=False,
		),
	]
	defaultItemsDict = {
		item._name: item
		for item in defaultItems
	}

	def __init__(self):
		CustomizableToolBox.__init__(
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
		CustomizableToolBox.updateVars(self)
		ud.mainToolbarData = self.getData()
