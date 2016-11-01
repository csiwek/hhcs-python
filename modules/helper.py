class Helper():
	def __init__(self, log, config, cache):
		self.log = log
		self.config = config
		self.cache = cache


	def getSensorsList(self):
		SensorList = {}
		for section in self.config.sections():
			if section[:7] == "sensor_":
				sensorID = section[7:]
				self.log.info("found sensor %s " % sensorID)
				items = self.config.items(section)
				itemsDict = {}
				for item in items:
					itemsDict[item[0]] = item[1]
					SensorList[sensorID] = itemsDict["name"]
		return SensorList	

	def getSensorsListAvailable(self):
		SensorList = {}
		for section in self.config.sections():
			if section[:7] == "sensor_":
				sensorID = section[7:]
				self.log.info("found sensor %s " % sensorID)
				items = self.config.items(section)
				itemsDict = {}
				for item in items:
					itemsDict[item[0]] = item[1]
					zoneMatched=0
					for ZoneSection in self.config.sections():
						if ZoneSection[:5] == "zone_":
							items = self.config.items(ZoneSection)
							itemsDict2 = {}
							for item in items:
								itemsDict2[item[0]] = item[1]
							self.log.info("%s ==: %s ? " % (itemsDict2["sensor"], sensorID))
							if itemsDict2["sensor"] == sensorID:
								zoneMatched=1
								self.log.debug("Sensor already assinged to zone : %s " % itemsDict2["name"])
								break
					if not zoneMatched:
						SensorList[sensorID] = itemsDict["name"]
			
		return SensorList	

	def getSensorById(self, sensorID):
		items = self.config.items('sensor_' + sensorID)
		itemsDict2 = {}
		for item in items:
			 itemsDict2[item[0]] = item[1]
		return itemsDict2

	def getZoneById(self, zoneID):
		items = self.config.items('zone_' + zoneID)
		itemsDict2 = {}
		for item in items:
			 itemsDict2[item[0]] = item[1]
		return itemsDict2
	


	def getSensorsListUnassigned(self):
		import pyownet.protocol
		ow = pyownet.protocol.proxy(host="127.0.0.1", port=4304)
		HWsensors = ow.dir()
		HWsensorslist = {}
		for HWsensor in HWsensors:
			print "HW SENSOR: "
			itemsDict = {}
			itemsDict["name"] = ""
			itemsDict["current_temp"] = float(0)
			itemsDict["address"] = ""
			itemsDict["sensor_id"] = ""
			HWsensorslist[HWsensor] = itemsDict
			for section in self.config.sections():
				if section[:7] == "sensor_":
					sensorID = section[7:]
					self.log.info("found sensor %s " % sensorID)
					items = self.config.items(section)
					itemsDict = {}
					for item in items:
						itemsDict[item[0]] = item[1]
					if itemsDict["address"] == HWsensor:
						itemsDict["current_temp"] = float(22)
						itemsDict["sensor_id"] = sensorID
						print "=================== FOUND SENSOR:  " + HWsensor	
						HWsensorslist[HWsensor] = itemsDict
		return HWsensorslist	


	def getRelaysUnassigned(self):
		RelaysUn =[]
		relays=self.config.options('gpio')
		for relay in relays:
			zoneMatched=0
			self.log.debug("checking relay: %s " % relay[:6])
			if relay[:6] == "relay_":
				for section in self.config.sections():
					self.log.debug("checking section: %s " % section[:5])
					if section[:5] == "zone_":
						items = self.config.items(section)
						itemsDict = {}
						for item in items:
							itemsDict[item[0]] = item[1]
						self.log.debug("%s ==: %s ? " % (itemsDict["relay"], relay))
						if itemsDict["relay"] == relay:
							zoneMatched=1
							self.log.debug("Relay already assinged to zone : %s " % itemsDict["name"])
							break
				if not zoneMatched:
					RelaysUn.append(relay)
		return RelaysUn


	def getOptions(self):
		options = {}
		try:
			items = self.config.items('options')
			for item in items:
				options[item[0]] = item[1]
			return options
		except:
			self.log.debug("No optionns section found")
			options = {'pump_enabled': 0,
				'pump_delay': 0,
				'pump_delay': 0,
				'return_sensor': '',
				'comfort_floor_enabled': 0,
				'comfort_floor_temp':30,
				'min_flow_temp': 40,
				'max_flow_temp': 50,
				'pump_relay': '',
				'boiler_relay': ''
			}		
			return options
			
			
