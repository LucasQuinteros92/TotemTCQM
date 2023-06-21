
import socket
import datetime
import os
import sys
#import requests
import time  
import threading  
#import usb.util
import json
#from usb.core import find as finddev 

from modulos import log as log
from modulos import hbl as hbl
from modulos import delays as delays
#from modulos import conexiones as conexiones
from modulos import auxiliar as auxiliar
from modulos import variablesGlobales as variablesGlobales
from modulos import auxiliar as auxiliar

global device
global canvas 

""" --------------------------------------------------------------------------------------------


    inicializa HBL


-------------------------------------------------------------------------------------------- """

def inicializacionHBL():
    auxiliar.EscribirFuncion("inicializacionHBL")
 
    # escribe inicializacion HBL
    log.escribeSeparador(hbl.LOGS_hblCore)
    log.escribeLineaLog(hbl.LOGS_hblCore, "Inicio HBL - " + " v." + variablesGlobales.versionHBL) 
    log.escribeLineaLog(hbl.LOGS_hblCore, "Num. Serie : " +  variablesGlobales.RPI_SerialNumber) 
    log.escribeLineaLog(hbl.LOGS_hblCore, "Revision : " +  variablesGlobales.RPI_Revision) 
    log.escribeLineaLog(hbl.LOGS_hblCore, "MAC address eth0 : " + variablesGlobales.RPI_MacEthernet)  
    log.escribeLineaLog(hbl.LOGS_hblCore, "MAC address wlan0 : " + variablesGlobales.RPI_MacWlan)  
    log.escribeLineaLog(hbl.LOGS_hblCore, "Temperatura : " + measure_temp()) 
    get_throttled()
   
    print("\n\n*****************************************************")
    print("    _   _ ____  _        ")    
    print("   | | | | __ )| |       ") 
    print("   | |_| |  _ \| |       ") 
    print("   |  _  | |_) | |___    ") 
    print("   |_| |_|____/|_____|   ")  
    print("")
    print(" v.", variablesGlobales.versionHBL)  
    print(" Num. Serie : ", variablesGlobales.RPI_SerialNumber)
    print(" Revision : ", variablesGlobales.RPI_Revision)
    print(" MAC eth0 : ", variablesGlobales.RPI_MacEthernet)
    print(" MAC wlan0 : ", variablesGlobales.RPI_MacWlan) 
    print("")
    print("*****************************************************\n\n")

    # escribe configuracion HBL 
    log.configuracionHBL(hbl.LOGS_hblCore)    

    # realiza un update en el JSON con los valores de la RPI  
    lecturaParametrosHBL()

    # sincroniza reloj segun NTP
    sincronizarHora()
 
 
""" --------------------------------------------------------------------------------------------

    get_throttled - Status del sistema  

    11110000000000001111
    ||||            ||||_ bajo voltaje
    ||||            |||_ frecuencia del cpu al limite 
    ||||            ||_ cpu trabajando forzadamente
    ||||            |_ pico de temperatura activo
    ||||_ ocurrio un bajo voltaje desde el ultimo reset
    |||_ ocurrio un frecuencia del cpu al limite desde el ultimo reset
    ||_ ocurrio un forzado del cpu desde el ultimo reset
    |_ ocurrio un pico de temperatura desde el ultimo reset

-------------------------------------------------------------------------------------------- """

