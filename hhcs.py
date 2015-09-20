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

def serve():
	return "OK"


if __name__ == '__main__':
    
    disp = display.handler() 
    lc = task.LoopingCall(disp.generate)
    lc.start(0.1)
    site = server.Site(restapi.Dispatcher(disp))
    reactor.listenTCP(3000, site)
    reactor.run()
