#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import Image
import ImageDraw
import ImageFont

import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import time
import psutil
from datetime import time as TIME
from datetime import datetime




class handler():
	def __init__(self):


		# Raspberry Pi configuration.
		#DC = 18
		#RST = 23
		#SPI_PORT = 0
		#SPI_DEVICE = 0
		# BeagleBone Black configuration.
		DC = 'P9_15'
		RST = 'P9_12'
		SPI_PORT = 1
		SPI_DEVICE = 0

		# Create TFT LCD display class.
		self.disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=128000000))

		# Initialize display.
		self.disp.begin()

		# Clear the display to a red background.
		# Can pass any tuple of red, green, blue values (from 0 to 255 each).
		self.disp.clear((0, 0, 0))

		# Alternatively can clear to a black screen by calling:
		# disp.clear()
		draw = self.disp.draw()


		# Load default font.
		#font = ImageFont.load_default()
		self.font = ImageFont.truetype('ArialBold.ttf', 20)
		# Alternatively load a TTF font.
		# Some other nice fonts to try: http://www.dafont.com/bitmap.php
		#font = ImageFont.truetype('Minecraftia.ttf', 16)

		# Define a function to create rotated text.  Unfortunately PIL doesn't have good
		# native support for rotated fonts, but this function can be used to make a 
		# text image and rotate it so it's easy to paste in the buffer.
		self.A = 1000
		t = datetime.now()
		self.tbef = t.strftime("%H:%M:%S")
		self.textToDisp = ""

	def draw_rotated_text(self, image, text, position, angle, font, fill=(255,255,255)):
		# Get rendered font width and height.
		draw = ImageDraw.Draw(image)
		width, height = draw.textsize(text, font=font)
		# Create a new image with transparent background to store the text.
		textimage = Image.new('RGBA', (width, height), (0,0,0,0))
		# Render the text.
		textdraw = ImageDraw.Draw(textimage)
		textdraw.text((0,0), text, font=font, fill=fill)
		# Rotate the text image.
		rotated = textimage.rotate(angle, expand=1)
		# Paste the text into the image, using it as a mask for transparency.
		image.paste(rotated, position, rotated)


	

# Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
	def generate(self):
		t = datetime.now()
		tnow = t.strftime("%H:%M:%S")
		if self.tbef != tnow:
			self.draw_rotated_text(self.disp.buffer, self.textToDisp , (100, 120), 90, self.font, fill=(255,255,0))
			self.draw_rotated_text(self.disp.buffer, tnow , (130, 120), 90, self.font, fill=(255,0,0))
			self.draw_rotated_text(self.disp.buffer, 'Hello World!', (150, 120), 90, self.font, fill=(255,255,255))
			text = "CPU usage: %s Step nr: %d " % (psutil.cpu_percent(), self.A)
			self.draw_rotated_text(self.disp.buffer, text, (180, 20), 90, self.font, fill=(255,255,255))
			self.disp.display()
			self.disp.clear()
			self.tbef = tnow
		self.A=self.A+1
		return 0