def get_throttled():
    auxiliar.EscribirFuncion("get_throttled")

    throttled = os.popen("vcgencmd get_throttled").readline()
    throttled = throttled.replace("throttled=", "")  
    throttled = throttled.replace("\n", "")  
    throttled = int(throttled, 16)
    numeroBinario = bin(throttled)[2:].zfill(20) 

    if numeroBinario[19] == 1:
        log.escribeSeparador(hbl.LOGS_hblCore) 
        log.escribeLineaLog(hbl.LOGS_hblCore, "ocurrio un pico de temperatura desde el ultimo reset")
    if numeroBinario[18] == 1:
        log.escribeSeparador(hbl.LOGS_hblCore) 
        log.escribeLineaLog(hbl.LOGS_hblCore, "ocurrio un forzado del cpu desde el ultimo reset")
    if numeroBinario[17] == 1:
        log.escribeSeparador(hbl.LOGS_hblCore) 
        log.escribeLineaLog(hbl.LOGS_hblCore, "ocurrio un frecuencia del cpu al limite desde el ultimo reset")
    if numeroBinario[16] == 1:
        log.escribeSeparador(hbl.LOGS_hblCore) 
        log.escribeLineaLog(hbl.LOGS_hblCore, "ocurrio un bajo voltaje desde el ultimo reset")
    if numeroBinario[3] == 1:
        log.escribeSeparador(hbl.LOGS_hblCore) 
        log.escribeLineaLog(hbl.LOGS_hblCore, "pico de temperatura activo")
    if numeroBinario[2] == 1:
        log.escribeSeparador(hbl.LOGS_hblCore) 
        log.escribeLineaLog(hbl.LOGS_hblCore, "cpu trabajando forzadamente")         
    if numeroBinario[1] == 1:
        log.escribeSeparador(hbl.LOGS_hblCore) 
        log.escribeLineaLog(hbl.LOGS_hblCore, "frecuencia del cpu al limite")
    if numeroBinario[0] == 1:
        log.escribeSeparador(hbl.LOGS_hblCore) 
        log.escribeLineaLog(hbl.LOGS_hblCore, "bajo voltaje")    

""" --------------------------------------------------------------------------------------------

    get_throttled - Status del sistema  

    * lee el status del sistema y lo acomoda en un byte (8 bits) para envio al reporte

-------------------------------------------------------------------------------------------- """

def get_throttled_bytes():
    auxiliar.EscribirFuncion("get_throttled_bytes")

    throttled = os.popen("vcgencmd get_throttled").readline()
    throttled = throttled.replace("throttled=", "")  
    throttled = throttled.replace("\n", "")  
    throttled = int(throttled, 16)
    numeroBinario = bin(throttled)[2:].zfill(20) 
    seleccionBytes = numeroBinario[0] + numeroBinario[1] + numeroBinario[2] + numeroBinario[3] + numeroBinario[16] + numeroBinario[17] + numeroBinario[18] + numeroBinario[19]
    
    return seleccionBytes

""" --------------------------------------------------------------------------------------------

    lee los parametros unicos de hbl

    * numero de serie
    * revision
    * mac address Ethernet adaptor

    y lo graba en el json del hbl

-------------------------------------------------------------------------------------------- """

def lecturaParametrosHBL():
    auxiliar.EscribirFuncion("lecturaParametrosHBL")

    # path del archivo
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    # Leo los parametros de configuracion en el JSON
    with open(os.path.join(__location__ , 'hbl.json'), "r") as f:
        data = json.load(f)

    # actualizo los parametros en el JSON y le da formato al mismo
    with open(os.path.join(__location__ , 'hbl.json'), "w") as f:
        json.dump(data, f, indent=4)   

""" --------------------------------------------------------------------------------------------

   leer temperatura del core de la RPI

-------------------------------------------------------------------------------------------- """

def measure_temp():
    auxiliar.EscribirFuncion("measure_temp")

    temp = os.popen("vcgencmd measure_temp").readline()
    return (temp.replace("temp=", ""))

""" --------------------------------------------------------------------------------------------

   Retorna la fecha actual del HBL

-------------------------------------------------------------------------------------------- """

def timeNow():
    auxiliar.EscribirFuncion("timeNow")

    return str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))

""" --------------------------------------------------------------------------------------------

    Retorna la fecha actual del HBL ( otro metodo )

-------------------------------------------------------------------------------------------- """

def getDate():
    auxiliar.EscribirFuncion("getDate")

    p = os.popen("date '+%F %T'") 
    line = p.readline() 
    return line 

""" --------------------------------------------------------------------------------------------

    Sincroniza la fecha del HBL con el servidor NTP  

-------------------------------------------------------------------------------------------- """

