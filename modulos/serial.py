
import sys
import os
import serial
import threading
import time
from modulos import auxiliar as auxiliar

from time import sleep 
from serial import SerialException

from modulos import hbl as hbl 
from modulos import log as log
from modulos import hblCore as hblCore
from modulos import variablesGlobales as VG
from modulos import auxiliar as auxiliar

global pi

global ser1
global ser2

""" --------------------------------------------------------------------------------------------

    Thread para la comunicacion serial

-------------------------------------------------------------------------------------------- """

def startThreadSerial1(): 
    auxiliar.EscribirFuncion("startThreadSerial1")

    global pi

    global ser1

    ser1 = serial.Serial(port=hbl.SERIAL_COM1_port, baudrate=hbl.SERIAL_COM1_baudrate, bytesize=hbl.SERIAL_COM1_bytesize, parity=hbl.SERIAL_COM1_parity, stopbits=hbl.SERIAL_COM1_stopbits)
    ser1.write(b"Serial start")
    ser1.flushInput()
              
    while True: 

        if hbl.SERIAL_COM1_activado == 1:
            if VG.TareaAcutal == "Leer Serial":

                try: 
                    VG.Serial_COM1_Rx_Data = ser1.readline()
                    time.sleep(0.03)
                    data_left = ser1.inWaiting()
                    VG.Serial_COM1_Rx_Data +=ser1.read(data_left) 

                    log.escribeSeparador(hbl.LOGS_hblSerial)
                    log.escribeLineaLog(hbl.LOGS_hblSerial, "Datos Serial recibidos : " + str(VG.Serial_COM1_Rx_Data)) 



    
                except Exception as e:
                
                    exc_type, exc_obj, exc_tb = sys.exc_info() 
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
                    errorExcepcion = "ERROR : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

                    log.escribeSeparador(hbl.LOGS_hblSerial)
                    log.escribeLineaLog(hbl.LOGS_hblSerial, "Error : " + str(errorExcepcion)) 
        
        time.sleep(0.01)

def startThreadSerial2(): 
    auxiliar.EscribirFuncion("startThreadSerial2")

    global pi
    global ser2

    ser2 = serial.Serial(port=hbl.SERIAL_COM2_port, baudrate=hbl.SERIAL_COM2_baudrate, bytesize=hbl.SERIAL_COM2_bytesize, parity=hbl.SERIAL_COM2_parity, stopbits=hbl.SERIAL_COM2_stopbits)
    ser2.write(b"Serial start")
    ser2.flushInput()
              
    while True: 

        if hbl.SERIAL_COM2_activado == 1:
            if VG.TareaAcutal == "Leer Serial":

                try: 
                    VG.Serial_COM2_Rx_Data = ser2.readline()
                    time.sleep(0.03)
                    data_left = ser2.inWaiting()
                    VG.Serial_COM2_Rx_Data +=ser2.read(data_left) 

                    log.escribeSeparador(hbl.LOGS_hblSerial)
                    log.escribeLineaLog(hbl.LOGS_hblSerial, "Datos Serial recibidos : " + str(VG.Serial_COM2_Rx_Data)) 

                      
    
                except Exception as e:
                
                    exc_type, exc_obj, exc_tb = sys.exc_info() 
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
                    errorExcepcion = "ERROR : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

                    log.escribeSeparador(hbl.LOGS_hblSerial)
                    log.escribeLineaLog(hbl.LOGS_hblSerial, "Error : " + str(errorExcepcion)) 
        
        time.sleep(0.01)
    
""" --------------------------------------------------------------------------------------------

    inicializacion comunicacion Serial

-------------------------------------------------------------------------------------------- """

def inicializacion(pi2): 
    auxiliar.EscribirFuncion("inicializacion")

    global pi
 
    pi = pi2

    if hbl.SERIAL_COM1_activado == 1:
 
        try:

            serialHBL = threading.Thread(target=startThreadSerial1, name='HBLSerial1')
            serialHBL.setDaemon(True)
            serialHBL.start()   

            log.escribeSeparador(hbl.LOGS_hblSerial)
            log.escribeLineaLog(hbl.LOGS_hblSerial, "Serial Start")  
        
        except Exception as e:
              
            exc_type, exc_obj, exc_tb = sys.exc_info() 
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
            errorExcepcion = "ERROR : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

            log.escribeSeparador(hbl.LOGS_hblSerial)
            log.escribeLineaLog(hbl.LOGS_hblSerial, "Error : " + str(errorExcepcion)) 

    if hbl.SERIAL_COM2_activado == 1:
 
        try:

            serialHBL = threading.Thread(target=startThreadSerial2, name='HBLSerial2')
            serialHBL.setDaemon(True)
            serialHBL.start()   

            log.escribeSeparador(hbl.LOGS_hblSerial)
            log.escribeLineaLog(hbl.LOGS_hblSerial, "Serial Start")  
        
        except Exception as e:
              
            exc_type, exc_obj, exc_tb = sys.exc_info() 
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
            errorExcepcion = "ERROR : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

            log.escribeSeparador(hbl.LOGS_hblSerial)
            log.escribeLineaLog(hbl.LOGS_hblSerial, "Error : " + str(errorExcepcion))  


def serial_write():
    global ser1
    global ser2

    ser1.write(b"XXX")
    ser2.write(b"XXX")