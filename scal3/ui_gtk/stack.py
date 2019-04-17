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
from scal3.ui_gtk import *

class MyStack(gtk.Stack):
	def __init__(self, rtl=False, iconSize=gtk.IconSize.BUTTON, vboxSpacing=5):
		gtk.Stack.__init__(self)
		self.set_transition_duration(300) # milliseconds
		###
		self._rtl = rtl
		self._iconSize = iconSize
		self._vboxSpacing = vboxSpacing
		###
		self._nameStack = [] # type: List[str]

	def _setSlideForward(self):
		self.set_transition_type(
			gtk.RevealerTransitionType.SLIDE_RIGHT if self._rtl
			else gtk.RevealerTransitionType.SLIDE_LEFT
		)

	def _setSlideBackward(self):
		self.set_transition_type(
			gtk.RevealerTransitionType.SLIDE_LEFT if self._rtl
			else gtk.RevealerTransitionType.SLIDE_RIGHT
		)

	def _newNavButtonBox(self, desc=""):
		hbox = gtk.HBox()
		backButton = gtk.Button()
		backButton.set_label("Back")
		backButton.set_image(gtk.Image.new_from_icon_name("gtk-go-back", self._iconSize))
		backButton.connect("clicked", self._goBackClicked)
		pack(hbox, backButton)
		pack(hbox, gtk.Label(), 1, 1)
		if desc:
			pack(hbox, gtk.Label(label=desc), 0, 0)
		hbox.show_all()
		return hbox

	def addPage(self, name: str, widget: gtk.Widget, addBackButton: bool, desc: str = ""):
		vbox = gtk.VBox(spacing=self._vboxSpacing)
		if addBackButton:
			pack(vbox, self._newNavButtonBox(desc=desc))
		pack(vbox, widget)
		self.add_named(vbox, name=name)
		widget.show()
		vbox.show()
		##
		if not self._nameStack:
			self.gotoPage(name, False)

	def gotoPage(self, name: str, backward=False):
		if backward:
			if len(self._nameStack) < 2:
				raise ValueError("gotoPage: backward=True passed while there are only %s pages" % len(self._nameStack))
			if name != self._nameStack[-2]:
				raise ValueError("gotoPage: page name does not match the last page")
		##
		if backward:
			self._setSlideBackward()
		else:
			self._setSlideForward()

		self.set_visible_child_name(name)
		
		self.show()
		##
		if backward:
			self._nameStack.pop()
		else:
			self._nameStack.append(name)

	def goBack(self):
		self.gotoPage(self._nameStack[-2], backward=True)

	def _goBackClicked(self, button):
		self.goBack()


