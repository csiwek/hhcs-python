#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import sys, os, string
from twisted.web import server, resource
from twisted.internet import threads, reactor, defer
from twisted.web.server import Session
from twisted.python.components import registerAdapter
import cgi
import pprint
#from twisted.web.error import NoResource

#from concurrent.futures.thread import ThreadPoolExecutor
import pprint
from tornado import template
from tornado import escape
import uuid
import time
import re
import helper

class Dispatcher(resource.Resource):
    def __init__(self, log, config, cache):
       	resource.Resource.__init__(self)
	self.log = log
	self.config = config
	self.cache = cache
	
    def getChild(self, name, request):
	if request.path=="/":
		return ProcessIndex(name, self.log, self.config, self.cache)
	elif request.path=="/zones" or request.path=="/zones/add":
		return ProcessZones(name, self.log, self.config, self.cache)
	elif request.path=="/towel" or request.path=="/towel/add":
		return ProcessTowel(name, self.log, self.config, self.cache)
	elif re.match(r"^/towel/delete/(.*)$", request.path, flags=0):
		return ProcessTowel(name, self.log, self.config, self.cache)
	elif request.path=="/sensors":
		return ProcessSensors(name, self.log, self.config, self.cache)
	elif re.match(r"^/sensors/assign/(.*)$", request.path, flags=0):
		return ProcessSensors(name, self.log, self.config, self.cache)
	elif re.match(r"^/sensors/assign$", request.path, flags=0):
		return ProcessSensors(name, self.log, self.config, self.cache)
	elif re.match(r"^/sensors/delete/(.*)$", request.path, flags=0):
		return ProcessSensors(name, self.log, self.config, self.cache)
	elif re.match(r"^/zones/delete/(.*)$", request.path, flags=0):
		return ProcessZoneDelete(name, self.log, self.config, self.cache)
	elif re.match(r"^/zones/edit/(.*)$", request.path, flags=0):
		return ProcessZoneEdit(name, self.log, self.config, self.cache)
	elif request.path=="/login":
		return ProcessLogin(name, self.log, self.config, self.cache)
	elif request.path=="/options":
		return ProcessOptions(name, self.log, self.config, self.cache)
	
	else:
		return ProcessError(request.path, self.log, self.config, self.cache)
		#return NoResource("oops...")
		#return self.Nothing(request)
    def Nothing(self, request):
        request.setResponseCode(404)
	return "<html><body>Page not found.</body></html>"  



class ProcessError(resource.Resource):
    isLeaf = True
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache
	self.log.info("Initialising ProcessError")


    def render_GET(self, request):
	self.log.info("No handler found for %s . replying 404" % self.name)
	request.setResponseCode(404, message="Not Found")
	return "<html><body>Page not found.</body></html>"  

    def render(self, request):
	self.log.info("No handler found for %s . replying 404" % self.name)
	request.setResponseCode(404, message="Not Found")
	return "<html><body>Page not found.</body></html>"  


class ProcessLogin(resource.Resource):
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache
	self.session = None

    def render_GET(self, request):
	#request.getSession().expire()
	self.session = SessionManager(request, self.log)
	self.session.expireSession()
	loader = template.Loader(os.path.dirname(__file__) + "/../" + self.config.get('web', 'template_name'))
	return loader.load("login.html").generate()
	
    def render_POST(self, request):
	self.session = SessionManager(request, self.log)
	self.log.info("Serving POST: %s " % self.name)
	#Session.sessionTimeout 	= 3600
	username = cgi.escape(request.args["username"][0])
	password = cgi.escape(request.args["password"][0])
	self.log.info("User " + username + " entered")
	if self.config.get('web', 'admin_username') == username  and self.config.get('web', 'admin_password') == password:
		self.log.info(" =================   User " + username + " Authenticated")
		#ses = request.getSession()
		ses = self.session.startSession()
		self.cache.setValue(ses + "_user", username)
		request.redirect("/zones")
	else:
		self.log.info("User " + username + " NOT  Authenticated")
		request.redirect("/login")
	request.finish()
	return server.NOT_DONE_YET


