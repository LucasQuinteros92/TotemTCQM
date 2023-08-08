#!/bin/sh
cd /usr/programas/hbl
sudo pigpiod &
sudo python3 main.py &
