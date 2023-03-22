
import datetime
import threading
import time
import base64
import json
import requests
import os 
import re  
import sys

from modulos import ftp as ftp
from modulos import conexiones as conexiones
from modulos import hblCore as hblCore
from modulos import log as log
from modulos import hbl as hbl
from modulos import auxiliar as auxiliar


""" --------------------------------------------------------------------------------------------

    Reporte HBL

    * Token
    * Reporte
    * Configuracion

-------------------------------------------------------------------------------------------- """

def consultarToken(): 
    auxiliar.EscribirFuncion("consultarToken")

    tokenLeido = 0

    #tokenTest = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTAzNiwiaWF0IjoxNjA4MTM4ODU5LCJ2ZW5jaW1pZW50byI6MTYwOTQzNDg1OSwiZGF0b3NDb25leGlvbiI6eyJtb3Rvcl9kYiI6Im1zc3FsIiwiaG9zdF9kYiI6ImpwaGxpb25zLmRkbnMubmV0IiwicG9ydF9kYiI6IjE0MzgiLCJuYW1lX2RiIjoiQ09OTkVDVCIsInVzZXJfZGIiOiJzYSIsInBhc3NfZGIiOiJKcGgxMzUifSwiaWRVc3VhcmlvTml0cm80IjoxMDM2LCJyb2xlcyI6W3siaWRSb2wiOjYsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBNQVNDQVJBUyAgLSBBQ0NFU08ifSx7ImlkUm9sIjo3LCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gTUFTQ0FSQVMgLSBBTFRBIn0seyJpZFJvbCI6OCwibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIE1BU0NBUkFTIC0gQkFKQSJ9LHsiaWRSb2wiOjgzNywibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIEVOVElEQURFUyAtIEFMVEEifSx7ImlkUm9sIjo4MzksIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBFTlRJREFERVMgLSBNT0RJRklDQUNJT04ifSx7ImlkUm9sIjo4NDEsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBFTlRJREFEUkVMQUNJT05FUyAtIEFMVEEifSx7ImlkUm9sIjo4NDMsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBFTlRJREFEUkVMQUNJT05FUyAtIE1PRElGSUNBQ0lPTiJ9LHsiaWRSb2wiOjg0NCwibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIEVNUFJFU0FTIC0gQUNDRVNPIn0seyJpZFJvbCI6ODQ2LCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gRU1QUkVTQVMgLSBCQUpBIn0seyJpZFJvbCI6ODQ1LCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gRU1QUkVTQVMgLSBBTFRBIn0seyJpZFJvbCI6ODQ4LCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gUk9MRVMgLSBBQ0NFU08ifSx7ImlkUm9sIjo4NTAsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBST0xFUyAtIEJBSkEifSx7ImlkUm9sIjo4NTMsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBQRVJGSUxFUyAtIEFMVEEifSx7ImlkUm9sIjo4NTUsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBQRVJGSUxFUyAtIE1PRElGSUNBQ0lPTiJ9LHsiaWRSb2wiOjg1Nywibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIFVTVUFSSU9QRVJGSUxFUyAtIEFMVEEifSx7ImlkUm9sIjo4NTksIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBVU1VBUklPUEVSRklMRVMgLSBNT0RJRklDQUNJT04ifSx7ImlkUm9sIjo4NjEsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBVU1VBUklPUyAtIEFMVEEifSx7ImlkUm9sIjo4NjIsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBVU1VBUklPUyAtIEJBSkEifSx7ImlkUm9sIjo4NjQsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBDQU1CSU9DTEFWRSAtIEFDQ0VTTyJ9LHsiaWRSb2wiOjg2Nywibm9tYnJlIjoiQVNJU1RFTkNJQSAtIE9QRVJBQ0lPTkVTIC0gQUNDRVNPIn0seyJpZFJvbCI6ODk2LCJub21icmUiOiJBU0lTVEVOQ0lBIC0gT1BFUkFDSU9ORVMgLSBFTVBSRVNBRkFDVFVSQUNJT04gLSBCQUpBIn0seyJpZFJvbCI6ODM1LCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gTUFTQ0FSQVMgLSBNT0RJRklDQUNJT04ifSx7ImlkUm9sIjo4NTIsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBQRVJGSUxFUyAtIEFDQ0VTTyJ9LHsiaWRSb2wiOjg5NCwibm9tYnJlIjoiQVNJU1RFTkNJQSAtIE9QRVJBQ0lPTkVTIC0gRU1QUkVTQUZBQ1RVUkFDSU9OIC0gQUNDRVNPIn0seyJpZFJvbCI6ODM2LCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gRU5USURBREVTIC0gQUNDRVNPIn0seyJpZFJvbCI6ODM4LCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gRU5USURBREVTIC0gQkFKQSJ9LHsiaWRSb2wiOjg0MCwibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIEVOVElEQURSRUxBQ0lPTkVTIC0gQUNDRVNPIn0seyJpZFJvbCI6ODQyLCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gRU5USURBRFJFTEFDSU9ORVMgLSBCQUpBIn0seyJpZFJvbCI6ODQ3LCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gRU1QUkVTQVMgLSBNT0RJRklDQUNJT04ifSx7ImlkUm9sIjo4NDksIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBST0xFUyAtIEFMVEEifSx7ImlkUm9sIjo4NTEsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBST0xFUyAtIE1PRElGSUNBQ0lPTiJ9LHsiaWRSb2wiOjg1NCwibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIFBFUkZJTEVTIC0gQkFKQSJ9LHsiaWRSb2wiOjg1Niwibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIFVTVUFSSU9QRVJGSUxFUyAtIEFDQ0VTTyJ9LHsiaWRSb2wiOjg1OCwibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIFVTVUFSSU9QRVJGSUxFUyAtIEJBSkEifSx7ImlkUm9sIjo4NjAsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBDT05GSUdVUkFDSU9ORVMgLSBVU1VBUklPUyAtIEFDQ0VTTyJ9LHsiaWRSb2wiOjg2Mywibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIFVTVUFSSU9TIC0gTU9ESUZJQ0FDSU9OIn0seyJpZFJvbCI6ODkzLCJub21icmUiOiJBU0lTVEVOQ0lBIC0gQ09ORklHVVJBQ0lPTkVTIC0gUkVJTklDSU8gLSBBQ0NFU08ifSx7ImlkUm9sIjo4OTUsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBPUEVSQUNJT05FUyAtIEVNUFJFU0FGQUNUVVJBQ0lPTiAtIEFMVEEifSx7ImlkUm9sIjo4OTcsIm5vbWJyZSI6IkFTSVNURU5DSUEgLSBPUEVSQUNJT05FUyAtIEVNUFJFU0FGQUNUVVJBQ0lPTiAtIE1PRElGSUNBQ0lPTiJ9LHsiaWRSb2wiOjg2NCwibm9tYnJlIjoiQVNJU1RFTkNJQSAtIENPTkZJR1VSQUNJT05FUyAtIENBTUJJT0NMQVZFIC0gQUNDRVNPIn1dfQ.OTXif-F-57O5gHTkT6G79Y1Vd8dI1_gN0Ierq0g81Gc"

    try: 
        # Encode Autorization
        encoded = base64.b64encode(hbl.REPORTE_encodeAutorization.encode('utf-8'))  

        newheaders = {   
            'Content-Type': 'application/x-www-form-urlencoded', 
            'Authorization': 'Basic ' + encoded.decode('utf-8')
            #'token' : tokenTest
        } 

        bodyParam = {  
            'usuario': 'hbl@jphlions.com',
            'clave': 'Jphlionshbl',
            'idEmpresa': '7'     
        }   
  
        response = requests.post(hbl.REPORTE_URLToken, data = bodyParam, headers = newheaders, timeout=int(hbl.REPORTE_timeOutRequest))

        # carga la respuesta del post en un json para poder acceder al item token
        response_native = json.loads(response.text)

        tokenLeido = response_native['token']

        #print(tokenLeido)

        log.escribeSeparador(hbl.LOGS_hblReporte) 
        log.escribeLineaLog(hbl.LOGS_hblReporte, "Token leido OK")

    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblReporte)
        log.escribeLineaLog(hbl.LOGS_hblReporte, "Error : " + str(errorExcepcion)) 

    return tokenLeido