def sincronizarHora():
    auxiliar.EscribirFuncion("sincronizarHora")
    
    try:
        # escribe en el archivo de seleccion del servidor el indicado en el json del HBL
        parametrosNet = ['# Server para sincronizacion del reloj', ' ' , '[Time]', 'NTP=' + variablesGlobales.NTP_URL, ' ']
        auxiliar.append_multiple_lines('/etc/systemd/timesyncd.conf', parametrosNet, "w+") 

        # activa la sincronizacion con el servidor NTP y hace un reload del daemon
        os.system("sudo systemctl restart systemd-timesyncd.service")  
        os.system("sudo timedatectl set-ntp true") 
        os.system("sudo systemctl daemon-reload") 

        log.escribeSeparador(hbl.LOGS_hblCore) 
        log.escribeLineaLog(hbl.LOGS_hblCore, "Sincronizada la fecha del HBL con el servidor NTP") 

    except Exception as e:  
    
        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 
    
        log.escribeSeparador(hbl.LOGS_hblCore)
        log.escribeLineaLog(hbl.LOGS_hblCore, "Error : " + str(errorExcepcion))  



""" --------------------------------------------------------------------------------------------

   leer % de uso de CPU

-------------------------------------------------------------------------------------------- """

def usoCPU(numeroCPU):  
    auxiliar.EscribirFuncion("usoCPU")

    if numeroCPU == 0 : 
        line = os.popen("cat /proc/stat | grep '^cpu0'").readline() 
    elif numeroCPU == 1 : 
        line = os.popen("cat /proc/stat | grep '^cpu1'").readline() 
    elif numeroCPU == 2 : 
        line = os.popen("cat /proc/stat | grep '^cpu2'").readline() 
    elif numeroCPU == 3 : 
        line = os.popen("cat /proc/stat | grep '^cpu3'").readline() 
    else : 
        line = os.popen("cat /proc/stat | grep '^cpu'").readline() 

    valores = line.split()
    totalCPU = int(valores[1]) + int(valores[2]) + int(valores[3]) + int(valores[4]) + int(valores[5]) + int(valores[6]) + int(valores[7]) + int(valores[8]) + int(valores[9]) + int(valores[10])     
    idleCPU = (int(valores[4]) * 100 ) / totalCPU # valor del CPU sin uso teniendo en cuenta todos los procesos activos
     
    CPUenUso = format(100 - idleCPU, ".2f")

    return str(CPUenUso)

""" --------------------------------------------------------------------------------------------

    Return RAM information (unit=kb) in a list                                        
        Index 0: total RAM                                                                
        Index 1: used RAM                                                                 
        Index 2: free RAM  

-------------------------------------------------------------------------------------------- """
                                                
def getRAMinfo():
    auxiliar.EscribirFuncion("getRAMinfo")

    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            valores = line.split()[1:4]
            ram = str(format((float(valores[1]) * 100) / float(valores[0]), ".2f")) 
            return(ram)       

""" --------------------------------------------------------------------------------------------

    Return information about disk space as a list (unit included)                     
        Index 0: total disk space                                                         
        Index 1: used disk space                                                          
        Index 2: remaining disk space                                                     
        Index 3: percentage of disk used 

-------------------------------------------------------------------------------------------- """

def getDiskSpace():
    auxiliar.EscribirFuncion("getDiskSpace")

    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            valores = line.split()[1:5]
            spaceDisk = valores[3]
            spaceDisk = spaceDisk.replace("%", "")
            spaceDisk = str(format(float(spaceDisk), ".2f")) 
            return spaceDisk      

""" --------------------------------------------------------------------------------------------

    Retorna la version del bootloader instalada en el HBL

-------------------------------------------------------------------------------------------- """

def getBootloaderVersion():
    auxiliar.EscribirFuncion("getBootloaderVersion")
    
    try:

        p = os.popen("vcgencmd bootloader_version") 
        line = p.readline() 
        return(line)  
    
    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCore)
        log.escribeLineaLog(hbl.LOGS_hblCore, "Error : " + str(errorExcepcion)) 

        return "error getBootloaderVersion"


