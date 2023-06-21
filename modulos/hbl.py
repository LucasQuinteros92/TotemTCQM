import json
import os
import sys


""" --------------------------------------------------------------------------------------------


   Cargar parametros del JSON en memoria


-------------------------------------------------------------------------------------------- """
   
def cargarParametros(archivo):

    global ID_HBL
 
    global REPORTE_idNitro4       
    global REPORTE_lastUpdate 
    global REPORTE_tiempoUpdate 
    global REPORTE_activado 
    global REPORTE_timeOutRequest 
    global REPORTE_encodeAutorization
    global REPORTE_URLToken 
    global REPORTE_URLChequeoConfiguracion 
    global REPORTE_URLReporteInicial 
    global REPORTE_URLReporte


    global TAREAS_Tarea1
    global TAREAS_Tarea2
    global TAREAS_Tarea3
    global TAREAS_Tarea4
    global TAREAS_Tarea5
    global TAREAS_Tarea6
    global TAREAS_Tarea7
    global TAREAS_Tarea8
    global TAREAS_Tarea9
    global TAREAS_Tarea10
    global TareasJSON
    global CantidadTareas

    global WD_W1_activado
    global WD_W1_modo
    global WD_W1_esperaSenial
    global WD_W1_bits
    global WD_W1_delayPulso
    global WD_W1_delayIntervalo
    global WD_W1_primerBit 

    global WD_W2_activado
    global WD_W2_modo
    global WD_W2_esperaSenial
    global WD_W2_bitsSalida
    global WD_W2_delayPulso
    global WD_W2_delayIntervalo
    global WD_W2_primerBit 
     


    global DIG_in_pushDelay

    global DIG_in_in1_activado
    global DIG_in_in1_logica
    global DIG_in_in1_id
    global DIG_in_in1_ON
    global DIG_in_in1_OFF

    global DIG_in_in2_activado
    global DIG_in_in2_logica
    global DIG_in_in2_id
    global DIG_in_in2_ON
    global DIG_in_in2_OFF

    global DIG_in_in3_activado
    global DIG_in_in3_logica
    global DIG_in_in3_id
    global DIG_in_in3_ON
    global DIG_in_in3_OFF

    global DIG_in_in4_activado
    global DIG_in_in4_logica
    global DIG_in_in4_id
    global DIG_in_in4_ON
    global DIG_in_in4_OFF
  
    global DIG_out_out1_activado 
    global DIG_out_out1_id 
    global DIG_out_out1_repeticion 
    global DIG_out_out1_tiempo

    global DIG_out_out2_activado 
    global DIG_out_out2_id 
    global DIG_out_out2_repeticion 
    global DIG_out_out2_tiempo

    global DIG_out_out3_activado 
    global DIG_out_out3_id
    global DIG_out_out3_repeticion  
    global DIG_out_out3_tiempo

    global DIG_out_out4_activado 
    global DIG_out_out4_id 
    global DIG_out_out4_repeticion
    global DIG_out_out4_tiempo

    global ON
    global OFF

    global SERIAL_COM1_activado
    global SERIAL_COM1_port
    global SERIAL_COM1_baudrate
    global SERIAL_COM1_bytesize
    global SERIAL_COM1_parity
    global SERIAL_COM1_stopbits 

    global SERIAL_COM2_activado
    global SERIAL_COM2_port
    global SERIAL_COM2_baudrate
    global SERIAL_COM2_bytesize
    global SERIAL_COM2_parity
    global SERIAL_COM2_stopbits
 
    global HID_device1_activado
    global HID_device1_bufferSize 
    global HID_device1_timeout
    global HID_device1_endpoint 
    global HID_device1_vendor_ID
    global HID_device1_product_ID

    global HID_device2_activado 
    global HID_device2_bufferSize 
    global HID_device2_timeout
    global HID_device2_endpoint 
    global HID_device2_vendor_ID
    global HID_device2_product_ID

    global HID_device3_activado 
    global HID_device3_bufferSize 
    global HID_device3_timeout
    global HID_device3_endpoint
    global HID_device3_vendor_ID
    global HID_device3_product_ID

    global HID_device4_activado 
    global HID_device4_bufferSize 
    global HID_device4_timeout
    global HID_device4_endpoint
    global HID_device4_vendor_ID
    global HID_device4_product_ID

    global TCP_serverDefault_ip 
    global TCP_serverDefault_port 
    global TCP_serverDefault_activado 
    global TCP_serverDefault_intentosConexion 

    global HTTP_server_activado
    global HTTP_server_port
    global HTTP_server_respuesta

    global FUNC_modo
 
    global REQ_activado
    global REQ_seleccionURL
    global REQ_urlRequest1
    global REQ_urlRequest2
    global REQ_urlRequest3
    global REQ_urlRequest4
    global REQ_urlRequest5
    global REQ_urlError
    global REQ_timeoutRequest
    global REQ_timerActivado 

    global TXT_activado
    global TXT_path

    global LOGS_pathBackup 
    global LOGS_tamanioRotator 
    global LOGS_hblCore  
    global LOGS_hblConexiones
    global LOGS_hblWiegand
    global LOGS_hblTcp
    global LOGS_hblEntradas
    global LOGS_hblHTTP
    global LOGS_hblReporte
    global LOGS_hblhidDevice
    global LOGS_hbli2c
    global LOGS_FTP
    global LOGS_hblSerial
    global LOGS_hblCacheo
    global LOGS_hblKiosco
    global LOGS_hblTareas
    
    global LOGS_hblBioStar2_WebSocket
    global LOGS_hblEsclusa
    global LOGS_hblMQTT
    global LOGS_hblTimer
    
    global LOGS_hblPuerta
    global LOGS_hblMail

    global IDHBL

    global DISPLAY_activado
    global DISPLAY_line0
    global DISPLAY_line1
    global DISPLAY_line2
    global DISPLAY_line3
    global DISPLAY_Internet
    global DISPLAY_Internet_fila
    global DISPLAY_Internet_columna

    global NETWORK_activado

    global NETWORK_eth0_activado
    global NETWORK_eth0_dhcp
    global NETWORK_eth0_static_ip_address
    global NETWORK_eth0_static_routers
    global NETWORK_eth0_netmask
    global NETWORK_eth0_network
    global NETWORK_eth0_broadcast 
    global NETWORK_eth0_metric
    global NETWORK_eth0_gateway
    global NETWORK_eth0_DNS

    global NETWORK_eth1_activado
    global NETWORK_eth1_dhcp
    global NETWORK_eth1_static_ip_address
    global NETWORK_eth1_static_routers
    global NETWORK_eth1_netmask
    global NETWORK_eth1_network
    global NETWORK_eth1_broadcast 
    global NETWORK_eth1_metric
    global NETWORK_eth1_gateway
    global NETWORK_eth1_DNS
    global NETWORK_eth1_vendor_ID 
    global NETWORK_eth1_product_ID 
    global NETWORK_eth1_timeDelay

    global NETWORK_wlan0_activado
    global NETWORK_wlan0_dhcp
    global NETWORK_wlan0_static_ip_address
    global NETWORK_wlan0_static_routers
    global NETWORK_wlan0_metric 
    global NETWORK_wlan0_netmask
    global NETWORK_wlan0_network
    global NETWORK_wlan0_broadcast 
    global NETWORK_wlan0_gateway
    global NETWORK_wlan0_DNS
    global NETWORK_wlan0_ssid
    global NETWORK_wlan0_password  
 
    global NETWORK_ppp0_activado
    global NETWORK_ppp0_vendor_ID 
    global NETWORK_ppp0_product_ID  
    global NETWORK_ppp0_dialcommand
    global NETWORK_ppp0_init1
    global NETWORK_ppp0_init2
    global NETWORK_ppp0_init3
    global NETWORK_ppp0_init4
    global NETWORK_ppp0_stupidmode
    global NETWORK_ppp0_ISDN
    global NETWORK_ppp0_modemType
    global NETWORK_ppp0_askPassword
    global NETWORK_ppp0_phone 
    global NETWORK_ppp0_username
    global NETWORK_ppp0_password
    global NETWORK_ppp0_baud
    global NETWORK_ppp0_newPPPD 
    global NETWORK_ppp0_carrierCheck
    global NETWORK_ppp0_autoReconnect  
    global NETWORK_ppp0_dialAttempts 
    global NETWORK_ppp0_metric

    global NETWORK_testConexion_activado 
    global NETWORK_testConexion_url 
    global NETWORK_testConexion_timeoutUrl
    global NETWORK_testConexion_timeDelay
    global NETWORK_testConexion_timeRepeat 
    global NETWORK_testConexion_intentosConexion  
    global NETWORK_testConexion_resetActivado

    global FTP_activado
    global FTP_server
    global FTP_user
    global FTP_pass 

    global CACHEO_activado
    global CACHEO_cantidadCacheos
    global CACHEO_cacheosPositivos
    global CACHEO_tiempoRelePositivo
    global CACHEO_repRelePositivo
    global CACHEO_tiempoReleNegativo
    global CACHEO_repReleNegativo

    global KIOSCO_activado
    global KIOSCO_URL
    global KIOSCO_width
    global KIOSCO_height

    global MQTT_activado
    global MQTT_broker
    global MQTT_port
    global MQTT_TopicSend
    global MQTT_TopicRecv
    
    global BioStar2_WebSocket_activado
    global BioStar2_WebSocket_WebSocket_Host
    global BioStar2_WebSocket_Api_Host
    global BioStar2_WebSocket_Tipo_Evento
    global BioStar2_WebSocket_Device_ID
    global BioStar2_WebSocket_BioStar2_User
    global BioStar2_WebSocket_BioStar2_Password

    global Audio_activado
    global Audio_path_Pasa
    global Audio_path_NoPasa
    global Audio_path_ErrorDNI

    global Contador_activado
    global Contador_SegundosParafichar         
    global Contador_LedPuertaAbiertaON          
    global Contador_LedIntrusoON           
    global Contador_MaxTimeLEDCicloCompleto
    global Contador_MaxTimePuertaAbierta          
    global Contador_MaxTimeAlarmaPuertaAbiertaActivada       
    global Contador_MaxTimeAlarmaPuertaAbiertaDesactivada    
    
    global Contador_IntrusosPendientesPath
    global Contador_ID
    global Contador_RED
    global Contador_Buzzer
    global Contador_MailPuertaAbierta
    global Contador_DebugSensores
    global Contador_Noreseth1
    global Contador_Noreseth2
    global Contador_intentos_conexion
    
    global Mail_destinatarios
    global Mail_remitente
    global Mail_user
    global Mail_key
    global Mail_subject
    global Mail_activado
    
    global data



    # ******************************************************************************************************************************************
    

    # variable para guardar que pantalla esta activa
    global pantallaOled

    pantallaOled = 1
  

    # ******************************************************************************************************************************************
    #   Inicio de la carga de datos en las variables
    # ******************************************************************************************************************************************

    # path del archivo
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) 
 

    # Leo los parametros de configuracion en el JSON
    with open(os.path.join(__location__ , archivo), "r") as f:
        data = json.load(f)



    
    ID_HBL = data["IDHBL"]
  
    # reporte
    REPORTE_idNitro4=data["reporte"]["idNitro4"]       
    REPORTE_lastUpdate=data["reporte"]["lastUpdate"]  
    REPORTE_tiempoUpdate=data["reporte"]["tiempoUpdate"]
    REPORTE_activado=data["reporte"]["activado"]   
    REPORTE_timeOutRequest=data["reporte"]["timeOutRequest"]  
    REPORTE_encodeAutorization=data["reporte"]["encodeAutorization"]
    REPORTE_URLToken=data["reporte"]["URLToken"]
    REPORTE_URLChequeoConfiguracion=data["reporte"]["URLChequeoConfiguracion"] 
    REPORTE_URLReporteInicial=data["reporte"]["URLReporteInicial"]
    REPORTE_URLReporte=data["reporte"]["URLReporte"]




    TAREAS_Tarea1=data['Tareas']['Tarea1']
    TAREAS_Tarea2=data['Tareas']['Tarea2']
    TAREAS_Tarea3=data['Tareas']['Tarea3']
    TAREAS_Tarea4=data['Tareas']['Tarea4']
    TAREAS_Tarea5=data['Tareas']['Tarea5']
    TAREAS_Tarea6=data['Tareas']['Tarea6']
    TAREAS_Tarea7=data['Tareas']['Tarea7']
    TAREAS_Tarea8=data['Tareas']['Tarea8']
    TAREAS_Tarea9=data['Tareas']['Tarea9']
    TAREAS_Tarea10=data['Tareas']['Tarea10']

    TareasJSON = data['Tareas']
    CantidadTareas = 0

    for key in TareasJSON:
        if TareasJSON[key] != "":
            CantidadTareas = CantidadTareas + 1

    #  Seleccion de funcionamiento hbl
    #
    #   0  :  repetidor wiegand IN : W1 -> OUT : W2
    #   1  :  funcionamiento supeditado al request - IN : W1 -> OUT : W2
    #   2  :  decodificador wiegand W1 - TCP
    #   3  :  decodificador wiegand W1 - decodificador wiegand W2
    #   4  :  hidDevice Teclado - Display LCD - TCP
    #   5  :  lector DNI HID -> wiegand 34
    #   6  :  decodificador wiegand W1 -> envio ID con request a URL (test lector Tags RFID)
    #   7  :  conexion TCP con minipc para envio de datos del teclado
    #   8  :  lectura serial de lector de dni 2D -> envio wiegand 34 al reloj
    #   9  :  decodificador wiegand W1 -> envio ID a dato.json
    FUNC_modo=data["funcionamiento"]["modo"]  
    
    # wiegand
    WD_W1_activado=data["wiegand"]["W1"]["activado"]
    WD_W1_modo=data["wiegand"]["W1"]["modo"]
    WD_W1_esperaSenial=data["wiegand"]["W1"]["esperaSenial"]
    WD_W1_bits=data["wiegand"]["W1"]["bitsSalida"]
    WD_W1_delayPulso=data["wiegand"]["W1"]["delayPulso"]
    WD_W1_delayIntervalo=data["wiegand"]["W1"]["delayIntervalo"]
    WD_W1_primerBit=data["wiegand"]["W1"]["primerBit"]

    WD_W2_activado=data["wiegand"]["W2"]["activado"]
    WD_W2_modo=data["wiegand"]["W2"]["modo"]
    WD_W2_esperaSenial=data["wiegand"]["W2"]["esperaSenial"]
    WD_W2_bitsSalida=data["wiegand"]["W2"]["bitsSalida"]
    WD_W2_delayPulso=data["wiegand"]["W2"]["delayPulso"]
    WD_W2_delayIntervalo=data["wiegand"]["W2"]["delayIntervalo"]
    WD_W2_primerBit=data["wiegand"]["W2"]["primerBit"]


  
    # digital
    DIG_in_pushDelay=data["digital"]["in"]["pushDelay"] 
    DIG_in_in1_activado=data["digital"]["in"]["in1"]["activado"]
    DIG_in_in1_logica=data["digital"]["in"]["in1"]["logica"]
    DIG_in_in1_id=data["digital"]["in"]["in1"]["id"]    

    DIG_in_in2_activado=data["digital"]["in"]["in2"]["activado"]
    DIG_in_in2_logica=data["digital"]["in"]["in2"]["logica"]
    DIG_in_in2_id=data["digital"]["in"]["in2"]["id"]
    
    DIG_in_in3_activado=data["digital"]["in"]["in3"]["activado"]
    DIG_in_in3_logica=data["digital"]["in"]["in3"]["logica"]
    DIG_in_in3_id=data["digital"]["in"]["in3"]["id"]

    DIG_in_in4_activado=data["digital"]["in"]["in4"]["activado"]
    DIG_in_in4_logica=data["digital"]["in"]["in4"]["logica"]
    DIG_in_in4_id=data["digital"]["in"]["in4"]["id"]

    if DIG_in_in1_logica == "NA":
        DIG_in_in1_ON = 0
        DIG_in_in1_OFF = 1
    if DIG_in_in2_logica == "NA":
        DIG_in_in2_ON = 0
        DIG_in_in2_OFF = 1
    if DIG_in_in3_logica == "NA":
        DIG_in_in3_ON = 0
        DIG_in_in3_OFF = 1
    if DIG_in_in4_logica == "NA":
        DIG_in_in4_ON = 0
        DIG_in_in4_OFF = 1







 
    DIG_out_out1_activado=data["digital"]["out"]["out1"]["activado"]
    DIG_out_out1_id=data["digital"]["out"]["out1"]["id"]
    DIG_out_out1_repeticion=data["digital"]["out"]["out1"]["repeticion"]
    DIG_out_out1_tiempo=data["digital"]["out"]["out1"]["tiempo"]

    DIG_out_out2_activado=data["digital"]["out"]["out2"]["activado"]
    DIG_out_out2_id=data["digital"]["out"]["out2"]["id"]
    DIG_out_out2_repeticion=data["digital"]["out"]["out2"]["repeticion"]
    DIG_out_out2_tiempo=data["digital"]["out"]["out2"]["tiempo"]

    DIG_out_out3_activado=data["digital"]["out"]["out3"]["activado"]
    DIG_out_out3_id=data["digital"]["out"]["out3"]["id"]
    DIG_out_out3_repeticion=data["digital"]["out"]["out3"]["repeticion"]
    DIG_out_out3_tiempo=data["digital"]["out"]["out3"]["tiempo"]

    DIG_out_out4_activado=data["digital"]["out"]["out4"]["activado"]
    DIG_out_out4_id=data["digital"]["out"]["out4"]["id"]
    DIG_out_out4_repeticion=data["digital"]["out"]["out4"]["repeticion"]
    DIG_out_out4_tiempo=data["digital"]["out"]["out4"]["tiempo"]
    
    # define la logica si es inversa o directa

    ON = 0
    OFF = 1

    
    # serial
    SERIAL_COM1_activado=data["serial"]["COM1"]["activado"]
    SERIAL_COM1_port=data["serial"]["COM1"]["port"]
    SERIAL_COM1_baudrate=data["serial"]["COM1"]["baudrate"]
    SERIAL_COM1_bytesize=data["serial"]["COM1"]["bytesize"]
    SERIAL_COM1_parity=data["serial"]["COM1"]["parity"]
    SERIAL_COM1_stopbits=data["serial"]["COM1"]["stopbits"] 

    SERIAL_COM2_activado=data["serial"]["COM2"]["activado"]
    SERIAL_COM2_port=data["serial"]["COM2"]["port"]
    SERIAL_COM2_baudrate=data["serial"]["COM2"]["baudrate"]
    SERIAL_COM2_bytesize=data["serial"]["COM2"]["bytesize"]
    SERIAL_COM2_parity=data["serial"]["COM2"]["parity"]
    SERIAL_COM2_stopbits=data["serial"]["COM2"]["stopbits"]   

    # hidDevices   
    HID_device1_activado=data["hidDevices"]["device1"]["activado"]
    HID_device1_bufferSize=data["hidDevices"]["device1"]["bufferSize"]
    HID_device1_timeout=data["hidDevices"]["device1"]["timeout"]
    HID_device1_endpoint=data["hidDevices"]["device1"]["endpoint"]
    HID_device1_vendor_ID=data["hidDevices"]["device1"]["vendor_ID"]
    HID_device1_product_ID=data["hidDevices"]["device1"]["product_ID"]

    HID_device2_activado=data["hidDevices"]["device2"]["activado"]
    HID_device2_bufferSize=data["hidDevices"]["device2"]["bufferSize"]
    HID_device2_timeout=data["hidDevices"]["device2"]["timeout"]
    HID_device2_endpoint=data["hidDevices"]["device2"]["endpoint"]
    HID_device2_vendor_ID=data["hidDevices"]["device2"]["vendor_ID"]
    HID_device2_product_ID=data["hidDevices"]["device2"]["product_ID"]

    HID_device3_activado=data["hidDevices"]["device3"]["activado"]
    HID_device3_bufferSize=data["hidDevices"]["device3"]["bufferSize"]
    HID_device3_timeout=data["hidDevices"]["device3"]["timeout"]
    HID_device3_endpoint=data["hidDevices"]["device3"]["endpoint"]
    HID_device3_vendor_ID=data["hidDevices"]["device3"]["vendor_ID"]
    HID_device3_product_ID=data["hidDevices"]["device3"]["product_ID"]

    HID_device4_activado=data["hidDevices"]["device4"]["activado"]
    HID_device4_bufferSize=data["hidDevices"]["device4"]["bufferSize"]
    HID_device4_timeout=data["hidDevices"]["device4"]["timeout"]
    HID_device4_endpoint=data["hidDevices"]["device4"]["endpoint"]
    HID_device4_vendor_ID=data["hidDevices"]["device4"]["vendor_ID"]
    HID_device4_product_ID=data["hidDevices"]["device4"]["product_ID"]

    # tcp 
    TCP_serverDefault_ip=data["tcp"]["serverDefault"]["ip"]
    TCP_serverDefault_port=data["tcp"]["serverDefault"]["port"]
    TCP_serverDefault_activado=data["tcp"]["serverDefault"]["activado"]
    TCP_serverDefault_intentosConexion=data["tcp"]["serverDefault"]["intentosConexion"] 

    # http
    HTTP_server_activado=data["http"]["server"]["activado"]
    HTTP_server_port=data["http"]["server"]["port"]
    HTTP_server_respuesta=data["http"]["server"]["respuesta"] 

  
    # request
    REQ_activado=data["request"]["activado"]
    REQ_seleccionURL=data["request"]["seleccionURL"] 
    REQ_urlRequest1=data["request"]["urlRequest1"] 
    REQ_urlRequest2=data["request"]["urlRequest2"] 
    REQ_urlRequest3=data["request"]["urlRequest3"] 
    REQ_urlRequest4=data["request"]["urlRequest4"] 
    REQ_urlRequest5=data["request"]["urlRequest5"] 

    REQ_urlError=data["request"]["urlError"] 
    REQ_timeoutRequest=data["request"]["timeoutRequest"] 
    REQ_timerActivado=data["request"]["timerActivado"]


    TXT_activado=data["GenerarTXT"]["activado"]
    TXT_path=data["GenerarTXT"]["path"]

    # log   
    LOGS_pathBackup=data["logs"]["pathBackup"] 
    LOGS_tamanioRotator=data["logs"]["tamanioRotator"] 
    LOGS_hblCore=data["logs"]["hblCore"]  
    LOGS_hblConexiones=data["logs"]["hblConexiones"] 
    LOGS_hblWiegand=data["logs"]["hblWiegand"] 
    LOGS_hblTcp=data["logs"]["hblTcp"] 
    LOGS_hblEntradas=data["logs"]["hblEntradas"] 
    LOGS_hblHTTP=data["logs"]["hblHTTP"]  
    LOGS_hblReporte=data["logs"]["hblReporte"]  
    LOGS_hblhidDevice=data["logs"]["hblhidDevice"]  
    LOGS_hbli2c=data["logs"]["hbli2c"] 
    LOGS_FTP=data["logs"]["hblFTP"] 
    LOGS_hblSerial=data["logs"]["hblSerial"]   
    LOGS_hblCacheo=data["logs"]["hblCacheo"]    
    LOGS_hblKiosco=data["logs"]["hblKiosco"]    
    LOGS_hblTareas=data["logs"]["hblTareas"]
    LOGS_hblBioStar2_WebSocket=data["logs"]["hblBioStar2_WebSocket"]
    
    LOGS_hblEsclusa = data["logs"]["hblEsclusa"]
    LOGS_hblMQTT = data["logs"]["hblMQTT"]
    LOGS_hblTimer = data["logs"]["hblTimer"]

    LOGS_hblPuerta = data["logs"]["hblPuerta"]
    LOGS_hblMail   = data["logs"]["hblMail"]

    IDHBL=data["IDHBL"] 


    DISPLAY_activado           =  data["display"]["activado"]
    DISPLAY_line0              =  data["display"]["line0"]
    DISPLAY_line1              =  data["display"]["line1"]
    DISPLAY_line2              =  data["display"]["line2"]
    DISPLAY_line3              =  data["display"]["line3"]
    DISPLAY_Internet           =  data["display"]["internet"]["activado"]
    DISPLAY_Internet_fila      =  data["display"]["internet"]["fila"]
    DISPLAY_Internet_columna   =  data["display"]["internet"]["columna"] 
    
    # network
    NETWORK_activado=data["network"]["activado"]

    NETWORK_eth0_activado=data["network"]["eth0"]["activado"]
    NETWORK_eth0_dhcp=data["network"]["eth0"]["dhcp"]
    NETWORK_eth0_static_ip_address=data["network"]["eth0"]["static_ip_address"]
    NETWORK_eth0_static_routers=data["network"]["eth0"]["static_routers"]
    NETWORK_eth0_gateway=data["network"]["eth0"]["gateway"]
    NETWORK_eth0_DNS=data["network"]["eth0"]["DNS"]
    NETWORK_eth0_netmask=data["network"]["eth0"]["netmask"]
    NETWORK_eth0_network=data["network"]["eth0"]["network"]
    NETWORK_eth0_broadcast=data["network"]["eth0"]["broadcast"]  
    NETWORK_eth0_metric=data["network"]["eth0"]["metric"]

    NETWORK_eth1_activado=data["network"]["eth1"]["activado"]
    NETWORK_eth1_dhcp=data["network"]["eth1"]["dhcp"]
    NETWORK_eth1_static_ip_address=data["network"]["eth1"]["static_ip_address"]
    NETWORK_eth1_static_routers=data["network"]["eth1"]["static_routers"]
    NETWORK_eth1_gateway=data["network"]["eth1"]["gateway"]
    NETWORK_eth1_DNS=data["network"]["eth1"]["DNS"]
    NETWORK_eth1_netmask=data["network"]["eth1"]["netmask"]
    NETWORK_eth1_network=data["network"]["eth1"]["network"]
    NETWORK_eth1_broadcast=data["network"]["eth1"]["broadcast"]  
    NETWORK_eth1_metric=data["network"]["eth1"]["metric"]
    NETWORK_eth1_vendor_ID=data["network"]["eth1"]["vendor_ID"]  
    NETWORK_eth1_product_ID=data["network"]["eth1"]["product_ID"] 
    NETWORK_eth1_timeDelay=data["network"]["eth1"]["timeDelay"] 

    NETWORK_wlan0_activado=data["network"]["wlan0"]["activado"]
    NETWORK_wlan0_dhcp=data["network"]["wlan0"]["dhcp"]
    NETWORK_wlan0_static_ip_address=data["network"]["wlan0"]["static_ip_address"]
    NETWORK_wlan0_static_routers=data["network"]["wlan0"]["static_routers"]
    NETWORK_wlan0_gateway=data["network"]["wlan0"]["gateway"]
    NETWORK_wlan0_DNS=data["network"]["wlan0"]["DNS"]
    NETWORK_wlan0_netmask=data["network"]["wlan0"]["netmask"]
    NETWORK_wlan0_network=data["network"]["wlan0"]["network"]
    NETWORK_wlan0_broadcast=data["network"]["wlan0"]["broadcast"] 
    NETWORK_wlan0_metric=data["network"]["wlan0"]["metric"]
    NETWORK_wlan0_ssid=data["network"]["wlan0"]["ssid"]
    NETWORK_wlan0_password=data["network"]["wlan0"]["password"] 

    NETWORK_ppp0_activado=data["network"]["ppp0"]["activado"]
    NETWORK_ppp0_vendor_ID=data["network"]["ppp0"]["vendor_ID"]
    NETWORK_ppp0_product_ID=data["network"]["ppp0"]["product_ID"]  
    NETWORK_ppp0_dialcommand=data["network"]["ppp0"]["dialcommand"]
    NETWORK_ppp0_init1=data["network"]["ppp0"]["init1"]
    NETWORK_ppp0_init2=data["network"]["ppp0"]["init2"]
    NETWORK_ppp0_init3=data["network"]["ppp0"]["init3"]
    NETWORK_ppp0_init4=data["network"]["ppp0"]["init4"]
    NETWORK_ppp0_stupidmode=data["network"]["ppp0"]["stupidmode"]
    NETWORK_ppp0_ISDN=data["network"]["ppp0"]["ISDN"]
    NETWORK_ppp0_modemType=data["network"]["ppp0"]["modemType"]
    NETWORK_ppp0_askPassword=data["network"]["ppp0"]["askPassword"]
    NETWORK_ppp0_phone=data["network"]["ppp0"]["phone"] 
    NETWORK_ppp0_username=data["network"]["ppp0"]["username"]
    NETWORK_ppp0_password=data["network"]["ppp0"]["password"]
    NETWORK_ppp0_baud=data["network"]["ppp0"]["baud"]
    NETWORK_ppp0_newPPPD=data["network"]["ppp0"]["newPPPD"]
    NETWORK_ppp0_carrierCheck=data["network"]["ppp0"]["carrierCheck"]
    NETWORK_ppp0_autoReconnect=data["network"]["ppp0"]["autoReconnect"] 
    NETWORK_ppp0_dialAttempts=data["network"]["ppp0"]["dialAttempts"] 
    NETWORK_ppp0_metric=data["network"]["ppp0"]["metric"] 
 
    NETWORK_testConexion_activado=data["network"]["testConexion"]["activado"] 
    NETWORK_testConexion_url=data["network"]["testConexion"]["url"] 
    NETWORK_testConexion_timeoutUrl=data["network"]["testConexion"]["timeoutUrl"] 
    NETWORK_testConexion_timeDelay=data["network"]["testConexion"]["timeDelay"] 
    NETWORK_testConexion_timeRepeat=data["network"]["testConexion"]["timeRepeat"] 
    NETWORK_testConexion_intentosConexion=data["network"]["testConexion"]["intentosConexion"] 
    NETWORK_testConexion_resetActivado=data["network"]["testConexion"]["resetActivado"]   

    FTP_activado=data["ftp"]["activado"] 
    FTP_server=data["ftp"]["server"] 
    FTP_user=data["ftp"]["user"] 
    FTP_pass=data["ftp"]["pass"]     

    CACHEO_activado=data["cacheo"]["activado"] 
    CACHEO_cantidadCacheos=data["cacheo"]["cantidadCacheos"]
    CACHEO_cacheosPositivos=data["cacheo"]["cacheosPositivos"]
    CACHEO_tiempoRelePositivo=data["cacheo"]["tiempoRelePositivo"]
    CACHEO_repRelePositivo=data["cacheo"]["repRelePositivo"]
    CACHEO_tiempoReleNegativo=data["cacheo"]["tiempoReleNegativo"]
    CACHEO_repReleNegativo=data["cacheo"]["repReleNegativo"]


    KIOSCO_activado=data["kiosco"]["activado"]
    KIOSCO_URL=data["kiosco"]["URL"]
    KIOSCO_width=data["kiosco"]["width"]
    KIOSCO_height=data["kiosco"]["height"]
    
    MQTT_activado=data["MQTT"]["activado"]
    MQTT_broker=data["MQTT"]["broker"]
    MQTT_port=data["MQTT"]["port"]
    MQTT_TopicSend=data["MQTT"]["TopicSend"]
    MQTT_TopicRecv=data["MQTT"]["TopicRecv"]


    Audio_activado=data["Audio"]["activado"]
    Audio_path_Pasa=data["Audio"]["path"]["Pasa"]
    Audio_path_NoPasa=data["Audio"]["path"]["NoPasa"]
    Audio_path_ErrorDNI=data["Audio"]["path"]["ErrorDNI"]
    
    BioStar2_WebSocket_activado=data["BioStar2_WebSocket"]["activado"]
    BioStar2_WebSocket_WebSocket_Host=data["BioStar2_WebSocket"]["WebSocket_Host"]
    BioStar2_WebSocket_Api_Host=data["BioStar2_WebSocket"]["Api_Host"]
    BioStar2_WebSocket_Tipo_Evento=data["BioStar2_WebSocket"]["Tipo_Evento"]
    BioStar2_WebSocket_Device_ID=data["BioStar2_WebSocket"]["Device_ID"]
    BioStar2_WebSocket_BioStar2_User=data["BioStar2_WebSocket"]["BioStar2_User"]
    BioStar2_WebSocket_BioStar2_Password=data["BioStar2_WebSocket"]["BioStar2_Password"]

    #CONTADOR DE PERSONAS
    Contador_activado                              = data["ContadorPersonas"]["activado"]
    Contador_SegundosParafichar                    = data["ContadorPersonas"]["tiempos"]["SegundosParafichar"]
    Contador_LedPuertaAbiertaON                    = data["ContadorPersonas"]["tiempos"]["LedPuertaAbiertaON"]
    Contador_LedIntrusoON                          = data["ContadorPersonas"]["tiempos"]["LedIntrusoON"]
    Contador_MaxTimeLEDCicloCompleto               = data["ContadorPersonas"]["tiempos"]["MaxTimeLEDCicloCompleto"]
    Contador_MaxTimePuertaAbierta                  = data["ContadorPersonas"]["tiempos"]["MaxTimePuertaAbierta"]
    Contador_MaxTimeAlarmaPuertaAbiertaActivada    = data["ContadorPersonas"]["tiempos"]["MaxTimeAlarmaPuertaAbiertaActivada"]
    Contador_MaxTimeAlarmaPuertaAbiertaDesactivada = data["ContadorPersonas"]["tiempos"]["MaxTimeAlarmaPuertaAbiertaDesactivada"]
    Contador_IntrusosPendientesPath                = data["ContadorPersonas"]["IntrusosPendientesPath"]
    Contador_ID                                    = data["ContadorPersonas"]["credenciales"]["ID"]
    Contador_RED                                   = data["ContadorPersonas"]["credenciales"]["Red"]
    Contador_Buzzer                                = data["ContadorPersonas"]["opciones"]["Buzzer"]
    Contador_MailPuertaAbierta                     = data["ContadorPersonas"]["opciones"]["MailPuertaAbierta"]
    Contador_DebugSensores                         = data["ContadorPersonas"]["opciones"]["DebugSensores"]
    Contador_Noreseth1                             = data["ContadorPersonas"]["noreseth1"]
    Contador_Noreseth2                             = data["ContadorPersonas"]["noreseth2"]
    Contador_intentos_conexion                     = data["ContadorPersonas"]["IntentosConexion"]
    
    #Mails
    Mail_activado = data["Mail"]["activado"]
    Mail_destinatarios = data["Mail"]["destinatarios"]
    Mail_remitente = data["Mail"]["remitente"]
    Mail_user = data["Mail"]["user"]
    Mail_subject = data["Mail"]["subject"]
    Mail_key = data["Mail"]["key"]
   

 