import websocket
import time

import requests
import ssl
import json
from threading import Thread 
from modulos import hbl as hbl
from modulos import log as log
from modulos import variablesGlobales as vg



"""
    *Para usar la libreria de websocket, hay que instalar:
        pip install websocket-client
        pip install rel
    Si se comete el error de instalar el paquete de websocket, hacer lo siguiente:
        pip uninstall websocket
        pip uninstall websocket-client
        pip install websocket-client

    *Hay dos tipos de eventos:
        # IDENTIFY_SUCCESS_FINGERPRINT
        # VERIFY_SUCCESS_CARD
"""
 

from threading import Thread, Event
class temporizador1(object):
    '''
    Inicializa un thread que luego del tiempo seteado realizara la funcion
    que se le pase como callback, a menos que se lo detenga antes
    Una vez detenido o de cumplido el tiempo seteado
    se lo puede reciclar llamando nuevamente a start
    '''
    
    def __init__(self,logObject = None, segundos = 10, callback = None, name = "", debug  = False , status = "" ):
        super().__init__()
        self.segundos = segundos
        self._running = False
        self.callback = callback
        self._stopEvent = Event()
        self.debug = debug
        self.count = 0
        self.log : log.LogReport = logObject
        self.name = name
        self.Status = status
        self.t = Thread( target= self.__run, daemon=False, name = name)
        self.t.start()
        
    def start(self):
        self.count = 0
        self._running = True
        if self.debug:
            if self.segundos/60 > 1:
                self.LogReport("Timer corriendo, Contara: "+str(int(self.segundos/60))+" minutos","g")
            else:
                self.LogReport("Timer corriendo, Contara: "+str(self.segundos)+" segundos","g")
    def is_running(self):
        return self._running
    
    def setEncendido(self,time):
        self.Status = "AlarmaSonando"
        self.setSegundos(time)
        
    def setDesactivado(self,time):
        self.Status = "AlarmaDesactivada"
        self.setSegundos(time)
        
    def status(self):
        return self.Status
        
    ''' metodo privado de la clase usar solo start y stop luego del init '''
    def __run(self):
        
        self.LogReport('Timer inicializado',"y")
        
        while True:
            if self._running :
                
                #if self.debug:
                    #if self.count % 10:
                        #self.LogReport(str(self.count) + "segundos")
                time.sleep(1)
                if self.count >= self.segundos:
                    #self.LogReport('Se supero el tiempo establecido')
                    self.count = 0
                    self._running = False
                    if self.callback is not None:
                        self.callback()
                    
                elif self._stopEvent.isSet():
                    self._stopEvent.clear()
                    self.count =0

                self.count += 1
            else : 
                time.sleep(0.1)
                
    def setSegundos(self,segundos : int):            
        self.segundos = segundos
        
    def stop(self):
        self.count = 0
        #self._stopEvent.set()
        self._running = False
        if self.debug:
            self.LogReport("Timer detenido ","r")
        
    def LogReport(self, texto, color = None):
        if self.log != None:
            self.log.EscribirLinea(hbl.LOGS_hblTimer)
            self.log.EscribirLinea(hbl.LOGS_hblTimer, self.name +": " +texto, color)
            if self.Status != "":
                self.log.EscribirLinea(hbl.LOGS_hblTimer, "Estado: "+ self.Status)
        
    
        
