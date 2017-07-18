#!/usr/bin/python
#updated 31 July 2015

import ephem
import datetime
import time
import RPi.GPIO as GPIO
import math
import random
import pickle
import math
#this file has your account info
# Parameters you need to supply Taccount, Ttoken, Tnumber, To_number
# 
# wehre to put the twillo account information
#Taccount= 'twillo account'
#Ttoken ='twillo token'
#Tnumber = 'Twillo number'
#To_number = 'NUMBER TO CALL'
from twilloaccount import *

# twillo account:  password:  ...      username: user@gmail.com
from twilio.rest import TwilioRestClient
client = TwilioRestClient(account=Taccount, token=Ttoken)


# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
#single endded ADC right now.   
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        # commandout &= 0xF7  # make the differential bit zero (bit 4) for diff adc (ch0-ch1)
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout




if __name__ == "__main__":

    statfile = "status.txt"
    statfile2 = "status2.txt"

    # setting up the sunset parameters   
    # Place the latitude and logitude degree values into the o.lat and o.long parameters.
    o = ephem.Observer()
    o.lat = '33.4672'
    o.long = '-117.6981'
    s=ephem.Sun()
    s.compute()
    
    #default minimum and maximum on times for the lights (in hours)
    min_on_time= 6
    max_on_time= 9.5
    
    #default turn on delay after sunset (in seconds= hours*60*60)
    turn_on_delay= int(0.1*60*60)
    
    # on duration in seconds is a random number 
    # this is in seconds
    OnDuration = int(random.uniform(min_on_time,max_on_time)*60*60)
    
    # The ephem library will provide the next sunset, next sunrise
    # the next turn off is a random value shown above.  
    next_sunset = ephem.localtime(o.next_setting(s))
    next_sunrise = ephem.localtime(o.next_rising(s))
    next_turnoff = next_sunset + datetime.timedelta(seconds=(turn_on_delay+OnDuration))
    
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
 
    # SPI port on the ADC to the Cobbler
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 12
    # set up the SPI interface pins
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)

    # current reading information 
    ## ADC port number of the positive current transformer winding
    current_tran_winding_pos_adc = 0;
    ## ADC port number of the negative current transformer winding
    current_tran_winding_neg_adc = 1;
    peak_read = 0       # this keeps track of the last potentiometer value
    trim_pot = 0
    tolerance = 5       # to keep from being jittery we'll only change
    peak_save = 0
    ave_read = 0        # keeps track of the average value
    read_neg_adc = 0    # DC value of the adc reader
    ave_neg_adc = 0     # average of the DC value.
    peak_neg_adc = 0
    min_neg_adc = 0
    
    # we need to initialize the digital filter 
    H0 = 0
    H1 = 0
    H2 = 0

    Current_On_State = False
    Off_On_State = False
    On_Off_State = False

    lamp_save_trig = 0
    lamp_save_ref = 0

    # The boolean that determines if a Lamp has burnt out : Lamp_off
    Lamp_off = False

    oneday = 60*60*24
    twoday = 60*60*24*2
    # text timer (once a day in seconds)
    text_timer = time.time() + oneday

    # ADC value to power output
    # ADC is based on 3.3v range, or 3.22mv/bit with 10bits.
    # Rsecondary is 470ohms
    # transformer is 1:2500
    # primary current = ADC*3.3v/1024/470*2500*sqrt(2)   
    ADCtoCurrentGain = 3.3/1024/470*2500/math.sqrt(2)
    print(ADCtoCurrentGain)
    
    # threshold To detect that a Lamp has burnt out: 7 out of 1024 time sthe ADC current gain
    Lamp_Off_Threshold = 7.0*ADCtoCurrentGain

    # calibrate the lamp status on the first turn off to on transition
    # this boolean is also set if the Calibrate button is pressed on the web page
    Lamp_Calibrate = True
    
    # determine if LightOn should be On or Off 
    # if next_sunset > next_sunrise and now() < next_turnoff - 24 hours
    # the first inequality deteremines it is night.   
    # the second inequality determines if we need to adjust the turn off time by 24 hours 
    LightOn = False
    
    # Check the current time and turn on the lights if we are currently after sunset and before
    #   the next scheduled turnoff
    if datetime.datetime.now() < next_sunset + datetime.timedelta(seconds=turn_on_delay):
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
    # this file is communicated to the web page.   
    with open(statfile,'w') as f:
            pickle.dump((LightOn,Lamp_Calibrate,next_sunset,next_turnoff,peak_read,Lamp_off),f)
    TimeToOff = 0
 
 # monitor the states
 # Current LIght condition
 
    while True:
        # read the status file to see if the user turned on lights from web page:
        while True:
            try:
                with open(statfile,'r') as f:
                   LightOn, Lamp_Calibrate, next_sunset, next_turnoff, peak_read, Lamp_off = pickle.load(f)
                break 
            except:
                time.sleep(.1)
                
        # on duration in seconds
        OnDuration = int(random.uniform(min_on_time,max_on_time)*60*60)
   
    # test if we should turn on lights or turn off lights
    # adjust the state of the lights  
        if LightOn == False:
            if datetime.datetime.now() > (next_sunset + datetime.timedelta(seconds=turn_on_delay)):
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
                next_turnoff = next_sunset + datetime.timedelta(seconds=(turn_on_delay+OnDuration))
        
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
	# read the ADC for 100 cycle to find the peak current
        peak_read = 0
        trim_pot = 0

        # test to see if we have a changge of state for the lights  
        # if we do, then we can set or reset the digital filter
        if (LightOn != Current_On_State):
            Current_On_State = LightOn
            if (LightOn):
                Off_On_State = True
                On_Off_State = False
            else:
                Off_On_State = False
                On_Off_State = True
        else:
            Off_On_State = False
            On_Off_State = False

        #read the peak value of 99 reads
        #We are performing full wave rectified peak current detection via software
        # it is assumed that 99 reads will be at least a half 60Hz sine wave cycle
        y = []
        z = []
        for x in range(0,99):
            # read the analog pin
            trim_pot = readadc(current_tran_winding_pos_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
            # do a differential measuremtn across the current transformer winding
            # the negative side is assumed to be a DC value
            # also take the absolute value of returned difference.
            read_neg_adc = readadc(current_tran_winding_neg_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
            trim_pot = abs(trim_pot - read_neg_adc)
            y.append(trim_pot)
            z.append(read_neg_adc)
            # how much has it changed since the last read?
            # pot_adjust = abs(trim_pot - last_read)
            if ( peak_read < trim_pot):
                peak_read = trim_pot
        ave_read = sum(y)/float(len(y))
        ave_neg_adc = sum(z)/float(len(z))
        z.sort()
        peak_neg_adc = z.pop()
        min_neg_adc = z[0]
        
        peak_read = peak_read*ADCtoCurrentGain

        # if the device turns on, initialize filter at saved value
        if (Off_On_State):
           H2 = peak_save
           H1 = peak_save
           H0 = peak_save
           peak_read = peak_save
           
        # a 3 tap FIR filter for peak read value        
        H2 = H1
        H1 = H0
        H0 = peak_read
        peak_read = H0/3 + H1/3 + H2/3

        #ensure the peak_read is immediately zero when relay off
        if On_Off_State: 
             H2 = 0
             H1 = 0
             H0 = 0
             peak_read = 0
   
        # adjust the peak_save parameter if the differential is only one value
        
        print "the peak read"
        print peak_read
        print "the peak save read"
        print peak_save
        print "the average read"
        print ave_read
        print "average dc read"
        print ave_neg_adc
        print "peak dc value"
        print peak_neg_adc
        print "min dc value"
        print min_neg_adc
           
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

        # the Lamp will calibrate if the lamp is on for first turned on and if set by webpage.   
        if (LightOn):
           if (Lamp_Calibrate):
              # go ahead and read the ADC to set the peak_save.
              Lamp_Calibrate = False
              time.sleep(3)
              peak_read = 0
              for x in range(0,200):
                 trim_pot = readadc(current_tran_winding_pos_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
                 trim_pot = abs(trim_pot - readadc(current_tran_winding_neg_adc, SPICLK, SPIMOSI, SPIMISO, SPICS))
                 if ( peak_read < trim_pot):
                    peak_read = trim_pot
              peak_read = peak_read*ADCtoCurrentGain
              peak_save = peak_read
              
              H2 = peak_save
              H1 = peak_save
              H0 = peak_save
              peak_read = peak_save
  
           peak_diff = (peak_save - peak_read)
           # if the difference is only -1 for a slow decrease then allow peak read to drop.
           # in the case the the current drops to 2-3 at the start, then the peak 
           # is allowed to drop slowly (analog peak with drop).   
           # if the difference is > -1 then use envenlope

           #peak_diff = abs(peak_diff)
           print "Peak Difference with save"
           print peak_diff   
           if (Lamp_off==False):   
               if (peak_diff >= Lamp_Off_Threshold):
                   Lamp_off = True
                   lamp_save_trip = peak_read
                   lamp_save_ref = peak_save
                   #trail account
                   try: 
                      client.messages.create(to=To_number,from_=Tnumber,body="A lawn light was burnt out!")
                   except:
                      print "Twilio Didn't Work: A Lawn Light Burnt Out"
                   text_timer = time.time()+oneday   
           else:
               # allow the lights to be fixed live with hysterisis
               if (peak_diff < (Lamp_Off_Threshold*0.6)):
                   Lamp_off = False
                   text_timer = time.time()+oneday
            
               # check the text_timer and repeat if the timer count down is zero
               if time.time()>text_timer :
               #text again
                   try: 
                      client.messages.create(to=To_number,from_=Tnumber,body="A lawn light was burnt out!")
                   except:
                      print "Twilio Didn't Work: A Lawn Light Burnt Out"
                   #reset timer
                   text_timer = time.time()+oneday 


        print "lamp burnt"
        print Lamp_off
        if (Lamp_off):
           print "lamp_save_trig", lamp_save_trig
           print "lamp_save_ref", lamp_save_ref
       

        with open(statfile,'w') as f:
            pickle.dump((LightOn,Lamp_Calibrate,next_sunset,next_turnoff,peak_read,Lamp_off),f)

        with open(statfile2,'w') as f:
            f.write(str(LightOn) + '\n')
            f.write(str(next_sunset) + '\n')
            f.write(str(next_turnoff) + '\n')


        time.sleep(1.5)
    
