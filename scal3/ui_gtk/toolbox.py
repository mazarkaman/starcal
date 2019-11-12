#!/usr/bin/env python3

from scal3 import logger
log = logger.get()

from time import time as now

from typing import Optional, Tuple, Dict, Union, Callable, Any

from scal3 import core
from scal3.locale_man import tr as _
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk.utils import (
	set_tooltip,
	imageFromIconName,
	pixbufFromFile,
)
from scal3.ui_gtk.mywidgets.button import ConButtonBase
from scal3.ui_gtk import gtk_ud as ud
from scal3.ui_gtk.customize import CustomizableCalObj


@registerSignals
class ToolBoxItem(gtk.Button, ConButtonBase, CustomizableCalObj):
	hasOptions = False

	signals = CustomizableCalObj.signals + [
		("con-clicked", []),
	]

	def __init__(
		self,
		name: str,
		iconName: str,
		onClick: Union[str, Callable],
		desc: str = "",
		shortDesc: str = "",
		enableTooltip: bool = True,
		labelOnly: bool = False,
		continuousClick: bool = True,
		onPress: Optional[Union[str, Callable]] = None,
	) -> None:
		"""
			if labelOnly=True, button will have no icon,
				and self.label will be accessible
		"""
		gtk.Button.__init__(self)
		if continuousClick:
			ConButtonBase.__init__(self)
		######
		self._name = name
		self.filename = ""
		self.onClick = onClick
		self.onPress = onPress
		self.iconSize = 0
		self.labelOnly = labelOnly
		self.continuousClick = continuousClick
		self.vertical = False
		######
		if not desc:
			desc = name.capitalize()
		if not shortDesc:
			shortDesc = desc
		##
		desc = _(desc)
		shortDesc = _(shortDesc)
		self.desc = desc
		# self.shortDesc = shortDesc  # FIXME
		######
		if not labelOnly and iconName:
			# render_icon_pixbuf is Deprecated since version 3.10:
			# Use Gtk.IconTheme.load_icon() instead.
			self.bigPixbuf = self.render_icon_pixbuf(
				iconName,
				gtk.IconSize.DIALOG,
			)
		else:
			self.bigPixbuf = None
		######
		if labelOnly:
			self.label = gtk.Label()
			self.add(self.label)
			self.image = None
		else:
			self.image = gtk.Image()
			self.image.show()
			self.add(self.image)
		###
		self.initVars()
		if enableTooltip:
			set_tooltip(self, desc)

	def setIconName(self, iconName: str) -> None:
		if not iconName:
			self.bigPixbuf = None
			if self.image is not None:
				self.image.clear()
			return
		self.bigPixbuf = self.render_icon_pixbuf(
			iconName,
			gtk.IconSize.DIALOG,
		)
		self._setIconSizeImage(self.iconSize)

	def setIconFile(self, fname: str) -> None:
		self.filename = fname
		if not fname:
			self.bigPixbuf = None
			if self.image is not None:
				self.image.clear()
			return
		self.bigPixbuf = pixbufFromFile(fname, size=self.iconSize)
		if fname.endswith(".svg"):
			self.image.set_from_pixbuf(self.bigPixbuf)
		else:
			self._setIconSizeImage(self.iconSize)

	def setIconSize(self, iconSize: int) -> None:
		if self.labelOnly:
			return
		if iconSize == self.iconSize:
			return
		self.iconSize = iconSize
		if self.bigPixbuf is not None:
			self._setIconSizeImage(iconSize)

	def _setIconSizeImage(self, iconSize: int) -> None:
		if self.bigPixbuf is None:
			if self.filename:
				self.image.set_from_pixbuf(pixbufFromFile(
					self.filename,
					size=iconSize,
				))
				return
			raise RuntimeError(f"bigPixbuf=None, self.filename={self.filename}")
		# self.image.set_from_pixbuf(self.bigPixbuf) # works
		pixbuf = self.bigPixbuf.scale_simple(
			iconSize,
			iconSize,
			GdkPixbuf.InterpType.BILINEAR,
		)
		self.image.set_from_pixbuf(pixbuf)

	def show(self) -> None:
		gtk.Button.show_all(self)

	def setVertical(self, vertical: bool) -> None:
		self.vertical = vertical

	# the following methods (do_get_*) are meant to make the button a square
	def do_get_request_mode(self) -> gtk.SizeRequestMode:
		if self.vertical:
			return gtk.SizeRequestMode.HEIGHT_FOR_WIDTH
		return gtk.SizeRequestMode.WIDTH_FOR_HEIGHT

	def do_get_preferred_height_for_width(self, size: int) -> Tuple[int, int]:
		# must return minimum_size, natural_size
		if not self.vertical:
			return self.get_preferred_height()
		return size, size

	def do_get_preferred_width_for_height(self, size: int) -> Tuple[int, int]:
		# must return minimum_size, natural_size
		if self.vertical:
			return self.get_preferred_width()
		return size, size




