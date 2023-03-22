
import os
from pickle import TRUE

from modulos import log as log
from modulos import variablesGlobales as variablesGlobales
from modulos import hbl as hbl
import time

from urllib.request import urlopen

""" --------------------------------------------------------------------------------------------
 
    Funciones auxiliares del HBL
 
    * Funciones para el manejo de textos en archivos 
    * Funciones de compresion de archivos
 
-------------------------------------------------------------------------------------------- """  

def EscribirFuncion(Funcion):
    myFile = open(variablesGlobales.Seguimiento_file_path, 'a')
    myFile.write(Funcion + "  -  " + time.strftime("%d/%m/%y") + "  -  " + time.strftime("%H:%M:%S")+"\n\n")
    myFile.close()

""" --------------------------------------------------------------------------------------------


    Zippeado de directorio


-------------------------------------------------------------------------------------------- """

def zipdir(path, ziph):
    EscribirFuncion("zipdir")

    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
            
"""-------------------------------------------------------------------------------------------- 

   Agrega multiples lineas de texto a un archivo

-------------------------------------------------------------------------------------------- """

def append_multiple_lines(file_name, lines_to_append, tipoApertura):
    EscribirFuncion("append_multiple_lines")

    # Open the file in append & read mode ('a+')
    with open(file_name, tipoApertura) as file_object:
        appendEOL = False
        # Move read cursor to the start of file.
        file_object.seek(0)
        # Check if file is not empty
        data = file_object.read(100)
        if len(data) > 0:
            appendEOL = True
        # Iterate over each string in the list
        for line in lines_to_append:
            # If file is not empty then append '\n' before first line for
            # other lines always append '\n' before appending line
            if appendEOL == True:
                file_object.write("\n")
            else:
                appendEOL = True
            # Append element at the end of file
            file_object.write(line)


""" --------------------------------------------------------------------------------------------

   busca un texto en un archivo

-------------------------------------------------------------------------------------------- """

def buscarTexto(file_name, textoAbuscar):
    EscribirFuncion("buscarTexto")
 
    PosicionTextoURL = -1 

    with open(file_name, 'r') as ObjFichero:

        for line in ObjFichero: 

            PosicionTextoURL = line.find(textoAbuscar)
            
            if PosicionTextoURL >= 0: 
                # si encontro el texto, devuelve un true, sino un false
                return 1
        
        return 0 

""" --------------------------------------------------------------------------------------------

    Split y extraccion del valor del DNI de la cadena completa del DNI

-------------------------------------------------------------------------------------------- """

def splitDNI(dniLeido, logueo): 
    EscribirFuncion("splitDNI")
    
    # Parseo valor del dni en el string completo
    stringSplit=dniLeido.split('@')

    log.escribeLineaLog(logueo,"Split valor DNI: " + str(stringSplit)) 

    tamanioLista = len(stringSplit)

    log.escribeLineaLog(logueo,"Tamaño lista DNI: " + str(tamanioLista))  

    # extraigo DNI segun la version del mismo
    #
    #   dni nuevo ej:
    #                00542631492"OCHOA DE EGUILEOR CALIGIURI"AGUSTINA SOFIA"F"41780151"C"29-05-1999"04-04-2018"276 
    #   dni viejo ej:
    #                "38464428    "A"1"PAN PERALTA"NICOLAS"ARGENTINA"19-08-1994"M"22-06-2011"00056089158"7059 "22-06-2026"378"0"
    #                ILRÑ2.01 CÑ110613.02 )No Cap.="UNIDAD ·09 ÇÇ S-NÑ 0040:2008::0009

    if tamanioLista > 12 :
        dni = stringSplit[1]
    else:
        dni = stringSplit[4]  
    
    return dni

""" --------------------------------------------------------------------------------------------

   conversor dni to wiegand x bits

-------------------------------------------------------------------------------------------- """

