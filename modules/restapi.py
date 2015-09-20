#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import sys, os, string
from twisted.web import server, resource
from twisted.internet import threads, reactor, defer
#from concurrent.futures.thread import ThreadPoolExecutor
import pprint


class Dispatcher(resource.Resource):
    isLeaf = True
    def __init__(self,disp):
        resource.Resource.__init__(self)
	self.disp = disp

    def render_GET(self, request):
	try:
		self.disp.textToDisp = request.args['text'][0]
		print request.args['text'][0]
	except:
		print None
        return 'OK'
