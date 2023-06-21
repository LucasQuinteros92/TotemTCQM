# python 3.6

import random
import time

from modulos import hbl as hbl
from paho.mqtt import client as mqtt_client
from modulos import salidas as salidas
from threading import Thread

from modulos import log as log
import json
import os
from modulos import auxiliar as auxiliar
from modulos import variablesGlobales as variablesGlobales


# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

global MQTTclient

global MQTTConectado
MQTTConectado = 0


def inicializacion():
    auxiliar.EscribirFuncion("inicializacion")
    global MQTTclient
    
    try:
        global MQTTConectado
        MQTTclient = connect_mqtt()
        MQTTclient.loop_start()
        
        while(MQTTConectado):
            time.sleep(1)
                    
        publish("Contador Inicializado")
        subscribe()
        
    except Exception as e:
        print(str(e))
        print("No se pudo iniciar la conexion MQTT")
        MQTTConectado = 0


def connect_mqtt():
    auxiliar.EscribirFuncion("connect_mqtt")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            global MQTTConectado
            MQTTConectado = 1
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
   
    client.connect(hbl.MQTT_broker, hbl.MQTT_port)
    
    return client

def publish( msg = ""):
    auxiliar.EscribirFuncion("publish")
    time.sleep(1)
    global MQTTConectado
    
    if MQTTConectado:
            MQTTclient.publish(hbl.MQTT_TopicSend,msg)

def subscribe():
    auxiliar.EscribirFuncion("subscribe")
    global MQTTConectado
    
    if MQTTConectado:
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        global MQTTclient 
        
        MQTTclient.subscribe(hbl.MQTT_TopicRecv)
        MQTTclient.on_message = on_message



        
class ClientMqtt(object):
    
    def __init__( self, broker, port,topicSend,topicRecv,handlerRecv  ):
        
        if hbl.MQTT_activado == 1:
            self.autoconnect  = Thread(target=self.__run, daemon=False, name = "clientMqttAutoconnect")
            client_id = f'python-mqtt-{random.randint(0, 1000)}'
            self.topicSend = topicSend
            self.topicRecv = topicRecv
            self.broker = broker
            self.port = port
            self.handlerRecv = handlerRecv
            self.client = mqtt_client.Client(client_id)
            self.connected = False
            self.autoconnect.start()
            
    def __run(self):
        
        while not self.connected:
            try:
                
                self.client.on_connect = self.handler_onconnect
                self.client.connect(self.broker,self.port)
                self.client.loop_start()
                self.connected = True
                
            except Exception as e:
                time.sleep(5)
                print("No se pudo iniciar la conexion MQTT: ")
                print(str(e))
        
    def handler_onconnect(self,client,userdata,flags,rc):
        if rc == 0:
            self.LogReport("CONEXION MQTT ESTABLECIDA")
            self.subscribe()
           
        else:
            self.LogReport("Failed to connect, return code %d\n", rc)


    def subscribe(self):
        if hbl.MQTT_activado == 1:
            self.client.subscribe(self.topicRecv)
            self.client.on_message = self.handlerRecv
        
    def publish(self, msg):
        if hbl.MQTT_activado == 1:
            try:
                result = self.client.publish(self.topicSend, msg)
            
                status = result[0]
                if status == 0:
                    self.LogReport(f"Send to topic {self.topicSend}: {msg}")
                else:
                    self.LogReport(f"Failed to send message to topic {self.topicSend}")
            except Exception as e:
                self.LogReport("No se pudo publicar el mensaje MQTT")
            
    def LogReport(self, reporte):
        log.escribeSeparador(hbl.LOGS_hblMQTT)
        log.escribeLineaLog(hbl.LOGS_hblMQTT, reporte) 