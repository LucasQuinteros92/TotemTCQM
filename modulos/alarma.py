from threading import Thread, Event
from modulos import log
from modulos import hbl
from modulos import salidas
from modulos import variablesGlobales as vg
import time

class alarma(object):
    '''

    '''
    
    def __init__(self, pi, routine = None, name = ""):
        super().__init__()
        
        
        self.pi = pi
        self._running = False
        self.routine = routine
        self._stopEvent = Event()
        self.count = 0
        
        self.name = name
        self.Status = "EsperandoPuertaAbierta"
        self.t = Thread( target= self.__run, daemon=False)
        self.t.start()
        
    def start(self):
        
        self.count += 1
        self._running = True
        #self.LogReport("Timer corriendo")

    def is_running(self):
        return self._running
    
    def stop(self):
               
        self._stopEvent.set()
        self._running = False
        
        #self.LogReport("Alarma detenida ")
    
    def __run(self):
        #self.Alarma.LogReport('Timer inicializado')
        
        while True:
            if self._running :
                
                if self.Status == "PuertaAbierta":
                    for i in range(8):
                        self.AlarmaPuertaAbierta()
                        
                        if self.Status == "Intruso":
                            while(self.count):
                                self.count -= 1
                                self.AlarmaIntruso()
                            
                    
                if self.Status == "Intruso":
                    while(self.count):
                        self.count -= 1
                        self.AlarmaIntruso()
                    
                self._running = False
            else : 
                time.sleep(0.5)
                
    def AlarmaIntruso(self):
        #print(f"AlarmaIntruso quedan:{self.count}")     
        self.pi.write(vg.Pin_LED1,hbl.OFF)
        time.sleep(hbl.Contador_MaxTimeBlink)
        self.pi.write(vg.Pin_LED1,hbl.ON)
        time.sleep(hbl.Contador_MaxTimeBlink)
        
    def AlarmaPuertaAbierta(self):
        self.pi.write(vg.Pin_LED1,hbl.OFF)
        time.sleep(hbl.Contador_MaxTimeAlarma)
        self.pi.write(vg.Pin_LED1,hbl.ON)
        time.sleep(hbl.Contador_MaxTimeAlarma)
    
        
    def LogReport(self, texto):
        log.escribeSeparador(hbl.LOGS_hblTimer)
        log.escribeLineaLog(hbl.LOGS_hblTimer,self.name +": " +texto)
    
       
    


    
   
    
    