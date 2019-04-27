#!/usr/bin/env python3
from scal3 import core
from scal3.locale_man import tr as _
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.font_utils import gfontDecode, gfontEncode


# Note: this widget does not support Auto option

class FontFamilyButton(gtk.FontButton):
	def __init__(self):
		gtk.FontButton.__init__(self)
		self.set_show_size(False)
		self.set_level(gtk.FontChooserLevel.FAMILY) # FAMILY, STYLE, SIZE

	def get_value(self):
		font = gfontDecode(self.get_font_name())
		return font[0]

	def set_value(self, fontFamilyName):
		if fontFamilyName is None:
			fontFamilyName = ui.getFont()[0]
		self.set_font_name(gfontEncode((fontFamilyName, False, False, 15)))
