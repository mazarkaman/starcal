#!/usr/bin/env python3
from os.path import join

from scal3.path import *
from scal3 import core
from scal3.locale_man import tr as _
from scal3 import ui

from scal3.ui_gtk import *
from scal3.ui_gtk.decorators import *
from scal3.ui_gtk.utils import (
	labelIconMenuItem,
	labelImageMenuItem,
	imageFromIconName,
	pixbufFromFile,
)


@registerSignals
class IconSelectButton(gtk.Button):
	signals = [
		("changed", [str]),
	]

	def __init__(self, filename=""):
		gtk.Button.__init__(self)
		self.image = gtk.Image()
		self.add(self.image)
		self.dialog = gtk.FileChooserDialog(
			title=_("Select Icon File"),
			action=gtk.FileChooserAction.OPEN,
		)
		okB = self.dialog.add_button("gtk-ok", gtk.ResponseType.OK)
		cancelB = self.dialog.add_button("gtk-cancel", gtk.ResponseType.CANCEL)
		clearB = self.dialog.add_button("gtk-clear", gtk.ResponseType.REJECT)
		if ui.autoLocale:
			cancelB.set_label(_("_Cancel"))
			cancelB.set_image(imageFromIconName(
				"gtk-cancel",
				gtk.IconSize.BUTTON,
			))
			okB.set_label(_("_OK"))
			okB.set_image(imageFromIconName(
				"gtk-ok",
				gtk.IconSize.BUTTON,
			))
			clearB.set_label(_("Clear"))
			clearB.set_image(imageFromIconName(
				"gtk-clear",
				gtk.IconSize.BUTTON,
			))
		###
		menu = gtk.Menu()
		self.menu = menu
		menu.add(labelIconMenuItem(
			_("None"),
			"",
			func=self.menuItemActivate,
			args=("",),
		))
		for item in ui.eventTags:
			icon = item.icon
			if not icon:
				continue
			menu.add(labelImageMenuItem(
				_(item.desc),
				icon,
				func=self.menuItemActivate,
				args=(icon,),
			))
		menu.show_all()
		###
		self.dialog.connect("file-activated", self.fileActivated)
		self.dialog.connect("response", self.dialogResponse)
		#self.connect("clicked", lambda button: button.dialog.run())
		self.connect("button-press-event", self.onButtonPressEvent)
		###
		self.set_filename(filename)

	def onButtonPressEvent(self, widget, gevent):
		b = gevent.button
		if b == 1:
			self.dialog.run()
		elif b == 3:
			self.menu.popup(None, None, None, None, b, gevent.time)

	def menuItemActivate(self, widget, icon):
		self.set_filename(icon)
		self.emit("changed", icon)

	def dialogResponse(self, dialog, response=0):
		dialog.hide()
		if response == gtk.ResponseType.OK:
			fname = dialog.get_filename()
		elif response == gtk.ResponseType.REJECT:
			fname = ""
		else:
			return
		self.set_filename(fname)
		self.emit("changed", fname)

	def _setImage(self, filename):
		self.image.set_from_pixbuf(pixbufFromFile(
			filename,
			ui.imageInputIconSize,
			resize=True,
		))

	def fileActivated(self, dialog):
		fname = dialog.get_filename()
		self.filename = fname
		self._setImage(self.filename)
		self.emit("changed", fname)
		self.dialog.hide()

	def get_filename(self):
		return self.filename

	def set_filename(self, filename):
		if filename is None:
			filename = ""
		self.dialog.set_filename(filename)
		self.filename = filename
		if not filename:
			self._setImage(join(pixDir, "empty.png"))
		else:
			self._setImage(filename)