def dniToWiegandConverter(dni, bits, logueo):
    EscribirFuncion("dniToWiegandConverter")
 
    # convierte el valor del dni a binario
    # y completa con 0 hasta llegar a x bits

    valorsinparidad = bits-2 # al valor final de wiegand le quito dos digitos para el calculo
    mitadvalorsinparidad = int(valorsinparidad / 2) # mitad del valor wiegand para calculo de paridad

    log.escribeLineaLog(logueo,"Bits sin paridad : " + str(valorsinparidad))
    log.escribeLineaLog(logueo,"Mitad bits sin paridad : " + str(mitadvalorsinparidad))

    dniBinario = bin(int(dni))[2:].zfill(valorsinparidad) 
    
    log.escribeLineaLog(logueo,"DNI bin : " + str(dniBinario))  

    # parte alta del binario 
    dinBinarioAlta = dniBinario[:-mitadvalorsinparidad]
    
    log.escribeLineaLog(logueo,"DNI Alta bin : " + str(dinBinarioAlta)) 

    dinIntegerAlta = int(dinBinarioAlta, 2) 

    log.escribeLineaLog(logueo,"DNI Alta int : " + str(dinIntegerAlta)) 

    # cuenta cantidad de bits en 1 en esta parte para calcular la paridad Par (EVEN)
    cantBitsParteAlta = 0

    while (dinIntegerAlta): 
        cantBitsParteAlta += dinIntegerAlta & 1
        dinIntegerAlta >>= 1
    
    log.escribeLineaLog(logueo,"Cant. 1 parte alta : " + str(cantBitsParteAlta))     

    # parte baja del binario
    dinBinarioBaja = dniBinario[mitadvalorsinparidad:]   
    
    log.escribeLineaLog(logueo,"DNI Baja : " + str(dinBinarioBaja)) 

    dinIntegerBaja = int(dinBinarioBaja, 2)
    
    log.escribeLineaLog(logueo,"DNI Baja int : " + str(dinIntegerBaja)) 

    # cuenta cantidad de bits en 1 en esta parte para calcular la paridad Impar (ODD)
    cantBitsParteBaja = 0

    while (dinIntegerBaja): 
        cantBitsParteBaja += dinIntegerBaja & 1
        dinIntegerBaja >>= 1
                                    
    log.escribeLineaLog(logueo,"Cant. 1 parte baja : " + str(cantBitsParteBaja))

    # agrego los bits de paridad al binario del dni para completar el 
    # codigo wiegand antes de enviarlo
    dniToWiegand = ""

    # si el numero es par
    if (cantBitsParteAlta % 2) == 0:   
        dniToWiegand = "0" + dniBinario
    else:  
        dniToWiegand = "1" + dniBinario 
    
    # si el numero es impar
    if (cantBitsParteBaja % 2) == 1:   
        dniToWiegand = dniToWiegand + "0" 
    else:  
        dniToWiegand = dniToWiegand + "1"  
    
    log.escribeLineaLog(logueo,"Wiegand completo: " + str(dniToWiegand)) 

    return dniToWiegand



def GetInfoID(id,modo):
    if modo == "IN":
        if hbl.DIG_in_in1_id == id:
            return variablesGlobales.Pin_Entrada1 , hbl.DIG_in_in1_ON, hbl.DIG_in_in1_OFF
        elif hbl.DIG_in_in2_id == id:
            return variablesGlobales.Pin_Entrada2 , hbl.DIG_in_in2_ON, hbl.DIG_in_in2_OFF
        elif hbl.DIG_in_in3_id == id:
            return variablesGlobales.Pin_Entrada3 , hbl.DIG_in_in3_ON, hbl.DIG_in_in3_OFF
        elif hbl.DIG_in_in4_id == id:
            return variablesGlobales.Pin_Entrada4 , hbl.DIG_in_in4_ON, hbl.DIG_in_in4_OFF
        else:
            return 99,99,99 #ERROR
    else:
        if hbl.DIG_out_out1_id == id:
            return variablesGlobales.Pin_Salida1 , hbl.DIG_out_out1_repeticion , hbl.DIG_out_out1_tiempo
        elif hbl.DIG_out_out2_id == id:
            return variablesGlobales.Pin_Salida2 , hbl.DIG_out_out2_repeticion , hbl.DIG_out_out2_tiempo
        elif hbl.DIG_out_out3_id == id:
            return variablesGlobales.Pin_Salida3 , hbl.DIG_out_out3_repeticion , hbl.DIG_out_out3_tiempo
        elif hbl.DIG_out_out4_id == id:
            return variablesGlobales.Pin_Salida4 , hbl.DIG_out_out4_repeticion , hbl.DIG_out_out4_tiempo
        else:
            return 99 #ERROR

def EscribirSalida(pi,id):
    pin,rep,tiempo = GetInfoID(id,"OUT")
    for x in range(rep):
        pi.write(pin,hbl.ON)
        time.sleep(tiempo)
        pi.write(pin,hbl.OFF)
        time.sleep(tiempo)

def CheckFlag(id):
    pin,on,off = GetInfoID(id,"IN")
    if pin == variablesGlobales.Pin_Entrada1:
        return variablesGlobales.Pulso_Anterior_IN1
    elif pin == variablesGlobales.Pin_Entrada2:
        return variablesGlobales.Pulso_Anterior_IN2
    elif pin == variablesGlobales.Pin_Entrada3:
        return variablesGlobales.Pulso_Anterior_IN3
    elif pin == variablesGlobales.Pin_Entrada4:
        return variablesGlobales.Pulso_Anterior_IN4
    else:
        return 99 #ERROR

def CheckID(id):
    pin,on,off = GetInfoID(id,"IN")
    if pin == 99:
        return False
    else:
        return True

def CheckTarea(id):
    flag = False
    for x in hbl.TareasJSON:
        if hbl.TareasJSON[x] == id:
            flag = True
    return flag



'''
def PlayAudio(AudioPath,pi):
    pi.write(variablesGlobales.Pin_Salida1, hbl.ON)
    pygame.mixer.init()
    pygame.mixer.music.load(AudioPath)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    time.sleep(0.5)
    pi.write(variablesGlobales.Pin_Salida1, hbl.OFF)
'''

def CheckInternet():
    try:
        url = "https://www.google.com"
        urlopen(url)
        return True
    except:
        return False