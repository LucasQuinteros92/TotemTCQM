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
    
    def __init__(self, segundos = 10, callback = None, name = "",):
        super().__init__()
        self.segundos = segundos
        self._running = False
        self.callback = callback
        self._stopEvent = Event()
        self.count = 0
        self.name = name
        self.Status = "EsperandoPuertaAbierta"
        self.t = Thread( target= self.__run, daemon=False)
        self.t.start()
        
    def start(self):
        
        self.count = 0
        self._running = True
        self.LogReport("Timer corriendo")

    def is_running(self):
        return self._running
    
    ''' metodo privado de la clase usar solo start y stop luego del init '''
    def __run(self):
        self.LogReport('Timer inicializado')
        
        while True:
            if self._running :
                
                self.LogReport(str(self.count) + "segundo")
                time.sleep(1)
                if self.count >= self.segundos:
                    #self.LogReport('Se supero el tiempo establecido')
                    self.count =0
                    self._running = False
                    if self.callback is not None:
                        self.callback()
                    
                elif self._stopEvent.isSet():
                    self._stopEvent.clear()
                    self.count =0

                self.count += 1
            else : 
                time.sleep(0.5)
                
    def setSegundos(self,segundos : int):            
        self.segundos = segundos
        
    def stop(self):
        
        self._stopEvent.set()
        self._running = False
        #self.LogReport("Timer detenido ")
        
    def LogReport(self, texto):
        log.escribeSeparador(hbl.LOGS_hblTimer)
        log.escribeLineaLog(hbl.LOGS_hblTimer,"Estado: "+ self.Status)
        log.escribeLineaLog(hbl.LOGS_hblTimer,self.name +": " +texto)
    
def rutina():
    print('imprimiendo desde rutina')       
    

if __name__ == '__main__':
    
    alarma = temporizador(callback = rutina)
    alarma.start()
    
    if(input ("Esperando String")):
        alarma.stop()
        
    alarma.start()
    
   
    
    