""" --------------------------------------------------------------------------------------------


    Chequeo de configuracion del HBL - JSON y Firmware - Reporte Inicial HBL


-------------------------------------------------------------------------------------------- """
 
def chequearConfiguracionHBL(token):
    auxiliar.EscribirFuncion("chequearConfiguracionHBL")

    statusConnect = 0

    try: 

        # Encode Autorization
        encoded = base64.b64encode(hbl.REPORTE_encodeAutorization.encode('utf-8'))

        ### REALIZO EL GET PARA TOMAR LA CONFIGURACION DEL HBL SEGUN EL ID NITRO4 chequeando el valor del horario para saber
        # si realizo el update en el json

        newheaders = {   
            'Content-Type': 'application/json', 
            'Authorization': 'Basic ' + encoded.decode('utf-8'), 
            'Token': token
        } 
        
        # agrega el idNitro4 al final de la url para hacer el GET
        response = requests.get(hbl.REPORTE_URLChequeoConfiguracion + str(hbl.REPORTE_idNitro4), headers = newheaders, timeout=int(hbl.REPORTE_timeOutRequest))
        
        # revisa el valor de estado, al ser 1 continua con el reporte, si es 0 no, ya que puede haber una
        # falla en el sistema

        response_estado = json.loads(response.text)

        valorEstado = response_estado['estado'] 

        if valorEstado == 1:
                        
            log.escribeLineaLog(hbl.LOGS_hblReporte, "Servicio connect OK")
            # setea el flag del status de connect en 1 para avisarle que realice el reporte
            statusConnect = 1

            # revisa el response para saber si la HBL esta reportada o no , si no encuentra la palabra resultados
            # es porque no esta registrada, ya sea porque la eliminaron o se reporta por primera vez 
            resultadosSearch = re.search(r'\b(resultados)\b', response.text) 

            if resultadosSearch == None :    
                reporteInicial = 1 # hay que reportarla por primera vez
            else:   
                reporteInicial = 0 # chequea la configuracion para ver si hay que hacer update

            if reporteInicial == 1 :
                # reportar al connect 
                log.escribeSeparador(hbl.LOGS_hblReporte)  
                log.escribeLineaLog(hbl.LOGS_hblReporte, "Reporte inicial del HBL...")  
                reporteInicialHBL(token)

            else: 

                # leo la fecha de la ultima actualizacion para saber si es mas reciente que la fecha de actualizacion tengo
                # que guardar la configuracion leida en el json

                response_native = json.loads(response.text)

                serverLastUpdate = response_native['resultados']['lastUpdate']

                log.escribeLineaLog(hbl.LOGS_hblReporte,"serverLastUpdate : " + str(serverLastUpdate))
                
                # ej : 2021-01-07T17:04:34.000Z  
                # date and time in yyyy/mm/dd hh:mm:ss format 
                # fecha ultimo update server
                date1 = datetime.datetime(int(serverLastUpdate[0] + serverLastUpdate[1] + serverLastUpdate[2] + serverLastUpdate[3]) , int(serverLastUpdate[5] + serverLastUpdate[6]), int(serverLastUpdate[8] + serverLastUpdate[9]), int(serverLastUpdate[11] + serverLastUpdate[12]), int(serverLastUpdate[14] + serverLastUpdate[15]), int(serverLastUpdate[17] + serverLastUpdate[18])) 
                
                # fecha ultimo update HBL
                date2 = datetime.datetime(int(hbl.REPORTE_lastUpdate[0] + hbl.REPORTE_lastUpdate[1] + hbl.REPORTE_lastUpdate[2] + hbl.REPORTE_lastUpdate[3]) , int(hbl.REPORTE_lastUpdate[5] + hbl.REPORTE_lastUpdate[6]), int(hbl.REPORTE_lastUpdate[8] + hbl.REPORTE_lastUpdate[9]), int(hbl.REPORTE_lastUpdate[11] + hbl.REPORTE_lastUpdate[12]), int(hbl.REPORTE_lastUpdate[14] + hbl.REPORTE_lastUpdate[15]), int(hbl.REPORTE_lastUpdate[17] + hbl.REPORTE_lastUpdate[18])) 
            
                log.escribeLineaLog(hbl.LOGS_hblReporte,"Fecha Servidor : " + str(date1))
                log.escribeLineaLog(hbl.LOGS_hblReporte,"Fecha HBL : " + str(date2))
                    
                # compara las dos fechas, si la del server es mas reciente tiene que hacer un update del json local con el json remoto
                if date1 > date2 : 

                    # actualizar json 
                    JSONUpdate = response_native['resultados']['json']  

                    # leer el valor del comando bash a ejecutar

                    # grabo el json en el archivo
                    # path del archivo
                    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

                    # actualizo los parametros en el JSON
                    with open(os.path.join(__location__ , 'hbl.json'), 'w') as json_file:
                        json_file.write(JSONUpdate)

                    #### -------------------------------------------------------------------------------------
                    ####  Graba fecha actualizada del server en el json i el idNitro4 por problemas de sincro

                    # Leo los parametros de configuracion en el JSON
                    with open(os.path.join(__location__ , 'hbl.json'), "r") as f:
                        data = json.load(f) 

                    # toma la hora de actualizacion del serverlastupdate para grabarlo en el json
                    # ej : 2021-01-07 17:04:34
                    data["reporte"]["lastUpdate"] = str(date1)
                    
                    # piso el valor del json con el idnitro4 enviado en el request ya que queda 
                    # el numero antiguo en el json del connect
                    data["reporte"]["idNitro4"] = response_native['resultados']['idNitro4']

                    # verifica si hay que realizar la ejecucion de un comando bash o 
                    # lectura de valores de interaccion del connect con el hbl                  
                    versionFirmware = data['reporte']['versionFirmware']
                    comandoBash = data['reporte']['comandoBash']
                    readLogs = data['reporte']['readLogs']
                    borrarTemp = data['reporte']['borrarTemp']

                    log.escribeSeparador(hbl.LOGS_hblReporte)
                    log.escribeLineaLog(hbl.LOGS_hblReporte, "versionFirmware : " + str(versionFirmware)) 
                    log.escribeLineaLog(hbl.LOGS_hblReporte, "comandoBash : " + str(comandoBash))  
                    log.escribeLineaLog(hbl.LOGS_hblReporte, "readLogs : " + str(readLogs))  
                    log.escribeLineaLog(hbl.LOGS_hblReporte, "borrarTemp : " + str(borrarTemp))  

                    # blanqueo las variables en el json
                    data["reporte"]["versionFirmware"] = ""
                    data["reporte"]["comandoBash"] = ""
                    data["reporte"]["readLogs"] = 0
                    data["reporte"]["borrarTemp"] = 0

                    # actualizo los parametros en el JSON
                    with open(os.path.join(__location__ , 'hbl.json'), "w") as f:
                        json.dump(data, f, indent=4)  
                        
                    #### -------------------------------------------------------------------------------

                    # actualizacion firmware


                    # ejecucion de comandos 
                    if comandoBash != "":
                        log.escribeLineaLog(hbl.LOGS_hblReporte, "Ejecutar comando : " + str(comandoBash))
                        os.system(str(comandoBash))

                    # enviar logs al FTP, se guardaran en una carpeta creada con el numero de serie del equipo
                    if readLogs == 1 :
                        ftp.uploadLogs()

                    # borrar contenido carpeta temp
                    if borrarTemp == 1 :
                        pass
                        
                    #### -------------------------------------------------------------------------------
                    
                    # recarga los parametros de hbl.json por actualizacion
                    hbl.cargarParametros('hbl.json')   
                    
        else:     
            log.escribeLineaLog(hbl.LOGS_hblReporte, "Error en el servicio de connect. Operacion abortada")
            # setea el flag del status de connect en 0 para que NO realice el reporte
            statusConnect = 0

    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblReporte)
        log.escribeLineaLog(hbl.LOGS_hblReporte, "Error : " + str(errorExcepcion)) 
     
    return statusConnect

