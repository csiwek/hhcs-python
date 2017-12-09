#!/usr/bin/python

# This class provides inter-thread cache

import time
import threading
import pprint
import memcache
import sys
 
from twisted.internet import reactor
class cache():
        def __init__(self,l):
		l.info("Cache initialized")
		self.ContinueLoop=1
		self.Sensor0_temp = 0
		self.defaultExpirytime = 0
		self.Dict = {}
		self.l = l
		self.usemc = False
		if self.usemc == True:
			try:
				self.mc = memcache.Client(['127.0.0.1:11211'], debug=0)
			except:
				self.l.error("Using Memcache but failed to connect to")
				sys.Exit(1)

	def getValue(self, keyInp):
		self.l.debug("Cache getting value for key " + keyInp)
		if not self.usemc:
			if keyInp in self.Dict.keys():
				self.l.debug("Cache returning " + pprint.pformat(self.Dict.get(keyInp)))
				return self.Dict.get(keyInp)['data']
			else:
				self.l.debug("Cache returning  None " )
				return None
		else:
			return self.mc.get(keyInp)


	def setValue(self, keyInp, value):
		self.l.debug("Cache setting '" + str(value) + "' value for key " + keyInp)
		if not self.usemc:
			self.Dict[keyInp] = {
				'data': value,
				'timestamp': int(time.time()),
				'expireTime': self.defaultExpirytime
			}
			#t = threading.Timer(self.defaultExpirytime, self.expiryVars, [keyInp])
			#t.start()
			if self.defaultExpirytime > 0:	
				reactor.callLater(self.defaultExpirytime, self.expiryVars , keyInp)
		else:
			self.mc.set(keyInp, value, time=self.defaultExpirytime)

		return True
		
	def expiryVars(self, key):
		self.l.debug("Key: " + key + "  has just expired")
		if key in self.Dict:
    			self.Dict.pop(key, None)
		return None
