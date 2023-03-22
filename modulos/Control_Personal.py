import datetime
import time
import json
from modulos import SendMail as SendMail
from modulos import auxiliar as auxiliar
from modulos.entradas import Entradas
import modulos.salidas as salidas
from modulos import variablesGlobales as vg
from modulos import hbl,log,i2cDevice, MQTT
from modulos.SendMail import SendMail
from modulos.timer import temporizador
from modulos.alarma import alarma
from threading import Thread
import pigpio
file_path = 'Intrusos_Pendientes.txt'


        
class Puerta(object):
    #Cada puerta tiene 2 sensores ->  2 entradas
    #                  1 alarma   ->  1 salida
    #                  1 pantalla ->  1 i2c  (imprimir en esta pantalla seria otra tarea pero el control pertenece a este objeto)
    #                  1 rtc      ->  1 i2c
    #                  mails      ->  seria otra tarea pero cada puerta podria reportar a gente distinta
    
    '''
    "MaxTimeIN": 120,
    "MaxTimeAlarma": 0.5,
    "MaxTimeBlink": 3,
    "MaxTimeLEDCicloCompleto": 1000,
    "MaxTimePuerta": 720,
    "MaxTimeEnable": 180,
    "MaxTimeDisable": 420,
    "TiempoBlinkAlarmaPuerta": 1000
    '''
    
    def __init__(self, pi, ClienteMqtt : MQTT.ClientMqtt, 
                 lcd1 : i2cDevice.Lcd):
        if hbl.Contador_activado == 1:
            self.__setTiempos()
            
            #
            #VARIABLES ASOCIADAS A LOS PINES
            #
            
            self.pi : pigpio.pi = pi
            
            vg.flagPuerta = bool( self.pi.read(vg.Pin_Entrada3) )
            self.IR1 = 0
            self.IR2 = 0
            self.EstadoPuerta = 0
            self.lcd1 = lcd1
            #
            #VARIABLES ASOCIADAS A LA MAQ DE EST
            #
            
            self.Status = vg.Esperando_Reloj
            self.AlarmaStatus = ""
            self.contador = vg.contador
            self.lastIN = 0
            self.LastAlarma = 0
            self.CantidadDePersonas = 0
            self.LastDNI = 99999999
            self.ClienteMqtt = ClienteMqtt
            self.ClienteMqtt.handlerRecv = self.__Leer_Ordenes_Server
            self.mail = SendMail()
            #
            #TAREAS
            #            
            self.thread = Thread( target=self.__Control_FSM,
                                  daemon=False)
            
            self.Alarma = alarma(self.pi, name= "Alarma" )
            
            self.timerFichada = temporizador(self.MaxTimeIN, 
                                             self.__cbFichadavencida, 
                                             name="TimerFichada")
            
            self.timerPuertaAbierta = temporizador(self.MaxTimePuerta,
                                                  self.__cbAlarmaPuertaAbierta,
                                                  name="TimerAlarmaPuertaAbierta")
            
            self.timerReloj = temporizador(10, self.__cbTimerReloj,
                                                   name="TimerReloj")
            self.timerReloj.start()
            self.thread.start()
            self.__LogReport("Modo Contador Inicializado")
        else:
            self.__LogReport("Modo Contador Desactivado")
     

    
    #metodos privados
    def __cbTimerReloj(self):
        self.timerReloj.stop()
        self.lcd1.lcdWrite(0,str(datetime.datetime.now().strftime("  %d/%m/%Y %H:%M")))
        self.timerReloj.start()
        
    def __Leer_Ordenes_Server(self, client, userdata, msg): 
        data = msg.payload.decode()
        self.ClienteMqtt.LogReport(f"Received from {msg.topic} topic: \n{data} ")
        data = json.loads(data)
        
        
        cantidad  = data.get("cantidad")
        if( cantidad >= 0):
            self.CantidadDePersonas = cantidad
            
            self.Actualizarlcd() 
    
    
    def __cbAlarmaPuertaAbierta(self):
        #Activo la alarma con la rutina del buzzer de puerta abierta
        #esto deberia rearmar el timer de manera de realizar otra cuenta
        #que mantendra la alarma activada osea otro thread
        #luego que de vencerse este otro hilo que mantenga la alarma desactivada
        #durante cierto periodo
        # y despues volver a la operacion normal
        self.timerPuertaAbierta.stop()
        #si se vence el timer de la puerta abierta paso a activar la alarm
        if self.timerPuertaAbierta.Status == "EsperandoPuertaAbierta":
            self.timerPuertaAbierta.Status = "AlarmaSonando"
            self.timerPuertaAbierta.setSegundos(self.MaxTimeEnable)
            if self.Alarma.Status == "Intruso":
                time.sleep(5)
            self.Alarma.Status = "PuertaAbierta"
            self.Alarma.start()
            
            
        #si la puerta no se cerro apago la alarma
        elif self.timerPuertaAbierta.Status == "AlarmaSonando":
            self.timerPuertaAbierta.Status = "AlarmaDesactivada"
            if self.Alarma.is_running():
                self.Alarma.Status = ""
                self.Alarma.stop()

            self.timerPuertaAbierta.setSegundos(self.MaxTimeDisable)
            
            
        #si no se cerro la puerta se activa la alarma nuevamente
        elif self.timerPuertaAbierta.Status == "AlarmaDesactivada":
            self.timerPuertaAbierta.setSegundos(self.MaxTimeEnable)
            self.timerPuertaAbierta.Status = "AlarmaSonando"
            if self.Alarma.Status == "Intruso":
                time.sleep(5)
            self.Alarma.Status = "PuertaAbierta"
            self.Alarma.start()

        self.timerPuertaAbierta.start()
        
    def __cbFichadavencida(self):
        vg.contador -= 1
        if vg.contador > 0:
            #print(f"Fichada Descontada {vg.contador}")
            self.timerFichada.start()
        else:
            self.timerFichada.stop()
            vg.contador = 0
            
            self.Status = vg.Esperando_Reloj
        vg.LastDNI = 99999999
    
    def __LeerEntradas(self):
        self.IR1 = not self.pi.read(vg.Pin_Entrada1)
        self.IR2 = not self.pi.read(vg.Pin_Entrada2)
        self.prevEstadoPuerta = self.EstadoPuerta
        self.EstadoPuerta  = self.pi.read(vg.Pin_Entrada3)
    
       
    def __Timer(self):
        #EL TIMER SE INICIA CADA VEZ QUE SE ABRE LA PUERTA
        #Y SE DETIENE CADA VEZ QUE SE CIERRA
        if self.EstadoPuerta > self.prevEstadoPuerta: 
            #si abro la puerta la entrada pasa a 0
            vg.flagPuerta = True
            self.timerPuertaAbierta.start()
            print("corriendo timer")
                
        elif self.EstadoPuerta < self.prevEstadoPuerta:
            #si cierro la puerta la entrada pasa a 1
            if self.timerPuertaAbierta.is_running():
                self.timerPuertaAbierta.stop()
                if self.Alarma.Status == "PuertaAbierta":
                    self.Alarma.Status =""
                    self.Alarma.stop()
                print("timer detenido")
            vg.flagPuerta = False
        
    def __LogReport(self, mensaje):
        log.escribeSeparador(hbl.LOGS_hblPuerta)
        
        log.escribeLineaLog(hbl.LOGS_hblPuerta, "PersonasDentro: "+ str(self.CantidadDePersonas))
        log.escribeLineaLog(hbl.LOGS_hblPuerta, "UltimaEntrada: "+ str(self.lastIN))
        log.escribeLineaLog(hbl.LOGS_hblPuerta, "Estado Puerta: "+ str(self.EstadoPuerta))
        log.escribeLineaLog(hbl.LOGS_hblPuerta, "Estado: "+ str(self.Status))
        log.escribeLineaLog(hbl.LOGS_hblPuerta, "Last DNI: "+ str(vg.LastDNI))
        log.escribeLineaLog(hbl.LOGS_hblPuerta, "Last Alarma: "+ str(self.LastAlarma))
        
        log.escribeLineaLog(hbl.LOGS_hblPuerta, mensaje)    
        
    def __Control_FSM(self):
        while True:
            self.__LeerEntradas()
            self.__Timer()
            #
            #DETECCION DE RUTINA
            # 
            
            if self.Status == vg.Esperando_Reloj:
                if self.IR1 and not self.IR2 and not vg.contador:
                    
                    self.Status = vg.VerificacionIntruso
                    self.__LogReport("Posible Intruso, verificando sentido")
                    
                if vg.contador:
                    
                    self.fichada()
                    self.__LogReport("Esperando IR1")
                    self.Status = vg.Esperando_IR1
                    
                if not self.IR1 and self.IR2:
                    self.Status = vg.Esperando_IR1_IR2_Saliente
                    self.__LogReport("Posible Saliente")
            #
            #SECUENCIA ENTRANTE
            # 
            
            elif self.Status == vg.Esperando_IR1:
                if self.IR1 and not self.IR2:
        
                    self.__LogReport("Esperando IR1 y IR2")
                    self.Status = vg.Esperando_IR1_IR2
                    
            elif self.Status == vg.Esperando_IR1_IR2:
                if self.IR1 and self.IR2:

                    self.__LogReport("Esperando IR2")
                    self.Status = vg.Esperando_IR2
                    
            elif self.Status == vg.Esperando_IR2:
                if not self.IR1 and self.IR2:

                    self.__LogReport("Esperando que se libere IR2")
                    self.Status = vg.Esperando_CompletarCiclo
                    
            elif self.Status == vg.Esperando_CompletarCiclo:
                if not self.IR1 and not self.IR2:
                    self.ingresoValido()
                    
            #
            #SECUENCIA INTRUSO
            # 
                 
            elif self.Status == vg.VerificacionIntruso: #s1 = 1 , s2 = 0
                if self.IR1 and self.IR2 and self.EstadoPuerta:
                    self.Status = vg.VerificacionIntruso2
                    self.__LogReport("verificacion de intruso 1")
                    
                elif not self.IR1 and not self.IR2:
                    self.Status = vg.Esperando_Reloj
                    
            elif self.Status == vg.VerificacionIntruso2: #s1 = 1 , s2 = 1
                if not self.IR1 and self.IR2 and self.EstadoPuerta:
                    self.__LogReport("Verificacion de intruso 2")
                    self.Status = vg.VerificacionIntruso3
                    
                elif self.IR1 and not self.IR2:
                    self.Status = vg.VerificacionIntruso
                    
            elif self.Status == vg.VerificacionIntruso3:
                if not self.IR1 and not self.IR2 and self.EstadoPuerta:
                    self.Status = vg.Esperando_Reloj
                    self.__LogReport("Verificacion de intruso completa sonara la alarma")
                    #
                    # Rutina de aviso
                    #
                    self.intruso_detectado()
                    
                elif self.IR1 and self.IR2:
                    self.Status = vg.VerificacionIntruso2
            #
            #SECUENCIA SALIENTE
            #        
            elif self.Status == vg.Esperando_IR1_IR2_Saliente:#s1 = 0 , s2 = 1
                if self.IR1 and self.IR2 and self.EstadoPuerta:
                    self.__LogReport("Posible Intruso Estado:Esperando IR1 IR2 Saliente")
                    self.Status = vg.Esperando_IR1_Saliente
                    
                if not self.IR1 and not self.IR2:
                    self.Status = vg.Esperando_Reloj
                
            elif self.Status == vg.Esperando_IR1_Saliente:# s1 = 1 , s2 = 1
                if self.IR1 and not self.IR2 and self.EstadoPuerta:
                    
                    self.__LogReport("Intruso casi confirmado Estado: Esperando IR1 Saliente")
                    self.Status = vg.Confirmando_Saliente
                    
                elif not self.IR1 and self.IR2:
                    self.Status = vg.Esperando_IR1_IR2_Saliente
                    
                
            elif self.Status == vg.Confirmando_Saliente:# s1 = 1 , s2 = 0
                if not self.IR1 and not self.IR2 and self.EstadoPuerta:
                    if self.CantidadDePersonas > 0:
                        self.CantidadDePersonas -= 1
                        self.actualizarCantidadDePersonas("-1")
                    else:
                        self.CantidadDePersonas = 0
                    
                    self.Status = vg.Esperando_Reloj
                    self.__LogReport("Cantidad De personas dentro: " + str(self.CantidadDePersonas))
                    
                elif self.IR1 and self.IR2:
                    self.Status = vg.Esperando_IR1_Saliente
                    
            time.sleep(self.MaxTimeCheck)
    
    def __setTiempos(self):
        self.MaxTimeIN               = hbl.Contador_MaxTimeIN                      #Tiempo de gracia que se le da a la persona para finalizar el ingreso una vez que ficho            self.MaxTimeCheck            =  0.02
        self.MaxTimeAlarma           = hbl.Contador_MaxTimeAlarma                  #Quizas innecesario reemplazado por maxtimeEnable
        self.MaxTimeBlink            = hbl.Contador_MaxTimeBlink                   #Tiempo que blinkea la alarma por intruso
        self.MaxTimeLEDCicloCompleto = hbl.Contador_MaxTimeLEDCicloCompleto        
        self.MaxTimePuerta           = hbl.Contador_MaxTimePuerta                  #Tiempo que tiene que estar la puerta abierta para que empiece a sonar el buzzer
        self.MaxTimeEnable           = hbl.Contador_MaxTimeEnable                  #Tiempo que pasa la alarma encendida por puerta abierta
        self.MaxTimeDisable          = hbl.Contador_MaxTimeDisable                 #Tiempo que pasa la alarma por puerta abierta desactivada
        self.TiempoBlinkAlarmaPuerta = hbl.Contador_TiempoBlinkAlarmaPuerta                     
        self.MaxTimeCheck            = 0.002                                       #Tiempo entre iteraciones en la maquina de estados

    def fichada(self):
        #inicio timer tiempo de gracia para fichar
        self.timerFichada.start()
        self.lastIN = datetime.datetime.now() 

    def ingresoValido(self):
        self.timerFichada.stop()
       
        vg.contador -= 1
        if vg.contador < 0:
            vg.contador = 0
            self.__LogReport("El contador se paso a negativo")

        self.CantidadDePersonas += 1
        self.actualizarCantidadDePersonas("+1")
        self.Status = vg.Esperando_Reloj
        
        
        self.__LogReport("Ciclo Completo")
        self.__LogReport("Cantidad De personas dentro: " + str(self.CantidadDePersonas))
        
    def intruso_detectado(self):
        
        self.LastAlarma = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.CantidadDePersonas += 1
        self.Alarma.Status = "Intruso"
        self.Alarma.start()
        self.actualizarCantidadDePersonas("+1","si")
        
        if auxiliar.CheckInternet():
            print("Envio el mail si esta activado\n")
            self.mail.send()
        else:
            print("Agrego intruso \n")
            self.add_intruso(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    
    def add_intruso(self, date):
        myFile = open(hbl.Contador_IntrusosPendientesPath, 'a')

        with myFile:
            myFile.write(date + "\n")
            myFile.close() 
        self.mail.pendientes = True 
            
    def Actualizarlcd(self):
        espacios = "          "
        len = str(self.CantidadDePersonas).__len__()

        quitar = int(len/2)
            
        if quitar:
            espacios = espacios[:-quitar]
        #print(aux+str(self.CantidadDePersonas))
         
        self.lcd1.lcdWrite(2,espacios+str(self.CantidadDePersonas))

    def actualizarCantidadDePersonas(self,personas : str ,intruso : str = "no"):
        self.Actualizarlcd()
        self.ClienteMqtt.publish('{ "puerta"  : "Acesso Repetto",\
                                    "cambio"  : ' +personas+ ',   \
                                    "intruso" : "'+intruso + '"  }')            



        
        