""" --------------------------------------------------------------------------------------------


    Reporte inicial HBL


-------------------------------------------------------------------------------------------- """

def reporteInicialHBL(token):
    auxiliar.EscribirFuncion("reporteInicialHBL")

    # primero revisa si tiene el idNitro4, en el caso de que no lo tenga tiene que reportarse por
    # primera vez, sino no se reporta en esta instancia y chequeara despues por fecha si tiene que
    # reportarse   
    
    try:

        # Encode Autorization
        encoded = base64.b64encode(hbl.REPORTE_encodeAutorization.encode('utf-8'))  

        # path del archivo
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        # Leo los parametros de configuracion en el JSON
        with open(os.path.join(__location__ , 'hbl.json'), "r") as f:
            data = json.load(f) 

        # Creo un diccionario
        Dict = {  
            'configured': '0',
            'lastUpdate' : str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')),
            'json': { }             
        }   

        # actualiza el diccionario con el contenido del archivo json
        Dict.update({"json": json.dumps(data, indent=4)}) 

        # imprime por pantalla el diccionario completo
        # print(Dict)   
        
        newheaders = {   
            'Content-Type': 'application/json', 
            'Authorization': 'Basic ' + encoded.decode('utf-8'), 
            'Token': token
        } 

        response = requests.post(hbl.REPORTE_URLReporteInicial, json = Dict, headers = newheaders, timeout=int(hbl.REPORTE_timeOutRequest))

        # response del request  
        log.escribeSeparador(hbl.LOGS_hblReporte) 
        log.escribeLineaLog(hbl.LOGS_hblReporte, response.text)
        
        response_native = json.loads(response.text)

        # ID Nitro 4
        idNitroString = response_native['resultado']['idNitro4'] 
        log.escribeSeparador(hbl.LOGS_hblReporte) 
        log.escribeLineaLog(hbl.LOGS_hblReporte, "ID Nitro 4 : " + str(idNitroString))

        #### -------------------------------------------------------------------------------
        ####  Graba el id y la fecha en el json

        # path del archivo
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        # Leo los parametros de configuracion en el JSON
        with open(os.path.join(__location__ , 'hbl.json'), "r") as f:
            data = json.load(f)

        data["reporte"]["idNitro4"] = idNitroString 

        ## grabo la fecha y hora actual como inicio de hbl y comparacion con el get del server para descargar el json
        # ej : 2021-01-07 17:04:34
        data["reporte"]["lastUpdate"] = str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))

        # actualizo los parametros en el JSON
        with open(os.path.join(__location__ , 'hbl.json'), "w") as f:
            json.dump(data, f, indent=4)  
        #### -------------------------------------------------------------------------------

        # cargar parametros del archivo de configuracion
        hbl.cargarParametros('hbl.json')

    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblReporte)
        log.escribeLineaLog(hbl.LOGS_hblReporte, "Error : " + str(errorExcepcion)) 