class SessionManager:
     def __init__(self, request, log):
	self.session  = request.getSession()
	self.request = request
	self.uuid = None
	self.log = log

     def startSession(self):
	self.uuid = str(uuid.uuid4().get_hex().upper())
	lease = 3600  # 14 days in seconds
	end = time.gmtime(time.time() + lease)
	expires = time.strftime("%a, %d-%b-%Y %T GMT", end)
	self.log.info("Starting Session %s that expires on %s " % (self.uuid, expires))
	self.request.addCookie("HHCS_SESSION", self.uuid, expires=expires, domain=None, path=None, max_age=None, comment=None, secure=None)
	return self.uuid

     def getSession(self):
	sessId = self.request.getCookie("HHCS_SESSION")
	return sessId

     def expireSession(self):
	sessId = self.getSession()
	if sessId != None:
		self.request.addCookie("HHCS_SESSION", sessId, expires=time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(time.time())), domain=None, path=None, max_age=None, comment=None, secure=None)




class ProcessZones(resource.Resource):
    isLeaf=True
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache

    def render_GET(self, request):
	self.log.info("Serving: %s " % self.name)
	self.log.info("reuest: %s " % pprint.pformat(request.getClientIP()))
	hlp = helper.Helper(self.log, self.config, self.cache)
	loader = template.Loader("./" + self.config.get('web', 'template_name'))
	if request.path=="/zones/add":
		return loader.load("zone_add.html").generate(
				sensors=hlp.getSensorsListAvailable(''),
				relays=self.config.options('gpio')
		)


	zoneslist = {}
	for section in self.config.sections():
		if section[:5] == "zone_":
			self.log.info("found zone %s " % section[5:])
			itemsDict = {}
			itemsDict["current_temperature"] = self.cache.getValue(section[5:] + "_zone_current_temp") 	
			itemsDict["current_direction"] = self.cache.getValue(section[5:] + "_zone_direction") 	
			items = self.config.items(section)
			for item in items:
				itemsDict[item[0]] = item[1]
			zoneslist[section[5:]] = itemsDict
	pprint.pprint(zoneslist)
	return loader.load("zones.html").generate(
				sensors=hlp.getSensorsListAvailable(''),
				relays=self.config.options('gpio'),
				zones=zoneslist
				)	


    def render_POST(self, request):
	self.session = SessionManager(request, self.log)
	self.log.info("Serving POST: %s " % self.name)
	#Session.sessionTimeout 	= 3600
	zoneName = cgi.escape(request.args["zonename"][0])
	zoneTemp = float(cgi.escape(request.args["zonetemp"][0]))
	zoneHist = float(cgi.escape(request.args["zonehist"][0]))
	zoneSensor = cgi.escape(request.args["sensor"][0])
	zoneRelay = cgi.escape(request.args["relay"][0])
	zoneEnabled = cgi.escape(request.args["enabled"][0])
	self.log.info("Creating Zone " + zoneName)
	if len(zoneName) > 2:
		import uuid
		zoneId = str(uuid.uuid4())
		section = "zone_" + zoneId
		self.config.add_section(section)
		self.config.set(section, "temperature", zoneTemp)
		self.config.set(section, "name", zoneName)
		self.config.set(section, "relay", zoneRelay)
		self.config.set(section, "sensor", zoneSensor)
		self.config.set(section, "hysteresis", zoneHist)
		self.config.set(section, "enabled", zoneEnabled)
		with open('hhcs.cfg', 'wb') as configfile:
			self.config.write(configfile)	
		self.cache.setValue(zoneId + "_zone_direction", "INIT")
		self.log.info("Zone Created: " + zoneName)
	request.redirect("/zones")
	request.finish()
	return server.NOT_DONE_YET




