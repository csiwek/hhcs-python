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
import uuid
import time

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
	elif request.path=="/login":
		return ProcessLogin(name, self.log, self.config, self.cache)
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
	loader = template.Loader("./" + self.config.get('web', 'template_name'))
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
		request.redirect("/")
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
	loader = template.Loader("./" + self.config.get('web', 'template_name'))
	for section in self.config.sections():
		if section[:5] == "zone_":
			self.log.info("found zone %s " % section[5:])
	return loader.load("zones.html").generate()	


    def render_POST(self, request):
	self.session = SessionManager(request, self.log)
	self.log.info("Serving POST: %s " % self.name)
	#Session.sessionTimeout 	= 3600
	zoneName = cgi.escape(request.args["zonename"][0])
	self.log.info("Creating Zone " + zoneName)
	if len(zoneName) > 2:
		self.config.add_section("zone_" + zoneName)
		with open('hhcs1.cfg', 'wb') as configfile:
			self.config.write(configfile)	
		self.log.info("Zone Created: " + zoneName)
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

#    def render(self, request):
#	self.log.info("Serving: " . self.name)
#	loader = template.Loader("./template")
#	return loader.load("index.html").generate()







