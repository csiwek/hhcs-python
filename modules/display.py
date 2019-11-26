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
#import Adafruit_GPIO as GPIO
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import time
import psutil
from datetime import time as TIME
from datetime import datetime
import random
import socket
import fcntl
import struct
import sys, os

class handler():
	def __init__(self,l,c, config):
		self.cache=c
		self.config = config
		if int(config.get('display', 'enabled')) != 1:
			return

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
		try:
			self.disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
		except:
			l.error("No Display found. ")
			config.set('display', 'enabled',0)
			sys.exit(0)
		# Initialize display.
		self.disp.begin()

		# Clear the display to a red background.
		# Can pass any tuple of red, green, blue values (from 0 to 255 each).
		self.disp.clear((0, 0, 0))

		# Alternatively can clear to a black screen by calling:
		# disp.clear()
		self.draw = self.disp.draw()


		# Load default font.
		#font = ImageFont.load_default()
		self.font = ImageFont.truetype(os.path.dirname(os.path.realpath(__file__)) + '/../ArialBold.ttf', 14)
		# Alternatively load a TTF font.
		# Some other nice fonts to try: http://www.dafont.com/bitmap.php
		#font = ImageFont.truetype('Minecraftia.ttf', 16)

		# Define a function to create rotated text.  Unfortunately PIL doesn't have good
		# native support for rotated fonts, but this function can be used to make a 
		# text image and rotate it so it's easy to paste in the buffer.
		t = datetime.now()
		self.tbef = t.strftime("%H:%M:%S")
		self.textToDisp = ""
		l.info("Display Initialized")	
		self.l = l
		self.LoopRunning=1
		self.loopNumber = 0
		self.ip_address = False

	def draw_rotated_text(self, image, text, position, angle, font, fill=(255,255,255)):
		if int(self.config.get('display', 'enabled')) != 1:
			return

		# Get rendered font width and height.
		position_top, position_right = position
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
		image.paste(rotated, (position_top, 320- position_right - width), rotated)
		del draw
		del textdraw
		del rotated
		del textimage
		del image

	def clear(self, color=(0,0,0)):
		"""Clear the image buffer to the specified RGB color (default black)."""
		width, height = self.disp.buffer.size
		#self.buffer.putdata([color]_(width_height))
		draw = ImageDraw.Draw(self.disp.buffer)
		draw.rectangle([(0,0),(width,height)], fill=color)
		del draw
			

# Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
	def generate(self):
		if int(self.config.get('display', 'enabled')) != 1:
			return
		if self.loopNumber == 5:
			self.loopNumber = 0
		t = datetime.now()
		tnow = t.strftime("%H:%M:%S")
		if not self.cache.ContinueLoop:
			return 0
		if self.tbef != tnow:
			# Top BAr
			text = "CPU: %s%%" % (psutil.cpu_percent())
			self.draw_rotated_text(self.disp.buffer, text, (2, 240), 90, self.font, fill=(255,255,255))
			self.draw_rotated_text(self.disp.buffer, 'Welcome to HHCS', (2, 100), 90, self.font, fill=(255,255,255))
			self.draw_rotated_text(self.disp.buffer, tnow , (2, 10), 90, self.font, fill=(255,0,0))
			self.draw.line((20, 1, 20, 320), fill=(255,255,255))
			n = 0
			ZoneLine = "Zone %d  %s %sC" % ((n), self.cache.Sensor0_temp, u'\u00b0')
			zoneslist = {}
			for section in self.config.sections():
				if section[:5] == "zone_":
					self.l.debug("found zone %s " % section[5:])
					itemsDict = {}
					itemsDict["current_temperature"] = self.cache.getValue(section[5:] + "_zone_current_temp") 	
					itemsDict["current_direction"] = self.cache.getValue(section[5:] + "_zone_direction")
					items = self.config.items(section)
					for item in items:
						itemsDict[item[0]] = item[1]
					ZoneLine = "'%s'" % (itemsDict["name"]) 	
					TempLine = " : %.2f  %sC" % (itemsDict["current_temperature"],  u'\u00b0') 	
					self.draw_rotated_text(self.disp.buffer, ZoneLine, (45+(n*20), 10) , 90, self.font, fill=(255,255,255))
					self.draw_rotated_text(self.disp.buffer, TempLine, (45+(n*20), 120) , 90, self.font, fill=(255,255,255))
					self.draw_rotated_text(self.disp.buffer, itemsDict["current_direction"], (45+(n*20), 200) , 90, self.font, fill=(255,255,255))
					n = n +1
			
		#	while n < 8:
		#		ZoneLine = "Zone %d  %.2f %sC" % ((n+1), random.uniform(19.0,25.0), u'\u00b0')
		#		#self.draw_rotated_text(self.disp.buffer, self.textToDisp , (100, 120), 90, self.font, fill=(255,255,0))
		#		self.draw_rotated_text(self.disp.buffer, ZoneLine, (45+(n*20), 200), 90, self.font, fill=(255,255,255))
		#		n = n+1
	
			if self.loopNumber == 0:	
				try:
					self.ip_address = self.get_ip_address("eth0")
				except:
					seld.ip_address = False
			

			if not self.ip_address:
				self.draw_rotated_text(self.disp.buffer, "No IP address! Connect HHCS to your router!", (200, 10) , 90, self.font, fill=(255,255,255))	
			else:
				self.draw_rotated_text(self.disp.buffer, "Web admin http://" + self.ip_address , (200, 10) , 90, self.font, fill=(255,255,255))	
				self.draw_rotated_text(self.disp.buffer, "User name:" + self.config.get('web', 'admin_username') + "  Password: " + self.config.get('web', 'admin_password') , (220, 10) , 90, self.font, fill=(255,255,255))	
			self.disp.display()
			self.clear()
			self.tbef = tnow

		self.loopNumber += 1
		return 0

	def __del__(self):
		if int(self.config.get('display', 'enabled')) != 1:
			return
		self.l.info("Destructor called")
		self.ExitText()

	def ExitText(self):
		if int(self.config.get('display', 'enabled')) != 1:
			return
		self.l.info("Exit function Called ")
		self.disp.clear()
		self.draw_rotated_text(self.disp.buffer, 'Goodbye', (80, 20), 90,  ImageFont.truetype('DejaVuSans.ttf', 60), fill=(255,255,255))
		self.disp.display()

	def get_ip_address(self, ifname):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		return socket.inet_ntoa(fcntl.ioctl(
			s.fileno(),
			0x8915,  # SIOCGIFADDR
			 struct.pack('256s', ifname[:15])
		)[20:24])

