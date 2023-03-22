import os
import sys
import time
import random

from modulos import hbl as hbl
from modulos import variablesGlobales as variablesGlobales
from modulos import log as log
from modulos import auxiliar as auxiliar


""" ******************************************************************************************

    PINOUT 

        luzVerde = Pin_Salida1
        sirena  = Pin_Salida2
        luzRoja = Pin_Salida3
        barrera = Pin_Salida4

****************************************************************************************** """  


def aleatorioValor(cacheosPositivos, cantidadCacheos):
    auxiliar.EscribirFuncion("aleatorioValor")

    try:

        random.seed()
        listaNumeros = random.sample(range(0, cantidadCacheos), cacheosPositivos) 
        listaNumeros.sort()

        return listaNumeros
    
    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCacheo)
        log.escribeLineaLog(hbl.LOGS_hblCacheo, "Error : " + str(errorExcepcion))

""" ******************************************************************************************

     



****************************************************************************************** """ 

def ApagaReles(pi):
    auxiliar.EscribirFuncion("ApagaReles")

    try:

        pi.write(variablesGlobales.Pin_Salida1, hbl.OFF)    
        pi.write(variablesGlobales.Pin_Salida2, hbl.OFF)
        pi.write(variablesGlobales.Pin_Salida3, hbl.OFF)
        pi.write(variablesGlobales.Pin_Salida4, hbl.OFF)

    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCacheo)
        log.escribeLineaLog(hbl.LOGS_hblCacheo, "Error : " + str(errorExcepcion))

""" ******************************************************************************************

     

     

****************************************************************************************** """ 

def AbreBarrera(pi):
    auxiliar.EscribirFuncion("AbreBarrera")
   
    try:

        pi.write(variablesGlobales.Pin_Salida4, hbl.ON)
    
    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCacheo)
        log.escribeLineaLog(hbl.LOGS_hblCacheo, "Error : " + str(errorExcepcion))  

""" ******************************************************************************************

     

     

****************************************************************************************** """ 

def CierraBarrera(pi):
    auxiliar.EscribirFuncion("CierraBarrera")

    try:

        pi.write(variablesGlobales.Pin_Salida4, hbl.OFF)

    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCacheo)
        log.escribeLineaLog(hbl.LOGS_hblCacheo, "Error : " + str(errorExcepcion))  
   
""" ******************************************************************************************

     

     

****************************************************************************************** """ 

def NoPasa(pi):
    auxiliar.EscribirFuncion("NoPasa")

    try: 

        contador = 0

        while contador < hbl.CACHEO_repRelePositivo:
            pi.write(variablesGlobales.Pin_Salida2, hbl.ON)
            pi.write(variablesGlobales.Pin_Salida3, hbl.ON)
            time.sleep(int(hbl.CACHEO_tiempoRelePositivo))
            pi.write(variablesGlobales.Pin_Salida2, hbl.OFF)
            pi.write(variablesGlobales.Pin_Salida3, hbl.OFF)
            time.sleep(int(hbl.CACHEO_tiempoRelePositivo))
            contador = contador + 1
        
        # abre la barrera
        AbreBarrera(pi)
        time.sleep(int(hbl.CACHEO_tiempoRelePositivo))    
        # cierra la barrera
        CierraBarrera(pi)  

    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCacheo)
        log.escribeLineaLog(hbl.LOGS_hblCacheo, "Error : " + str(errorExcepcion))

""" ******************************************************************************************

     

     

****************************************************************************************** """ 

def Pasa(pi):
    auxiliar.EscribirFuncion("Pasa")

    try:

        contador = 0

        # abre la barrera
        AbreBarrera(pi)
        time.sleep(int(hbl.CACHEO_tiempoReleNegativo))  
        # cierra la barrera
        CierraBarrera(pi)  

        while contador < hbl.CACHEO_repReleNegativo:
            pi.write(variablesGlobales.Pin_Salida1, hbl.ON)
            time.sleep(int(hbl.CACHEO_tiempoReleNegativo))
            pi.write(variablesGlobales.Pin_Salida1, hbl.OFF)
            time.sleep(int(hbl.CACHEO_tiempoReleNegativo))
            contador = contador + 1
    
    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCacheo)
        log.escribeLineaLog(hbl.LOGS_hblCacheo, "Error : " + str(errorExcepcion))

