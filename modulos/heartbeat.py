from threading import Thread
from modulos import hblCore


class heartbeat(object):
    def __init__(self, pi):
        
        self.t = Thread(target=hblCore.heartBeat,args=(pi,),daemon=False)
        self.t.start()