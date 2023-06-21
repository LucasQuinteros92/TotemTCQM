from threading import Thread, Event
from modulos import log
from modulos import hbl
from modulos import salidas
from modulos import variablesGlobales as vg
import time

class alarma(object):
    '''

    '''
    
    def __init__(self, pi, routine = None, name = "",logObject = None ):
        super().__init__()
        
        
        self.pi = pi
        self._running = False
        self.routine = routine
        self._stopEvent = Event()
        self.count = 0
        self.log : log.LogReport = logObject
        self.LED = vg.Pin_Salida1
        self.BUZZER = vg.Pin_Salida2
        self.name = name
        self.Status = "EsperandoPuertaAbierta"
        self.t = Thread( target= self.__run, daemon=False, name = name)
        self.t.start()
        
        
    def SonarAlarmaPuertaAbierta(self):
        self.CheckIntruso()
        self.Status = "PuertaAbierta"        
        self._running = True
        #self.LogReport("Timer corriendo")

    def is_running(self):
        return self._running
    
    def CheckIntruso(self):
        if self.Status == "Intruso":
                time.sleep(5)
    
    def SonarAlarmaIntruso(self):
        
        self.Status = "Intruso"
        self.count += 1
        self._running = True
        
    def stop(self):
        if self._running:
            self.Status = ""
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
                        if self._running == False:
                            break
                        if self.Status == "Intruso":
                            while(self.count):
                                self.count -= 1
                                self.AlarmaIntruso()
                      
                    
                if self.Status == "Intruso":
                    while(self.count):
                        self.count -= 1
                        self.AlarmaIntruso()
                
                self.count = 0     
                self._running = False
            else : 
                time.sleep(0.1)
                
    def AlarmaIntruso(self):
        #print(f"AlarmaIntruso quedan:{self.count}")     
        self.pi.write(self.LED,hbl.OFF)
        if hbl.Contador_Buzzer:
            self.pi.write(self.BUZZER, hbl.OFF)
            
        time.sleep(hbl.Contador_LedIntrusoON)
        
        self.pi.write(self.LED,hbl.ON)
        if hbl.Contador_Buzzer:
            self.pi.write(self.BUZZER, hbl.ON)
            
        #time.sleep(hbl.Contador_MaxTimeBlink)
        
    def AlarmaPuertaAbierta(self):
        self.pi.write(self.LED,hbl.OFF)
        if hbl.Contador_Buzzer:
            self.pi.write(self.BUZZER, hbl.OFF)
            
        time.sleep(hbl.Contador_LedPuertaAbiertaON)
        
        self.pi.write(self.LED,hbl.ON)
        if hbl.Contador_Buzzer:
            self.pi.write(self.BUZZER, hbl.OFF)
            
        time.sleep(hbl.Contador_LedPuertaAbiertaON)
        
    def LogReport(self, texto, color):
        if self.log != None:
            self.log.EscribirLinea(hbl.LOGS_hblTimer)
            self.log.EscribirLinea(hbl.LOGS_hblTimer,self.name +": " +texto)
    
       
    


    
   
    
    