class ProcessZoneEdit(resource.Resource):
    isLeaf=True
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache

    def render_GET(self, request):
	self.log.info("Serving: %s " % self.name)
	hlp = helper.Helper(self.log, self.config, self.cache)
	self.log.info("reuest: %s " % pprint.pformat(request.getClientIP()))
	m = re.match(r"^/zones/edit/(.*)$", request.path, flags=0)
	loader = template.Loader("./" + self.config.get('web', 'template_name'))
	if m:
		zone_name= m.group(1)
		section = "zone_" + zone_name
		self.log.info("Getting information about zone: %s " % section)
		name = self.config.get(section, 'name')
		zone_temperature = float(self.config.get(section, 'temperature'))
		zone_hysteresis = float(self.config.get(section, 'hysteresis'))
		zone_sensor_name = self.config.get(section, 'sensor')
		zone_enabled = self.config.getboolean(section, 'enabled')
		zone_sensor = self.config.get('sensor_'+zone_sensor_name, 'address')
		zone_relay_name = self.config.get(section, 'relay')
		return loader.load("zone_edit.html").generate(
				name=name,
				zonename=zone_name,
				zone_enabled=zone_enabled,	
				zone_temperature=str(zone_temperature),
				zone_hysteresis=str(zone_hysteresis),
				zone_sensor_name=str(zone_sensor_name),
				zone_sensor=zone_sensor,
				zone_relay_name=zone_relay_name,
				sensors=hlp.getSensorsListAvailable(zone_sensor_name),
				relays=self.config.options('gpio')
				)	


	else:

		request.redirect("/zones")
		request.finish()
		return server.NOT_DONE_YET

    def render_POST(self, request):
	self.session = SessionManager(request, self.log)
	self.log.info("Serving POST: %s " % self.name)
	#Session.sessionTimeout 	= 3600
	m = re.match(r"^/zones/edit/(.*)$", request.path, flags=0)
	zoneId= m.group(1)
	try:
		zoneTemp = float(cgi.escape(request.args["zonetemp"][0]))
		zoneName = cgi.escape(request.args["zonename"][0])
		zoneHist = float(cgi.escape(request.args["zonehist"][0]))
		zoneSensor = cgi.escape(request.args["sensor"][0])
		zoneRelay = cgi.escape(request.args["relay"][0])
		zoneEnabled = cgi.escape(request.args["enabled"][0])
	except:
		request.redirect("/zones/edit/" + zoneId )
		request.finish()
		return server.NOT_DONE_YET

	self.log.info("Updating Zone " + zoneName)
	if len(zoneId) > 2:
		section = "zone_" + zoneId
		self.config.set(section, "name", zoneName)
		self.config.set(section, "temperature", zoneTemp)
		self.config.set(section, "relay", zoneRelay)
		self.config.set(section, "sensor", zoneSensor)
		self.config.set(section, "hysteresis", zoneHist)
		self.config.set(section, "enabled", zoneEnabled)
		with open('hhcs.cfg', 'wb') as configfile:
			self.config.write(configfile)	
		self.log.info("Zone Created: " + zoneId) 
	request.redirect("/zones")
	request.finish()
	return server.NOT_DONE_YET




class ProcessZoneDelete(resource.Resource):
    isLeaf=True
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache

    def render_GET(self, request):
	self.log.info("Serving: %s " % self.name)
	self.log.info("reuest: %s " % pprint.pformat(request.getClientIP()))
	m = re.match(r"^/zones/delete/(.*)$", request.path, flags=0)
	if m:
		zone = "zone_" + m.group(1)
		self.config.remove_section(zone)
	request.redirect("/zones")
	request.finish()
	return server.NOT_DONE_YET




class ProcessIndex(resource.Resource):
    
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache

    def render_GET(self, request):
	self.session = SessionManager(request, self.log)
	self.log.info("Serving: %s " % self.name)
	self.log.info("reuest: %s " % pprint.pformat(request.getClientIP()))
	loader = template.Loader("./" + self.config.get('web', 'template_name'))
	if self.name == "" or self.name=="index.html":
		#session = request.getSession().uid
		session = self.session.getSession()
		if session:
			user = self.cache.getValue(session + "_user")
			if not user:
				request.redirect("/login")
				request.finish()
				return server.NOT_DONE_YET
			else:
				return loader.load("index.html").generate(sid=user)
		else:
			request.redirect("/login")
			request.finish()
			return server.NOT_DONE_YET
	
	elif self.name == "login.html":
		request.getSession().expire()
		self.session.expireSession()
		return loader.load(self.name).generate()
	else:
		return loader.load(self.name).generate()



