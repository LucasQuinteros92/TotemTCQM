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
    "SegundosParafichar": 120,
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
            self.Router = RouterWifi(self.pi, vg.Pin_Salida3)
            self.entrantes = 0
            self.salientes = 0
            self.FueraDeHorario = False
            self.cuentaAcumulada = 0
            self.conexionesFallidas = 0
        
            #
            #TAREAS
            #
            self.log = log.LogReport(name = "logControlPersonal") 
                       
            self.thread = Thread( target=self.__Control_FSM,
                                  daemon=False, name = "ControlPersonal")
            
            self.Alarma = alarma( self.pi, name= "Alarma", logObject=self.log)
            
            self.timerFichada = temporizador(self.log,
                                             self.SegundosParafichar, 
                                             self.__cbFichadavencida, 
                                             name="TimerFichada",
                                             debug=True
                                             )
            
            self.timerPuertaAbierta = temporizador(self.log,
                                                   self.MaxTimePuertaAbierta,  
                                                   self.__cbAlarmaPuertaAbierta,
                                                   name="TimerAlarmaPuertaAbierta",
                                                   debug=True,
                                                   status="PuertaCerrada"
                                                )
                #"MaxTimePuerta": 720,
                #"MaxTimeEnable": 180,
                #"MaxTimeDisable": 420,
            
            self.timerReloj = temporizador(self.log,30, self.__cbTimerReloj,
                                                   name="TimerReloj")
            
            self.timerReport = temporizador(self.log,60, self.__InformarServidor,
                                                name = "TimerReport",
                                                debug=False)
            
            
            self.timerReport.start()
            self.timerReloj.start()
            self.thread.start()
            self.__LogReport("Modo Contador Inicializado")
            
            
            while not self.ClienteMqtt.connected: 
                time.sleep(1)

            if self.__ChequearHora():
            
                self.ClienteMqtt.publish(   '{ "ID"  : "' + hbl.Contador_ID + '",\
                                                "Entrantes"  :"' + str(self.entrantes) + '",   \
                                                "Salientes" : "' + str(self.salientes) + '", \
                                                "RED":"'          + hbl.Contador_RED+ '",\
                                                "HORA":"'+ str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))+'"}')
            
            if vg.internet:
                self.lcd1.internet()

    #metodos privados
    def __cbTimerReloj(self):
        self.timerReloj.stop()
        if not vg.IR1 and not vg.IR2: 
            self.lcd1.reset(self.CantidadDePersonas)
        else:

            time = str(datetime.datetime.now().strftime("  %d/%m/%Y %H:%M"))
            self.lcd1.lcdWrite(0,time)
            self.lcd1.internet()

        if self.__ChequearHora():
            if not self.Router.estaEncendido():
                self.Router.encender()
        else:
            if not self.mail.pendientes:
                
                self.Router.apagar()
                self.conexionesFallidas = 0
        
                
            self.CantidadDePersonas = 0
            self.entrantes = 0
            self.salientes = 0
            #print(self.CantidadDePersonas, self.entrantes, self.salientes)
            self.Actualizarlcd()
            
        self.timerReloj.start()
        
    def __ChequearHora(self):
        hora = datetime.datetime.now().strftime("%H%M")
        #print(hora)
        #print(self.mail.pendientes)
        if (hbl.Contador_Noreseth1 < int(hora) < hbl.Contador_Noreseth2):
            return True
        return False
        
    def __Leer_Ordenes_Server(self, client, userdata, msg): 
        try:
            data = msg.payload.decode()
            self.ClienteMqtt.LogReport(f"Received from {msg.topic} topic: \n{data} ")
            data = json.loads(data)
            
            ID = data.get("ID").strip(" ")
            RED  = data.get("RED").strip(" ")
            cantidad = int(data.get("CANTIDAD"))
            if self.__ChequearHora():
                if RED == hbl.Contador_RED and cantidad != None :
                    
                    if cantidad != self.CantidadDePersonas:
                        self.CantidadDePersonas = cantidad
                        self.__LogReport("Cantidad modificada por el server a: " \
                                         + str(self.CantidadDePersonas),color="y")
                    if ID == hbl.Contador_ID.strip(" "):
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
        Estado = self.timerPuertaAbierta.status()
        
        #si se vence el timer de la puerta abierta paso a activar la alarma
        #si no se cerro la puerta se activa la alarma nuevamente
        if Estado == "PuertaAbierta" or Estado == "AlarmaDesactivada":
            self.timerPuertaAbierta.setEncendido(self.MaxTimeAlarmaPuertaAbiertaActivada)
            self.mail.sendDoorMail()
            self.Alarma.SonarAlarmaPuertaAbierta()
            self.__LogReport("La puerta esta abierta sonara la alarma", color= "r")
            
        #si la puerta no se cerro apago la alarma
        elif Estado == "AlarmaSonando":
            self.timerPuertaAbierta.setDesactivado(self.MaxTimeAlarmaPuertaAbiertaDesactivada)
            self.Alarma.stop()
            self.__LogReport("La puerta sigue abierta se desactivara la alarma", color= "r")

        self.timerPuertaAbierta.start()
        
    def __cbFichadavencida(self):
        vg.contador -= 1
        self.cuentaAcumulada -= 1
        
        if vg.contador > 0:
            #print(f"Fichada Descontada {vg.contador}")
            self.timerFichada.start()
        else:
            self.timerFichada.stop()
            vg.contador = 0
            
            vg.Status = vg.Esperando_Reloj
        self.__LogReport("Fichada Vencida Quedan "+ str(vg.contador) ,color= "r")
        vg.LastDNI = 99999999
    

    def __Timer(self):
        self.prevEstadoPuerta = self.EstadoPuerta
        try:
            self.EstadoPuerta  = self.pi.read(vg.Pin_Entrada3)
        except:
            pass
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
                    self.__LogReport("Se cerro la puerta", color="g")
                    self.Alarma.Status = ""
                    self.Alarma.stop()
                print("timer detenido")
            vg.flagPuerta = False   

    def __Control_FSM(self):
        while True:
            self.__Timer()
            if hbl.Contador_DebugSensores:
                self.lcd1.lcdWrite(debug = True, message=str(vg.IR1)+str(vg.IR2))
                
            if vg.contador != self.cuentaAcumulada:
                for i in range(vg.contador - self.cuentaAcumulada):
                    self.fichada()
                self.cuentaAcumulada = vg.contador
            
            if vg.Status == vg.Esperando_Reloj:   
                if vg.contador:

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
                    
                
    def __setTiempos(self):
        self.SegundosParafichar                   = hbl.Contador_SegundosParafichar             #Tiempo de gracia que se le da a la persona para finalizar el ingreso una vez que ficho            self.MaxTimeCheck            =  0.02
        self.LedPuertaAbiertaON                   = hbl.Contador_LedPuertaAbiertaON                  #Quizas innecesario reemplazado por maxtimeEnable
        self.LedIntrusoON                         = hbl.Contador_LedIntrusoON                   #Tiempo que blinkea la alarma por intruso
        self.MaxTimeLEDCicloCompleto              = hbl.Contador_MaxTimeLEDCicloCompleto        #sin uso
        self.MaxTimePuertaAbierta                 = hbl.Contador_MaxTimePuertaAbierta           #Tiempo que tiene que estar la puerta abierta para que empiece a sonar el buzzer
        self.MaxTimeAlarmaPuertaAbiertaActivada   = hbl.Contador_MaxTimeAlarmaPuertaAbiertaActivada                  #Tiempo que pasa la alarma encendida por puerta abierta
        self.MaxTimeAlarmaPuertaAbiertaDesactivada= hbl.Contador_MaxTimeAlarmaPuertaAbiertaDesactivada                 #Tiempo que pasa la alarma por puerta abierta desactivada
        
                       
    def fichada(self):
        #inicio timer tiempo de gracia para fichar
        self.timerFichada.start()
        self.lastIN = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.__LogReport("Fichada recibida",color="y")

    def salida(self):
        if self.CantidadDePersonas > 0:
                self.CantidadDePersonas -= 1
                self.actualizarCantidadDePersonas("-1")
        else:
                self.CantidadDePersonas = 0
        
        self.__LogReport("Salida completa", "full","g")
        
    def ingresoValido(self):
        
        
        
        vg.contador -= 1
        if vg.contador == 0 :
           self.timerFichada.stop()
        if vg.contador < 0:
            vg.contador = 0
            self.__LogReport("El contador se paso a negativo")

        self.CantidadDePersonas += 1
        self.actualizarCantidadDePersonas("+1")
        
        #self.__LogReport("Ciclo Completo")
        self.__LogReport(" Ingreso Valido ","full","g")
        
    def intruso_detectado(self):
        
        CheckInternet()
        self.LastAlarma = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.CantidadDePersonas += 1
        self.Alarma.SonarAlarmaIntruso()
        self.actualizarCantidadDePersonas("+1","si")
        self.__LogReport(" Intruso detectado ","full","r")
        
        if not self.__ChequearHora():
            self.Router.encender()
            
        
        self.lcd1.internet()
        
        self.mail.sendIntrusoMail()


    def actualizarCantidadDePersonas(self,personas : str ,intruso : str = "no"):
        self.Actualizarlcd()
        if personas == "+1":
            self.entrantes += 1
        else:
            self.salientes += 1
            
    def Actualizarlcd(self):
        espacios = "          "
        len = str(self.CantidadDePersonas).__len__()

        quitar = int(len/2)
            
        if quitar:
            espacios = espacios[:-quitar]
        #print(aux+str(self.CantidadDePersonas))
         
        self.lcd1.lcdWrite(2,espacios+str(self.CantidadDePersonas))   
         
    def __InformarServidor(self):
        self.timerReport.stop()
        CheckInternet()
        if not self.IR1 and not self.IR2 and (self.entrantes != 0 or self.salientes != 0):
            if vg.internet and self.__ChequearHora():
                self.ClienteMqtt.publish(   '{ "ID"  : "' + hbl.Contador_ID + '",\
                                            "Entrantes"  :"' + str(self.entrantes) + '",   \
                                            "Salientes" : "' + str(self.salientes) + '", \
                                            "RED":"'          + hbl.Contador_RED+ '",     \
                                            "HORA":"'+ str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))+'"}')
        if self.__ChequearHora():
            self.RouterWifiHandler()
        
        self.timerReport.start()
        
    def RouterWifiHandler(self):
        if not vg.internet:
            
            self.__LogReport("Desconectado",color="r")
            self.conexionesFallidas += 1
            
            if self.conexionesFallidas == hbl.Contador_intentos_conexion:
                self.Router.apagar()
                self.__LogReport("Apagando Modem",color="r")
                
            elif self.conexionesFallidas == hbl.Contador_intentos_conexion + 1:
                self.conexionesFallidas = 0
                self.Router.encender()
                self.__LogReport("Encendiendo Modem",color="r")
                
        else:
            if self.conexionesFallidas != 0:
                self.conexionesFallidas = 0
                self.__LogReport("Conectado",color="r")
  
    
        
        
    def __LogReport(self, mensaje, modo = None, color = None):
        self.log.EscribirLinea(hbl.LOGS_hblPuerta)
        
        if modo == 'full':
            
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"PersonasDentro: "+ str(self.CantidadDePersonas))
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"UltimaEntrada: "+ str(self.lastIN))
            if not self.EstadoPuerta:
                Puerta = 'Cerrada'
            else:
                Puerta = 'Abierta'
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Estado Puerta: "+ Puerta)
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Estado Internet: "+ str(vg.internet))
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Fichadas Pendientes: "+ str(vg.contador))
            #self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Estado: "+ str(self.Status))
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Last DNI: "+ str(vg.LastDNI))
            self.log.EscribirLinea(hbl.LOGS_hblPuerta,"Last Alarma: "+ str(self.LastAlarma))
        
        self.log.EscribirLinea(hbl.LOGS_hblPuerta,mensaje,color)     
        
class CheckInternet(object):
    def __init__(self) -> None:
        self.t = Thread(target= auxiliar.CheckInternet,daemon= False, name = "CheckInternet")
        self.t.start()    

class RouterWifi(object):
    def __init__(self, pi, pinsalida ) -> None:
        self.pi : pigpio.pi = pi
        self.pinsalida = pinsalida
    def encender(self):
        self.pi.write(self.pinsalida, 1 )
    
    def apagar(self):
        self.pi.write(self.pinsalida, 0 )
    
    
    def estaEncendido(self):
        return self.pi.read(self.pinsalida)