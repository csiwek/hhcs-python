#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import sys, os, string
from twisted.web import server, resource
from twisted.internet import threads, reactor, defer
from twisted.web.server import Session
from twisted.python.components import registerAdapter
import cgi


#from concurrent.futures.thread import ThreadPoolExecutor
import pprint
from tornado import template

class Dispatcher(resource.Resource):

    def __init__(self, log, config, cache):
       	resource.Resource.__init__(self)
	self.log = log
	self.config = config
	self.cache = cache
	
    def getChild(self, name, request):
	return Process(name, self.log, self.config, self.cache)

class ShortSession(Session):
    sessionTimeout = 5


class SessionManager:
     def __init__(self, request):
	self.session  = request.getSession()
	self.request = request

     def getSessionId(self):
	return self.session.uid

     def expirySession(self):
	self.session.expire() 


class Process(resource.Resource):
    
    def __init__(self, name, log, config, cache):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log
	self.config = config
	self.cache = cache

    def render_GET(self, request):
	self.log.info("Serving: %s " % self.name)
	loader = template.Loader("./template")
	if self.name == "" or self.name=="index.html":
		session = request.getSession().uid
		user = self.cache.getValue(session + "_user")
		if not user:
			request.redirect("login.html")
			request.finish()
			return server.NOT_DONE_YET
		else:
			return loader.load("index.html").generate(sid=user)
			
	elif self.name == "login.html":
		request.getSession().expire()
		return loader.load(self.name).generate()
	else:
		return loader.load(self.name).generate()

    def render_POST(self, request):
	self.log.info("Serving POST: %s " % self.name)
	if self.name == "login.html":
		#registerAdapter(Session)
		#request.getSession().expire()
		
		username = cgi.escape(request.args["username"][0])
		password = cgi.escape(request.args["password"][0])
		self.log.info("User " + username + " entered")
		if self.config.get('web', 'admin_username') == username  and self.config.get('web', 'admin_password') == password:
			self.log.info(" =================   User " + username + " Authenticated")
			ses = request.getSession().uid
			self.cache.setValue(ses + "_user", username)
			request.redirect("index.html")
		else:
			self.log.info("User " + username + " NOT  Authenticated")
			request.redirect("login.html")
		request.finish()
		return server.NOT_DONE_YET
#    def render(self, request):
#	self.log.info("Serving: " . self.name)
#	loader = template.Loader("./template")
#	return loader.load("index.html").generate()