""" --------------------------------------------------------------------------------------------

    Reporte HBL

    idHbl
    temp
    riskBytes
    redundancy
    lastUpdate
    cpuPercentage
    memUsage
    hddUsage 

    http://hbl.jphlions.com:3600/api/hblstatuses/

-------------------------------------------------------------------------------------------- """

def ReporteHBL(token):
    auxiliar.EscribirFuncion("ReporteHBL")
    
    # formateo las variables para enviarlas al reporte HBL
    temperatura = hblCore.measure_temp().replace("'C", "")
    temperatura = format(float(temperatura), ".2f")  
    usoProcesador = float(hblCore.usoCPU(9))
    usoMemoria = float(hblCore.getRAMinfo())
    usoHDD = float(hblCore.getDiskSpace())    
    rx_bytes_ppp0 = float(conexiones.bytesppp0('rx'))
    tx_bytes_ppp0 = float(conexiones.bytesppp0('tx')) 
    bootVersion = hblCore.getBootloaderVersion()
    fechaActual = hblCore.timeNow()   
    
    try:

        # Encode Autorization
        encoded = base64.b64encode(hbl.REPORTE_encodeAutorization.encode('utf-8'))  

        newheaders = {   
            'Content-Type': 'application/x-www-form-urlencoded', 
            'Authorization': 'Basic ' + encoded.decode('utf-8'),
            'Token': token
        } 

        bodyParam = {  
            'idHbl': int(hbl.REPORTE_idNitro4),
            'temp': temperatura,
            'riskBytes': hblCore.get_throttled_bytes(),   
            'redundancy': redundancy, 
            'lastUpdate': fechaActual, 
            'cpuPercentage': usoProcesador, 
            'memUsage': usoMemoria, 
            'hddUsage': usoHDD,
            'dataTX': tx_bytes_ppp0,
            'dataRX': rx_bytes_ppp0,
            'bootloaderVersion' : bootVersion 
        }   

        response = requests.post(hbl.REPORTE_URLReporte, data = bodyParam, headers = newheaders, timeout=int(hbl.REPORTE_timeOutRequest)) 

        log.escribeSeparador(hbl.LOGS_hblReporte)  
        log.escribeLineaLog(hbl.LOGS_hblReporte, response.text)

    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblReporte)
        log.escribeLineaLog(hbl.LOGS_hblReporte, "Error : " + str(errorExcepcion)) 


