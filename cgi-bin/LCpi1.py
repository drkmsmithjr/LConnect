#!/usr/bin/env python
# update 11/28:  globally increased sample rate. removed red background for boiler_on

import cgi
import cgitb
import time
import json
import pickle
import datetime

# enable trace backs of exceptions
cgitb.enable()

# print data from a file formatted as a javascript array
# return a string containing the table
# 

	

# print an HTTP header
#
def printHTTPheader():
    print "Content-type: text/html\n"

statfile = "/home/pi/LConnect/status.txt" 
statfile3 = "/home/pi/LConnect/status3.txt" 
dateformat = "%d-%m-%y: %I:%M %p"   


def main():

    
     # read the file and initiate each variable
    # FILE NEEDS THREE LINES OF DATA
    # Line 1: Main Switch; Line 2: Brew Switch: Line 3: sTeam switch
    while True:
        try:
            with open(statfile,'r') as f:
               LC_ON, next_sunset, next_turnoff, peak_read = pickle.load(f)
            break 
        except:
            time.sleep(.1)
 

    dform = cgi.FieldStorage()
    if dform.getvalue("LawnConnect_On"):
        LC_ON = True
    elif dform.getvalue("LawnConnect_Off"):
        LC_ON = False

    with open(statfile,'w') as f:
        pickle.dump((LC_ON,next_sunset,next_turnoff,peak_read),f)
  
    a = json.dumps({
          "LC_ON" : LC_ON,
          "NextTurnOn": "Next Sunset: " + next_sunset.strftime(dateformat),
          "NextTurnOff":"Next Turnoff: " + next_turnoff.strftime(dateformat),
          "PeakRead":"Current (A): " + str(peak_read)
    })
    # now print the AJAX information

    printHTTPheader()
    print a

  
if __name__=="__main__":
    main()
