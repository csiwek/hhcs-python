#!/usr/bin/python
import Adafruit_BBIO.GPIO as GPIO
import time
import sys, os, string
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/modules/')
import pyownet.protocol
class Engine():

	def __init__ (self,l,c):	
#		GPIO.setup("P8_16", GPIO.OUT)
		self.l = l
		self.c = c
		l.info("Initialized Engine")
		self.ow = pyownet.protocol.proxy(host="127.0.0.1", port=4304)
#	PWM.start("P8_16", 50)
	def loop(self):
		while self.c.ContinueLoop:
			#l.debug("tick %d\n" % c.ContinueLoop)
		#GPIO.output("P8_16", GPIO.HIGH)
#		#time.sleep(0.0001)
			#GPIO.output("P8_16", GPIO.LOW)
			s = self.ow.read('/28.9521EA030000/temperature')
			p = s.strip()
			self.c.Sensor0_temp = float(p)
			print p
			time.sleep(1)
	def __del__(self):
		self.l.info("Cleaning up Engine")
