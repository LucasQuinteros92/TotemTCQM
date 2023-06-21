import os
import pigpio 
import datetime 

""" --------------------------------------------------------------------------------------------

   leer los numeros de serie / revision / mac address de la RPI

   ej:

    # MAC Address del Ethernet adapter
    ethtool --show-permaddr eth0    
    # res : dc:a6:32:52:2d:ee

    # otro metodo :
    $ vcgencmd otp_dump | grep '65:' 
    $ vcgencmd otp_dump | grep '64:' 

    # MAC Address del WiFi adapter
    ethtool --show-permaddr wlan0   

    # averiguar el numero de serie de la RPI
    $ vcgencmd otp_dump | grep '28:' 
    # res : 28:f9976413

    # averiguar la revision de la RPI (2G, 4G, etc)
    $ vcgencmd otp_dump | grep '30:' 
    # res : 30:00c03112

-------------------------------------------------------------------------------------------- """

def leer_numero_serie():
    numeroSerie = os.popen("vcgencmd otp_dump | grep '28:'").readline()
    numeroSerie = numeroSerie.replace("\n", "")
    return (numeroSerie.replace("28:", ""))

def leer_revision():
    revision = os.popen("vcgencmd otp_dump | grep '30:'").readline()
    revision = revision.replace("\n", "")
    return (revision.replace("30:", ""))

def leer_MAC_Address(interfase):
    macAddress = os.popen("ethtool --show-permaddr " + interfase).readline()
    macAddress = macAddress.replace("\n", "")
    return (macAddress.replace("Permanent address: ", "")) 

""" ******************************************************************************************

     variables globales  

****************************************************************************************** """ 

#
#   cacheo.py
#

global ubicacionCacheo  
global listaAleatoria
global valorEncontrado 
global cacheoActivo
  

#
#   hblCore.py
#  

global HBLCORE_contadorReset 


#
#   entradas.py
#  
  
global pressTick

#   hidDevice

global jsonEnvioDNI



# inicializacion variables globales
valorEncontrado = 0
ubicacionCacheo = 0 
cacheoActivo = 0
listaAleatoria = []
HBLCORE_contadorReset = 0
pressTick = 0
jsonEnvioDNI = ""
Seguimiento_file_path = "Seguimiento.log"

versionHBL = "3.0"

############################################################################
#                                                                          #
#                                 Tareas                                   #
#                                                                          #
############################################################################

TareaAcutal = ""
NumeroTarea = 1
Serial_COM1_Rx_Data = ""
Serial_COM2_Rx_Data = ""
WD1_Data = ""
WD2_Data = ""
WebSock_Data = ""
LastID = "" # Este es el ultimo ID que se recibio, ya sea del Wiegand, del Serial o lo que sea
#TimerSalidas = 
ResultadoCacheo = 0
CharTeclado = ""
internet = False


############################################################################
#                                                                          #
#                                Entradas                                  #
#                                                                          #
############################################################################

Pulso_Anterior_IN1 = 0
Pulso_Anterior_IN2 = 0
Pulso_Anterior_IN3 = 0
Pulso_Anterior_IN4 = 0


############################################################################
#                                                                          #
#                                Reporte                                   #
#                                                                          #
############################################################################

RPI_SerialNumber = leer_numero_serie()
RPI_Revision = leer_revision()
RPI_MacEthernet = leer_MAC_Address('eth0')
RPI_MacWlan = leer_MAC_Address('wlan0')
NTP_URL = "time.cloudflare.com"

############################################################################
#                                                                          #
#                          Definicion de pines                             #
#                                                                          #
############################################################################

"""       GPIO       """

#pi = pigpio.pi()


"""       ENTRADAS       """

Pin_Entrada1 = 21
Pin_Entrada2 = 20
Pin_Entrada3 = 25
Pin_Entrada4 = 22


"""       SALIDAS       """

Pin_Salida1 = 5
Pin_Salida2 = 6
Pin_Salida3 = 26
Pin_Salida4 = 16

"""     USER LEDS      """

Pin_LED1 = 13
Pin_LED2 = 19
Pin_LED3 = 12
Pin_Buzzer = 18

"""     WIEGAND      """

