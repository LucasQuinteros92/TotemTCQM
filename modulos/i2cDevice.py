import pigpio
import time
import datetime
from threading import Thread
from modulos import lcd_i2c as lcd_i2c
from modulos import hbl as hbl
from modulos import delays as delays
from modulos import log as log
from modulos import auxiliar as auxiliar
from modulos import variablesGlobales as variablesGlobales


global lcd1

def inicializacion(pi):
    auxiliar.EscribirFuncion("inicializacion")

    global lcd1

    # inicializa displays LCD   
    try:
        if hbl.DISPLAY_activado == 1:
            lcd1 = lcd_i2c.lcd(pi, width=20, bus=variablesGlobales.BusDisplay) 
            delays.ms(100)
            lcd1.put_line(0, hbl.DISPLAY_line0)
            lcd1.put_line(1, hbl.DISPLAY_line1)
            lcd1.put_line(3, hbl.DISPLAY_line3)
            
 
    except Exception as inst: 

        log.escribeSeparador(hbl.LOGS_hbli2c) 
        log.escribeLineaLog(hbl.LOGS_hbli2c, "Error : " + str(inst))
    
    
def lcdWrite(line, message):
    if hbl.DISPLAY_activado == 1:
        lcd1.put_line(line, message)
        
class Lcd(object):
    
    def __init__(self, pi):
        self.message = ''
        self.line = 0
        if hbl.DISPLAY_activado == 1:
            try:
                
                self.lcd1 = lcd_i2c.lcd(pi, width=20, bus=variablesGlobales.BusDisplay) 
                delays.ms(100)
                self.lcd1.put_line(0,str(datetime.datetime.now().strftime("  %d/%m/%Y %H:%M")))
                self.lcd1.put_line(1, hbl.DISPLAY_line0)
                self.lcd1.put_line(2, hbl.DISPLAY_line1)
                self.lcd1.put_line(3, hbl.DISPLAY_line3)
                self.t = Thread(target= self.__run, daemon=False)
                self.t.start()
                
            except Exception as inst: 

                log.escribeSeparador(hbl.LOGS_hbli2c) 
                log.escribeLineaLog(hbl.LOGS_hbli2c, "Error : " + str(inst))
        else:
            return None
    
    def lcdWrite(self, line, message):
        self.line = line
        self.message = message
        
    
    def __run(self):
        while True:
            if self.message is not '':
                
                self.lcd1.put_line(self.line, self.message)
                
                self.message = ''
            else:
                time.sleep(0.5)
            
            