""" --------------------------------------------------------------------------------------------

    Thread para el reporte

-------------------------------------------------------------------------------------------- """

def startThreadReporte():
    auxiliar.EscribirFuncion("startThreadReporte")
  
    while True:

        # lee token
        log.escribeSeparador(hbl.LOGS_hblReporte)  
        log.escribeLineaLog(hbl.LOGS_hblReporte, "Leyendo token...") 
        token = consultarToken()

        # chequear si hay que hacer un update en el HBL Json o Firwmare o volver a hacer el reporte inicial
        # por eliminacion de la HBL del connect
        log.escribeSeparador(hbl.LOGS_hblReporte)  
        log.escribeLineaLog(hbl.LOGS_hblReporte, "Chequear configuracion...") 
        estado = chequearConfiguracionHBL(token) 

        # realizar el reporte del HBL si el response del estado es 1 sino no lo hace ya que hubo un
        # problema con el servicio
        if estado == 1:
            log.escribeSeparador(hbl.LOGS_hblReporte)  
            log.escribeLineaLog(hbl.LOGS_hblReporte, "Realizar reporte...") 
            ReporteHBL(token)

        time.sleep(int(hbl.REPORTE_tiempoUpdate * 60)) # convierte los minutos del valor del hbl a segundos 

""" --------------------------------------------------------------------------------------------

    inicializacion reporte HBL

-------------------------------------------------------------------------------------------- """

def inicializacion():  
    auxiliar.EscribirFuncion("inicializacion")
    if hbl.REPORTE_activado == 1:

        reporteHBL = threading.Thread(target=startThreadReporte, name='HBLReport')
        reporteHBL.setDaemon(True)
        reporteHBL.start()   
