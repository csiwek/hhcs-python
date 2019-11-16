import Adafruit_BBIO.GPIO as GPIO

class Buttons():
	def __init__(self,l,c, config):
		self.cache=c
		self.l=l
		self.config = config
		#GPIO.setup(self.config.get('gpio', 'button_ok'), GPIO.IN, pull_up_down=GPIO.PUD_UP)
		#GPIO.add_event_detect(self.config.get('gpio', 'button_ok'), GPIO.FALLING, callback=self.OK_Button)


	def OK_Button(self, but):
    		print "OK !" + but

	def __del__(self):
		if int(self.config.get('display', 'enabled')) != 1:
			return
		self.l.info("Destructor called")
		self.ExitText()

