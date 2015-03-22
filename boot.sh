#!/bin/bash
cd /home/pi/LawnConnect
sleep 2
sudo python LawnConnect.py 2>>outlog.log &
sleep 5
python -m CGIHTTPServer 8010 
