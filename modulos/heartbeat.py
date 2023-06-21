from threading import Thread
from modulos import hblCore

import websocket
import socket

class heartbeat(object):
    def __init__(self, pi):
        

        self.t = Thread(target=hblCore.heartBeat,args=(pi,),daemon=False, name = "heartbeat")
        self.t.start()
        

