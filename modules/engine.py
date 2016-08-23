#!/usr/bin/python
import Adafruit_BBIO.GPIO as GPIO
import time
import sys, os, string
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/modules/')
import pyownet.protocol
class Engine():

	def __init__ (self,l,c, config):	
		self.l = l
		self.c = c
		self.config = config
		GPIO.setup(self.config.get('gpio', 'heartbeat_led'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_1'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_2'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_3'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_4'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_5'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_6'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_7'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_8'), GPIO.OUT)
		l.info("Initialized Engine")
		self.ow = pyownet.protocol.proxy(host="127.0.0.1", port=4304)
#	PWM.start("P8_16", 50)
	def loop(self):
		while self.c.ContinueLoop:
			self.l.debug("tick %d\n" % self.c.ContinueLoop)
			GPIO.output(self.config.get('gpio', 'heartbeat_led'), GPIO.HIGH)
			time.sleep(0.01)
			GPIO.output(self.config.get('gpio', 'heartbeat_led'), GPIO.LOW)
			GPIO.output(self.config.get('gpio', 'relay_1'), GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_2'), GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_3'), GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_4'), GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_5'), GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_6'), GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_7'), GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_8'), GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_1'), GPIO.LOW)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_2'), GPIO.LOW)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_3'), GPIO.LOW)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_4'), GPIO.LOW)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_5'), GPIO.LOW)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_6'), GPIO.LOW)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_7'), GPIO.LOW)
			time.sleep(0.05)
			GPIO.output(self.config.get('gpio', 'relay_8'), GPIO.LOW)
			time.sleep(0.05)
			try:
				s = self.ow.read('/28.9521EA030000/temperature')
				p = s.strip()
				self.c.Sensor0_temp = float(p)
				print p
			except:
				self.l.info("No Sensor was found")
			time.sleep(self.config.getint('engine', 'loop_interval'))
	def __del__(self):
		self.l.info("Cleaning up Engine")
		GPIO.output(self.config.get('gpio', 'heartbeat_led'), GPIO.LOW)
		GPIO.output(self.config.get('gpio', 'relay_1'), GPIO.LOW)
		GPIO.output(self.config.get('gpio', 'relay_2'), GPIO.LOW)
		GPIO.output(self.config.get('gpio', 'relay_3'), GPIO.LOW)
		GPIO.output(self.config.get('gpio', 'relay_4'), GPIO.LOW)
		GPIO.output(self.config.get('gpio', 'relay_5'), GPIO.LOW)
		GPIO.output(self.config.get('gpio', 'relay_6'), GPIO.LOW)
		GPIO.output(self.config.get('gpio', 'relay_7'), GPIO.LOW)
		GPIO.output(self.config.get('gpio', 'relay_8'), GPIO.LOW)

