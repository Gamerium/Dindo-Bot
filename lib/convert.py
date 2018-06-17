# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GdkPixbuf
from PIL import Image

# Convert GdkPixbuf to Pillow image
def pixbuf2image(pixbuf):
	data = pixbuf.get_pixbufels()
	width = pixbuf.props.width
	height = pixbuf.props.height
	stride = pixbuf.props.rowstride
	mode = 'RGB'
	if pixbuf.props.has_alpha == True:
		mode = 'RGBA'
	image = Image.frombytes(mode, (width, height), data, 'raw', mode, stride)
	return image

# Convert Pillow image to GdkPixbuf
def image2pixbuf(image):
	data = image.tobytes()
	w, h = image.size
	data = GLib.Bytes.new(data)
	pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB, False, 8, w, h, w * 3)
	return pixbuf
