#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import sys, os, string
import Adafruit_BBIO.GPIO as GPIO
from twisted.web import server, resource
from twisted.internet import threads, reactor, defer
#from concurrent.futures.thread import ThreadPoolExecutor
import pprint
import re


class Dispatcher(resource.Resource):
    #isLeaf = True   
    def __init__(self, log, config, cache):
       	resource.Resource.__init__(self)
	self.log = log
	self.config = config
	self.cache = cache
	
    def getChild(self, name, request):
	if re.match(r"^/relays/(.*)/(.*)$", request.path, flags=0):
		return Relays(name, self.log, self.config, self.cache)
	else:
		return ProcessError(request.path, self.log, self.config, self.cache)
		#return NoResource("oops...")
		#return self.Nothing(request)
    def Nothing(self, request):
        request.setResponseCode(404)

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
	return ""  

    def render(self, request):
	self.log.info("No handler found for %s . replying 404" % self.name)
	request.setResponseCode(404, message="Not Found")
	return ""  



class Relays(resource.Resource):
    isLeaf=True
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache

    def render_GET(self, request):
	return "OK"
	
    def render_POST(self, request):
	self.log.info("Serving POST: %s " % self.name)
	m = re.match(r"^/relays/(.*)/(.*)$", request.path, flags=0)
	self.log.info("1: %s 2: %s " % (m.group(1), m.group(2)))
	if m:
		if m.group(1) == "enable":
			relay =  m.group(2)
			self.log.info("Enabling relay: %s " % relay)
			GPIO.output(self.config.get('gpio', relay), GPIO.HIGH)
			self.cache.setValue(relay + "_relay_state", 1)
		elif m.group(1) == "disable":
			relay =  m.group(2)
			self.log.info("Disabling relay: %s " % relay)
			GPIO.output(self.config.get('gpio', relay), GPIO.LOW)
			self.cache.setValue(relay + "_relay_state", 0)
	
	return "OK"
