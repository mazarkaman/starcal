#!/usr/bin/env python3
from scal3.cal_types import calTypes
from scal3 import core
from scal3.locale_man import tr as _
from scal3.locale_man import rtl
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.mywidgets.datelabel import DateLabel
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk.customize import CustomizableCalObj
from scal3.ui_gtk.color_utils import colorizeSpan


@registerSignals
class CalObj(gtk.Box, CustomizableCalObj):
	_name = "statusBar"
	desc = _("Status Bar")
	itemListCustomizable = False
	hasOptions = True

	def __init__(self):
		from scal3.ui_gtk.mywidgets.resize_button import ResizeButton
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		self.initVars()
		####
		self.labelBox = HBox()
		pack(self, self.labelBox, 1, 1)
		resizeB = ResizeButton(ui.mainWin)
		pack(self, resizeB, 0, 0)
		if rtl:
			self.set_direction(gtk.TextDirection.LTR)
			self.labelBox.set_direction(gtk.TextDirection.LTR)

	def onConfigChange(self, *a, **kw):
		CustomizableCalObj.onConfigChange(self, *a, **kw)
		###
		for label in self.labelBox.get_children():
			label.destroy()
		###
		activeCalTypes = calTypes.active
		if ui.statusBarDatesReverseOrder:
			activeCalTypes = reversed(activeCalTypes)
		for calType in activeCalTypes:
			label = DateLabel(None)
			label.calType = calType
			pack(self.labelBox, label, 1)
		self.show_all()
		###
		self.onDateChange()

	def onDateChange(self, *a, **kw):
		CustomizableCalObj.onDateChange(self, *a, **kw)
		labels = self.labelBox.get_children()
		for i, label in enumerate(labels):
			text = ui.cell.format(ud.dateFormatBin, label.calType)
			if label.calType == calTypes.primary:
				text = "<b>%s</b>" % text
			if ui.statusBarDatesColorEnable:
				text = colorizeSpan(text, ui.statusBarDatesColor)
			label.set_label(text)

	def getOptionsWidget(self):
		from scal3.ui_gtk.pref_utils import LiveCheckPrefItem, CheckPrefItem, \
			ColorPrefItem, LiveCheckColorPrefItem
		if self.optionsWidget:
			return self.optionsWidget
		####
		optionsWidget = VBox(spacing=10)
		####
		prefItem = LiveCheckPrefItem(
			ui,
			"statusBarDatesReverseOrder",
			label=_("Reverse the order of dates"),
			onChangeFunc=self.onConfigChange,
		)
		pack(optionsWidget, prefItem.getWidget())
		####
		prefItem = LiveCheckColorPrefItem(
			CheckPrefItem(ui, "statusBarDatesColorEnable", _("Dates Color")),
			ColorPrefItem(ui, "statusBarDatesColor", True),
			self.onDateChange,
		)
		pack(optionsWidget, prefItem.getWidget())
		####
		optionsWidget.show_all()
		self.optionsWidget = optionsWidget
		return self.optionsWidget