#@registerSignals
class CustomizableToolBox(gtk.Box, CustomizableCalObj):
	_name = "toolbar"
	desc = _("Toolbar")
	#signals = CustomizableCalObj.signals + [
	#	("popup-main-menu", [int, int, int]),
	#]
	styleList = (
		# Gnome"s naming is not exactly the best here
		# And Gnome"s order of options is also different from Gtk"s enum
		"Icon", # "icons", "Icons only"
		"Text", # "text", "Text only"
		"Text below Icon", # "both", "Text below items"
		"Text beside Icon", # "both-horiz", "Text beside items"
	)
	defaultItems = []
	defaultItemsDict = {}

	def __init__(
		self,
		funcOwner: Any,
		vertical: bool = False,
		iconSize: int = 22,
		continuousClick: bool = True,
	) -> None:
		self.vertical = vertical
		gtk.Box.__init__(self, orientation=self.get_orientation())
		self.funcOwner = funcOwner
		self.iconSize = iconSize
		self.continuousClick = continuousClick
		self.buttonBorder = 0
		self.buttonPadding = 3
		#self.add_events(gdk.EventMask.POINTER_MOTION_MASK)
		self.initVars()

		# set on setData(), used in getData() to keep compatibility
		self.data = {}

	def get_orientation(self) -> gtk.Orientation:
		if self.vertical:
			return gtk.Orientation.VERTICAL
		return gtk.Orientation.HORIZONTAL

	def getOptionsWidget(self) -> gtk.Widget:
		from scal3.ui_gtk.pref_utils import SpinPrefItem
		if self.optionsWidget:
			return self.optionsWidget
		###
		optionsWidget = VBox()
		##
		prefItem = SpinPrefItem(
			self,
			"iconSize",
			5, 128,
			digits=1, step=1,
			label=_("Icon Size"),
			live=True,
			onChangeFunc=self.onIconSizeChange,
		)
		pack(optionsWidget, prefItem.getWidget())
		####
		prefItem = SpinPrefItem(
			self,
			"buttonBorder",
			0, 99,
			digits=1, step=1,
			label=_("Buttons Border"),
			live=True,
			onChangeFunc=self.onButtonBorderChange,
		)
		pack(optionsWidget, prefItem.getWidget())
		####
		prefItem = SpinPrefItem(
			self,
			"buttonPadding",
			0, 99,
			digits=1, step=1,
			label=_("Space between buttons"),
			live=True,
			onChangeFunc=self.onButtonPaddingChange,
		)
		pack(optionsWidget, prefItem.getWidget())
		##
		optionsWidget.show_all()
		self.optionsWidget = optionsWidget
		return optionsWidget

	def getIconSize(self) -> int:
		return self.iconSize

	def setIconSize(self, size: int) -> None:
		self.iconSize = size
		self.onIconSizeChange()

	def onIconSizeChange(self) -> None:
		size = self.iconSize
		for item in self.items:
			item.setIconSize(size)

	def setButtonBorder(self, buttonBorder):
		self.buttonBorder = buttonBorder
		self.onButtonBorderChange()

	def onButtonBorderChange(self) -> None:
		buttonBorder = self.buttonBorder
		for item in self.items:
			item.set_border_width(buttonBorder)

	def setButtonPadding(self, padding: int) -> None:
		self.buttonPadding = padding
		self.onButtonPaddingChange()

	def onButtonPaddingChange(self) -> None:
		padding = self.buttonPadding
		for item in self.items:
			self.set_child_packing(
				item,
				False,
				False,
				padding,
				gtk.PackType.START,
			)

	def moveItemUp(self, i: int) -> None:
		button = self.items[i]
		self.remove(button)
		self.insert(button, i - 1)
		self.items.insert(i - 1, self.items.pop(i))

	def appendItem(self, item: ud.CalObjType) -> None:
		CustomizableCalObj.appendItem(self, item)
		item.setIconSize(self.iconSize)
		item.onConfigChange(toParent=False)
		pack(self, item, padding=self.buttonPadding)
		if item.enable:
			item.show()

	def getData(self) -> Dict[str, Any]:
		self.data.update({
			"items": self.getItemsData(),
			"iconSizePixel": self.getIconSize(),
			"buttonBorder": self.buttonBorder,
			"buttonPadding": self.buttonPadding,
		})
		return self.data

	def setupItemSignals(self, item: ud.CalObjType) -> None:
		if item.onClick:
			if isinstance(item.onClick, str):
				onClick = getattr(self.funcOwner, item.onClick)
			else:
				onClick = item.onClick
			item.connect("clicked", onClick)
			if self.continuousClick and item.continuousClick:
				item.connect("con-clicked", onClick)

		if item.onPress:
			if isinstance(item.onPress, str):
				onPress = getattr(self.funcOwner, item.onClick)
			else:
				onPress = item.onPress
			item.connect("button-press-event", onPress)

	def setData(self, data: Dict[str, Any]) -> None:
		self.data = data
		for (name, enable) in data["items"]:
			item = self.defaultItemsDict.get(name)
			if item is None:
				log.info(f"toolbar item {name!r} does not exist")
				continue
			item.enable = enable
			item.setVertical(self.vertical)
			self.setupItemSignals(item)
			self.appendItem(item)
		###
		self.getOptionsWidget()
		# ^ because we update the Customize dialog widgets as well
		# FIXME: is this really needed?
		###
		iconSize = data.get("iconSizePixel")
		if iconSize:
			self.setIconSize(iconSize)
		###
		bb = data.get("buttonBorder", 0)
		self.setButtonBorder(bb)
		###
		padding = data.get("buttonPadding", 0)
		self.setButtonPadding(padding)
		self.optionsWidget = None
