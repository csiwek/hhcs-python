#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import sys, os, string
from twisted.web import server, resource
from twisted.internet import threads, reactor, defer
from twisted.web.server import Session
from twisted.python.components import registerAdapter

#from concurrent.futures.thread import ThreadPoolExecutor
import pprint
from tornado import template

class Dispatcher(resource.Resource):

    def __init__(self, log):
       	resource.Resource.__init__(self)
	self.log = log
	
    def getChild(self, name, request):
	return Process(name, self.log)

class Process(resource.Resource):
    
    def __init__(self, name, log):
       	resource.Resource.__init__(self)
	self.name = name
	self.log = log

    def render_GET(self, request):
	self.log.info("Serving: %s " % self.name)
	loader = template.Loader("./template")
	if self.name == "" or self.name=="index.html":
		return loader.load("index.html").generate(sid=request.getSession().uid)
	elif self.name == "login.html":
		request.getSession().expire()
		return loader.load(self.name).generate()
	else:
		return loader.load(self.name).generate()

    def render_POST(self, request):
	self.log.info("Serving POST: %s " % self.name)
	if self.name == "login.html":
		#registerAdapter(Session)
		session = request.getSession()
	request.redirect("index.html")
        request.finish()
	return server.NOT_DONE_YET
#    def render(self, request):
#	self.log.info("Serving: " . self.name)
#	loader = template.Loader("./template")
#	return loader.load("index.html").generate()







