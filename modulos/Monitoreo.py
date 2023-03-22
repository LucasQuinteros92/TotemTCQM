from genericpath import getsize
from os import system
import time
import subprocess
import os
from modulos import auxiliar as auxiliar




def getSize(filename):
    auxiliar.EscribirFuncion("getSize")

    st = os.stat(filename)

    return st.st_size

def Control():
    auxiliar.EscribirFuncion("Control")
    
    command = "vcgencmd get_throttled -"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.communicate()

    msg=str(output[0])
    bitmsg=msg[-4]

    file_path = '/home/pi/Desktop/LogsErrores.csv'
    myFile = open(file_path, 'a')

    with myFile:

        #El OS arroja un codigo hexa de acuerdo a los errores que tiene siguiendo la tabla adjunta. 
        #Si tiene dos errores simultaneamente, suma los codigos hexa de los errores. Si dentro de esa suma esta la baja
        #tension, el codigo hexa tendra en su ultimo bit alguno de los siguiente numeros que estan en el if

        if bitmsg=="1" or bitmsg=="3" or bitmsg=="5" or bitmsg=="9": 
            myFile.write(" Baja Tension  -  " + time.strftime("%d/%m/%y") + "  -  " + time.strftime("%H:%M:%S") + os.linesep)



    myFile.close()
    command = "vcgencmd measure_temp"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.communicate()
    T=str(output[0])[7:9]

    myFile = open(file_path, 'a')

    with myFile:

        if int(T)>=70:
            myFile.write(" Temp = "+ T + "°C  -  " + time.strftime("%d/%m/%y") + "  -  " + time.strftime("%H:%M:%S") + os.linesep)
            myFile.close() 



    if getSize(file_path)>1e7: ## 1e7 bytes = 10 MB
        os.remove(file_path)