class ProcessSensors(resource.Resource):
    isLeaf=True
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache

    def render_GET(self, request):
	self.log.info("Serving: %s " % self.name)
	self.log.info("reuest: %s " % pprint.pformat(request.getClientIP()))
	m = re.match(r"^/sensors/delete/(.*)$", request.path, flags=0)
	if m:
		sensor = "sensor_" + m.group(1)
		self.log.info("Removing sensor: : %s " % sensor)
		self.config.remove_section(sensor)
		request.redirect("/sensors")
		request.finish()
		return server.NOT_DONE_YET

	hlp = helper.Helper(self.log, self.config, self.cache)
	HWsensorslist = hlp.getSensorsListUnassigned()

	loader = template.Loader("./" + self.config.get('web', 'template_name'))
	m = re.match(r"^/sensors/assign/(.*)$", request.path, flags=0)
        if m:
		return loader.load("sensor_add.html").generate(
				sensors=self.config.options('sensors'),
				relays=self.config.options('gpio'),
				address=escape.url_unescape(m.group(1))
		)


	sensorslist = {}
	for section in self.config.sections():
		if section[:7] == "sensor_":
			self.log.info("found sensor %s " % section[7:])
			itemsDict = {}
			items = self.config.items(section)
			for item in items:
				itemsDict[item[0]] = item[1]
			sensorslist[section[7:]] = itemsDict
	return loader.load("sensors.html").generate(
				relays=self.config.options('gpio'),
				sensors=HWsensorslist
				)	


    def render_POST(self, request):
	self.session = SessionManager(request, self.log)
	self.log.info("Serving POST: %s " % self.name)
	#Session.sessionTimeout 	= 3600

	if request.path == "/sensors/assign":
		pprint.pprint(request.args)
		try:
			sensorAddress = cgi.escape(request.args["address"][0])
			sensorName = cgi.escape(request.args["sensname"][0])
			sensorType = cgi.escape(request.args["sensor_type"][0])
		except:
			self.log.error("One of form field was empty 1")
			request.redirect("/sensors")
			request.finish()
			return server.NOT_DONE_YET		
	
		if sensorAddress == "" or sensorName == "" or sensorType == "":
			self.log.error("One of form field was empty 2")
			request.redirect("/sensors")
			request.finish()
			return server.NOT_DONE_YET		
	
		import uuid
                sensorID = str(uuid.uuid4())
		section = "sensor_" + sensorID
		self.config.add_section(section)
		self.config.set(section, "name", sensorName)
		self.config.set(section, "address", sensorAddress)
		self.config.set(section, "type", sensorType)
		with open('hhcs.cfg', 'wb') as configfile:
			self.config.write(configfile)	
		self.log.info("Sensor assigned: " + sensorName)
	request.redirect("/sensors")
	request.finish()
	return server.NOT_DONE_YET

