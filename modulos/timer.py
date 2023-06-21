from threading import Thread, Event
from modulos import log
from modulos import hbl
import time

class temporizador(object):
    '''
    Inicializa un thread que luego del tiempo seteado realizara la funcion
    que se le pase como callback, a menos que se lo detenga antes
    Una vez detenido o de cumplido el tiempo seteado
    se lo puede reciclar llamando nuevamente a start
    '''
    
    def __init__(self,logObject = None, segundos = 10, callback = None, name = "", debug  = False , status = "" ):
        super().__init__()
        self.segundos = segundos
        self._running = False
        self.callback = callback
        self._stopEvent = Event()
        self.debug = debug
        self.count = 0
        self.log : log.LogReport = logObject
        self.name = name
        self.Status = status
        self.t = Thread( target= self.__run, daemon=False, name = name)
        self.t.start()
        
    def start(self):
        self.count = 0
        self._running = True
        if self.debug:
            if self.segundos/60 > 1:
                self.LogReport("Timer corriendo, Contara: "+str(int(self.segundos/60))+" minutos","g")
            else:
                self.LogReport("Timer corriendo, Contara: "+str(self.segundos)+" segundos","g")
    def is_running(self):
        return self._running
    
    def setEncendido(self,time):
        self.Status = "AlarmaSonando"
        self.setSegundos(time)
        
    def setDesactivado(self,time):
        self.Status = "AlarmaDesactivada"
        self.setSegundos(time)
        
    def status(self):
        return self.Status
        
    ''' metodo privado de la clase usar solo start y stop luego del init '''
    def __run(self):
        
        self.LogReport('Timer inicializado',"y")
        
        while True:
            if self._running :
                
                #if self.debug:
                    #if self.count % 10:
                        #self.LogReport(str(self.count) + "segundos")
                time.sleep(1)
                if self.count >= self.segundos:
                    #self.LogReport('Se supero el tiempo establecido')
                    self.count = 0
                    self._running = False
                    if self.callback is not None:
                        self.callback()
                    
                elif self._stopEvent.isSet():
                    self._stopEvent.clear()
                    self.count =0

                self.count += 1
            else : 
                time.sleep(0.1)
                
    def setSegundos(self,segundos : int):            
        self.segundos = segundos
        
    def stop(self):
        self.count = 0
        #self._stopEvent.set()
        self._running = False
        if self.debug:
            self.LogReport("Timer detenido ","r")
        
    def LogReport(self, texto, color = None):
        if self.log != None:
            self.log.EscribirLinea(hbl.LOGS_hblTimer)
            self.log.EscribirLinea(hbl.LOGS_hblTimer, self.name +": " +texto, color)
            if self.Status != "":
                self.log.EscribirLinea(hbl.LOGS_hblTimer, "Estado: "+ self.Status)
        
    
def rutina():
    print('imprimiendo desde rutina')       
    

if __name__ == '__main__':
    
    alarma = temporizador(callback = rutina)
    alarma.start()
    
    if(input ("Esperando String")):
        alarma.stop()
        
    alarma.start()
    
   
    
    