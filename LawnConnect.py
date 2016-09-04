#!/usr/bin/python


import ephem
import datetime
import time
import RPi.GPIO as GPIO
import math
import random
import pickle


if __name__ == "__main__":

    statfile = "status.txt"
    statfile2 = "status2.txt"

# setting up the sunset parameters

    o = ephem.Observer()
    o.lat = '33.5951'
    o.long = '-117.6914'
    s=ephem.Sun()
    s.compute()
    
    # on duration in seconds
    OnDuration = int(random.uniform(5,7)*60*60)
    # delay of the turn on by 15 minutes
    DelayOn = datetime.timedelta(seconds=(15*60)) 
    
    next_sunset = ephem.localtime(o.next_setting(s))
    next_sunrise = ephem.localtime(o.next_rising(s))
    next_turnoff = next_sunset+DelayOn + datetime.timedelta(seconds=OnDuration)
    
    # BCM numbering
    GPIO.setmode(GPIO.BCM)
    # channe1 1 relay
    GPIO.setup(25,GPIO.OUT, initial=GPIO.HIGH)
    # channel 2 relay
    GPIO.setup(17,GPIO.OUT, initial=GPIO.HIGH)
    # channel 3 relay
    GPIO.setup(5,GPIO.OUT, initial=GPIO.HIGH)
    # channel 4 relay
    GPIO.setup(6,GPIO.OUT, initial=GPIO.HIGH)
    
    # determine if LightOn should be On or Off 
    # if next_sunset > next_sunrise and now() < next_turnoff - 24 hours
    # the first inequality deteremines it is night.   
    # the second inequality determines if we need to adjust the turn off time by 24 hours 
    LightOn = False
    
    if datetime.datetime.now() < (next_sunset+DelayOn):
        temp = next_turnoff + datetime.timedelta(hours = -24)
        if datetime.datetime.now() < temp:
            LightOn = True
            GPIO.setup(25,GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(17,GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(5,GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(6,GPIO.OUT, initial=GPIO.LOW)
            next_turnoff = temp
            print(temp)
     
    print ephem.localtime(o.next_setting(s))
 
    # reset the status file with the inital values. 
    with open(statfile,'w') as f:
            pickle.dump((LightOn,next_sunset,next_turnoff),f)
    TimeToOff = 0
 
 # monitor the states
 # Current LIght condition
 
    while True:
        # read the status file to see if the user turned on lights:
        while True:
            try:
                with open(statfile,'r') as f:
                   LightOn, next_sunset, next_turnoff = pickle.load(f)
                break 
            except:
                time.sleep(.1)
                
        # on duration in seconds
        OnDuration = int(random.uniform(5,7)*60*60)
    
    # test if we should turn on lights or turn off lights
    # adjust the state of the lights  
        if LightOn == False:
            if datetime.datetime.now() > (next_sunset+DelayOn):
                LightOn = True
                print "The lights were turn on"
                print LightOn
                #GPIO.setup(25,GPIO.OUT, initial=GPIO.LOW)
                # using a 65 second delay to ensure next_setting picks tomorrow
                b = datetime.datetime.now() + datetime.timedelta(hours = 24)
                next_sunset = ephem.localtime(o.next_setting(s, start=b))
        else:
            if datetime.datetime.now() > next_turnoff:
                LightOn = False
                print "The lights were turned off"
                print LightOn
                #GPIO.setup(25,GPIO.OUT, initial=GPIO.HIGH)
                next_turnoff = (next_sunset+DelayOn) + datetime.timedelta(seconds=OnDuration)
        
        print "The Lights are:"
        print LightOn
        print "The next sunset"
        print next_sunset
        print "the next sunrise"
        print next_sunrise
        print "the next turnoff"
        print next_turnoff
        print "the current time"
        print datetime.datetime.now()
        with open(statfile,'w') as f:
            pickle.dump((LightOn,next_sunset,next_turnoff),f)
        with open(statfile2,'w') as f:
            f.write(str(LightOn) + '\n')
            f.write(str(next_sunset) + '\n')
            f.write(str(next_turnoff) + '\n')
           
        #Set the Relay(s) with the state of The LightOn parameter
        if LightOn == True:
            GPIO.setup(25,GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(17,GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(5,GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(6,GPIO.OUT, initial=GPIO.LOW)
        else:
            GPIO.setup(25,GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(17,GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(5,GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(6,GPIO.OUT, initial=GPIO.HIGH)
        time.sleep(2.5)
    
