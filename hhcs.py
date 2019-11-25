#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import sys, os, string
sys.path.append('/home/hhcs/modules/')
sys.path.append('/home/csiwek/hhcs-python/modules/')
from twisted.internet import reactor
from twisted.python import threadable, log as twlog
from twisted.web import server, resource, static
#from twisted.web.resource import Resource
from twisted.internet import task, defer
import urllib
import time
from signal import signal, SIGHUP, SIGTERM, SIGINT
import json
import pprint
import re
import ConfigParser
import restapi
import web
import display
import engine
import cache
import logger
import ConfigParser





log = logger.Logger("hhcs")
l = log.get_logger("hhcs") 
l.info("Starting")
c = cache.cache(l)
config = ConfigParser.RawConfigParser()
config.read(os.path.dirname(__file__) + '/hhcs.cfg')

disp = display.handler(l,c,config) 
engine = engine.Engine(l,c,config)

def signal_handler(signal, frame):
    global disp
    l.info("terminating hhcs")
    c.ContinueLoop=0
   # del c
    reactor.stop()
#    time.sleep(3)
    l.info("Waiting for the display to finish")
    disp.ExitText()

signal(SIGINT, signal_handler)
signal(SIGTERM, signal_handler)


def serve():
	return "OK"


if __name__ == '__main__':
    
#    disp = display.handler(c) 
    lc = task.LoopingCall(disp.generate)
    lc.start(0.1)
    
    root = web.Dispatcher(l, config, c)
    root.putChild("css", static.File(os.path.dirname(__file__) + "/template/css"))
    root.putChild("js", static.File(os.path.dirname(__file__) + "/template/js"))
    root.putChild("img", static.File(os.path.dirname(__file__) + "/template/img"))
    root.putChild("font", static.File(os.path.dirname(__file__) + "/template/font"))
    root.putChild("images", static.File(os.path.dirname(__file__) + "/transdmin_light/images"))
    root.putChild("style", static.File(os.path.dirname(__file__) +"/transdmin_light/style"))
 #   root.putChild("", web.Dispatcher())
    #root.processors = {'.html': web.Dispatcher()}
    restServer = server.Site(restapi.Dispatcher(l,config,c))
    webServer = server.Site(root)
    reactor.listenTCP(3001, restServer)
    reactor.listenTCP(config.getint('web', 'port'), webServer)
    reactor.callInThread(engine.loop)
    reactor.run()
