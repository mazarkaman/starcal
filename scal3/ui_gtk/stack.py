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

import time

from scal3.locale_man import tr as _

from scal3.ui_gtk import *
from scal3.ui_gtk.utils import imageFromIconName


class StackPage:
	def __init__(self):
		self.pageWidget = None
		self.pageParent = ""
		self.pageName = ""
		self.pageTitle = ""
		self.pageLabel = ""
		self.pageIcon = ""
		self.pageExpand = True


class MyStack(gtk.Stack):
	def __init__(self, iconSize=gtk.IconSize.BUTTON, vboxSpacing=5):
		gtk.Stack.__init__(self)
		self.set_transition_duration(300) # milliseconds
		###
		self._rtl = self.get_direction() == gtk.TextDirection.RTL # type: bool
		self._iconSize = iconSize # type: int
		self._vboxSpacing = vboxSpacing # type: int
		###
		self._parentNames = {} # Dict[str, str]
		self._currentName = ""
		self._titles = {} # Dict[str, str]
		###
		self.connect("key-press-event", self._keyPress)
		###
		self._titleFontSize = "x-small"
		self._titleCentered = False
		###
		self._windowTitleEnable = False
		self._window = None
		self._windowTitleMain = ""
		self._windowTitleMainFirst = False

	def setTitleFontSize(self, fontSize: str):
		'''
		Font size in 1024ths of a point, or one of the absolute sizes
		'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large',
		or one of the relative sizes 'smaller' or 'larger'.
		If you want to specify a absolute size, it's usually easier to take
		advantage of the ability to specify a partial font description using 'font';
		you can use font='12.5' rather than size='12800'.
		https://developer.gnome.org/pango/stable/PangoMarkupFormat.html#PangoMarkupFormat
		'''
		self._titleFontSize = fontSize

	def setTitleCentered(self, centered: bool):
		self._titleCentered = centered

	def setupWindowTitle(self, window: gtk.Window, mainTitle: str, mainTitleFirst: bool):
		self._windowTitleEnable = True
		self._window = window
		self._windowTitleMain = mainTitle
		self._windowTitleMainFirst = mainTitleFirst

	def _keyPress(self, arg, gevent):
		if gdk.keyval_name(gevent.keyval) == "BackSpace":
			if self._currentName:
				parentName = self._parentNames[self._currentName]
				if parentName:
					self.gotoPage(parentName, backward=True)
					return True
		return False

	def _setSlideForward(self):
		self.set_transition_type(
			gtk.RevealerTransitionType.SLIDE_LEFT
		)

	def _setSlideBackward(self):
		self.set_transition_type(
			gtk.RevealerTransitionType.SLIDE_RIGHT
		)

	def _newNavButtonBox(self, parentName: str, title=""):
		hbox = HBox()
		# hbox.set_direction(gtk.TextDirection.LTR)
		backButton = gtk.Button()
		backHbox = HBox(spacing=3)
		backHbox.set_border_width(5)
		pack(backHbox, imageFromIconName(
			"gtk-go-forward" if self._rtl else "gtk-go-back",
			self._iconSize,
		))
		pack(backHbox, gtk.Label(label=_("Back")))
		backButton.add(backHbox)
		backButton.connect(
			"clicked",
			lambda w: self.gotoPage(parentName, backward=True),
		)
		pack(hbox, backButton)
		pack(hbox, gtk.Label(), 1, 1)
		if title:
			if self._titleFontSize:
				title = "<span font_size=\"%s\">%s</span>" % (self._titleFontSize, title)
			label = gtk.Label(label=title)
			if self._titleFontSize:
				label.set_use_markup(True)
			pack(hbox, label, 0, 0)
			if self._titleCentered:
				pack(hbox, gtk.Label(), 1, 1)
		hbox.show_all()
		return hbox

	def addPage(
		self,
		name: str,
		parentName: str,
		widget: gtk.Widget,
		title: str = "",
		expand=False,
		fill=False,
	):
		vbox = VBox(spacing=self._vboxSpacing)
		if parentName:
			pack(vbox, self._newNavButtonBox(parentName, title=title))
		pack(vbox, widget, expand=expand, fill=fill)
		self.add_named(vbox, name=name)
		widget.show()
		vbox.show()
		##
		self._parentNames[name] = parentName
		self._titles[name] = title
		##
		if not self._currentName:
			self.gotoPage(name, False)


	def addPageObj(self, page: StackPage):
		self.addPage(
			page.pageName,
			page.pageParent,
			page.pageWidget,
			title=page.pageTitle,
			expand=page.pageExpand,
			fill=page.pageExpand,
		)

	def hasPage(self, name: str):
		return self.get_child_by_name(name=name) != None

	def _setPageWindowTitle(self, name: str):
		if not self._windowTitleEnable:
			return
		title = self._titles[name]
		if not title:
			self._window.set_title(self._windowTitleMain)
			return
		if self._windowTitleMain:
			if self._windowTitleMainFirst:
				title = self._windowTitleMain + " - " + title
			else:
				title = title + " - " + self._windowTitleMain
		self._window.set_title(title)

	def gotoPage(self, name: str, backward: bool = False):
		if backward:
			self._setSlideBackward()
		else:
			self._setSlideForward()
		self.set_visible_child_name(name)
		self.show()
		self._currentName = name
		self._setPageWindowTitle(name)
