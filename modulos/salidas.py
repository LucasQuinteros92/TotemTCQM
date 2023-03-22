import pigpio
 
from modulos import hbl as hbl
from modulos import delays as delays
from modulos import auxiliar as auxiliar
from modulos.variablesGlobales import *

""" --------------------------------------------------------------------------------------------

   Clase salidas hbl
   
-------------------------------------------------------------------------------------------- """

class Salidas:

    def __init__(self, pi , out1 = Pin_Salida1 ,
                            out2 = Pin_Salida2 ,
                            out3 = Pin_Salida3 ,
                            out4 = Pin_Salida4 ):

        auxiliar.EscribirFuncion("Salidas - __init__")

        self.pi : pigpio.pi = pi 

        self.pi.write(out1, hbl.OFF)   
        self.pi.write(out2, hbl.OFF) 
        self.pi.write(out3, hbl.OFF) 
        self.pi.write(out4, hbl.OFF)
        
        # si el W1 de wiegand esta desactivado, puedo usar los
        # pines como salidas digitales, las inicializo

        if hbl.WD_W1_activado == 0:

            self.pi.write(Pin_W1_WD0, hbl.OFF)   
            self.pi.write(Pin_W1_WD1, hbl.OFF) 
            self.pi.write(Pin_W2_WD0, hbl.OFF) 
            self.pi.write(Pin_W1_WD1, hbl.OFF)
        
    def TogglePin(self, pin, tiempo):
        '''toggle pin la cant de ms que se desee'''
        auxiliar.EscribirFuncion("Salidas - activaSalida numero: "+ str(pin) )
        self.pi.write(pin, hbl.ON) 
        delays.ms(int(tiempo))
        self.pi.write(pin, hbl.OFF)  
    
    def SetearSalida(self, pin, estado): 
        auxiliar.EscribirFuncion("Salidas - seteo "+ str(pin) + "en estado:" + str(estado))
        self.pi.write(pin, estado)

def TogglePin(pi, pin, tiempo):
        '''toggle pin la cant de ms que se desee'''
        auxiliar.EscribirFuncion("Salidas - activaSalida numero: "+ str(pin) )
        pi.write(pin, hbl.ON) 
        delays.ms(int(tiempo))
        pi.write(pin, hbl.OFF)