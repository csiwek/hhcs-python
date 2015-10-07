#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import sys, os, string
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/modules/')
from twisted.internet import reactor
from twisted.python import threadable, log as twlog
from twisted.web import server, resource
from twisted.internet import task, defer
import urllib
import time
from signal import signal, SIGHUP, SIGTERM, SIGINT
import json
import pprint
import re
import ConfigParser
import restapi
import display
import cache
import logger

log = logger.Logger("hhcs")
l = log.get_logger("hhcs") 
l.info("Starting")
c = cache.cache(l)

disp = display.handler(l,c) 

def signal_handler(signal, frame):
    global disp
    l.info("terminating hhck")
    c.ContinueLoop=0
   # del c
    reactor.stop()
    time.sleep(2)
    disp.ExitText()

signal(SIGINT, signal_handler)
signal(SIGTERM, signal_handler)



def serve():
	return "OK"



def loop(c):
	while c.ContinueLoop:
		l.debug("tick %d\n" % c.ContinueLoop)
		time.sleep(1)


if __name__ == '__main__':
    
#    disp = display.handler(c) 
    lc = task.LoopingCall(disp.generate)
    lc.start(0.2)
    site = server.Site(restapi.Dispatcher(disp))
    reactor.listenTCP(3000, site)
    reactor.callInThread(loop,c)
    reactor.run()
