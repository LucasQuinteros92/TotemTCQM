#!/bin/sh
cd Desktop/ContadorRasp
sudo pigpiod &
sudo python3 main.py &
