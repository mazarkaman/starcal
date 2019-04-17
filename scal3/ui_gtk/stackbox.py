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

from scal3.ui_gtk import *

class StackBox(gtk.VBox):
    def __init__(self, iconSize=gtk.IconSize.BUTTON, vboxSpacing=5):
        gtk.VBox.__init__(self)
        self._iconSize = iconSize
        self._vboxSpacing = vboxSpacing
        ###
        self._pageDict = {} # type: Dict[str, gtk.Widget]
        self._pageStack = [] # type: List[str]
        self._currentName = ""
        self._currentRevealer = None # type: Optional[gtk.Revealer]
        self._currentVBox = None # type: Optional[gtk.VBox]
        ###

    def _backButtonClicked(self, button):
        print("backButtonClicked")
        self.gotoPage(self._pageStack[-2], isBack=True)

    def _newNavButtonBox(self):
        hbox = gtk.HBox()
        backButton = gtk.Button()
        backButton.set_label("Back")
        backButton.set_image(gtk.Image.new_from_icon_name("gtk-go-back", self._iconSize))
        backButton.connect("clicked", self._backButtonClicked)
        pack(hbox, backButton)
        pack(hbox, gtk.Label(), 1, 1)
        hbox.show_all()
        return hbox

    def addPage(self, name: str, widget: gtk.Widget):
        self._pageDict[name] = widget
        if not self._currentName:
            self.gotoPage(name, isBack=False)

    def gotoPage(self, name: str, isBack=False):
        widget = self._pageDict[name]
        # self._nextWidget = widget
        ##
        if isBack:
            if len(self._pageStack) < 2:
                raise ValueError("gotoPage: isBack=True passed while there are only %s pages" % len(self._pageStack))
            if name != self._pageStack[-2]:
                raise ValueError("gotoPage: page name does not match the last page")
            addBackButton = len(self._pageStack) > 2
        else:
            addBackButton = len(self._pageStack) > 0
        ##
        # vbox = None
        if self._currentRevealer:
            # widget.unparent()
            self._currentVBox.remove(widget)
            self._currentRevealer.remove(self._currentVBox)
            self.remove(self._currentRevealer)
            # if isBack:
            #     vbox = self._currentVBox
            # else:
        ##
        vbox = gtk.VBox(spacing=self._vboxSpacing)
        if addBackButton:
            pack(vbox, self._newNavButtonBox())
        pack(vbox, widget)
        revealer = gtk.Revealer()
        revealer.set_transition_type(gtk.RevealerTransitionType.SLIDE_LEFT)
        revealer.set_transition_duration(1000) # milliseconds
        revealer.add(vbox)
        widget.show()
        vbox.show()
        revealer.show()
        ##
        pack(self, revealer, 1, 1)
        ##
        self._currentName = name
        self._currentVBox = vbox
        self._currentRevealer = revealer
        if isBack:
            self._pageStack.pop()
        else:
            self._pageStack.append(name)
        ##
        revealer.set_reveal_child(True)
        ##
        print("switched to:", name)



 


if __name__ == "__main__":
    stackbox = StackBox()
    ###
    vbox = gtk.VBox(spacing=20)
    pack(vbox, gtk.Label(label="Line 1"))
    pack(vbox, gtk.Label(label="Line 2"))
    button = gtk.Button(label="Next Page (2)")
    pack(vbox, button)
    button.connect("clicked", lambda w: stackbox.gotoPage("page2"))
    vbox.show_all()
    stackbox.addPage("page1", vbox)
    ###
    vbox = gtk.VBox(spacing=20)
    pack(vbox, gtk.Label(label="Line 3"))
    pack(vbox, gtk.Label(label="Line 4"))
    button = gtk.Button(label="Next Page (3)")
    pack(vbox, button)
    button.connect("clicked", lambda w: stackbox.gotoPage("page3"))
    vbox.show_all()
    stackbox.addPage("page2", vbox)
    ###
    vbox = gtk.VBox(spacing=20)
    pack(vbox, gtk.Label(label="Line 5"))
    pack(vbox, gtk.Label(label="Line 6"))
    button = gtk.Button(label="Next Page (4)")
    pack(vbox, button)
    # button.connect("clicked", lambda w: stackbox.gotoPage("page4"))
    vbox.show_all()
    stackbox.addPage("page3", vbox)
    ###
    dialog = gtk.Dialog()
    pack(dialog.vbox, stackbox, 1, 1)
    stackbox.show()
    dialog.vbox.show()
    dialog.run()

