
import socket
import sys 
import datetime
import time   
import os 
import threading

 
from modulos import log as log
from modulos import hbl as hbl
from modulos import delays as delays 
from modulos import variablesGlobales as variablesGlobales
from modulos import auxiliar as auxiliar

global sock
 
""" --------------------------------------------------------------------------------------------

   iniciar conexion TCP

-------------------------------------------------------------------------------------------- """

def iniciarConexion():
    auxiliar.EscribirFuncion("iniciarConexion")
    
    global sock

    if hbl.TCP_serverDefault_activado == 1: 

        # Crea un socket TCP/IP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # Conecta el socket al puerto del servidor que esta escuchando
        server_address = (hbl.TCP_serverDefault_ip, hbl.TCP_serverDefault_port) 
        
        log.escribeSeparador(hbl.LOGS_hblTcp) 
        log.escribeLineaLog(hbl.LOGS_hblTcp, "Conectando a " + str(server_address[0]) + " / puerto " + str(server_address[1])) 
        
        # si los intentos es 0, prueba una vez y continua, sino entra en el bucle while
        if hbl.TCP_serverDefault_intentosConexion > 0:

            intentos = 0

            while intentos < hbl.TCP_serverDefault_intentosConexion: 

                try:        
                    sock.connect(server_address)
                    break
                except:
                    log.escribeLineaLog(hbl.LOGS_hblTcp, "Reintentando la conexion : " +  str(intentos)) 
                    delays.ms(250)
                    pass

                intentos = intentos + 1
            
            if intentos == hbl.TCP_serverDefault_intentosConexion:
                log.escribeLineaLog(hbl.LOGS_hblTcp, "Error conexion") 
                return 0
            else:
                log.escribeLineaLog(hbl.LOGS_hblTcp, "Conectado")    
                return 1
        
        else:

            try:        
                sock.connect(server_address)
                log.escribeLineaLog(hbl.LOGS_hblTcp, "Conectado") 
                return 1            
            except:
                log.escribeLineaLog(hbl.LOGS_hblTcp, "Error conexion con el servidor")
                return 0 

 
""" --------------------------------------------------------------------------------------------

   envio datos id por TCP

-------------------------------------------------------------------------------------------- """

def envioTCP(id):
    auxiliar.EscribirFuncion("envioTCP")

    global sock  

    envioOK = 0
   
    try:
        sock.sendall(bytes(str(id), encoding = "utf-8")) 
        log.escribeLineaLog(hbl.LOGS_hblTcp, "Envio OK")
        sock.close() 
        envioOK = 1

    except:
        log.escribeLineaLog(hbl.LOGS_hblTcp, "Error en el envio")
        sock.close() 
        envioOK = 0
    
    return envioOK


""" --------------------------------------------------------------------------------------------

    inicializacion comunicacion TCP por thread

-------------------------------------------------------------------------------------------- """

def startThreadTCP(): 
    auxiliar.EscribirFuncion("startThreadTCP")

    global pi
 
              
    while True: 

        if hbl.FUNC_modo == 7:

            try: 

                # espera que la variable de dni cambie y se le asigne un valor ingresado por el teclado para iniciar
                # la conexion
                while(variablesGlobales.jsonEnvioDNI==""):
                    # cuando se conecto sale del while    
                    time.sleep(0.5)

                log.escribeLineaLog(hbl.LOGS_hblTcp, "DNI Recibido : " + str(variablesGlobales.jsonEnvioDNI)) 

                rst = 0
                status = 0
                # se queda en este loop hasta que se conecta               
                
                while( status == 0 ):
                    
                    while( rst == 0 ):

                        rst = iniciarConexion()
                    
                    status = envioTCP(variablesGlobales.jsonEnvioDNI)  
                       
                variablesGlobales.jsonEnvioDNI = ""

            except Exception as e:
              
                exc_type, exc_obj, exc_tb = sys.exc_info() 
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
                errorExcepcion = "ERROR : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

                log.escribeSeparador(hbl.LOGS_hblTcp)
                log.escribeLineaLog(hbl.LOGS_hblTcp, "Error : " + str(errorExcepcion)) 
        
        time.sleep(0.01)

 

def inicializacion(pi2): 
    auxiliar.EscribirFuncion("inicializacion tcp")

    global pi
 
    pi = pi2

    if hbl.TCP_serverDefault_activado == 1: 
 
        try:

            TCPHBL = threading.Thread(target=startThreadTCP, name='HBLTcp')
            TCPHBL.setDaemon(True)
            TCPHBL.start()   

            log.escribeSeparador(hbl.LOGS_hblTcp)
            log.escribeLineaLog(hbl.LOGS_hblTcp, "TCP Start")  
        
        except Exception as e:
              
            exc_type, exc_obj, exc_tb = sys.exc_info() 
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
            errorExcepcion = "ERROR : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

            log.escribeSeparador(hbl.LOGS_hblTcp)
            log.escribeLineaLog(hbl.LOGS_hblTcp, "Error : " + str(errorExcepcion))         



    
