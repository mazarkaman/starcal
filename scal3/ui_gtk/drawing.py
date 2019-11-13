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

from scal3 import logger
log = logger.get()

from os.path import join
from math import pi
from math import sin, cos
import re

from typing import Optional, Tuple

from scal3.path import *
from scal3.utils import toBytes
from scal3 import core
from scal3.locale_man import cutText, rtl
from scal3 import ui

from scal3.color_utils import rgbToInt

from scal3.ui_gtk import *
from scal3.ui_gtk.font_utils import *
from scal3.ui_gtk.color_utils import *
from scal3.ui_gtk.svg_utils import pixbufFromSvgFile

from gi.repository import cairo
from gi.repository.PangoCairo import show_layout

if not ui.fontCustom:
	ui.fontCustom = ui.fontDefault[:]

with open(join(rootDir, "svg", "color-check.svg")) as fp:
	colorCheckSvgTextChecked = fp.read()
colorCheckSvgTextUnchecked = re.sub(
	"<path[^<>]*?id=\"check\"[^<>]*?/>",
	"",
	colorCheckSvgTextChecked,
	flags=re.M | re.S,
)


def setColor(cr, color):
	# arguments to set_source_rgb and set_source_rgba must be between 0 and 1
	if len(color) == 3:
		cr.set_source_rgb(
			color[0] / 255.0,
			color[1] / 255.0,
			color[2] / 255.0,
		)
	elif len(color) == 4:
		cr.set_source_rgba(
			color[0] / 255.0,
			color[1] / 255.0,
			color[2] / 255.0,
			color[3] / 255.0,
		)
	else:
		raise ValueError(f"bad color {color}")


def fillColor(cr, color):
	setColor(cr, color)
	cr.fill()


