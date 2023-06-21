from modulos import PlantillasImpresora, hbl as hbl
from modulos import variablesGlobales as VG
from modulos import log as log
from modulos import auxiliar as auxiliar
from modulos.encoderWiegand import Encoder
from modulos import decoderWiegand
from modulos import hblCore as hblCore
from modulos import cacheo as cacheo
from modulos import PlantillasImpresora
from modulos import Control_Personal as CP
import requests
import pigpio 


global DNI_data_serial
global WordTeclado
WordTeclado = ""
global pi


global flagLog
flagLog = 0


global flagTeclado
flagTeclado = 0




def Tareas(RunTask):
    global DNI_data_serial
    global WordTeclado
    global pi
    if RunTask == "Leer Serial":
        if VG.Serial_COM1_Rx_Data != "":
            VG.LastID = TareaLeerSerial(VG.Serial_COM1_Rx_Data)
            VG.Serial_COM1_Rx_Data = ""
        if VG.Serial_COM2_Rx_Data != "":
            VG.LastID = TareaLeerSerial(VG.Serial_COM2_Rx_Data)
            VG.Serial_COM2_Rx_Data = ""
    if RunTask == "Enviar Wiegand":
        TareaEnviarWD(VG.LastID,pi)
    if RunTask == "Leer Wiegand":
        if VG.WD1_Data != "":
            VG.LastID = TareaLeerWD(VG.WD1_Data ,1)
            VG.WD1_Data = ""
        if VG.WD2_Data != "":
            VG.LastID = TareaLeerWD(VG.WD2_Data ,2)
            VG.WD2_Data = ""
    if RunTask == "Request":
        TareaRequest()
    if RunTask == "Confirmacion Reloj":
        TareaConfirmacionReloj()
    if RunTask == "Cacheo":
        TareaCacheo()
    if RunTask == "Generar txt":
        TareaGenerarTXT(VG.LastID)
    if RunTask == "Abrir barrera":
        TareaAbrirBarrera()
    if RunTask == "Leer Teclado":
        TareaLeerTecladoUSB()
    if RunTask == "Imprimir":
        TareaImprimir()
    if RunTask == "ActualizarFichadasPendiente":
        TareaActualizarFichadasPendiente()
    if RunTask == "Leer Websocket":
        
            TareaLeerWebSock()
            
    if RunTask == "":
        VG.NumeroTarea = VG.NumeroTarea + 1
        
def TareaLeerWebSock():
    if VG.WebSock_Data != "":
        VG.LastID = VG.WebSock_Data
        VG.WebSock_Data = ""
        
        VG.NumeroTarea = VG.NumeroTarea+1

def TareaActualizarFichadasPendiente():
    if VG.LastDNI != VG.LastID:
        VG.contador += 1 
        
        VG.LastDNI = VG.LastID
                        #NO SE MODIFICA LA VARIABLE DE LA CLASE, HAY QUE REFERIRSE
                        #A VG.CONTADOR DENTRO DE LA MAQ DE ESTADO
                    
    VG.NumeroTarea = VG.NumeroTarea+1
    

def TareaLeerSerial(data):
    log.escribeSeparador(hbl.LOGS_hblTareas)
    log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Leer Serial") 
    log.escribeLineaLog(hbl.LOGS_hblTareas, "Datos Serial recibidos : " + str(data)) 
    VG.NumeroTarea = VG.NumeroTarea+1    ##Esto solo deberia estar cuando se finalice esta tarea
    return str(data)


def TareaEnviarWD(data,pi):
    log.escribeSeparador(hbl.LOGS_hblTareas)
    log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Enviar Wiegand") 

    #try:
        ### Extraccion del DNI y envio por Wiegand 34
        #valorDNI = auxiliar.splitDNI(data, hbl.LOGS_hblTareas)
        #log.escribeLineaLog(hbl.LOGS_hblTareas, "Valor DNI extraido: " + str(valorDNI)) 

        ### Conversion del DNI a wiegand
        #DNIWiegand = auxiliar.dniToWiegandConverter(valorDNI, 34, hbl.LOGS_hblTareas)
    #except Exception as e:
    #    print(e)

    if hbl.WD_W1_activado and hbl.WD_W1_modo == "OUT":
        ### Envio codigo wiegand
        try:
            Encoder.encoderWiegand(data, pi, VG.Pin_W1_WD0, VG.Pin_W1_WD1,34) 
            hblCore.encenderLed(pi, 1, int(50))
            log.escribeLineaLog(hbl.LOGS_hblTareas, "Wiegand enviado")
        except Exception as inst:
            print(inst)
    elif hbl.WD_W2_activado and hbl.WD_W2_modo == "OUT":
        try:
            ### Envio codigo wiegand
            Encoder.encoderWiegand(data, pi, VG.Pin_W2_WD0, VG.Pin_W2_WD1,34) 
            hblCore.encenderLed(pi, 1, int(50))
            log.escribeLineaLog(hbl.LOGS_hblTareas, "Wiegand enviado")
        except Exception as inst:
            print(inst)
    else:
        log.escribeSeparador(hbl.LOGS_hblTareas)
        log.escribeLineaLog(hbl.LOGS_hblTareas, "ERROR : Ninugno de los dos WD estan activados y/o en modo salida") 

    VG.NumeroTarea = VG.NumeroTarea + 1


