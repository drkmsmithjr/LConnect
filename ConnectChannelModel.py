#!/usr/bin/python
import time
import RPi.GPIO as GPIO

comfile = "/Users/Mark.Smith/Dropbox/personal/CoffeeConnect/max31855/communication.txt"

class ChannelModel():
        def __init__(self,init_gpio = 25):
                self.gpio = init_gpio
                self.LightOn = False
                #setup GPIO to use the BCM numbering.  The adufruit extension shows the BCM 
                # BCM numbering
                GPIO.setmode(GPIO.BCM)
                # heater relay
                GPIO.setup(self.gpio,GPIO.OUT, initial=GPIO.HIGH)
 
                
        def lighton(self,LIGHT_ON):
                if LIGHT_ON:
                        GPIO.setup(self.gpio,GPIO.OUT, initial=GPIO.LOW)
                        self.LightOn = True
                else:
                        GPIO.setup(self.gpio,GPIO.OUT, initial=GPIO.HIGH)
                        self.LightOn = False

        def lightstate(self):
                return self.LightOn



if __name__ == "__main__":
        model = ChannelModel()
        model.lighton(True)
        time.sleep(2)
        model.lighton(False)
        time.sleep(2)
        model.lighton(True)
        time.sleep(2)
        model.lighton(False)
        