""" --------------------------------------------------------------------------------------------

    Retorna los nombres de los volumenes usb    

-------------------------------------------------------------------------------------------- """

def getVolumeNames(drive):
    auxiliar.EscribirFuncion("getVolumeNames")

    try:
        p = os.popen("sudo lsblk -o UUID,NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL,MODEL | grep '" + drive + "'")     
        line = p.readline()  
        valores = line.split()
        return valores    
    
    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCore)
        log.escribeLineaLog(hbl.LOGS_hblCore, "Error : " + str(errorExcepcion)) 
        
        return "error getVolumeNames"

""" --------------------------------------------------------------------------------------------

   * heartBeat

   * reset programado del hbl

-------------------------------------------------------------------------------------------- """

def heartBeat(pi):
    ##auxiliar.EscribirFuncion("heartBeat")
    
    delay = 500
    try:
        while True:
            # heartBeat
            pi.write(variablesGlobales.Pin_LED2, hbl.OFF)    
            delays.ms(delay)      
            pi.write(variablesGlobales.Pin_LED2, hbl.ON)  
            delays.ms(delay)
            if variablesGlobales.internet:
                delay = 200
            else:
                delay = 2000
            
            
                
    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 
    
        log.escribeSeparador(hbl.LOGS_hblCore)
        log.escribeLineaLog(hbl.LOGS_hblCore, "Error : " + str(errorExcepcion)) 


""" --------------------------------------------------------------------------------------------


    encenderLed


-------------------------------------------------------------------------------------------- """

def encenderLed(pi, led, tiempo):
    auxiliar.EscribirFuncion("encenderLed")

    try:
        if led == 1: 
         
            # led rojo
            pi.write(variablesGlobales.Pin_LED1, hbl.OFF)    
            delays.ms(tiempo) 
            pi.write(variablesGlobales.Pin_LED1, hbl.ON)    
            delays.ms(tiempo) 
        
        elif led == 2:

            # led azul
            pi.write(variablesGlobales.Pin_LED2, hbl.OFF)    
            delays.ms(tiempo) 
            pi.write(variablesGlobales.Pin_LED2, hbl.ON)    
            delays.ms(tiempo) 
  
        elif led == 3:

            # led 
            pi.write(variablesGlobales.Pin_LED3, hbl.OFF)    
            delays.ms(tiempo)
            pi.write(variablesGlobales.Pin_LED3, hbl.ON)    
            delays.ms(tiempo)   

    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 
    
        log.escribeSeparador(hbl.LOGS_hblCore)
        log.escribeLineaLog(hbl.LOGS_hblCore, "Error : " + str(errorExcepcion)) 

""" --------------------------------------------------------------------------------------------


    checkLedsBuzzer


-------------------------------------------------------------------------------------------- """

def checkLedsBuzzer(pi):
    auxiliar.EscribirFuncion("checkLedsBuzzer")

    try:

        # Buzzer
        pi.write(variablesGlobales.Pin_Buzzer, hbl.OFF)    
        delays.ms(500)  
        pi.write(variablesGlobales.Pin_Buzzer, hbl.ON)  
        delays.ms(500) 

        # led rojo
        pi.write(variablesGlobales.Pin_LED1, hbl.OFF)    
        delays.ms(200) 
        pi.write(variablesGlobales.Pin_LED1, hbl.ON)    
        delays.ms(200) 

        # led azul
        pi.write(variablesGlobales.Pin_LED2, hbl.OFF)    
        delays.ms(200) 
        pi.write(variablesGlobales.Pin_LED2, hbl.ON)    
        delays.ms(200) 

        # led  
        pi.write(variablesGlobales.Pin_LED3, hbl.OFF)    
        delays.ms(200)
        pi.write(variablesGlobales.Pin_LED3, hbl.ON)    
        delays.ms(200)   

    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 
    
        log.escribeSeparador(hbl.LOGS_hblCore)
        log.escribeLineaLog(hbl.LOGS_hblCore, "Error : " + str(errorExcepcion)) 