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
            self.pi.write(vg.Pin_Salida1,hbl.ON)
            #
            #VARIABLES ASOCIADAS A LA MAQ DE EST
            #
            self.ID = hbl.Contador_ID
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
            self.entrantes = 0
            self.salientes = 0
            

            
            #
            #TAREAS
            #
            self.log = log.LogReport() 
                       
            self.thread = Thread( target=self.__Control_FSM,
                                  daemon=False)
            
            self.Alarma = alarma( self.pi, name= "Alarma", logObject=self.log)
            
            self.timerFichada = temporizador(self.log,
                                             self.MaxTimeIN, 
                                             self.__cbFichadavencida, 
                                             name="TimerFichada",
                                             debug=True
                                             )
            
            self.timerPuertaAbierta = temporizador(self.log,
                                                   5,  
                                                   self.__cbAlarmaPuertaAbierta,
                                                   name="TimerAlarmaPuertaAbierta",
                                                   debug=True,
                                                   status="PuertaCerrada"
                                                )
                #"MaxTimePuerta": 720,
                #"MaxTimeEnable": 180,
                #"MaxTimeDisable": 420,
            
            self.timerReloj = temporizador(self.log,60, self.__cbTimerReloj,
                                                   name="TimerReloj")
            
            self.timerReport = temporizador(self.log,60, self.__InformarServidor,
                                                name = "TimerReport",
                                                debug=False)
            self.timerReport.start()
            self.timerReloj.start()
            self.thread.start()
            self.__LogReport("Modo Contador Inicializado")

            if auxiliar.CheckInternet():
                self.ClienteMqtt.publish("Contador: " + hbl.Contador_ID)

    
    #metodos privados
    def __cbTimerReloj(self):
        self.timerReloj.stop()
        self.lcd1.lcdWrite(0,str(datetime.datetime.now().strftime("  %d/%m/%Y %H:%M")))
        self.timerReloj.start()
        
    def __Leer_Ordenes_Server(self, client, userdata, msg): 
        try:
            data = msg.payload.decode()
            self.ClienteMqtt.LogReport(f"Received from {msg.topic} topic: \n{data} ")
            data = json.loads(data)
            
            
            ID  = data.get("ID").strip(" ")
            cantidad = data.get("CANTIDAD")
            if ID == hbl.Contador_ID.strip(" ") and cantidad != None :
                self.CantidadDePersonas = int(cantidad)
                self.entrantes = 0
                self.salientes = 0
                
                self.Actualizarlcd() 
        except:
            pass
    
    def __cbAlarmaPuertaAbierta(self):
        #Activo la alarma con la rutina del buzzer de puerta abierta
        #esto deberia rearmar el timer de manera de realizar otra cuenta
        #que mantendra la alarma activada osea otro thread
        #luego que de vencerse este otro hilo que mantenga la alarma desactivada
        #durante cierto periodo
        # y despues volver a la operacion normal
        self.__Timer()
        self.timerPuertaAbierta.stop()
        
        #si se vence el timer de la puerta abierta paso a activar la alarm
        if self.timerPuertaAbierta.status() == "PuertaAbierta":
            self.timerPuertaAbierta.setEncendido(self.MaxTimeEnable)
            self.mail.sendDoorMail()
            self.Alarma.SonarAlarmaPuertaAbierta()
            
        #si la puerta no se cerro apago la alarma
        elif self.timerPuertaAbierta.status() == "AlarmaSonando":
            self.timerPuertaAbierta.setDesactivado(self.MaxTimeDisable)
            self.Alarma.stop()
            
        #si no se cerro la puerta se activa la alarma nuevamente
        elif self.timerPuertaAbierta.status() == "AlarmaDesactivada":
            self.timerPuertaAbierta.setEncendido(self.MaxTimeEnable)
            self.Alarma.SonarAlarmaPuertaAbierta()

        self.timerPuertaAbierta.start()
        
    def __cbFichadavencida(self):
        vg.contador -= 1
        if vg.contador > 0:
            #print(f"Fichada Descontada {vg.contador}")
            self.timerFichada.start()
        else:
            self.timerFichada.stop()
            vg.contador = 0
            
            vg.Status = vg.Esperando_Reloj
        vg.LastDNI = 99999999
    
    def __LeerEntradas(self):
        #self.IR1 =  self.pi.read(vg.Pin_Entrada1)
        #self.IR2 =  self.pi.read(vg.Pin_Entrada2)
        
        #self.prevEstadoPuerta = self.EstadoPuerta
        #self.EstadoPuerta  = self.pi.read(vg.Pin_Entrada3)
        '''
        if  vg.auxIR1 != self.IR1 and vg.auxIR2 != self.IR2:
            #self.lcd1.lcdWrite(2, str(vg.auxIR1) + str(vg.auxIR2),debug= True)
            
            vg.auxIR2 = self.IR2
            vg.auxIR1 = self.IR1
            print(str(self.IR1) + str(self.IR2))
            
        elif vg.auxIR1 != self.IR1:
            #self.lcd1.lcdWrite(2, str(vg.auxIR1) + '0',debug= True)
            
            vg.auxIR1 = self.IR1
            print(str(self.IR1) + str(self.IR2))
                
        elif vg.auxIR2 != self.IR2:
            #self.lcd1.lcdWrite(2, '0' + str(vg.auxIR2) ,debug= True)
            
            vg.auxIR2 = self.IR2
            print(str(self.IR1) + str(self.IR2))
        '''
    
    def __Timer(self):
        self.prevEstadoPuerta = self.EstadoPuerta
        self.EstadoPuerta  = self.pi.read(vg.Pin_Entrada3)
        #EL TIMER SE INICIA CADA VEZ QUE SE ABRE LA PUERTA
        #Y SE DETIENE CADA VEZ QUE SE CIERRA
        if self.EstadoPuerta > self.prevEstadoPuerta: 
            #si abro la puerta la entrada pasa a 0
            vg.flagPuerta = True
            self.timerPuertaAbierta.Status = "PuertaAbierta"
            self.timerPuertaAbierta.start()
            print("corriendo timer")
                
        elif self.EstadoPuerta < self.prevEstadoPuerta:
            #si cierro la puerta la entrada pasa a 1
            if self.timerPuertaAbierta.is_running():
                self.timerPuertaAbierta.Status = "PuertaCerrada"
                self.timerPuertaAbierta.stop()
                if self.Alarma.Status == "PuertaAbierta":
                    
                    self.Alarma.Status = ""
                    self.Alarma.stop()
                print("timer detenido")
            vg.flagPuerta = False   

    def __Control_FSM(self):
        while True:
            self.__Timer()
            if vg.Status == vg.Esperando_Reloj:   
                if vg.contador:
                    
                    self.fichada()
                    vg.Status = vg.Esperando_IR1
                    
            elif vg.Status == vg.EntradaCompleta:

                    self.ingresoValido()
                    vg.Status = vg.Esperando_Reloj                    

            elif vg.Status == vg.Intruso:

                    self.intruso_detectado()
                    vg.Status = vg.Esperando_Reloj
                    
            elif vg.Status == vg.Persona_Saliente:

                    self.salida()
                    vg.Status = vg.Esperando_Reloj
                    
                
    
    '''    
    def __Control_FSM(self):
        while True:
            #self.__LeerEntradas()
            #self.__Timer()
            #
            #DETECCION DE RUTINA
            # 
            if vg.Modo == vg.Esperando:
                if vg.Status == vg.Esperando_Reloj:
                    if vg.IR1 and not vg.IR2 and not vg.contador:
                        
                        vg.Modo = vg.Intruso
                        #self.__LogReport("Posible Intruso, verificando sentido")
                        
                    if vg.contador:
                        
                        self.fichada()
                        #self.__LogReport("Esperando IR1")
                        vg.Status = vg.Esperando_IR1
                        
                    if not vg.IR1 and vg.IR2:
                        pass
                        #vg.Status = vg.Esperando_IR1_IR2_Saliente
                        #self.__LogReport("Posible Saliente")
            #
            #SECUENCIA ENTRANTE
            # 
            
            elif vg.Modo == vg.Entrante:
                
                if vg.Status == vg.Esperando_IR1:
                    if vg.IR1 and not vg.IR2:
            
                        #self.__LogReport("Esperando IR1 y IR2")
                        vg.Status = vg.Esperando_IR1_IR2
                        
                elif vg.Status == vg.Esperando_IR1_IR2:
                    if vg.IR1 and vg.IR2:

                        #self.__LogReport("Esperando IR2")
                        vg.Status = vg.Esperando_IR2
                        
                elif vg.Status == vg.Esperando_IR2:
                    if not vg.IR1 and vg.IR2:

                        #self.__LogReport("Esperando que se libere IR2")
                        vg.Status = vg.Esperando_CompletarCiclo
                        
                elif vg.Status == vg.Esperando_CompletarCiclo:
                    if not vg.IR1 and not vg.IR2:
                        self.ingresoValido()
                    
            #
            #SECUENCIA INTRUSO
            #
            elif vg.Modo == vg.Intruso:
                
                if vg.Status == vg.VerificacionIntruso: #s1 = 1 , s2 = 0
                    if vg.IR1 and vg.IR2 and self.EstadoPuerta:
                        vg.Status = vg.VerificacionIntruso2
                        #self.__LogReport("verificacion de intruso 1")
                        
                    elif not vg.IR1 and not vg.IR2:
                        vg.Status = vg.Esperando_Reloj
                        
                elif vg.Status == vg.VerificacionIntruso2: #s1 = 1 , s2 = 1
                    if not vg.IR1 and vg.IR2 and self.EstadoPuerta:
                        #self.__LogReport("Verificacion de intruso 2")
                        vg.Status = vg.VerificacionIntruso3
                        
                    elif vg.IR1 and not vg.IR2:
                        vg.Status = vg.VerificacionIntruso
                        
                elif vg.Status == vg.VerificacionIntruso3:
                    if not vg.IR1 and not vg.IR2 and self.EstadoPuerta:
                        vg.Status = vg.Esperando_Reloj
                        #self.__LogReport("Verificacion de intruso completa sonara la alarma", "full")
                        #
                        # Rutina de aviso
                        #
                        self.intruso_detectado()
                        
                    elif vg.IR1 and vg.IR2:
                        vg.Status = vg.VerificacionIntruso2
            #
            #SECUENCIA SALIENTE
            #
            elif vg.Modo == vg.Saliente:
                        
                if vg.Status == vg.Esperando_IR1_IR2_Saliente:#s1 = 0 , s2 = 1
                    if vg.IR1 and vg.IR2 and self.EstadoPuerta:
                        #self.__LogReport("Posible Intruso Estado:Esperando IR1 IR2 Saliente")
                        vg.Status = vg.Esperando_IR1_Saliente
                        
                    if not vg.IR1 and not vg.IR2:
                        vg.Status = vg.Esperando_Reloj
                    
                elif vg.Status == vg.Esperando_IR1_Saliente:# s1 = 1 , s2 = 1
                    if self.IR1 and not self.IR2 and self.EstadoPuerta:
                        
                        #self.__LogReport("Intruso casi confirmado Estado: Esperando IR1 Saliente")
                        vg.Status = vg.Confirmando_Saliente
                        
                    elif not self.IR1 and self.IR2:
                        vg.Status = vg.Esperando_IR1_IR2_Saliente
                        
                    
                elif vg.Status == vg.Confirmando_Saliente:# s1 = 1 , s2 = 0
                    if not vg.IR1 and not vg.IR2 and self.EstadoPuerta:

                        self.salida()
                        vg.Status = vg.Esperando_Reloj
                        
                    elif vg.IR1 and vg.IR2:
                        vg.Status = vg.Esperando_IR1_Saliente
                    
            #time.sleep(self.MaxTimeCheck)
    '''
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

    def salida(self):
        if self.CantidadDePersonas > 0:
                self.CantidadDePersonas -= 1
                self.actualizarCantidadDePersonas("-1")
        else:
                self.CantidadDePersonas = 0
        
        self.__LogReport("Salida completa", "full","g")
        
    def ingresoValido(self):
        
        self.timerFichada.stop()
       
        vg.contador -= 1
        if vg.contador < 0:
            vg.contador = 0
            self.__LogReport("El contador se paso a negativo")

        self.CantidadDePersonas += 1
        self.actualizarCantidadDePersonas("+1")
        
        #self.__LogReport("Ciclo Completo")
        self.__LogReport(" Ingreso Valido ","full","g")
        
    def intruso_detectado(self):
        
        self.LastAlarma = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.CantidadDePersonas += 1
        self.Alarma.SonarAlarmaIntruso()
        self.actualizarCantidadDePersonas("+1","si")
        self.__LogReport(" Intruso detectado ","full","r")
        
        if auxiliar.CheckInternet():
            print("Envio el mail si esta activado\n")
            self.mail.sendIntrusoMail()
        else:
            print("Agrego intruso \n")
            self.add_intruso(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    
    def __LogReport(self, mensaje, modo = None, color = None):
        self.log.EscribirLinea(hbl.LOGS_hblPuerta)
        
        if modo == 'full':
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"PersonasDentro: "+ str(self.CantidadDePersonas))
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"UltimaEntrada: "+ str(self.lastIN))
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Estado Puerta: "+ str(self.EstadoPuerta))
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Estado: "+ str(self.Status))
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Last DNI: "+ str(vg.LastDNI))
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Last Alarma: "+ str(self.LastAlarma))
        
        self.log.EscribirLinea(hbl.LOGS_hblPuerta,mensaje,color) 
    
    
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
        if personas == "+1":
            self.entrantes += 1
        else:
            self.salientes += 1
        
    def __InformarServidor(self):
        self.timerReport.stop()
        if not self.IR1 and not self.IR2 and (self.entrantes != 0 or self.salientes != 0):
            if auxiliar.CheckInternet():
                self.ClienteMqtt.publish(   '{ "ID"  : "' + hbl.Contador_ID + '",\
                                            "Entrantes"  :"' + str(self.entrantes) + '",   \
                                            "Salientes" : "' + str(self.salientes) + '"  }')
                            
        self.timerReport.start()


        
        
