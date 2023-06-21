#!/usr/bin/env python3

""" --------------------------------------------------------------------------------------------

    _   _ ____  _
   | | | | __ )| |
   | |_| |  _ \| |
   |  _  | |_) | |___
   |_| |_|____/|_____|

   (Hardware building layers)
   v1.0

-------------------------------------------------------------------------------------------- """

import os
import sys
import pigpio
import signal
import time
import datetime

import main
from modulos import delays as delays
from modulos import hbl as hbl
from modulos import hidDevice as hidDevice
from modulos import i2cDevice as i2cDevice
from modulos import tcp as tcp
from modulos import log as log
from modulos import hblCore as hblCore
from modulos import conexiones as conexiones
from modulos import reporte as reporte
from modulos import ftp as ftp
from modulos import tcp as tcp
from modulos import httpServer as httpServer
from modulos import serial as serial
from modulos import kiosco as kiosco
from modulos import MQTT as MQTT
from modulos import Monitoreo as Monitoreo
from modulos import funcionamiento as funcionamiento
from modulos import Control_Personal as CP
from modulos import SendMail
from modulos import BioStar2_WebSocket
from modulos import heartbeat
from modulos import auxiliar

from modulos.decoderWiegand import Decoder
from modulos.encoderWiegand import Encoder
from modulos.salidas import Salidas
from modulos.entradas import Entradas
from modulos import variablesGlobales as variablesGlobales

global pi


""" --------------------------------------------------------------------------------------------

   signals

-------------------------------------------------------------------------------------------- """


def receiveSignal(signalNumber, frame):
    print("Signal received: ", signalNumber)
    print("Cleaning ...")
    hidDevice.threadCount()
    try:
        w1.cancel()                         # cancela el callback de wiegand
    except Exception as e:
        pass
    try:
        w2.cancel()                         # cancela el callback de wiegand
    except Exception as e:
        pass

    pi.stop()                          # detiene el pigpiod
    os.system("sudo killall pigpiod")  # elimina el deamon del pigpiod
    os.system("sudo killall wvdial")   # eliminar proceso del modem
    sys.exit()                         # sale del hbl


""" --------------------------------------------------------------------------------------------

   main

-------------------------------------------------------------------------------------------- """

if __name__ == "__main__":

    def callback():
        pass

    pi = pigpio.pi()

    # cargar parametros del archivo de configuracion
    hbl.cargarParametros('hbl.json')

    # escribe inicializacion HBL
    hblCore.inicializacionHBL()

    # inicializa las salidas de la hbl
    main.Salidas(pi)

    # inicializa las entradas de la hbl

    main.Entradas(pi, variablesGlobales.Pin_Entrada1,
                  variablesGlobales.Pin_Entrada2,
                  variablesGlobales.Pin_Entrada3,
                  variablesGlobales.Pin_W2_WD1)

    # inicializa decoder wiegand
    if hbl.WD_W1_activado == 1:
        if hbl.WD_W1_modo == "IN":
            w1 = main.Decoder(pi, variablesGlobales.Pin_W1_WD0,
                              variablesGlobales.Pin_W1_WD1, callback)
        if hbl.WD_W1_modo == "OUT":
            main.Encoder(pi, variablesGlobales.Pin_W1_WD0,
                         variablesGlobales.Pin_W1_WD1)

    # inicializa encoder wiegand
    if hbl.WD_W2_activado == 1:
        if hbl.WD_W2_modo == "IN":
            w2 = main.Decoder(pi, variablesGlobales.Pin_W2_WD0,
                              variablesGlobales.Pin_W2_WD1, callback)
        if hbl.WD_W2_modo == "OUT":
            main.Encoder(pi, variablesGlobales.Pin_W2_WD0,
                         variablesGlobales.Pin_W2_WD1)



    # inicializa dispositivos HID
    hidDevice.inicializacion(pi)

    # inicializa httpServer
    httpServer.inicializacion(pi)

    # signals
    signal.signal(signal.SIGINT, receiveSignal)
    signal.signal(signal.SIGTERM, receiveSignal)

    # configuracion de interfaces de red ETH/WLAN
    conexiones.NetworkConfig()


    CP.CheckInternet()

    # iniciaizacion GSM Modem ppp0
    conexiones.GSM_Modem_Init()

    # inicia reporte HBL
    reporte.inicializacion()

    # inicializacion modulo serial
    serial.inicializacion(pi)

    # Check inicial leds y buzzer
    hblCore.checkLedsBuzzer(pi)

    # inicializa la comunicacion TCP
    tcp.inicializacion(pi)

    kiosco.inicializacion()
    # inicializa displays LCD
    # i2cDevice.inicializacion(pi)
    lcd1 = i2cDevice.Lcd(pi)

    ClienteMqtt = MQTT.ClientMqtt(hbl.MQTT_broker,
                                  hbl.MQTT_port,
                                  hbl.MQTT_TopicSend,
                                  hbl.MQTT_TopicRecv,
                                  None
                                  )

    Puerta1 = CP.Puerta(pi, ClienteMqtt, lcd1)
    # BioStar2_WebSocket.inicializacion()

    websocket = BioStar2_WebSocket.BioStar2_WebSocket()

    b = datetime.datetime.now()
    print("HBL READY")

    heartbeat.heartbeat(pi)
    while True:


        a = datetime.datetime.now()
        funcionamiento.Control(pi)

        c = a-b

        if c.total_seconds() >= 500:
            Monitoreo.Control()
            b = datetime.datetime.now()

    w1.cancel()
    w2.cancel()
    pi.stop()