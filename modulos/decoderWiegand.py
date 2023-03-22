import pigpio 
import requests
import time
import datetime 
import json
import os

from modulos import hbl as hbl
from modulos import log as log
from modulos import tcp as tcp 

from modulos.encoderWiegand import Encoder
from modulos.salidas import Salidas
from modulos.entradas import Entradas
from modulos import auxiliar as auxiliar
from modulos import variablesGlobales as variablesGlobales
 

""" --------------------------------------------------------------------------------------------


   Decodificador Wiegand


-------------------------------------------------------------------------------------------- """
   
class Decoder:

   def __init__(self, pi, gpio_0, gpio_1, callback, bit_timeout=5):

      auxiliar.EscribirFuncion("Decoder-__init__")

      self.pi = pi
      self.gpio_0 = gpio_0
      self.gpio_1 = gpio_1

      self.callback = callback

      self.bit_timeout = bit_timeout

      self.in_code = False

      self.pi.set_mode(gpio_0, pigpio.INPUT)
      self.pi.set_mode(gpio_1, pigpio.INPUT)

      self.pi.set_pull_up_down(gpio_0, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpio_1, pigpio.PUD_UP)

      self.cb_0 = self.pi.callback(gpio_0, pigpio.FALLING_EDGE, self._cb)
      self.cb_1 = self.pi.callback(gpio_1, pigpio.FALLING_EDGE, self._cb)

   def _cb(self, gpio, level, tick):
      auxiliar.EscribirFuncion("Decoder - _cb")

      """
      Acumula bits 0 y 1
      """

      if level < pigpio.TIMEOUT:

         if self.in_code == False:
            self.bits = 1
            self.num = 0

            self.in_code = True
            self.code_timeout = 0
            self.pi.set_watchdog(self.gpio_0, 100)
            self.pi.set_watchdog(self.gpio_1, 100)
         else:
            self.bits += 1
            self.num = self.num << 1

         if gpio == self.gpio_0:
            self.code_timeout = self.code_timeout & 2 # borra gpio 0 timeout
         else:
            self.code_timeout = self.code_timeout & 1 # borra gpio 1 timeout
            self.num = self.num | 1

      else:

         if self.in_code:

            if gpio == self.gpio_0:
               self.code_timeout = self.code_timeout | 1 # timeout gpio 0
            else:
               self.code_timeout = self.code_timeout | 2 # timeout gpio 1

            if self.code_timeout == 3: # ambos gpios time out
               self.pi.set_watchdog(self.gpio_0, 0)
               self.pi.set_watchdog(self.gpio_1, 0)
               self.in_code = False

               # recarga los parametros de hbl.json por actualizacion
               hbl.cargarParametros('hbl.json')

               # decodifica el valor wiegand 
               # auto deteccion de cantidad de bits y formateo
               cantidadBits = self.bits
               numero = self.num 
               
               try:
                  numeroBinario = bin(numero)[2:].zfill(cantidadBits)   
                  if self.gpio_0 == variablesGlobales.Pin_W1_WD0:
                     id = int(numeroBinario.format(numero)[hbl.WD_W1_primerBit:int(cantidadBits-1)],2) 
                     variablesGlobales.WD1_Data = id
                  else:
                     id = int(numeroBinario.format(numero)[hbl.WD_W2_primerBit:int(cantidadBits-1)],2) 
                     variablesGlobales.WD2_Data = id

               except: 

                  log.escribeLineaLog(hbl.LOGS_hblWiegand, "ERROR 100 : Wiegand IN")
                  # hardcode de valor de error
                  numero = 99999
                  id = numero    

               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Fecha / Hora : " + str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Cant. Bits : " + str(cantidadBits))
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Valor Binario : " + str(numeroBinario))
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "ID : " + str(id))
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "-------------------------")


               # funcionamiento del hbl segun modo seleccionado
               # 0 : repetidor wiegand
               if hbl.FUNC_modo == 0:
                  self.repetidorID(cantidadBits, numero, numeroBinario, id, self.pi)
               
               # 1 : funcionamiento supeditado al request
               elif hbl.FUNC_modo == 1:
                  # si esta activo el modo de espera senial, debe esperar que
                  # se active esa entrada digital por el reloj para leer los datos
                  # validos que llegan al puerto

                  if hbl.WD_W1_esperaSenial == 1:
                     valorPin = Entradas.readPin(self.pi, variablesGlobales.Pin_Entrada2)

                     # se activa la entrada
                     if valorPin == 0: 
                           self.procesarID_Request(cantidadBits, numero, numeroBinario, id, self.pi)

                  # si no esta activo el modo espera senial, envia el dato directamente
                  # para el proceso sin leer la entrada digital
                  else:
                     self.procesarID_Request(cantidadBits, numero, numeroBinario, id, self.pi)
               
               # 2 : decodificado wiegand - TCP
               elif hbl.FUNC_modo == 2:

                  self.procesarID_TCP(cantidadBits, numero, numeroBinario, id, self.pi) 
               
               # 6 : decodificador wiegand W1 -> envio request a URL
               elif hbl.FUNC_modo == 6:

                  self.procesarID_URL(cantidadBits, numero, numeroBinario, id, self.pi)

               # 9 : decodificado wiegand - JSON
               elif hbl.FUNC_modo == 9:
               
                  if id!=99999:
                     self.procesarID_JSON(cantidadBits, numero, numeroBinario, id, self.pi) 

               # 10 : Funcionamiento de Workpass
               elif hbl.FUNC_modo == 10:

                  self.Workpass(cantidadBits, numero, numeroBinario, id, self.pi) 

               
               else:
                  pass

     
   """ --------------------------------------------------------------------------------------------

         Funcionamiento : Repetidor wiegand

         Identificador :  0

   -------------------------------------------------------------------------------------------- """
    
   def repetidorID(self, cantidadBits, numero, numeroBinario, id, pi):
      auxiliar.EscribirFuncion("Decoder - repetidorID")
      
      # escribe separador en el archivo log + la fecha actual
      log.escribeSeparador(hbl.LOGS_hblWiegand) 
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "Cant. Bits : " + str(cantidadBits))
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "Valor Binario : " + str(numeroBinario))
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "ID : " + str(id))
      
      
      # codificacion y envio del valor wiegand
      Encoder.encoderWiegand(numero, self.pi, variablesGlobales.Pin_W2_WD0, variablesGlobales.Pin_W2_WD1, cantidadBits)

      # indica status     
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "Codigo Wiegand Retransmitido")    


   """ --------------------------------------------------------------------------------------------

         Proceso ID wiegand + Request

         1 : funcionamiento supeditado al request

   -------------------------------------------------------------------------------------------- """
               
   def procesarID_Request(self, cantidadBits, numero, numeroBinario, id, pi): 
      auxiliar.EscribirFuncion("Decoder - procesarID_Request")

      # escribe separador en el archivo log + la fecha actual
      log.escribeSeparador(hbl.LOGS_hblWiegand) 
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "Cant. Bits : " + str(cantidadBits))
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "Valor Binario : " + str(numeroBinario))
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "ID : " + str(id))


      # mode 1 : transmision de datos sin chequeo de request
      # mode 2 : chequea el status del request para transmitir o no

      if hbl.REQ_activado == 0:
  
         log.escribeLineaLog(hbl.LOGS_hblWiegand, "Retransmision activada sin request")
         # codifico el valor wiegand y envio por salida wiegand 

         Encoder.encoderWiegand(numero, pi, variablesGlobales.Pin_W2_WD0, variablesGlobales.Pin_W2_WD1, cantidadBits)

      else: 
         
         log.escribeLineaLog(hbl.LOGS_hblWiegand, "Retransmision chequeada segun request")

         if hbl.REQ_seleccionURL == 1:
            UrlCompletaReq = hbl.REQ_urlRequest1 + str(id)
         elif hbl.REQ_seleccionURL == 2:
            UrlCompletaReq = hbl.REQ_urlRequest2 + str(id)
         elif hbl.REQ_seleccionURL == 3:
            UrlCompletaReq = hbl.REQ_urlRequest3 + str(id)
         elif hbl.REQ_seleccionURL == 4:
            UrlCompletaReq = hbl.REQ_urlRequest4 + str(id)
         elif hbl.REQ_seleccionURL == 5:
            UrlCompletaReq = hbl.REQ_urlRequest5 + str(id) 
         
         # Guardo la url completa para el request
         log.escribeLineaLog(hbl.LOGS_hblWiegand, "Url request : " + UrlCompletaReq)

         if hbl.REQ_timerActivado == 1:
            # arranco el timer
            tic = time.perf_counter()

         # Realiza el request
         try:
            req = requests.get(UrlCompletaReq, timeout=int(hbl.REQ_timeoutRequest))
            
            # Busca la palabra true en el request
            x = req.text.find("true") 
            
            log.escribeLineaLog(hbl.LOGS_hblWiegand, "Find: " + str(x))

            # retransmite si el request es True sino no retransmite
            if x == -1 :
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Request FALSE")
               
               # Guardo la respuesta del request
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Request : " + req.text)

               # escribe que salidas se activan y su uso    
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Enciende Rele 1 (Luz) - Rele 2 (Sirena)") 

               self.pi.write(variablesGlobales.Pin_Salida1, hbl.ON)   
               self.pi.write(variablesGlobales.Pin_Salida2, hbl.ON)  

               # delay mantener encendido el rele                       
               time.sleep(int(hbl.DIG_out_out1_tiempo))

               # escribe que salidas se desactivan y su uso    
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Apaga Rele 1 (Luz) - Rele 2 (Sirena)")    

               self.pi.write(variablesGlobales.Pin_Salida1, hbl.OFF)   
               self.pi.write(variablesGlobales.Pin_Salida2, hbl.OFF) 
         
            elif x != -1 :

               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Request TRUE")

               # Guardo la respuesta del request
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Request : " + req.text)
               
               # escribe que salida se activa y su uso    
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Enciende Rele 4 (Molinete)") 

               # Abre el molinete
               self.pi.write(variablesGlobales.Pin_Salida4, hbl.ON4)   

               # delay mantener encendido el rele
               time.sleep(int(hbl.DIG_out_out1_tiempo))

               # cierra molinete
               self.pi.write(variablesGlobales.Pin_Salida4, hbl.OFF)

               # escribe que salida se desactiva y su uso    
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Apaga Rele 4 (Molinete)") 
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "Codigo Wiegand Retransmitido") 

               # codifico el valor wiegand y envio por salida wiegand 
               Encoder.encoderWiegand(numero, self.pi, variablesGlobales.Pin_W2_WD0, variablesGlobales.Pin_W2_WD1, cantidadBits)

         except Exception as inst: 

            # timeout request  
            log.escribeLineaLog(hbl.LOGS_hblWiegand, "ERROR : " + str(inst) + "\n" + "\n") 

            # disparo la URL de error
            try:
               req = requests.get(hbl.REQ_urlError, timeout=int(hbl.REQ_timeoutRequest))

            except Exception as inst2: 
               
               # timeout url error request  
               log.escribeLineaLog(hbl.LOGS_hblWiegand, "ERROR : " + str(inst2) + "\n" + "\n") 

         if hbl.REQ_timerActivado == 1:             
            # apago el timer
            toc = time.perf_counter()
            
            log.escribeLineaLog(hbl.LOGS_hblWiegand, "Tiempo transcurrido: " + str(toc-tic) + "\n" + "\n")
 

   """ --------------------------------------------------------------------------------------------

         Proceso ID wiegand + TCP

         2 : decodificado wiegand - TCP

   -------------------------------------------------------------------------------------------- """ 

   def procesarID_TCP(self, cantidadBits, numero, numeroBinario, id, pi):
      
      auxiliar.EscribirFuncion("Decoder - procesarID_TCP")
 
      # escribe separador + fecha + hora
      log.escribeSeparador(hbl.LOGS_hblWiegand) 
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "Cant. Bits : " + str(cantidadBits))
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "Valor Binario : " + str(numeroBinario))
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "ID : " + str(id))
      
       
      # inicializacion conexion TCP 
      status = tcp.iniciarConexion() 

      # si se conecto correctamente al servidor
      if status == 1: 

         # envio del ID por conexion TCP
         status = tcp.envioTCP(id) 
         
         if status == 1:  
            log.escribeLineaLog(hbl.LOGS_hblWiegand, "Fecha / Hora : " + str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
            log.escribeLineaLog(hbl.LOGS_hblWiegand, "ID enviado : " + str(id))  
            log.escribeLineaLog(hbl.LOGS_hblWiegand, "\n") 
   
   """ --------------------------------------------------------------------------------------------

         Proceso ID wiegand + Request

         6 : decodificador wiegand W1 -> envio request a URL

   ----------------------------------------------------------|---------------------------------- """ 

   def procesarID_URL(self, cantidadBits, numero, numeroBinario, id, pi):
      auxiliar.EscribirFuncion("Decoder - procesarID_URL")
 
      # escribe separador + fecha + hora
      log.escribeSeparador(hbl.LOGS_hblWiegand) 
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "Cant. Bits : " + str(cantidadBits))
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "Valor Binario : " + str(numeroBinario))
      log.escribeLineaLog(hbl.LOGS_hblWiegand, "ID : " + str(id))
       
      try:

         # Creo un diccionario con el dato wiegand y el id del dispositivo 
         Dict = {  
            "wiegand" : str(id), 
            "deviceid" : str(hbl.ID_HBL)         
         }    

         log.escribeLineaLog(hbl.LOGS_hblWiegand, "JSON envio : " + str(Dict))  
            
         newheaders = {   
            'Content-Type': 'application/json'
         }  

         if hbl.REQ_seleccionURL == 1:
            URL_POST = hbl.REQ_urlRequest1 
         elif hbl.REQ_seleccionURL == 2:
            URL_POST = hbl.REQ_urlRequest2 
         elif hbl.REQ_seleccionURL == 3:
            URL_POST = hbl.REQ_urlRequest3 
         elif hbl.REQ_seleccionURL == 4:
            URL_POST = hbl.REQ_urlRequest4 
         elif hbl.REQ_seleccionURL == 5:
            URL_POST = hbl.REQ_urlRequest5 
      
  
         response = requests.post(URL_POST, json = Dict, headers = newheaders, timeout=int(hbl.REPORTE_timeOutRequest))

         # response del request  
         log.escribeLineaLog(hbl.LOGS_hblWiegand, "\n") 
         log.escribeLineaLog(hbl.LOGS_hblWiegand, response.text) 

      except Exception as inst: 

         log.escribeLineaLog(hbl.LOGS_hblWiegand, "\n")     
         log.escribeLineaLog(hbl.LOGS_hblWiegand, "Error : " + str(inst))    

   """ --------------------------------------------------------------------------------------------

         Proceso ID wiegand + JSON 

         9 : decodificado wiegand - JSON

   -------------------------------------------------------------------------------------------- """ 

   def procesarID_JSON(self, cantidadBits, numero, numeroBinario, id, pi):
      auxiliar.EscribirFuncion("Decoder - procesarID_JSON")
 
      try:
         # path del archivo
         datapath= '/var/www/html/wms'

         # Leo los parametros de configuracion en el JSON
         #with open(os.path.join(datapath , 'dato.json'), "r") as f:
         #      dato = json.load(f)

         ## grabo el id
         #dato["dni"] = str(id)
         dato = {
            'datos': str(id)
         }

         # actualizo los parametros en el JSON
         with open(os.path.join(datapath , 'datos.json'), "w") as f:
               #json.dump(dato, f, indent=4)  
               json.dump(dato, f) 

         log.escribeLineaLog(hbl.LOGS_hblWiegand, "JSON ID actualizado : " + str(id))  
         log.escribeLineaLog(hbl.LOGS_hblWiegand, "\n") 

      except Exception as inst: 

         log.escribeLineaLog(hbl.LOGS_hblWiegand, "\n")     
         log.escribeLineaLog(hbl.LOGS_hblWiegand, "Error : Dato no actualizado") 


   
   def Workpass(self, cantidadBits, numero, numeroBinario, id, pi):
      auxiliar.EscribirFuncion("Decoder - Workpass")

      print("Modo 10")

      if hbl.REQ_seleccionURL == 1:
         TextoURL = hbl.REQ_urlRequest1 
      elif hbl.REQ_seleccionURL == 2:
         TextoURL = hbl.REQ_urlRequest2 
      elif hbl.REQ_seleccionURL == 3:
         TextoURL = hbl.REQ_urlRequest3 
      elif hbl.REQ_seleccionURL == 4:
         TextoURL = hbl.REQ_urlRequest4 
      elif hbl.REQ_seleccionURL == 5:
         TextoURL = hbl.REQ_urlRequest5 
      
      TextoHBL=hbl.IDHBL

      
      
      """ Armar la URL completa """   
      try: 

         URLCompleta = TextoURL + "?" + "hbl=" + TextoHBL + "&" + "dni=" + str(id)
         print(URLCompleta)

         #webbrowser.open(URLCompleta) 
         x = requests.get(URLCompleta)
                  
         print(x.status_code)
         
         """ escribo el error en el archivo txt """
         #file1 = open("/var/log/wiegand/event.txt", "a")
         #file1.write(str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
         #file1.write(str(" - ")) 
         #file1.write("URL OK")
         #file1.write("\n")
         #file1.close()
         
         log.escribeLineaLog(hbl.LOGS_hblWiegand, "URL OK \n")
      
      except:
         print("Error en archivo de configuracion")
         
         """ escribo el error en el archivo txt """
         #file1 = open("/home/pi/Desktop/wiegand/event.txt", "a")
         #file1.write(str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
         #file1.write(str(" - ")) 
         #file1.write("Error de lectura en los parametros de configuración.")
         #file1.write("\n")
         #file1.close()
         log.escribeLineaLog(hbl.LOGS_hblWiegand, "Error de lectura en los parametros de configuración\n")
               #self.procesarID_URL(cantidadBits, numero, numeroBinario, id, self.pi)
               


   """ --------------------------------------------------------------------------------------------
 

        Cancela el callback decoder


   -------------------------------------------------------------------------------------------- """
    
   def cancel(self):
      auxiliar.EscribirFuncion("Decoder - cancel")
 
      self.cb_0.cancel()
      self.cb_1.cancel()
 