class ProcessOptions(resource.Resource):
    isLeaf=True
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache

    def render_GET(self, request):
	self.log.info("Serving: %s " % self.name)
	self.log.info("reuest: %s " % pprint.pformat(request.getClientIP()))
	loader = template.Loader("./" + self.config.get('web', 'template_name'))
	hlp = helper.Helper(self.log, self.config, self.cache)

	options  = hlp.getOptions()
	pprint.pprint(options)
	return loader.load("options.html").generate(
				pump_enabled=options['pump_enabled'],
				pump_delay=str(options['pump_delay']),
				return_sensor=options['return_sensor'],
				comfort_floor_enabled=options['comfort_floor_enabled'],
				comfort_floor_temp=str(options['comfort_floor_temp']),
				min_flow_temp=str(options['min_flow_temp']),
				max_flow_temp=str(options['max_flow_temp']),
				pump_relay_name=options['pump_relay'],
				boiler_relay_name=options['boiler_relay'],
				relays=hlp.getRelaysUnassigned(),
				sensors=hlp.getSensorsListAvailable('')
				)	
    
    def render_POST(self, request):
	self.session = SessionManager(request, self.log)
	self.log.info("Serving POST: %s " % self.name)
	
	#Session.sessionTimeout 	= 3600

	if request.path == "/options":
		if not self.config.has_section('options'):
			self.config.add_section('options')	
		self.config.set('options', 'pump_enabled',  int(cgi.escape(request.args["pump_enabled"][0]))) 
		self.config.set('options', 'pump_delay',  cgi.escape(request.args["pump_delay"][0]))
		self.config.set('options', 'return_sensor',  cgi.escape(request.args["return_sensor"][0]))
		self.config.set('options', 'comfort_floor_enabled',  int(cgi.escape(request.args["comfort_floor_enabled"][0])))
		self.config.set('options', 'comfort_floor_temp',  cgi.escape(request.args["comfort_floor_temp"][0]))
		self.config.set('options', 'min_flow_temp',  cgi.escape(request.args["min_flow_temp"][0]))
		self.config.set('options', 'max_flow_temp',  cgi.escape(request.args["max_flow_temp"][0]))
		self.config.set('options', 'pump_relay',  cgi.escape(request.args["pump_relay"][0]))
		self.config.set('options', 'boiler_relay',  cgi.escape(request.args["boiler_relay"][0]))
		with open('hhcs.cfg', 'wb') as configfile:
			self.config.write(configfile)	
	request.redirect("/zones")
	request.finish()
	return server.NOT_DONE_YET

class ProcessTowel(resource.Resource):
    isLeaf=True
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache

    def render_GET(self, request):
	self.log.info("Serving: %s " % self.name)
	self.log.info("reuest: %s " % pprint.pformat(request.getClientIP()))
	loader = template.Loader("./" + self.config.get('web', 'template_name'))
	m = re.match(r"^/towel/delete/(.*)$", request.path, flags=0)
	if m:
		time = m.group(1)
		oldtimes = self.config.get( "towel_times", "times").strip().split(',')
		newtimes = ""
		for item in oldtimes:
			if item != time:
				newtimes = item  + ","
		if len(newtimes) > 1:
			newtimes = newtimes[:-1]	
		self.config.set( "towel_times", "times", newtimes)
		with open('hhcs.cfg', 'wb') as configfile:
			self.config.write(configfile)	
		request.redirect("/towel")
		request.finish()
		return server.NOT_DONE_YET

	if request.path=="/towel/add":
		return loader.load("towel_add.html").generate()
		
	towel_times = self.config.get( "towel_times", "times").split(',')
	TimesList = []
	for item in towel_times:
		time_list = item.split(';')
		if len(time_list) == 2:
			self.log.info("time : " + time_list[0] + "  state: " + time_list[1])
			timeInfo = {}
			timeInfo["time"]  = time_list[0]
			timeInfo["action"]  = time_list[1]
			TimesList.append(timeInfo)
	return loader.load("towel.html").generate(
				times=TimesList
				)	
    
    def render_POST(self, request):
	self.session = SessionManager(request, self.log)
	self.log.info("Serving POST: %s " % self.name)
	
	#Session.sessionTimeout 	= 3600

	if request.path == "/towel/add":
		time = cgi.escape(request.args["hour"][0]) + ":" + cgi.escape(request.args["min"][0]) + ";" + cgi.escape(request.args["action"][0])
		oldtimes = self.config.get( "towel_times", "times").strip()
		if len(oldtimes) > 0:
			newtimes = oldtimes + ',' + time
		else:
			newtimes = time	
		self.config.set( "towel_times", "times", newtimes)
		with open('hhcs.cfg', 'wb') as configfile:
			self.config.write(configfile)	

	request.redirect("/towel")
	request.finish()
	return server.NOT_DONE_YET



#    def render(self, request):
#	self.log.info("Serving: " . self.name)
#	loader = template.Loader("./template")
#	return loader.load("index.html").generate()







