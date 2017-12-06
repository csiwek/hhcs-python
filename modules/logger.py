#!/usr/bin/python

import os
import logging
from logging import handlers
#from twisted.python import log as twisted_log


class Logger():    
    def __init__(self,name):
	print "nothing"

    def get_logger(self,name):
	logging.basicConfig()
        logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	logger.info("Logging initialized")
	fmt = logging.Formatter("%(filename)s:%(lineno)s  %(module)s::%(funcName)5s()  # %(message)s")
	syslog_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_INFO)
	syslog_handler.setFormatter(fmt)
	#Uncomment this for logs on the console
	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(fmt)
	logger.addHandler(syslog_handler)
	#logger.addHandler(stream_handler)
	self.l = logger 
	return self.l
'''	 
    def debug(self, msg):
        self.l.debug(msg)

    def info(self, msg):
        self.l.info(msg)

    def warning(self, msg):
        self.l.warning(msg)

    def error(self, msg):
        self.l.error(msg)

    def critical(self, msg):
        self.l.critical(msg)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(syslog_handler)
    logger.addHandler(stream_handler)

    logger.setLevel(logging.INFO)
    logger.info("Logging initialized")
    return logger

def rollover(logger):
        logger.info("Log file about to roate")
        file_handler.close()
        logger.info("Logs roated")


logging.basicConfig()
fmt = logging.Formatter("%(filename)s:%(lineno)s  %(module)s::%(funcName)5s()  # %(message)s")
syslog_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_INFO)
syslog_handler.setFormatter(fmt)
#Uncomment this for logs on the console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(fmt)

'''


