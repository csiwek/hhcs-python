#!/usr/bin/python

# This class provides inter-thread cache

 
class cache():
        def __init__(self,l):
		l.info("Cache initialized")
		self.ContinueLoop=1
		self.Sensor0_temp = 0
		self.Dict = {}
		self.l = l

	def getValue(self, keyInp):
		self.l.info("Cache getting value for key " + keyInp)
		if keyInp in self.Dict.keys():
			self.l.info("Cache returning " + self.Dict.get(keyInp))
			return self.Dict.get(keyInp)
		else:
			self.l.info("Cache returning  None " )
			return None

	def setValue(self, keyInp, value):
		self.Dict[keyInp] = value
		return True
		

