
import datetime
import os
import shutil
import zipfile  

from modulos import hbl as hbl

""" --------------------------------------------------------------------------------------------


   Escritura en el Log HBL


-------------------------------------------------------------------------------------------- """
   
def configuracionHBL(log):
 
    # escribe configuracion HBL  
    logFile = open(os.getcwd() + '/log/' + log, "a") 
    logFile.write("\n")
    logFile.write("Configuracion HBL :")
    logFile.write("\n")

    # path del archivo
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    # Leo los parametros de configuracion en el JSON y los escribe en el hbl.log
    with open(os.path.join(__location__ , "hbl.json"), "r") as f:  
        while True:
            linea = f.readline() 
            logFile.write(str(linea))
            if not linea:
                break
    
    f.close()

    logFile.close() 
   
def escribeCabecera(log, tipoEvento):
    logFile = open(log, "a") 
    logFile.write("***********************************************************************************") 
    logFile.write("\n")
    logFile.write("Configuracion HBL :")
    logFile.write("\n")
    logFile.write("Timeout request (seg): ")
    logFile.write(str(hbl.REQ_timeoutRequest))
    logFile.write("\n")
    logFile.write("Modo funcionamiento: ")
    logFile.write(str(hbl.FUNC_modo))
    logFile.write("\n")
    logFile.write("UrlRequest 1 : ")
    logFile.write(hbl.REQ_urlRequest1)
    logFile.write("\n")
    logFile.write("UrlRequest 2 : ")
    logFile.write(hbl.REQ_urlRequest2)
    logFile.write("\n")
    logFile.write("UrlRequest 3 : ")
    logFile.write(hbl.REQ_urlRequest3)
    logFile.write("\n")
    logFile.write("UrlRequest 4 : ")
    logFile.write(hbl.REQ_urlRequest4)
    logFile.write("\n")
    logFile.write("UrlRequest 5 : ")
    logFile.write(hbl.REQ_urlRequest5)
    logFile.write("\n")
    logFile.write("Url seleccionada : ")
    logFile.write(str(hbl.REQ_seleccionURL))
    logFile.write("\n")
    logFile.write("Url error : ")
    logFile.write(hbl.REQ_urlError)
    logFile.write("\n")
    logFile.write("Url mock : ")
    logFile.write(hbl.MOCK_url)
    logFile.write("\n")
    logFile.write("Mock activado ? : ")
    logFile.write(str(hbl.MOCK_activado))
    logFile.write("\n")
    logFile.write("Ubicacion archivos log : ")
    logFile.write("/usr/programas/hbl/log/")
    logFile.write("\n")
    logFile.write("Tiempo act/des salidas (seg) : ")
    logFile.write(str(hbl.DIG_out_tiempo))
    logFile.write("\n")
    logFile.write("----------------------------------------------------------------------------------") 
    logFile.write("\n")
    logFile.write("Tipo de evento : ")  
    logFile.write(str(tipoEvento))
    logFile.write("\n")
    logFile.write("----------------------------------------------------------------------------------")  
    logFile.write("\n")
    logFile.close() 

""" --------------------------------------------------------------------------------------------

    Escribe serparador + fecha actual
         
        * escribe una linea en el log seleccionado
        * realiza un zip al superar el tamaño seleccionado

-------------------------------------------------------------------------------------------- """

def escribeSeparador(log):
    logFile = open(os.getcwd() + '/log/' + log, "a")
    logFile.write("***********************************************************************************")
    logFile.write("\n")
    logFile.write("Fecha / Hora : " + str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
    logFile.write("\n")
    logFile.close() 
  

""" --------------------------------------------------------------------------------------------

    Escribe lineas logs
         
        * escribe una linea en el log seleccionado
        * realiza un zip al superar el tamaño seleccionado

-------------------------------------------------------------------------------------------- """

def escribeLineaLog(log, texto):

    try:

        ruta = os.getcwd() + '/log/' + log 

        #print(os.getcwd() + hbl.LOGS_pathBackup + log)

        # escribo la linea en el log seleccionado
        logFile = open(ruta, "a")
        logFile.write(texto)
        logFile.write("\n")
        logFile.close()   
    
        # leo el tamaño del archivo
        tamanioArchivo = os.path.getsize(ruta) 

        # si el tamaño del archivo supera lo indicaado, prosigue a la compresion y
        # borra el nuevo archivo para que continue grabando
        if tamanioArchivo >= hbl.LOGS_tamanioRotator:
            
            # lee la fecha y hora actual
            fechaHora = str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))  

            # genera la ruta para grabar el zip
            archivo = ruta + ' ' + fechaHora + '.zip' 

            # genera el .zip
            with zipfile.ZipFile(archivo, mode='w') as zf: 
                zf.write(ruta, compress_type=zipfile.ZIP_DEFLATED)

                # mueve el archivo recien zipeado a la carpeta backup
                origen = archivo
                destino = os.getcwd() + hbl.LOGS_pathBackup  
                
                # realiza el movimiento del archivo
                if os.path.exists(origen):  
                    shutil.move(origen, destino) 

                # vacia el archivo de log base
                logFile = open(ruta, "w")   
                logFile.close()         
 
    except Exception as inst: 

        log.escribeSeparador(hbl.LOGS_hblCore) 
        #log.escribeLineaLog(hbl.LOGS_hblCore, "Error : " + str(inst))