def TareaRequest():
    log.escribeSeparador(hbl.LOGS_hblTareas)
    log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Request") 
    try:
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

        log.escribeLineaLog(hbl.LOGS_hblTareas, "URL Request: " + UrlCompletaReq)

        req = requests.get(UrlCompletaReq, timeout=int(hbl.REQ_timeoutRequest))
        log.escribeLineaLog(hbl.LOGS_hblTareas, "Respuesta Request: " + req)
        VG.NumeroTarea = VG.NumeroTarea + 1

    except Exception as e:
        log.escribeLineaLog(hbl.LOGS_hblTareas, "ERROR Request: ")
        VG.NumeroTarea = VG.NumeroTarea + 1


def TareaLeerWD(id,WD_number):
    flag_data=0
    log.escribeSeparador(hbl.LOGS_hblTareas)
    log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Leer Wiegand") 

    log.escribeLineaLog(hbl.LOGS_hblTareas, "ID WD" + str(WD_number) + " = " + str(id)) 
    VG.NumeroTarea = VG.NumeroTarea + 1
    return id


def TareaConfirmacionReloj():
    global pi
    global flagLog
    if not(flagLog):
        log.escribeSeparador(hbl.LOGS_hblTareas)
        log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Corfirmacion de Reloj") 
        flagLog = 1
    pin,on,off = auxiliar.GetInfoID("Reloj","IN")
    if pin == 99:
        log.escribeLineaLog(hbl.LOGS_hblTareas, "ERROR : PIN INVALIDO") 
        VG.NumeroTarea = 1
    else:
        data = pi.read(pin)
        if data == on:
            log.escribeLineaLog(hbl.LOGS_hblTareas, "Confirmacion de Reloj Recibida") 
            VG.NumeroTarea = VG.NumeroTarea + 1
            flagLog = 0


def TareaGenerarTXT(id):
    log.escribeSeparador(hbl.LOGS_hblTareas)
    log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Generar txt") 
    myFile = open(hbl.TXT_path, 'w')
    with myFile:
        myFile.write("ID = " + str(id))
    VG.NumeroTarea = VG.NumeroTarea + 1


def TareaCacheo():
    global pi
    log.escribeSeparador(hbl.LOGS_hblTareas)
    log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Cacheo") 
    VG.ResultadoCacheo = cacheo.procesoCacheo(pi)
    if VG.ResultadoCacheo:
        log.escribeLineaLog(hbl.LOGS_hblTareas, "Resultado Cacheo : POSITIVO") 
        auxiliar.EscribirSalida(pi,"Sirena")
        if hbl.Audio_activado:
            auxiliar.PlayAudio(hbl.Audio_path_NoPasa)
    else:
        log.escribeLineaLog(hbl.LOGS_hblTareas, "Resultado Cacheo : NEGATIVO") 
    

    VG.NumeroTarea = VG.NumeroTarea + 1
        

def TareaAbrirBarrera():
    global pi
    log.escribeSeparador(hbl.LOGS_hblTareas)
    log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Abrir Barrera")
    
    if hbl.CACHEO_activado:#auxiliar.CheckTarea("Cacheo"):
        if VG.ResultadoCacheo == 0: #Cacheo Negativo
            if auxiliar.CheckID("Cacheo Manual"):
                if auxiliar.CheckFlag("Cacheo Manual"):
                    log.escribeLineaLog(hbl.LOGS_hblTareas, "Cacheo Manual : Activado") 
                    auxiliar.EscribirSalida(pi,"Sirena")
                    if hbl.Audio_activado:
                        auxiliar.PlayAudio(hbl.Audio_path_NoPasa,pi)
                    VG.ResultadoCacheo = 0
                else:
                    log.escribeLineaLog(hbl.LOGS_hblTareas, "Barrera Abierta")
                    auxiliar.EscribirSalida(pi,"Barrera")
                    if hbl.Audio_activado:
                        auxiliar.PlayAudio(hbl.Audio_path_Pasa,pi)
            else:
                log.escribeLineaLog(hbl.LOGS_hblTareas, "Barrera Abierta")
                auxiliar.EscribirSalida(pi,"Barrera")
                if hbl.Audio_activado:
                    auxiliar.PlayAudio(hbl.Audio_path_Pasa,pi)
        else:
            log.escribeLineaLog(hbl.LOGS_hblTareas, "Barrera Abierta")
            auxiliar.EscribirSalida(pi,"Barrera")
            if hbl.Audio_activado:
                    auxiliar.PlayAudio(hbl.Audio_path_Pasa,pi)
    else:
        log.escribeLineaLog(hbl.LOGS_hblTareas, "Barrera Abierta")
        auxiliar.EscribirSalida(pi,"Barrera")
        if hbl.Audio_activado:
            auxiliar.PlayAudio(hbl.Audio_path_Pasa,pi)

    VG.NumeroTarea = VG.NumeroTarea + 1