""" ******************************************************************************************

     

     

****************************************************************************************** """ 

def botonPanico(pi):
    auxiliar.EscribirFuncion("botonPanico")

    try:
 
        log.escribeLineaLog(hbl.LOGS_hblCacheo, "NoPasa (Boton Panico Activado)")
        NoPasa(pi) 
    
    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCacheo)
        log.escribeLineaLog(hbl.LOGS_hblCacheo, "Error : " + str(errorExcepcion)) 

""" ******************************************************************************************

     

     

****************************************************************************************** """ 


"""El proceso de Cacheo consiste en hacer una listaAleatoria con hbl.CACHEO_cacheosPositivos elementos donde cada elemento son numeros del 0 a hbl.CACHEO_cantidadCacheos.
Los numeros que contiene la listaAleatoria son los numeros que van a tener que hacer Cacheo. Es decir, supongamos que hbl.CACHEO_cacheosPositivos = 2 y hbl.CACHEO_cantidadCacheos = 10
entonces tengo listaAleatoria = [2,6] entonces con la variable n yo voy a recorrer la lista y comparar con ubicacionCacheo con cada valor de ubicacionCacheo desde el 0 hasta
10. Es decir que 10 veces voy a chequear si el 2 o el 6 son iguales al valor de ubicacionCacheo, osea que van a ser iguales cuando ubicacionCacheo sea igual a 2 y a 6 y en
esos dos casos tendre cacheos positivos. Una vez recorrido la listaAleatoria 10 veces genero una nueva lista y empiezo de vuelta"""
def procesoCacheo(pi):
    auxiliar.EscribirFuncion("procesoCacheo")

    try:
        flag = 0
        
        if variablesGlobales.ubicacionCacheo >= hbl.CACHEO_cantidadCacheos: # Una vez que recorrida la lista la cantidad de veces necesaria (CantidadCacheos), genero una lista nueva
            variablesGlobales.ubicacionCacheo = 0

        # si el valor de ubicacionCacheo es 0, significa que recien empieza el cacheo entonces
        # calcula las n posiciones a cachear por positivo
        if variablesGlobales.ubicacionCacheo == 0:           

            variablesGlobales.listaAleatoria = aleatorioValor(hbl.CACHEO_cacheosPositivos, hbl.CACHEO_cantidadCacheos)       

            log.escribeSeparador(hbl.LOGS_hblCacheo)       
            log.escribeLineaLog(hbl.LOGS_hblCacheo, "Calculo de valores de posicion de cacheo : " + str(variablesGlobales.listaAleatoria)) 
            log.escribeLineaLog(hbl.LOGS_hblCacheo, "Cantidad de cacheos : " + str(hbl.CACHEO_cantidadCacheos)) 
            log.escribeLineaLog(hbl.LOGS_hblCacheo, "Cantidad de cacheos positivos: " + str(hbl.CACHEO_cacheosPositivos)) 
 
        #Recorro la lista con la variable n la cual determinara las posiciones en las cuales voy a tener cacheo positivo
        for n in variablesGlobales.listaAleatoria:
            # Me fijo si en esta ubicacionCacheo tengo un cacheo positivo
            if variablesGlobales.ubicacionCacheo == n:   
                variablesGlobales.valorEncontrado = 1

        if variablesGlobales.valorEncontrado == 1:
            #NoPasa(pi)
            log.escribeLineaLog(hbl.LOGS_hblCacheo, "NoPasa :" + str(variablesGlobales.ubicacionCacheo)) 
            flag = 1
        else:
            #Pasa(pi)
            log.escribeLineaLog(hbl.LOGS_hblCacheo, "Pasa :" + str(variablesGlobales.ubicacionCacheo))            
            flag = 0
         
        # incrementa la variable en 1
        variablesGlobales.ubicacionCacheo = variablesGlobales.ubicacionCacheo + 1
        # reinicia la variable 
        variablesGlobales.valorEncontrado = 0 
        return flag
    
    except Exception as e:  

        exc_type, exc_obj, exc_tb = sys.exc_info() 
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 

        log.escribeSeparador(hbl.LOGS_hblCacheo)
        log.escribeLineaLog(hbl.LOGS_hblCacheo, "Error : " + str(errorExcepcion))  

        return 99