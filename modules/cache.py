#!/usr/bin/python

# This class provides inter-thread cache

import time
import threading
from datetime import datetime
import pprint
 
from twisted.internet import reactor
class cache():
        def __init__(self,l):
		l.info("Cache initialized")
		self.ContinueLoop=1
		self.Sensor0_temp = 0
		self.defaultExpirytime = 3600.0
		self.Dict = {}
		self.l = l

	def getValue(self, keyInp):
		self.l.info("Cache getting value for key " + keyInp)
		if keyInp in self.Dict.keys():
			self.l.info("Cache returning " + pprint.pformat(self.Dict.get(keyInp)))
			return self.Dict.get(keyInp)['data']
		else:
			self.l.info("Cache returning  None " )
			return None

	def setValue(self, keyInp, value):
		self.Dict[keyInp] = {
			'data': value,
			'timestamp': datetime.now(),
			'expireTime': self.defaultExpirytime
		}
		#t = threading.Timer(self.defaultExpirytime, self.expiryVars, [keyInp])
		#t.start()
		
		reactor.callLater(self.defaultExpirytime, self.expiryVars , keyInp)


		return True
		
	def expiryVars(self, key):
		self.l.info("Key: " + key + "  has just expired")
		if key in self.Dict:
    			self.Dict.pop(key, None)
		return None
