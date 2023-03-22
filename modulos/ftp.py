""" --------------------------------------------------------------------------------------------


    Modulo FTP de actualización y descarga


-------------------------------------------------------------------------------------------- """
 
from ftplib import error_perm 
from ftplib import FTP
from pathlib import Path
from os import rename
import ftplib
import os
import datetime
import zipfile 

from modulos import log as log
from modulos import hbl as hbl 
from modulos import auxiliar as auxiliar
from modulos import auxiliar as auxiliar
from modulos import variablesGlobales

global ftp

""" -------------------------------------------------------------------------------------------- 

    Pasos para actualizacion firmware HBL
    -------------------------------------

    Verificar que la version a actualizar sea diferente de la actual
    Verificar si la version ya esta en el local
    Descargar la version del firmware indicada
    Backup version actual HBL en directorio : /usr/programas/hbl/hbl.old
    Realizar un CRC del archivo y el hash
    Unzip + Replace
    Borrar flag updateFirmware + mantener datos del hbl (id, fecha, etc...)
    Reboot

-------------------------------------------------------------------------------------------- """
 

""" --------------------------------------------------------------------------------------------


    Sube los logs al VPN segun numero de serie del equipo


-------------------------------------------------------------------------------------------- """

def uploadLogs(): 
    auxiliar.EscribirFuncion("uploadLogs")

    try:  
        
        log.escribeSeparador(hbl.LOGS_FTP) 

        # connect to host, default port
        ftpObject = FTP(hbl.FTP_server)                               

        # login 
        ftpResponse = ftpObject.login(hbl.FTP_user, hbl.FTP_pass)     
        log.escribeLineaLog(hbl.LOGS_FTP, str(ftpResponse)) 

        # mensaje en la conexion
        ftpResponse = ftpObject.getwelcome()
        log.escribeLineaLog(hbl.LOGS_FTP, str(ftpResponse)) 

        # change into "hbl" directory
        ftpResponse = ftpObject.cwd('/hbl/logs')                            
        log.escribeLineaLog(hbl.LOGS_FTP, str(ftpResponse)) 

        # crea un directorio dentro de la carpeta del hbl/logs
        fechaHora = str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) 
        directorio = variablesGlobales.RPI_SerialNumber + '_' + fechaHora  

        # crea el directorio
        ftpObject.mkd(directorio)   

        # se mueve el ftp a este directorio                      
        ftpObject.cwd(directorio)                            
 
        # realiza el zip de todo el directorio
        ruta = os.getcwd() + '/log'
        nombreArchivo = 'logs_' + fechaHora + '.zip'

        # realiza el zip de todo el directorio de logs
        zipf = zipfile.ZipFile(os.getcwd() + '/temp/' + nombreArchivo, 'w', zipfile.ZIP_DEFLATED)
        auxiliar.zipdir(ruta, zipf)
        zipf.close()             
 
        # sube el archivo al ftp 
        # Open the file in binary mode 
        fileObject = open(os.getcwd() + '/temp/' + nombreArchivo, "rb")
        file2BeSavedAs = nombreArchivo
 
        ftpCommand = "STOR %s"%file2BeSavedAs
 
        # Transfer the file in binary mode
        ftpResponse = ftpObject.storbinary(ftpCommand, fp=fileObject)
        log.escribeLineaLog(hbl.LOGS_FTP, str(ftpResponse)) 

        # vuelve al directorio raiz del hbl
        ftpObject.cwd('/hbl') 

        # cierra la conexion con el ftp
        ftpObject.quit()

    except ftplib.all_errors as e:

        log.escribeSeparador(hbl.LOGS_FTP) 
        log.escribeLineaLog(hbl.LOGS_FTP, "Error ftp.py: " + str(e)) 
 