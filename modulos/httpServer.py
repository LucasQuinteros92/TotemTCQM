import threading
import os
import sys
import pigpio
import http.server
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs
import signal
import main
import datetime 

from modulos import hbl as hbl
from modulos import delays as delays
from modulos import log as log
from modulos import i2cDevice as i2cDevice
from modulos import variablesGlobales as variablesGlobales
from modulos import auxiliar as auxiliar

global pi

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
 
    def do_GET(self): 
        auxiliar.EscribirFuncion("do_GET")

        id = 0
        tiempo = 0
        linea1 = ""
        linea2 = ""
        linea3 = ""
        linea4 = ""
        cmd = "" 
        dni = ""

        # ex : http://172.16.1.157:8000/?id=1&tiempo=1000

        # envia la respuesta '200 OK'  
        self.send_response(200)

        # setea el header de la pagina
        self.send_header("Content-type", "text/html")

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        # extrae el parametro del query 
        query_components = parse_qs(urlparse(self.path).query)

        if 'id' in query_components:
            id = query_components["id"][0]
             
        if 'tiempo' in query_components:
            tiempo = query_components["tiempo"][0] 

        if 'linea1' in query_components:
            linea1 = query_components["linea1"][0]
            i2cDevice.lcd1.put_line(0, linea1) 

        if 'linea2' in query_components:
            linea2 = query_components["linea2"][0]
            i2cDevice.lcd1.put_line(1, linea2) 

        if 'linea3' in query_components:
            linea3 = query_components["linea3"][0]
            i2cDevice.lcd1.put_line(2, linea3) 

        if 'linea4' in query_components:
            linea4 = query_components["linea4"][0]
            i2cDevice.lcd1.put_line(3, linea4) 
        
        if 'cmd' in query_components:
            cmd = query_components["cmd"][0]

            if cmd == "borrar":
                i2cDevice.lcd1.put_line(0, "                    ") 
                i2cDevice.lcd1.put_line(1, "                    ") 
                i2cDevice.lcd1.put_line(2, "                    ") 
                i2cDevice.lcd1.put_line(3, "                    ") 
        
        if 'dni' in query_components: 
            dni = query_components["dni"][0]
            self.wfile.write(bytes(str(variablesGlobales.jsonEnvioDNI), "utf8")) 
 
 
        if hbl.HTTP_server_respuesta == 1:
            html = f"<html><head></head><body><h1>HBL v0.1 - id : {id} - Tiempo (ms) : {tiempo} </h1></body></html>" 
            # escribe el contenido html con UTF-8
            self.wfile.write(bytes(html, "utf8")) 
         

        # activa salidas segun tiempo indicado 
        if id == "1":   
            pi.write(variablesGlobales.Pin_Salida1, hbl.ON)  
            delays.ms(int(tiempo))
            pi.write(variablesGlobales.Pin_Salida1, hbl.OFF)  
        elif id == "2": 
            pi.write(variablesGlobales.Pin_Salida2, hbl.ON)     
            delays.ms(int(tiempo))
            pi.write(variablesGlobales.Pin_Salida2, hbl.OFF)  
        elif id == "3": 
            pi.write(variablesGlobales.Pin_Salida3, hbl.ON)     
            delays.ms(int(tiempo))
            pi.write(variablesGlobales.Pin_Salida3, hbl.OFF) 
        elif id == "4": 
            pi.write(variablesGlobales.Pin_Salida4, hbl.ON)     
            delays.ms(int(tiempo))
            pi.write(variablesGlobales.Pin_Salida4, hbl.OFF) 
        elif id == "5": 
            pi.write(variablesGlobales.Pin_Salida5, hbl.ON)     
            delays.ms(int(tiempo))
            pi.write(variablesGlobales.Pin_Salida5, hbl.OFF)
        elif id == "6": 
            pi.write(variablesGlobales.Pin_Salida6, hbl.ON)     
            delays.ms(int(tiempo))
            pi.write(variablesGlobales.Pin_Salida6, hbl.OFF) 
        elif id == "7": 
            pi.write(variablesGlobales.Pin_Salida7, hbl.ON)     
            delays.ms(int(tiempo))
            pi.write(variablesGlobales.Pin_Salida7, hbl.OFF) 
        elif id == "8": 
            pi.write(variablesGlobales.Pin_Salida8, hbl.ON)     
            delays.ms(int(tiempo)) 
            pi.write(variablesGlobales.Pin_Salida8, hbl.OFF)  
        else:
            pass

        if id != 0:
            # escribe en el log
            log.escribeSeparador(hbl.LOGS_hblHTTP) 
            log.escribeLineaLog(hbl.LOGS_hblHTTP, "Rele  : " + str(id))
            log.escribeLineaLog(hbl.LOGS_hblHTTP, "tiempo (ms): " + str(tiempo))
            

        return

""" --------------------------------------------------------------------------------------------

 


-------------------------------------------------------------------------------------------- """ 

def startServer():
    auxiliar.EscribirFuncion("startServer")

    try:

        # Create an object of the above class
        handler_object = MyHttpRequestHandler

        my_server = socketserver.TCPServer(("", hbl.HTTP_server_port), handler_object)
        
        # Star the server
        my_server.serve_forever()  
    
    except Exception as inst:

        log.escribeSeparador(hbl.LOGS_hblHTTP) 
        log.escribeLineaLog(hbl.LOGS_hblHTTP, "Error : " + str(inst)) 

        # sale del programa y hace un kill a los procesos activos de python
        os.system("sudo killall -v python3")

    while True:
        pass

""" --------------------------------------------------------------------------------------------

 


-------------------------------------------------------------------------------------------- """ 

def inicializacion(pi2): 
    auxiliar.EscribirFuncion("inicializacion")

    global pi

    pi = pi2

    if hbl.HTTP_server_activado == 1:

        http = threading.Thread(target=startServer, name='ServerHTTP')
        http.setDaemon(True)
        http.start()

        log.escribeSeparador(hbl.LOGS_hblHTTP) 
        log.escribeLineaLog(hbl.LOGS_hblHTTP, "HTTP Server iniciado en el puerto : " + str(hbl.HTTP_server_port))