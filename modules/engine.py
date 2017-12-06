#!/usr/bin/python



import Adafruit_BBIO.GPIO as GPIO
import time
import sys, os, string
import pprint
import helper

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/modules/')
import pyownet.protocol
class Engine():

	def __init__ (self,l,c, config):	
		self.l = l
		self.c = c
		self.config = config
		self.hlp = helper.Helper(l,config,c)
		GPIO.setup(self.config.get('gpio', 'heartbeat_led'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_1'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_2'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_3'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_4'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_5'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_6'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_7'), GPIO.OUT)
		GPIO.setup(self.config.get('gpio', 'relay_8'), GPIO.OUT)
		self.ow = pyownet.protocol.proxy(host="127.0.0.1", port=4304)
		for section in config.sections():
			if section[:5] == "zone_":
				zone = section[5:]
				zoneInfo = self.hlp.getZoneById(zone)
				l.info("Setting zone direction to INIT: %s " % zoneInfo['name'])
				#l.info("Setting zone direction to INIT: %s " % zone+"_zone_direction")
				c.setValue(zone + "_zone_direction", "INIT")	
				self.c.setValue(zone + "_zone_current_temp", float(0))	
		l.info("Initialized Engine")
		#self.test_relays()
	
#	PWM.start("P8_16", 50)
	def loop(self):
		boiler_enabled = 0
		boiler_relay_name = self.config.get('options', 'boiler_relay')
		pump_enabled = 0
		pump_relay_name = self.config.get('options', 'pump_relay')
		while self.c.ContinueLoop:
			self.l.debug("tick %d\n" % self.c.ContinueLoop)
			heating_required = False
			for section in self.config.sections():
				active_zone_count = 0
				if section[:5] == "zone_":
					zone = section[5:]
					self.l.debug("found zone %s " % zone)
					zoneInfo = self.hlp.getZoneById(zone)
					zone_temperature = float(self.config.get(section, 'temperature'))
					zone_hysteresis = float(self.config.get(section, 'hysteresis'))
					zone_sensor_name = self.config.get(section, 'sensor')
					zone_sensor = self.config.get('sensor_' + zone_sensor_name, 'address')
					zone_relay_name = self.config.get(section, 'relay')
					zone_enabled = self.config.getboolean(section, 'enabled')
					zone_direction = self.c.getValue(zone + "_zone_direction")
					if not zone_enabled:
						if zone_direction == "UP":
							self.l.info("Zone '%s' is disabled but it is currently in direction 'UP'. Disabling heating for this zone" % zone)
							self.c.setValue(zone + "_zone_direction", "DOWN")
							self.turn_relay(zone_relay_name, 0)
					
	
					try:
						self.l.debug("Trying to read sensor: "  + zone_sensor_name)
						sensor_temperature = float(self.ow.read(zone_sensor + 'temperature').strip())
						self.c.setValue(zone + "_zone_current_temp", sensor_temperature)
						self.l.info("Sensor '"  + zone_sensor_name + "' => '" + zone_sensor + "' temperature %f" % sensor_temperature)	
					except:
						self.l.error("Reading sensor has failed : "  + zone_sensor_name)
						continue

					
					zone_direction = self.c.getValue(zone + "_zone_direction")
					self.l.debug("Zone '" + zoneInfo['name']  + "' direction is: "+  str(zone_direction))						
					if zone_direction == "DOWN":
						if sensor_temperature <= (zone_temperature - zone_hysteresis/2):
							self.l.info("Current direction DOWN. Enabling heating in zone '"  + zone + "' sensor_temp: %f <=  requested zone_temp %f" % (sensor_temperature, (zone_temperature - zone_hysteresis/2)))	
							heating_required = True
							self.c.setValue(zone + "_zone_direction", "UP")
							self.turn_relay(zone_relay_name, 1)
							active_zone_count +=1
					elif zone_direction == "UP":
						if sensor_temperature >= (zone_temperature + zone_hysteresis/2):
							self.l.info("Current direction UP. Disabing heating in zone '"  + zone + "' sensor_temp: %f >=  requested zone_temp %f" % (sensor_temperature, (zone_temperature + zone_hysteresis/2)))	
							self.c.setValue(zone + "_zone_direction", "DOWN")
							self.turn_relay(zone_relay_name, 0)
							active_zone_count -=1
					elif zone_direction == "INIT":
						if sensor_temperature < (zone_temperature - zone_hysteresis/2):
							self.l.info("Current direction INIT. Changing Direction to UP in zone '"  + zone + "' sensor_temp: %f <  requested zone_temp %f" % (sensor_temperature, (zone_temperature - zone_hysteresis/2)))	
							self.c.setValue(zone + "_zone_direction", "UP")
							self.turn_relay(zone_relay_name, 1)
							active_zone_count +=1
						elif sensor_temperature >= (zone_temperature - zone_hysteresis/2):
							self.l.info("Current direction INIT. Changing Direction to DOWN in zone '"  + zone + "' sensor_temp: %f >=  requested zone_temp %f" % (sensor_temperature, (zone_temperature - zone_hysteresis/2)))	
							self.c.setValue(zone + "_zone_direction", "DOWN")
							active_zone_count -=1
			if boiler_enabled == 0 and active_zone_count > 0:
				self.l.debug("Heating requested by " + str(active_zone_count) + " Zones. Enabling boiler")
				self.turn_relay(boiler_relay_name, 1)
				boiler_enabled =1
			elif boiler_enabled ==1 and active_zone_count ==0:
				self.l.debug("Heating requested by " + str(active_zone_count) + " Zones. Disabling boiler")
				self.turn_relay(boiler_relay_name, 0)
				boiler_enabled =0
			# Control pump relay
			if self.config.getint('options', 'pump_enabled') == 1:
					if pump_enabled == 0 and boiler_enabled == 1:
						self.l.debug("Enabling pump")
						self.turn_relay(pump_relay_name, 1)
					elif pump_enabled ==1 and boiler_enabled ==0:
						self.turn_relay(pump_relay_name, 0)
						self.l.debug("Disabling pump")		
			time.sleep(self.config.getint('engine', 'loop_interval'))




	def turn_relay(self, relay, state):
		relay_state = self.c.getValue(relay + "_relay_state")
		gpio_state = self.c.getValue(self.config.get('gpio',relay) + "_gpio_state")
		if state!=relay_state:
			if state == 0:
				GPIO.output(self.config.get('gpio', relay), GPIO.LOW)
				self.l.info("Disabling relay: "  + relay)
			elif state == 1:
				GPIO.output(self.config.get('gpio', relay), GPIO.HIGH)
				self.l.info("Enabling relay: "  + relay)
			self.c.setValue(relay + "_relay_state", state)		
			self.c.setValue(relay + "_gpio_state", state)		
		else:
			self.l.debug("Relay: '"  + relay + "' in the same state. Leaving as is" )


	
	def test_relays(self):
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