class BioStar2_WebSocket(object):
    def __init__(self) :
        if hbl.BioStar2_WebSocket_activado:
            
            try:
                
                self.temporizadorSinEventos = temporizador1(segundos=10)
                self.ws = websocket.WebSocketApp(hbl.BioStar2_WebSocket_WebSocket_Host + '/wsapi',
                                                    on_open=self.on_open,
                                                    on_message=self.on_message,
                                                    on_error=self.on_error,
                                                    on_close=self.on_close,
                                                    on_ping= self.on_ping,
                                                    on_pong = self.on_pong)
                
                
                self.t = Thread( target=self.__run, daemon=False, name = "BioWebsocket")
                self.t.start()
            except Exception as e:
                print(str(e))
                log.escribeLineaLog(hbl.LOGS_hblBioStar2_WebSocket,"Conexion no establecida")
            #rel.signal(2, rel.abort)  # Keyboard Interrupt
            #rel.dispatch()
    
    
    
    def __run(self):
        print("in")
        self.ws.run_forever(reconnect=2, sslopt={"cert_reqs": ssl.CERT_NONE})  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
        print("out")
    def on_ping(self,ws,message):
        print("ping")
    def on_pong(self,ws,message):
        print("pong")
        
    def reconnect(self):
        self.temporizadorSinEventos.stop()
        self.connect()
        self.temporizadorSinEventos.start()
        
    def on_open(self,ws):
        bs_session_id = self.Get_bs_session_id()
        self.ws.send('bs-session-id' + "=" + bs_session_id)
        self.Inicializar_Eventos(bs_session_id)
        log.escribeSeparador(hbl.LOGS_hblBioStar2_WebSocket)
        log.escribeLineaLog(hbl.LOGS_hblBioStar2_WebSocket, "Conexion establecida")
        #self.getSettings(bs_session_id)
        self.temporizadorSinEventos.start()
        
    def getSettings(self,bs_session_id):
        url = hbl.BioStar2_WebSocket_Api_Host + '/api/setting/biostar'
        payload = "{\r\n    \"User\": {\r\n        \"login_id\": \"" + hbl.BioStar2_WebSocket_BioStar2_User + "\",\r\n        \"password\": \"" + hbl.BioStar2_WebSocket_BioStar2_Password + "\"\r\n    }\r\n}" 
        headers = {"bs-session-id" : bs_session_id}
        response = requests.request("GET", url, headers=headers, data=payload,verify=False)
        #print(response.text)
        
    def Inicializar_Eventos(self, bs_session_id):
        url = hbl.BioStar2_WebSocket_Api_Host + '/api/events/start'
        payload = "{\r\n    \"User\": {\r\n        \"login_id\": \"" + hbl.BioStar2_WebSocket_BioStar2_User + "\",\r\n        \"password\": \"" + hbl.BioStar2_WebSocket_BioStar2_Password + "\"\r\n    }\r\n}"
        headers = {"bs-session-id" : bs_session_id}
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        response = requests.request("POST", url, headers=headers, data=payload,verify=False)
        #print(response.text)
        time.sleep(4)
        
    def Get_bs_session_id(self):
        url = hbl.BioStar2_WebSocket_Api_Host + '/api/login'
        payload = "{\r\n    \"User\": {\r\n        \"login_id\": \"" + hbl.BioStar2_WebSocket_BioStar2_User + "\",\r\n        \"password\": \"" + hbl.BioStar2_WebSocket_BioStar2_Password + "\"\r\n    }\r\n}"
        headers = {}
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        response = requests.request("POST", url, headers=headers, data=payload,verify=False)
        bs_session_id = response.headers['bs-session-id']
        #print(bs_session_id)
        return bs_session_id

    def on_message(self, ws, message):
        
        self.temporizadorSinEventos.stop()
        
        message_json = json.loads(message)

        event_type_name = message_json["Event"]["event_type_id"]["name"]
        device_id = message_json["Event"]["device_id"]["id"]
        event = self.CoincidenciaDeEvento(event_type_name)
        log.escribeSeparador(hbl.LOGS_hblBioStar2_WebSocket)
        log.escribeLineaLog(hbl.LOGS_hblBioStar2_WebSocket,"Tipo de evento : " + event_type_name)
        log.escribeLineaLog(hbl.LOGS_hblBioStar2_WebSocket,"Device ID : " + device_id)
        if event and device_id == hbl.BioStar2_WebSocket_Device_ID:
            log.escribeSeparador(hbl.LOGS_hblBioStar2_WebSocket)
            log.escribeLineaLog(hbl.LOGS_hblBioStar2_WebSocket,"Tipo de evento : " + event_type_name)
            log.escribeLineaLog(hbl.LOGS_hblBioStar2_WebSocket,"Device ID : " + device_id)
            id = message_json["Event"]["user_id"]["user_id"]
            vg.WebSock_Data = id
            log.escribeLineaLog(hbl.LOGS_hblBioStar2_WebSocket,"ID : " + id)
        
        self.temporizadorSinEventos.start()
        
    def CoincidenciaDeEvento(self, event):
        for i in hbl.BioStar2_WebSocket_Tipo_Evento: 
            if i == event:
                return True
        return False
    
    def on_error(self,ws, error):
        log.escribeSeparador(hbl.LOGS_hblBioStar2_WebSocket)
        log.escribeLineaLog(hbl.LOGS_hblBioStar2_WebSocket,"Error : " + str(error))
        

    def on_close(self,ws, close_status_code, close_msg):
        print("### closed ###")
        self.temporizadorSinEventos.stop()

    def on_data(self,arg1,arg2,arg3):
        print("### New Data ###")

