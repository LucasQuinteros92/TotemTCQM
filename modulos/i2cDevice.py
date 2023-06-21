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
    wificon = [0xE, 0x1B, 0x11, 0xE, 0x1B, 0x11, 0x4, 0x4]
               															

    
    def __init__(self, pi):
        self.messages = []
        self.line = 0
        self.flagreset = False
        self.__running = False
        if hbl.DISPLAY_activado == 1:
            try:
                self.pi  = pi
                self.lcd1 = lcd_i2c.lcd(pi, width=20, bus=variablesGlobales.BusDisplay) 
                delays.ms(100)

                self.lcd1.put_line(0,str(datetime.datetime.now().strftime("  %d/%m/%Y %H:%M")))
                self.lcd1.put_line(1, hbl.DISPLAY_line0)
                self.lcd1.put_line(2, hbl.DISPLAY_line1[:-1])
                self.lcd1.put_line(3, hbl.DISPLAY_line3)
                
                
                self.t = Thread(target= self.__run, daemon=False,name = "lcd")
                self.t.start()
                
                if hbl.DISPLAY_Internet == 1:
                    self.lcd1.createChar(self.wificon)
                    self.filaiconointernet = hbl.DISPLAY_Internet_fila
                    self.columnaiconointernet = hbl.DISPLAY_Internet_columna
                    self.internet()
               
            except Exception as inst: 

                log.escribeSeparador(hbl.LOGS_hbli2c) 
                log.escribeLineaLog(hbl.LOGS_hbli2c, "Error : " + str(inst))
        else:
            return None
    
    def internet(self):
        
        if hbl.DISPLAY_Internet == 1 :
            
            
            if variablesGlobales.internet:
                self.lcdWrite(line="internet", message=True)
            else:
                self.lcdWrite(line="internet", message=False)
            
        
        
        
    def lcdWrite(self, line = None, message = None, debug = False):
        if hbl.DISPLAY_activado == 1:
            if not debug and message is not None:
                self.messages.append( line )
                self.messages.append( message ) 
                if not self.__running:
                    self.__running  = True
            
                    
            elif self.__running is False:
                self.lcd1.move_to(1,0)
                self.lcd1.put_str(message)
                self.lcd1.move_to(0,0)
                time.sleep(0.1)
            
            
    def reset(self, cantidad):
        if hbl.DISPLAY_activado == 1:
            if self.__running is False:
                self.flagreset = True
                espacios = "          "
                len = str(cantidad).__len__()

                quitar = int(len/2)
                    
                if quitar:
                    espacios = espacios[:-quitar]
                try: 
                    self.lcd1.close()
                    close = True
                except:
                    close = False
                    print("lcd1 not close")

                try : 
                    
                    
                    self.lcd1 = lcd_i2c.lcd(self.pi, width=20, bus=variablesGlobales.BusDisplay) 
                    delays.ms(100)                   
                    
                    self.lcd1.put_line(1, hbl.DISPLAY_line0)
                    self.lcd1.put_line(2, espacios + str( cantidad) )
                    self.lcd1.put_line(3, hbl.DISPLAY_line3)
                    if hbl.DISPLAY_Internet == 1:
                        self.lcd1.createChar(self.wificon)
                        self.internet()  
                    
                    self.lcd1.put_line(0,str(datetime.datetime.now().strftime("  %d/%m/%Y %H:%M")))
                
                except Exception as e:
                    print("lcd1 cant init close")
                    log.escribeSeparador(hbl.LOGS_hbli2c) 
                    log.escribeLineaLog(hbl.LOGS_hbli2c, "Error : " + str(e))
                    
                self.flagreset = False
    
    def __run(self):
        while True:
            if self.__running is True:
                while self.messages.__len__() != 0 and not self.flagreset:
                    try:
                        line = self.messages.pop(0)
                        msg = self.messages.pop(0)
                        if line == "internet":
                            self.lcd1.move_to(self.filaiconointernet,self.columnaiconointernet)
                            if msg:
                                self.lcd1.selectSpecialChar(0)
                            else:
                                self.lcd1.put_chr("X")
                            self.lcd1.move_to(0,0)

                        else:
                            self.lcd1.put_line(line, msg)
                        time.sleep(0.05)   
                    except:
                        pass
                            
                self.__running = False
               
            else:
                if self.messages.__len__() != 0:
                    self.__running = True
                time.sleep(0.05)
            
            