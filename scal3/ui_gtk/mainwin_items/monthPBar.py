#!/usr/bin/env python3

from scal3.date_utils import monthPlus
from scal3 import core
from scal3.locale_man import tr as _
from scal3.locale_man import rtl, textNumEncode, getMonthName
from scal3.cal_types import calTypes
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.pbar import MyProgressBar
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk.customize import CustomizableCalObj


@registerSignals
class CalObj(MyProgressBar, CustomizableCalObj):
	_name = "monthPBar"
	desc = _("Month Progress Bar")
	itemListCustomizable = False
	hasOptions = False

	def __init__(self):
		MyProgressBar.__init__(self)
		self.initVars()
		self.calType = calTypes.primary

	def onConfigChange(self, *a, **kw):
		self.update_font()

	def onDateChange(self, *a, **kw):
		CustomizableCalObj.onDateChange(self, *a, **kw)

		c = ui.cell
		jd0 = core.primary_to_jd(c.year, c.month, 1)
		jd1 = c.jd
		nyear, nmonth = monthPlus(c.year, c.month, 1)
		jd2 = core.primary_to_jd(nyear, nmonth, 1)
		length = jd2 - jd0
		past = jd1 - jd0
		fraction = float(past) / length
		if rtl:
			percent = "%d%%" % (fraction * 100)
		else:
			percent = "%%%d" % (fraction * 100)
		self.set_text(
			getMonthName(self.calType, c.month, c.year) +
			":   " +
			textNumEncode(
				percent,
				changeDot=True,
			) +
			"   =   " +
			"%s%s / %s%s" %(_(past), _(" days"), _(length), _(" days"))
		)
		self.set_fraction(fraction)