"""La tarea teclado usb tiene que checkear en el JSON si el LCD esta activado. De ser asi, tiene que cada vez que recibe un digito, mandarlo a una funcion 'LCD' que se va a encargar
de ver en el JSON a que funcion tiene que mandar ese dato para mostrarlo en el display, ya que voy a tener una manera de mostrar el dato para TRP, otra para LOMAX, etc"""
def TareaLeerTecladoUSB():
    global flagTeclado
    if not(flagTeclado):
        flagTeclado = 1
        log.escribeSeparador(hbl.LOGS_hblTareas)
        log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Leer Teclado")
    global WordTeclado
    if VG.CharTeclado != "":
        if VG.CharTeclado != "Enter":
            if VG.CharTeclado == "Cancel":
                WordTeclado =  WordTeclado[:-1]
            else:
                WordTeclado += str(VG.CharTeclado)
        else:
            VG.LastID = int(WordTeclado)
            WordTeclado = ""
            flagTeclado = 0
            VG.NumeroTarea += 1
        log.escribeLineaLog(hbl.LOGS_hblTareas, "Palabra Teclado : " + WordTeclado)
        VG.CharTeclado = ""


"""La tarea de imprimir va a recibir como parametro la funcion a la que tiene que llamar para imprimir, ya que voy a tener una funcion que imprima como se imprime en TRP, otra que
imprima como se imprime en LOMAX, etc"""
def TareaImprimir():
    global pi
    log.escribeSeparador(hbl.LOGS_hblTareas)
    log.escribeLineaLog(hbl.LOGS_hblTareas, "Tarea : Imprimir")
    PlantillasImpresora.ImpresionTest()
    VG.NumeroTarea += 1

def Control(pi2):
    global pi
    pi = pi2
    if VG.NumeroTarea > hbl.CantidadTareas:
        VG.NumeroTarea = 1

    if VG.NumeroTarea == 1:
        VG.TareaAcutal = hbl.TareasJSON['Tarea1']
        Tareas(hbl.TareasJSON['Tarea1'])
                
    if VG.NumeroTarea == 2:
        VG.TareaAcutal = hbl.TareasJSON['Tarea2']
        Tareas(hbl.TareasJSON['Tarea2'])

    if VG.NumeroTarea == 3:
        VG.TareaAcutal = hbl.TareasJSON['Tarea3']
        Tareas(hbl.TareasJSON['Tarea3'])

    if VG.NumeroTarea == 4:
        VG.TareaAcutal = hbl.TareasJSON['Tarea4']
        Tareas(hbl.TareasJSON['Tarea4'])

    if VG.NumeroTarea == 5:
        VG.TareaAcutal = hbl.TareasJSON['Tarea5']
        Tareas(hbl.TareasJSON['Tarea5'])

    if VG.NumeroTarea == 6:
        VG.TareaAcutal = hbl.TareasJSON['Tarea6']
        Tareas(hbl.TareasJSON['Tarea6'])

    if VG.NumeroTarea == 7:
        VG.TareaAcutal = hbl.TareasJSON['Tarea7']
        Tareas(hbl.TareasJSON['Tarea7'])

    if VG.NumeroTarea == 8:
        VG.TareaAcutal = hbl.TareasJSON['Tarea8']
        Tareas(hbl.TareasJSON['Tarea8'])

    if VG.NumeroTarea == 9:
        VG.TareaAcutal = hbl.TareasJSON['Tarea9']
        Tareas(hbl.TareasJSON['Tarea9'])

    if VG.NumeroTarea == 10:
        VG.TareaAcutal = hbl.TareasJSON['Tarea10']
        Tareas(hbl.TareasJSON['Tarea10'])          
    