def newTextLayout(
	widget,
	text="",
	font=None,
	maxSize=None,
	maximizeScale=0.6,
	truncate=False,
):
	"""
	None return value should be expected and handled, only if maxSize is given
	"""
	layout = widget.create_pango_layout("")  # a Pango.Layout object
	if font:
		font = list(font)
	else:
		font = ui.getFont()
	layout.set_font_description(pfontEncode(font))
	if text:
		layout.set_markup(text=text, length=len(text.encode("utf8")))
		if maxSize:
			layoutW, layoutH = layout.get_pixel_size()
			##
			maxW, maxH = maxSize
			maxW = float(maxW)
			maxH = float(maxH)
			if maxW <= 0:
				return
			if maxH <= 0:
				minRat = 1.0
			else:
				minRat = 1.01 * layoutH / maxH  # FIXME
			if truncate:
				if minRat > 1:
					font[3] = int(font[3] / minRat)
				layout.set_font_description(pfontEncode(font))
				layoutW, layoutH = layout.get_pixel_size()
				if layoutW > 0:
					char_w = float(layoutW) / len(text)
					char_num = int(maxW // char_w)
					while layoutW > maxW:
						text = cutText(text, char_num)
						if not text:
							break
						layout = widget.create_pango_layout(text)
						layout.set_font_description(pfontEncode(font))
						layoutW, layoutH = layout.get_pixel_size()
						char_num -= max(
							int((layoutW - maxW) // char_w),
							1,
						)
						if char_num < 0:
							layout = None
							break
			else:
				if maximizeScale > 0:
					minRat = minRat / maximizeScale
				if minRat < layoutW / maxW:
					minRat = layoutW / maxW
				if minRat > 1:
					font[3] = int(font[3] / minRat)
				layout.set_font_description(pfontEncode(font))
	return layout


"""
def newLimitedWidthTextLayout(
	widget,
	text,
	width,
	font=None,
	truncate=True,
	markup=True,
):
	if not font:
		font = ui.getFont()
	layout = widget.create_pango_layout("")
	length = len(text.encode("utf8")
	if markup:
		layout.set_markup(text=text, length=length)
	else:
		layout.set_text(text=text, length=length)
	layout.set_font_description(pfontEncode(font))
	if not layout:
		return None
	layoutW, layoutH = layout.get_pixel_size()
	if layoutW > width:
		if truncate:
			char_w = layoutW/len(text)
			char_num = int(width//char_w)
			while layoutW > width:
				text = cutText(text, char_num)
				layout = widget.create_pango_layout(text)
				layout.set_font_description(pfontEncode(font))
				layoutW, layoutH = layout.get_pixel_size()
				char_num -= max(int((layoutW-width)//char_w), 1)
				if char_num<0:
					layout = None
					break
		else:## use smaller font
			font2 = list(font)
			while layoutW > width:
				font2[3] = 0.9*font2[3]*width/layoutW
				layout.set_font_description(pfontEncode(font2))
				layoutW, layoutH = layout.get_pixel_size()
				# log.debug(layoutW, width)
			#print
	return layout
"""


def calcTextPixelSize(
	widget: gtk.Widget,
	text: str,
	font: Optional[Tuple[str, bool, bool, float]] = None,
) -> Tuple[float, float]:
	layout = widget.create_pango_layout(text)  # a Pango.Layout object
	if font is not None:
		layout.set_font_description(pfontEncode(list(font)))
	width, height = layout.get_pixel_size()
	return width, height


def calcTextPixelWidth(
	widget: gtk.Widget,
	text: str,
	font = None,
) -> float:
	width, height = calcTextPixelSize(widget, text, font=font)
	return width


def newColorCheckPixbuf(color, size, checked):
	if checked:
		data = colorCheckSvgTextChecked
	else:
		data = colorCheckSvgTextUnchecked
	data = data.replace(
		f"fill:#000000;",
		f"fill:{rgbToHtmlColor(color[:3])};",
	)
	data = toBytes(data)
	loader = GdkPixbuf.PixbufLoader.new_with_type("svg")
	loader.set_size(size, size)
	try:
		loader.write(data)
	finally:
		loader.close()
	pixbuf = loader.get_pixbuf()
	return pixbuf


def newDndDatePixbuf(ymd):
	imagePath = join(rootDir, "svg", "dnd-date.svg")
	with open(imagePath) as fp:
		data = fp.read()
	data = data.replace("YYYY", f"{ymd[0]:04d}")
	data = data.replace("MM", f"{ymd[1]:02d}")
	data = data.replace("DD", f"{ymd[2]:02d}")
	data = toBytes(data)
	loader = GdkPixbuf.PixbufLoader.new_with_type("svg")
	try:
		loader.write(data)
	finally:
		loader.close()
	pixbuf = loader.get_pixbuf()
	return pixbuf


def newDndFontNamePixbuf(name):
	imagePath = join(rootDir, "svg", "dnd-font.svg")
	with open(imagePath) as fp:
		data = fp.read()
	data = data.replace("FONTNAME", name)
	data = toBytes(data)
	loader = GdkPixbuf.PixbufLoader.new_with_type("svg")
	try:
		loader.write(data)
	finally:
		loader.close()
	pixbuf = loader.get_pixbuf()
	return pixbuf


def drawRoundedRect(cr, cx0, cy0, cw, ch, ro):
	ro = min(ro, cw / 2.0, ch / 2.0)
	cr.move_to(
		cx0 + ro,
		cy0,
	)
	# up side:
	cr.line_to(
		cx0 + cw - ro,
		cy0,
	)
	# up right corner:
	cr.arc(
		cx0 + cw - ro,
		cy0 + ro, ro,
		3 * pi / 2,
		2 * pi,
	)
	# right side:
	cr.line_to(
		cx0 + cw,
		cy0 + ch - ro,
	)
	# down right corner:
	cr.arc(
		cx0 + cw - ro,
		cy0 + ch - ro,
		ro,
		0,
		pi / 2,
	)
	# down side:
	cr.line_to(
		cx0 + ro,
		cy0 + ch,
	)
	# down left corner:
	cr.arc(
		cx0 + ro,
		cy0 + ch - ro,
		ro,
		pi / 2,
		pi,
	)
	# left side:
	cr.line_to(
		cx0,
		cy0 + ro,
	)
	# up left corner:
	cr.arc(
		cx0 + ro,
		cy0 + ro,
		ro,
		pi,
		3 * pi / 2,
	)
	# done
	cr.close_path()


def drawOutlineRoundedRect(cr, cx0, cy0, cw, ch, ro, d):
	ro = min(ro, cw / 2.0, ch / 2.0)
	#a = min(cw, ch); ri = ro*(a-2*d)/a
	ri = max(0, ro - d)
	# log.debug(ro, ri)
	# ####### Outline:
	cr.move_to(
		cx0 + ro,
		cy0,
	)
	cr.line_to(
		cx0 + cw - ro,
		cy0,
	)
	# up right corner:
	cr.arc(
		cx0 + cw - ro,
		cy0 + ro,
		ro,
		3 * pi / 2,
		2 * pi,
	)
	cr.line_to(
		cx0 + cw,
		cy0 + ch - ro,
	)
	# down right corner:
	cr.arc(
		cx0 + cw - ro,
		cy0 + ch - ro,
		ro,
		0,
		pi / 2,
	)
	cr.line_to(
		cx0 + ro,
		cy0 + ch,
	)
	# down left corner:
	cr.arc(
		cx0 + ro,
		cy0 + ch - ro,
		ro,
		pi / 2,
		pi,
	)
	cr.line_to(
		cx0,
		cy0 + ro,
	)
	# up left corner:
	cr.arc(
		cx0 + ro,
		cy0 + ro,
		ro,
		pi,
		3 * pi / 2,
	)
	# ## Inline:
	if ri == 0:
		cr.move_to(
			cx0 + d,
			cy0 + d,
		)
		cr.line_to(
			cx0 + d,
			cy0 + ch - d,
		)
		cr.line_to(
			cx0 + cw - d,
			cy0 + ch - d,
		)
		cr.line_to(
			cx0 + cw - d,
			cy0 + d,
		)
		cr.line_to(
			cx0 + d,
			cy0 + d,
		)
	else:
		cr.move_to(  # or line_to
			cy0 + d,
			cx0 + ro,
		)
		# up left corner:
		cr.arc_negative(
			cx0 + ro,
			cy0 + ro,
			ri,
			3 * pi / 2,
			pi,
		)
		cr.line_to(
			cx0 + d,
			cy0 + ch - ro,
		)
		# down left:
		cr.arc_negative(
			cx0 + ro,
			cy0 + ch - ro,
			ri,
			pi,
			pi / 2,
		)
		cr.line_to(
			cx0 + cw - ro,
			cy0 + ch - d,
		)
		# down right:
		cr.arc_negative(
			cx0 + cw - ro,
			cy0 + ch - ro,
			ri,
			pi / 2,
			0,
		)
		cr.line_to(
			cx0 + cw - d,
			cy0 + ro,
		)
		# up right:
		cr.arc_negative(
			cx0 + cw - ro,
			cy0 + ro,
			ri,
			2 * pi,
			3 * pi / 2,
		)
		cr.line_to(
			cx0 + ro,
			cy0 + d,
		)
	cr.close_path()


def drawCircle(cr, cx, cy, r):
	drawRoundedRect(
		cr,
		cx - r,
		cy - r,
		r * 2,
		r * 2,
		r,
	)


def drawCircleOutline(cr, cx, cy, r, d):
	drawOutlineRoundedRect(
		cr,
		cx - r,
		cy - r,
		r * 2,
		r * 2,
		r,
		d,
	)


def goAngle(x0, y0, angle, length):
	return x0 + cos(angle) * length, y0 + sin(angle) * length


def drawLineLengthAngle(cr, xs, ys, length, angle, d):
	xe, ye = goAngle(xs, ys, angle, length)
	##
	x1, y1 = goAngle(xs, ys, angle - pi / 2.0, d / 2.0)
	x2, y2 = goAngle(xs, ys, angle + pi / 2.0, d / 2.0)
	x3, y3 = goAngle(xe, ye, angle + pi / 2.0, d / 2.0)
	x4, y4 = goAngle(xe, ye, angle - pi / 2.0, d / 2.0)
	##
	cr.move_to(x1, y1)
	cr.line_to(x2, y2)
	cr.line_to(x3, y3)
	cr.line_to(x4, y4)
	cr.close_path()


def drawArcOutline(cr, xc, yc, r, d, a0, a1):
	"""
		cr: cairo context
		xc, yc: coordinates of center
		r: outer radius
		d: outline width (r - ri)
		a0: start angle (radians)
		a1: end angle (radians)
	"""
	x1, y1 = goAngle(xc, yc, a0, r - d)
	x2, y2 = goAngle(xc, yc, a1, r - d)
	x3, y3 = goAngle(xc, yc, a1, r)
	x4, y4 = goAngle(xc, yc, a0, r)
	####
	cr.move_to(x1, y1)
	cr.arc(xc, yc, r - d, a0, a1)
	#cr.move_to(x2, y2)
	cr.line_to(x3, y3)
	cr.arc_negative(xc, yc, r, a1, a0)
	#cr.move_to(x4, y4)
	#cr.line_to(x1, y1)

	cr.close_path()


class BaseButton(object):
	def __init__(
		self,
		onPress=None,
		onRelease=None,
		x=None,
		y=None,
		xalign="left",
		yalign="top",
		autoDir=True,
		opacity=1.0,  # earase the background drawing, only preserving bgColor
	):
		if x is None:
			raise ValueError("x is not given")
		if y is None:
			raise ValueError("y is not given")

		if x < 0 and xalign != "center":
			raise ValueError(f"invalid x={x}, xalign={xalign}")
		if y < 0 and yalign != "center":
			raise ValueError(f"invalid y={y}, yalign={yalign}")
		if xalign not in ("left", "right", "center"):
			raise ValueError(f"invalid xalign={xalign}")
		if yalign not in ("top", "buttom", "center"):
			raise ValueError(f"invalid yalign={yalign}")

		self.onPress = onPress
		self.onRelease = onRelease
		self.x = x
		self.y = y
		self.xalign = xalign
		self.yalign = yalign
		self.autoDir = autoDir
		self.opacity = opacity

		self.width = None
		self.height = None

	def setSize(self, width, height):
		self.width = width
		self.height = height

	def opposite(self, align):
		if align == "left":
			return "right"
		if align == "right":
			return "left"
		if align == "top":
			return "buttom"
		if align == "buttom":
			return "top"
		return align

	def getAbsPos(self, w, h):
		x = self.x
		y = self.y
		xalign = self.xalign
		yalign = self.yalign
		if self.autoDir and rtl:
			xalign = self.opposite(xalign)
		if xalign == "right":
			x = w - self.width - x
		elif xalign == "center":
			x = (w - self.width) / 2.0 + x
		if yalign == "buttom":
			y = h - self.height - y
		elif yalign == "center":
			y = (h - self.height) / 2.0 + y
		return (x, y)

	def contains(self, px, py, w, h):
		x, y = self.getAbsPos(w, h)
		return (
			x <= px < x + self.width
			and
			y <= py < y + self.height
		)

	def draw(self, cr, w, h, bgColor=None):
		raise NotImplementedError


class SVGButton(BaseButton):
	def __init__(
		self,
		imageName="",
		iconSize=16,
		**kwargs
	):
		BaseButton.__init__(self, **kwargs)

		if not imageName:
			raise ValueError("imageName is given")
		self.imageName = imageName
		pixbuf = pixbufFromSvgFile(imageName, iconSize)

		# we assume that svg image is square
		self.setSize(iconSize, iconSize)

		self.iconSize = iconSize
		self.pixbuf = pixbuf

	def getPixbuf(self, bgColor: Optional[Tuple[int, int, int]]):
		if self.opacity == 1.0:
			return self.pixbuf
		# now we have transparency
		if bgColor is None:
			log.info(f"Button.getPixbuf: opacity={opacity}, but no bgColor")
			return self.pixbuf

		r, g, b = bgColor[:3]
		bgColorInt = rgbToInt(r, g, b)
		return self.pixbuf.composite_color_simple(
			self.width, self.height,  # dest_width, dest_height
			GdkPixbuf.InterpType.BILINEAR,  # interp_type
			round(self.opacity * 255),  # overall_alpha: int: 0..255
			8,
			bgColorInt,
			bgColorInt,
		)

	def draw(self, cr, w, h, bgColor=None):
		x, y = self.getAbsPos(w, h)
		gdk.cairo_set_source_pixbuf(
			cr,
			self.getPixbuf(bgColor),
			x,
			y,
		)
		cr.rectangle(x, y, self.width, self.height)
		cr.fill()

	def __repr__(self):
		return (
			f"SVGButton({self.imageName!r}, {self.onPress.__name__!r}, " +
			f"{self.x!r}, {self.y!r}, {self.autoDir!r})"
		)



class Button(BaseButton):
	def __init__(
		self,
		imageName="",
		iconName="",
		iconSize=0,
		**kwargs
	):
		BaseButton.__init__(self, **kwargs)

		shouldResize = True

		if iconName:
			self.imageName = iconName
			if iconSize == 0:
				iconSize = 16
			# GdkPixbuf.Pixbuf.new_from_stock is removed
			# gtk.Widget.render_icon_pixbuf: Deprecated since version 3.10:
			# 		Use Gtk.IconTheme.load_icon()
			pixbuf = gtk.IconTheme.get_default().load_icon(
				iconName,
				iconSize,
				0, # Gtk.IconLookupFlags
			)
		else:
			if not imageName:
				raise ValueError("no imageName nor iconName were given")
			self.imageName = imageName
			if imageName.endswith(".svg"):
				if iconSize == 0:
					iconSize = 16
				shouldResize = False
				pixbuf = pixbufFromSvgFile(imageName, iconSize)
			else:
				pixbuf = GdkPixbuf.Pixbuf.new_from_file(join(pixDir, imageName))

		if shouldResize and iconSize != 0:  # need to resize
			pixbuf = pixbuf.scale_simple(
				iconSize,
				iconSize,
				GdkPixbuf.InterpType.BILINEAR,
			)

		# the actual/final width and height of pixbuf/button
		width, height = pixbuf.get_width(), pixbuf.get_height()
		# width, height = iconSize, iconSize
		self.setSize(width, height)

		self.iconSize = iconSize
		self.pixbuf = pixbuf

	def getPixbuf(self, bgColor: Optional[Tuple[int, int, int]]):
		if self.opacity == 1.0:
			return self.pixbuf
		# now we have transparency
		if bgColor is None:
			log.info(f"Button.getPixbuf: opacity={opacity}, but no bgColor")
			return self.pixbuf

		r, g, b = bgColor[:3]
		bgColorInt = rgbToInt(r, g, b)
		return self.pixbuf.composite_color_simple(
			self.width, self.height,  # dest_width, dest_height
			GdkPixbuf.InterpType.BILINEAR,  # interp_type
			round(self.opacity * 255),  # overall_alpha: int: 0..255
			8,
			bgColorInt,
			bgColorInt,
		)

	def draw(self, cr, w, h, bgColor=None):
		x, y = self.getAbsPos(w, h)
		gdk.cairo_set_source_pixbuf(
			cr,
			self.getPixbuf(bgColor),
			x,
			y,
		)
		cr.rectangle(x, y, self.width, self.height)
		cr.fill()

	def __repr__(self):
		return (
			f"Button({self.imageName!r}, {self.onPress.__name__!r}, " +
			f"{self.x!r}, {self.y!r}, {self.autoDir!r})"
		)