Pin_W1_WD0 = 23
Pin_W1_WD1 = 24

Pin_W2_WD0 = 17 
Pin_W2_WD1 = 27

"""     I2C      """
BusDisplay = 3

"""     ON/OFF      """
PIN_ON = 1      
PIN_OFF = 0

ON = 1
OFF = 0

############################################################################
#                                                                          #
#                               Esclusa                                    #
#                                                                          #
############################################################################

"""     BANDERAS   """
ModoEsclusa = enumerate(["ESCLUSA", "UNPORTON"])


""" MODO DE OPERACION"""

MODO_ESCLUSA =  0
MODO_MOVER_UN_PORTON = 1
MODO_MOVER_AMBOS_PORTONES = 2

MODOS_DE_OPERACION = list(enumerate([
                                        "MODO_ESCLUSA",
                                        "MODO_MOVER_UN_PORTON",
                                        "MODO_MOVER_AMBOS_PORTONES"]))

""" ESTADOS DE LOS PORTONES """

ESPERANDO_ORDEN         = 0
AMBOS_PORTONES_CERRADOS = 1
ABRIR_P1                = 2
ABRIENDO_P1             = 3
P1_ABIERTO              = 4
CERRANDO_P1             = 5
P1_CERRADO              = 6
ABRIR_P2                = 7
ABRIENDO_P2             = 8
P2_ABIERTO              = 9
CERRANDO_P2             = 10
P2_CERRADO              = 11
AMBOS_PORTONES_ABIERTOS = 12
MOVER_P1                = 13
MOVIENDO_P1             = 14
MOVER_P2                = 15
MOVIENDO_P2             = 16

ESTADOS_DE_LOS_PORTONES = list(enumerate([
                                        "ESPERANDO_ORDEN",   
                                        "AMBOS_PORTONES_CERRADOS", 
                                        "ABRIR_P1",
                                        "ABRIENDO_P1",
                                        "P1_ABIERTO",
                                        "CERRANDO_P1",
                                        "P1_CERRADO",
                                        "ABRIR_P2",
                                        "ABRIENDO_P2",
                                        "P2_ABIERTO",
                                        "CERRANDO_P2",
                                        "P2_CERRADO",
                                        "AMBOS_PORTONES_ABIERTOS",
                                        "MOVER_P1",
                                        "MOVIENDO_P1",
                                        "MOVER_P2",
                                        "MOVIENDO_P2"]))

""" ESTADOS ALARMA"""

STANDBY = 0
CORRIENDO_TIMER = 1
SONANDO = 2
DESACTIVADA = 3

ESTADOS_DE_ALARMA = list(enumerate([
                                    "STANDBY",
                                    "CORRIENDO_TIMER",
                                    "SONANDO",
                                    "DESACTIVADA"
]))


""" SENTIDOS DE APERTURA """

ENTRAR = 0
SALIR = 1

SENTIDOS_DE_APERTURA = list(enumerate([  
                                    "ENTRAR", 
                                    "SALIR" ]))

""" PINES PORTONES  """
P1 = 1
P2 = 2

""" ESTRUCTURA DE DATOS PARA SERVER """

DATA = {
        'MODO' :    "", 
        'SENTIDO' : "", 
        'ESTADO' :  "", 
        'PORTON1' : "", 
        'PORTON2' : "", 
}

############################################################################
#                                                                          #
#                           Control Personal                               #
#                                                                          #
############################################################################
"""         Variables           """
contador = 0
LastDNI = 99999999
DNIFichadaPendientes = []
flagPuerta = False
Status =  1
IR1 = 0
IR2 = 0

"""         ESTADOS PUERTA       """
Esperando_Reloj             =  1
Esperando_IR1               =  2
Esperando_IR1_IR2           =  3
Esperando_IR2               =  4
Esperando_CompletarCiclo    =  5
EntradaCompleta             =  6
VerificacionIntruso         =  7
VerificacionIntruso2        =  8
VerificacionIntruso3        =  9
Intruso                     =  10
Esperando_IR1_IR2_Saliente  =  11
Esperando_IR1_Saliente      =  12
Persona_Saliente            =  13
Esperando_IR2_Saliente      =  14


