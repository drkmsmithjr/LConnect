# [LawnConnect](https://drkmsmithjr.github.io/LConnect)

### A simple Raspberry Pi powered lawn light controller

Never have dark outside lighting again!!!  
LawnConnect automatically controls and monitors your lawn lights and lets you know when something is wrong

# Features:

1. Automatically Turns on Lights at Sunset
2. Turns off lights a random time 6-9 hours later
3. A Web Interface for monitoring and manual turning on and off lights
4. Detects when a Light has burnt out
5. Sends text messages when a light is out.
6. Accounts for daylight savings time

# Description:
Have you ever went outside and noticed all your lawn lights were burnt out?   This happened to me a little while ago.  So I decided there had to be a better way and a perfect project for the Raspberry Pi.   This Raspberry Pi project is a simple solution that will ensure you have complete control of your lights, even when you aren't around.  Try this simple but powerful internet of things project using the Raspberry pi.        

The Rasberry pi will control all the turn on and off of lights and will continually monitor the system power to determine if a light is not working.  On the event a light is not working or burnt out, a text message will be sent to the phone number of your choice telling you of the problem.

Through a web application, you can remotely monitor the status and control the turn on and off of the system.  Otherwise, the Raspberry pi will turn on your lights exactly at sunset each night and will turn them off a random time between 6 and 9 hours later.    

# Web Application:
The web application, hosted by the Raspberry Pi, gives a status of the system.   The Lights On button is used to turn on and off the lights.  Text messages tell when the lights will be turned on and off next.  there is a current monitor that shows represents the current being used right now by the system. A calibrate button (no implemented yet) will be used to calibrate the system when it first turns on.  

![alt text](https://github.com/drkmsmithjr/LConnect/blob/master/webpage_shot.png "web page screen shot")

# Block Diagram
A current sensor is used to monitor the power of the system.   A 15amp relay board will control the power to the system.
![alt text](https://github.com/drkmsmithjr/LConnect/blob/master/blockdiagram.png "System Block Diagram")

# Wiring Diagram:
This is how the Raspberry Pi is connected to the sensor board schematic and the relay board
![alt text](https://github.com/drkmsmithjr/LConnect/blob/master/WiringDiagram.png "wiring diagram")

# BOM:
The major components for the project are listed below
![alt text](https://github.com/drkmsmithjr/LConnect/blob/master/BOM.png "BOM")

# Sensor Board Schematic
The current sensor board is used to take the secondary of the current sensor and using a MCP3008 10bit ADC, convert into a digital signal that can be sampled by the Raspberry Pi
![alt text](https://github.com/drkmsmithjr/LConnect/blob/master/LawnConnect-CurrentSensor.png "Current Sensor")

The webpage for the project is located at https://drkmsmithjr.github.io/LConnect
