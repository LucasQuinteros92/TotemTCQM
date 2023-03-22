import datetime
import os
import requests
import time  
import threading  
import usb.util
from usb.core import find as finddev  
import json
import sys

from modulos import hbl as hbl
from modulos import delays as delays
from modulos import log as log
from modulos import auxiliar as auxiliar
from modulos import auxiliar as auxiliar

global device

global modemUSB_VendorID  
global modemUSB_ProductID  

global conexionPPPActiva
 
     
""" --------------------------------------------------------------------------------------------
 
    Funciones de conexiones de red
 
    * GSM
    * ETH
    * WLAN
 
-------------------------------------------------------------------------------------------- """ 
""" --------------------------------------------------------------------------------------------
 
    determinar si hay conexion segun la interfase de red

    ej : ping -I wlan0 -c 3 www.google.com
 
-------------------------------------------------------------------------------------------- """ 

# from subprocess import check_call, CalledProcessError, PIPE 


# def is_reachable(inter, i, add):
#     command = ["ping", "-I", inter, "-c", i, add]
#     try:
#         check_call(command, stdout=PIPE)
#         return True
#     except CalledProcessError as e:
#         if e.returncode == 1:
#             return False
#         raise
 
# if __name__ == "__main__":
    
#     ret = is_reachable("eth0", "3", "8.8.8.8")
#     print(ret)
 
""" --------------------------------------------------------------------------------------------

   carga parametros en el archivo wvdial.conf

    # leer configuracion del hbl para el archivo wvdialconf
    #
    # ejemplo de archivo de configuracion : 
    #
    # [Dialer Defaults]
    # Init1 = ATZ
    # Init2 = ATQ0 V1 E1 S0=0 &C1 &D2 +FCLASS=0
    # Init3 = AT+CFUN=1,0
    # Init4 = AT+CGDCONT=1,"IP","igprs.claro.com.ar"
    # Modem = /dev/ttyUSB1
    # Phone = *99#
    # Password = clarogprs999
    # Modem Type = Analog Modem
    # Stupid Mode = 1
    # Baud = 9600
    # New PPPD = yes
    # Dial Command = ATDT
    # Ask Password = 0
    # ISDN = 0
    # Username = clarogprs
    # Carrier Check = 0
    # Auto Reconnect = 1

-------------------------------------------------------------------------------------------- """

def cargarParametrosppp(portGSM):
    auxiliar.EscribirFuncion("cargarParametrosppp")

    with open("/etc/wvdial.conf", 'w') as ObjFichero:                
        ObjFichero.write("[Dialer Defaults]\n")
        ObjFichero.write("Dial Command = " + str(hbl.NETWORK_ppp0_dialcommand) + "\n")
        ObjFichero.write("Init1 = " + str(hbl.NETWORK_ppp0_init1) + "\n")
        ObjFichero.write("Init2 = " + str(hbl.NETWORK_ppp0_init2) + "\n")
        ObjFichero.write("Init3 = " + str(hbl.NETWORK_ppp0_init3) + "\n")
        ObjFichero.write("Init4 = " + (str(hbl.NETWORK_ppp0_init4)).replace(chr(39), chr(34)) + "\n") # reemplaza el caracter ' por el "
        ObjFichero.write("Modem = " + str(portGSM) + "\n")
        ObjFichero.write("Phone = " + str(hbl.NETWORK_ppp0_phone) + "\n")
        ObjFichero.write("Password = " + str(hbl.NETWORK_ppp0_password) + "\n")
        ObjFichero.write("Modem Type = " + str(hbl.NETWORK_ppp0_modemType) + "\n")
        ObjFichero.write("Stupid Mode = " + str(hbl.NETWORK_ppp0_stupidmode) + "\n")
        ObjFichero.write("Baud = " + str(hbl.NETWORK_ppp0_baud) + "\n")
        ObjFichero.write("New PPPD = " + str(hbl.NETWORK_ppp0_newPPPD) + "\n") 
        ObjFichero.write("Ask Password = " + str(hbl.NETWORK_ppp0_askPassword) + "\n")
        ObjFichero.write("ISDN = " + str(hbl.NETWORK_ppp0_ISDN) + "\n")
        ObjFichero.write("Username = " + str(hbl.NETWORK_ppp0_username) + "\n")
        ObjFichero.write("Carrier Check = " + str(hbl.NETWORK_ppp0_carrierCheck) + "\n")
        ObjFichero.write("Auto Reconnect = " + str(hbl.NETWORK_ppp0_autoReconnect) + "\n")
        ObjFichero.write("Dial Attempts = " + str(hbl.NETWORK_ppp0_dialAttempts)  + "\n")  

""" --------------------------------------------------------------------------------------------

   iniciar conexion GSM

   cargarParametrosppp(portGSM)

-------------------------------------------------------------------------------------------- """

def startGSM(): 
    auxiliar.EscribirFuncion("startGSM")

    global conexionPPPActiva

    log.escribeSeparador(hbl.LOGS_hblConexiones)
    log.escribeLineaLog(hbl.LOGS_hblConexiones, "Iniciando script conexion...")    
 
    intentosConexion = 0

    modemUSB_VendorID = "0"
    modemUSB_ProductID = "0"

    conexionPPPActiva = 0

    while True:

        try:

            response = requests.get(hbl.NETWORK_testConexion_url, timeout=int(hbl.NETWORK_testConexion_timeoutUrl))
            log.escribeLineaLog(hbl.LOGS_hblConexiones, response.text) 
            conexionPPPActiva = 1

        except (requests.ConnectionError, requests.Timeout):

            try:
                # busca que modem USB esta conectado al HBL 

                # inicializa el flag que indica que no hay conexion ppp0
                conexionPPPActiva = 0

                # modem movistar
                modemConectado = os.popen("lsusb -d 19d2:2000").read() 

                if modemConectado:
                    # realizar el switch del modem GSM 
                    log.escribeLineaLog(hbl.LOGS_hblConexiones, "USB Mode Switch (0x19d2 - 0x2000) ...")
                    os.system("sudo usb_modeswitch -v 0x19d2 -p 0x2000 -n -I -M 55534243123456702000000080000c85010101180101010101000000000000")                     
                    modemUSB_VendorID = "0x19d2"
                    modemUSB_ProductID = "0x0031"
                
                modemConectado = os.popen("lsusb -d 19d2:0031").read() 

                if modemConectado:
                    log.escribeLineaLog(hbl.LOGS_hblConexiones, "No es necesario el switch en el modem usb : v (0x19d2) - p (0x0031)")
                    modemUSB_VendorID = "0x19d2"
                    modemUSB_ProductID = "0x0031"
                 
                # modem HUAWEI
                modemConectado = os.popen("lsusb -d 12d1:1f01").read() 

                if modemConectado:
                    # realizar el switch del modem GSM 
                    log.escribeLineaLog(hbl.LOGS_hblConexiones, "USB Mode Switch (0x12d1 - 0x1f01) ...")
                    os.system("sudo usb_modeswitch -v 0x12d1 -p 0x1f01 -n -I -M 55534243123456780000000000000011063000000100010000000000000000") 
                    modemUSB_VendorID = "0x12d1"
                    modemUSB_ProductID = "0x155e"
                 
                modemConectado = os.popen("lsusb -d 12d1:155e").read() 

                if modemConectado:
                    log.escribeLineaLog(hbl.LOGS_hblConexiones, "No es necesario el switch en el modem usb : v (0x12d1) - p (0x155e)")
                    modemUSB_VendorID = "0x12d1"
                    modemUSB_ProductID = "0x155e"

                # modem CLARO
                modemConectado = os.popen("lsusb -d 19d2:1589").read() 

                if modemConectado:     
                    log.escribeLineaLog(hbl.LOGS_hblConexiones, "No es necesario el switch en el modem usb : v (0x19d2) - p (0x1589)")
                    modemUSB_VendorID = "0x19d2"
                    modemUSB_ProductID = "0x1589"

                time.sleep(int(hbl.NETWORK_testConexion_timeDelay))

                # no hay conexion, reseteo la conexion
                log.escribeLineaLog(hbl.LOGS_hblConexiones, "F/H : " + str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
                log.escribeLineaLog(hbl.LOGS_hblConexiones, "No hay conexion, reseteando...")

                intentosConexion = intentosConexion + 1

                log.escribeLineaLog(hbl.LOGS_hblConexiones,"Intentos Conexion : " + str(intentosConexion))
                
                if intentosConexion == int(hbl.NETWORK_testConexion_intentosConexion):
                    
                    intentosConexion = 0

                    # si el reset esta activado, resetea la RPI, sino continua sin reset 
                    if int(hbl.NETWORK_testConexion_resetActivado) == 1 :
                        log.escribeLineaLog(hbl.LOGS_hblConexiones,"Reboot device...")
                        os.system("sudo reboot") 

                log.escribeLineaLog(hbl.LOGS_hblConexiones, "Reset device...")

                dev = finddev(idVendor=int(modemUSB_VendorID, 0), idProduct=int(modemUSB_ProductID, 0))
                dev.reset()

                # delay necesario para el reset
                time.sleep(int(hbl.NETWORK_testConexion_timeDelay))

                log.escribeLineaLog(hbl.LOGS_hblConexiones, "Search device...")

                device = usb.core.find(find_all=True, idVendor=int(modemUSB_VendorID, 0), idProduct=int(modemUSB_ProductID, 0))
                time.sleep(int(hbl.NETWORK_testConexion_timeDelay))             

                # lee todos los puertos USB disponibles para realizar el test y conexion de cual es el del modem USB
                p = os.popen("ls /dev/ttyUSB*").read()  
                puertosUSB = p.split() 
                
                # escribe en el log los USB devices que pueden estar asignados
                log.escribeLineaLog(hbl.LOGS_hblConexiones, "Bash : ls /dev/ttyUSB* : " + str(p)) 
                log.escribeLineaLog(hbl.LOGS_hblConexiones, "Modems USB disponibles : " + str(puertosUSB)) 

                for portGSM in puertosUSB:

                    try:

                        # escribe en el log el puerto tty del Modem 
                        log.escribeLineaLog(hbl.LOGS_hblConexiones,"Test de Modem en puerto : " + portGSM)

                        # editar archivo wvconf
                        cargarParametrosppp(portGSM)

                        log.escribeLineaLog(hbl.LOGS_hblConexiones, "Start connection...")
                        os.system("sudo wvdial")
                    
                    except Exception as e:  
        
                        exc_type, exc_obj, exc_tb = sys.exc_info() 
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
                        errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 
                    
                        log.escribeSeparador(hbl.LOGS_hblConexiones)
                        log.escribeLineaLog(hbl.LOGS_hblConexiones, "Error : " + str(errorExcepcion))    

                # espera la conexion
                time.sleep(int(hbl.NETWORK_testConexion_timeDelay))

            except Exception as e:  
        
                exc_type, exc_obj, exc_tb = sys.exc_info() 
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
                errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 
            
                log.escribeSeparador(hbl.LOGS_hblConexiones)
                log.escribeLineaLog(hbl.LOGS_hblConexiones, "Error : " + str(errorExcepcion))    

                time.sleep(int(hbl.NETWORK_testConexion_timeDelay))

        time.sleep(int(hbl.NETWORK_testConexion_timeRepeat))


""" --------------------------------------------------------------------------------------------
   
   leer ip segun adaptador

-------------------------------------------------------------------------------------------- """

def get_ip_address(ifname): 
    auxiliar.EscribirFuncion("get_ip_address")

    try:
        ipv4 = os.popen('ip addr show ' + ifname).read().split("inet ")[1].split(" ")[0]
        return ipv4
    except:
        return "-"

""" --------------------------------------------------------------------------------------------
   
   leer los bytes entrantes y salientes de cada interfase (eth0 / wlan0 / ppp0)
   
   ej : 

       # cat /sys/class/net/eth0/statistics/rx_bytes 
       # cat /sys/class/net/eth0/statistics/tx_bytes

-------------------------------------------------------------------------------------------- """

def get_bytes_interface_rx(interface):
    auxiliar.EscribirFuncion("get_bytes_interface_rx")
    bytesRx = 0

    try:
        bytesRx = os.popen('cat /sys/class/net/' + interface + '/statistics/rx_bytes').read()
        return bytesRx
    except:
        return "0"

def get_bytes_interface_tx(interface):
    auxiliar.EscribirFuncion("get_bytes_interface_tx")

    bytesTx = 0

    try:
        bytesTx = os.popen('cat /sys/class/net/' + interface + '/statistics/tx_bytes').read()
        return bytesTx
    except:
        return "0"

def bytesppp0(rxtx):
    auxiliar.EscribirFuncion("bytesppp0")

    if hbl.NETWORK_ppp0_activado == 1 and conexionPPPActiva == 1:

        if rxtx == "rx":
                
            try:             
                rx_bytes_ppp0 = str(format(int(get_bytes_interface_rx('ppp0')) / 1024768, ".2f"))            
            except: 
                rx_bytes_ppp0 = "0.00"
            
            return rx_bytes_ppp0

        elif rxtx == "tx":
                
            try:            
                tx_bytes_ppp0 = str(format(int(get_bytes_interface_tx('ppp0')) / 1024768, ".2f"))          
            except:
                tx_bytes_ppp0 = "0.00" 
            
            return tx_bytes_ppp0
    
    else:

        return 0

 
""" --------------------------------------------------------------------------------------------

   escribir parametros archivo dhcpcd.conf

-------------------------------------------------------------------------------------------- """

def escribeParametros():
    auxiliar.EscribirFuncion("escribeParametros")
 
    # agrega la cabecera de inicializacion HBL
    parametrosNet = [' ', '#Configuracion HBL', ' ']
    auxiliar.append_multiple_lines('/etc/dhcpcd.conf', parametrosNet, "a+")

    # escribe los parametros por defecto en el archivo dhcpcd.conf

    # hostname
    # clientid
    # persistent
    # option rapid_commit   
    # option domain_name_servers, domain_name, domain_search, host_name
    # option classless_static_routes
    # option ntp_servers
    # option interface_mtu
    # require dhcp_server_identifier
    # slaac private
 
    parametrosNet = ['hostname', 'clientid', 'persistent', 'option rapid_commit', 'option domain_name_servers, domain_name, domain_search, host_name', 'option classless_static_routes','option ntp_servers', 'option interface_mtu', 'require dhcp_server_identifier', 'slaac private', ' ']
    auxiliar.append_multiple_lines('/etc/dhcpcd.conf', parametrosNet, "w+") 

    parametrosNet = [' ', 'source-directory /etc/network/interfaces.d', 'auto lo', 'iface lo inet loopback', ' ']
    auxiliar.append_multiple_lines('/etc/network/interfaces', parametrosNet, "w+") 
    
    # ************************************************************************************************************************************************
    # eth0
    if hbl.NETWORK_eth0_activado == 1:
        os.system("sudo ifconfig eth0 up") ##Habilita el puerto ethernet
        time.sleep(1)
        # si está habilitado el dhcp, escribe la configuracion pero la comenta para que no tenga efecto
        if hbl.NETWORK_eth0_dhcp == 1:
            parametrosNet = ['interface eth0', '#metric ' + str(hbl.NETWORK_eth0_metric), '#static ip_address=' + str(hbl.NETWORK_eth0_static_ip_address), '#static routers=' + str(hbl.NETWORK_eth0_static_routers)] 
            auxiliar.append_multiple_lines('/etc/dhcpcd.conf', parametrosNet, "a+")



            parametrosNet = ['allow-hotplug eth0' , 'iface eth0 inet dhcp', '#    address ' + str(hbl.NETWORK_eth0_static_ip_address), '#    netmask ' + str(hbl.NETWORK_eth0_netmask), '#    network ' + str(hbl.NETWORK_eth0_network), '#    broadcast '+ str(hbl.NETWORK_eth0_broadcast)] 
            auxiliar.append_multiple_lines('/etc/network/interfaces', parametrosNet, "a+")
        else:
            parametrosNet = ['interface eth0']
            if str(hbl.NETWORK_eth0_metric) != "":
                parametrosNet.append('metric ' + str(hbl.NETWORK_eth0_metric))
            
            if str(hbl.NETWORK_eth0_static_ip_address) != "":
                parametrosNet.append('static ip_address=' + str(hbl.NETWORK_eth0_static_ip_address))

            if str(hbl.NETWORK_eth0_DNS) != "":
                parametrosNet.append('static domain_name-servers=' + str(hbl.NETWORK_eth0_DNS))
            
            if str(hbl.NETWORK_eth0_gateway) != "":
                parametrosNet.append('static routers=' + str(hbl.NETWORK_eth0_gateway))

            auxiliar.append_multiple_lines('/etc/dhcpcd.conf', parametrosNet, "a+")

            # se agregan los parametros de IP estatica al archivo interfaces
            # source-directory /etc/network/interfaces.d

            # ex : 
            # allow-hotplug eth0
            # iface eth0 inet static
            #     address 192.168.1.1
            #     netmask 255.255.255.0
            #     network 192.168.1.0
            #     broadcast 192.168.1.255
            parametrosNet = ['allow-hotplug eth0' , 'iface eth0 inet static'] 
            if str(hbl.NETWORK_eth0_static_ip_address) != "":
                parametrosNet.append('    address ' + str(hbl.NETWORK_eth0_static_ip_address))
            
            if str(hbl.NETWORK_eth0_netmask) != "":
                parametrosNet.append('    netmask ' + str(hbl.NETWORK_eth0_netmask))
            
            if str(hbl.NETWORK_eth0_network) != "":
                parametrosNet.append('    network ' + str(hbl.NETWORK_eth0_network))
            
            if str(hbl.NETWORK_eth0_broadcast) != "":
                parametrosNet.append('    broadcast ' + str(hbl.NETWORK_eth0_broadcast))
            
            if str(hbl.NETWORK_eth0_DNS) != "":
                parametrosNet.append('    dns-nameservers ' + str(hbl.NETWORK_eth0_DNS))

            if str(hbl.NETWORK_eth0_gateway) != "":
                parametrosNet.append('    gateway ' + str(hbl.NETWORK_eth0_gateway))

            auxiliar.append_multiple_lines('/etc/network/interfaces', parametrosNet, "a+") 
        
        parametrosNet = [' ']
        auxiliar.append_multiple_lines('/etc/dhcpcd.conf', parametrosNet, "a+")
        auxiliar.append_multiple_lines('/etc/network/interfaces', parametrosNet, "a+")

        # ejecutar el comando ifdown / ifup : al cambiar de static a dhcp se detecto un problema que se corrigio con ese comando.
        # os.system("sudo ifdown eth0")
        # time.sleep(1)
        # os.system("sudo ifup eth0")
        # time.sleep(1)
    else:
        os.system("sudo ifconfig eth0 down")## Deshabilita el puerto ethernet
        time.sleep(1)

    
    # ************************************************************************************************************************************************
    # eth1
    if hbl.NETWORK_eth1_activado == 1:
        os.system("sudo ifconfig eth1 up")## Habilita el puerto ethernet
        time.sleep(1)
        try:
            # realiza un reset del dispositivo
            log.escribeLineaLog(hbl.LOGS_hblConexiones,"Reset device eth1...")
            devEth = finddev(idVendor=int(hbl.NETWORK_eth1_vendor_ID, 0), idProduct=int(hbl.NETWORK_eth1_product_ID, 0))
            devEth.reset()
            
        except Exception as e:  

            exc_type, exc_obj, exc_tb = sys.exc_info() 
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
            errorExcepcion = "ERROR - archivo : " + str(fname) + " - linea : " + str(sys.exc_info()[-1].tb_lineno) + " - mensaje : " + str(exc_obj) 
        
            log.escribeSeparador(hbl.LOGS_hblConexiones)
            log.escribeLineaLog(hbl.LOGS_hblConexiones, "Error : " + str(errorExcepcion)) 

        time.sleep(int(hbl.NETWORK_eth1_timeDelay)) 
        
        os.system("sudo dhclient eth1 -v") 

        # si está habilitado el dhcp, escribe la configuracion pero la comenta para que no tenga efecto
        if hbl.NETWORK_eth1_dhcp == 1:
            parametrosNet = ['interface eth1', 'metric ' + str(hbl.NETWORK_eth1_metric), '#static ip_address=' + str(hbl.NETWORK_eth1_static_ip_address), '#static routers=' + str(hbl.NETWORK_eth1_static_routers)] 
            auxiliar.append_multiple_lines('/etc/dhcpcd.conf', parametrosNet, "a+")

            parametrosNet = [' ','auto eth1','iface eth1 inet dhcp']            
            auxiliar.append_multiple_lines('/etc/network/interfaces', parametrosNet, "a+")
 
        else:
            parametrosNet = ['interface eth1']
            if str(hbl.NETWORK_eth1_metric) != "":
                parametrosNet.append('metric ' + str(hbl.NETWORK_eth1_metric))
            
            if str(hbl.NETWORK_eth1_static_ip_address) != "":
                parametrosNet.append('static ip_address=' + str(hbl.NETWORK_eth1_static_ip_address))

            if str(hbl.NETWORK_eth1_DNS) != "":
                parametrosNet.append('static domain_name-servers=' + str(hbl.NETWORK_eth1_DNS))
            
            if str(hbl.NETWORK_eth1_gateway) != "":
                parametrosNet.append('static routers=' + str(hbl.NETWORK_eth1_gateway))

            auxiliar.append_multiple_lines('/etc/dhcpcd.conf', parametrosNet, "a+")

            # se agregan los parametros de IP estatica al archivo interfaces
            # source-directory /etc/network/interfaces.d

            # ex : 
            # allow-hotplug eth1
            # iface eth1 inet static
            #     address 192.168.1.1
            #     netmask 255.255.255.0
            #     network 192.168.1.0
            #     broadcast 192.168.1.255
            parametrosNet = ['allow-hotplug eth1' , 'iface eth1 inet static'] 
            if str(hbl.NETWORK_eth1_static_ip_address) != "":
                parametrosNet.append('    address ' + str(hbl.NETWORK_eth1_static_ip_address))
            
            if str(hbl.NETWORK_eth1_netmask) != "":
                parametrosNet.append('    netmask ' + str(hbl.NETWORK_eth1_netmask))
            
            if str(hbl.NETWORK_eth1_network) != "":
                parametrosNet.append('    network ' + str(hbl.NETWORK_eth1_network))
            
            if str(hbl.NETWORK_eth1_broadcast) != "":
                parametrosNet.append('    broadcast ' + str(hbl.NETWORK_eth1_broadcast))
            
            if str(hbl.NETWORK_eth1_DNS) != "":
                parametrosNet.append('    dns-nameservers ' + str(hbl.NETWORK_eth1_DNS))

            if str(hbl.NETWORK_eth1_gateway) != "":
                parametrosNet.append('    gateway ' + str(hbl.NETWORK_eth1_gateway))
    else:
        os.system("sudo ifconfig eth1 down")## Deshabilita el puerto ethernet
        time.sleep(1)

    # ************************************************************************************************************************************************
    # wlan0
    if hbl.NETWORK_wlan0_activado == 1:
        os.system("sudo ifconfig wlan0 up")## Habilita el WIFI
        time.sleep(1)
        # si está habilitado el dhcp, escribe la configuracion pero la comenta para que no tenga efecto
        if hbl.NETWORK_wlan0_dhcp == 1:
            parametrosNet = [' ' , 'interface wlan0', 'metric ' + str(hbl.NETWORK_wlan0_metric), '#static ip_address=' + str(hbl.NETWORK_wlan0_static_ip_address), '#static routers=' + str(hbl.NETWORK_wlan0_static_routers)] 
            auxiliar.append_multiple_lines('/etc/dhcpcd.conf', parametrosNet, "a+")
            parametrosNet = [' ','allow-hotplug wlan0','iface wlan0 inet manual']   # Te habilita el simbolito azul de WIFI 
            auxiliar.append_multiple_lines('/etc/network/interfaces', parametrosNet, "a+")
        else:
            # se agregan los parametros de IP estatica al archivo dhcpcf.conf
            parametrosNet = [' ' , 'interface wlan0']
            if str(hbl.NETWORK_wlan0_metric) != "":
                parametrosNet.append('metric ' + str(hbl.NETWORK_wlan0_metric))
            
            if str(hbl.NETWORK_wlan0_static_ip_address) != "":
                parametrosNet.append('static ip_address=' + str(hbl.NETWORK_wlan0_static_ip_address))
                
            if str(hbl.NETWORK_wlan0_static_routers) != "":
                parametrosNet.append('static routers=' + str(hbl.NETWORK_wlan0_static_routers)) 

            if str(hbl.NETWORK_wlan0_DNS) != "":
                parametrosNet.append('static domain_name-servers=' + str(hbl.NETWORK_wlan0_DNS))
            
            if str(hbl.NETWORK_wlan0_gateway) != "":
                parametrosNet.append('static routers=' + str(hbl.NETWORK_wlan0_gateway))

            auxiliar.append_multiple_lines('/etc/dhcpcd.conf', parametrosNet, "a+")
    
        # archivo wpa_supplicant.conf
        # agrega la cabecera de inicializacion

        # ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        # update_config=1
        # country=AR



        parametrosNet = ['ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev' , 'update_config=1', 'country=AR', ' ' , ' ']
        auxiliar.append_multiple_lines('/etc/wpa_supplicant/wpa_supplicant.conf', parametrosNet, "w+")
                  
        parametrosNet = [' ' , 'network={', '    ssid="' + str(hbl.NETWORK_wlan0_ssid) + '"', '    psk="' + str(hbl.NETWORK_wlan0_password) + '"', '}']
        auxiliar.append_multiple_lines('/etc/wpa_supplicant/wpa_supplicant.conf', parametrosNet, "a+")
    else:
        os.system("sudo ifconfig wlan0 down")## Deshabilita el WIFI
        time.sleep(1)
   
    # ************************************************************************************************************************************************
    # ppp0 
    # si esta activada la interfaz de modem gsm, la selecciona como la default para la conectividad a internet.
    if hbl.NETWORK_ppp0_activado == 1:
        pass
        # # To delete the old default gateway
        # os.system("sudo route del default")
        # # To add the new gateway
        # os.system("sudo route add default gw 10.64.64.64 dev ppp0")

""" --------------------------------------------------------------------------------------------

   escribe log data transfer

-------------------------------------------------------------------------------------------- """

def dataTransferLog():
    auxiliar.EscribirFuncion("dataTransferLog")

    global conexionPPPActiva


    # para grabar la cabecera con la fecha y hora debe haber al menos una interfaz activa
    if hbl.NETWORK_eth0_activado == 1 or hbl.NETWORK_wlan0_activado == 1 or hbl.NETWORK_ppp0_activado == 1:
        log.escribeSeparador(hbl.LOGS_hblConexiones)  

    # eth0
    if hbl.NETWORK_eth0_activado == 1:
        tx_bytes_eth0 = str(format(int(get_bytes_interface_tx('eth0')) / 1024768, ".2f")) 
        rx_bytes_eth0 = str(format(int(get_bytes_interface_rx('eth0')) / 1024768, ".2f")) 
        log.escribeLineaLog(hbl.LOGS_hblConexiones, "eth0 (Mb) /  Tx : " + tx_bytes_eth0 + "  /  Rx : " + rx_bytes_eth0)

    # wlan0
    if hbl.NETWORK_wlan0_activado == 1:        
        tx_bytes_wlan0 = str(format(int(get_bytes_interface_tx('wlan0')) / 1024768, ".2f")) 
        rx_bytes_wlan0 = str(format(int(get_bytes_interface_rx('wlan0')) / 1024768, ".2f")) 
        log.escribeLineaLog(hbl.LOGS_hblConexiones, "wlan0 (Mb) /  Tx : " + tx_bytes_wlan0 + "  /  Rx : " + rx_bytes_wlan0)

    # ppp0
    if hbl.NETWORK_ppp0_activado == 1 and conexionPPPActiva == 1:
        rx_bytes_ppp0 = bytesppp0('rx')
        tx_bytes_ppp0 = bytesppp0('tx')         
        log.escribeLineaLog(hbl.LOGS_hblConexiones, "ppp0 (Mb) /  Tx : " + tx_bytes_ppp0 + "  /  Rx : " + rx_bytes_ppp0) 

  
""" --------------------------------------------------------------------------------------------

   configuracion de las redes

-------------------------------------------------------------------------------------------- """

def NetworkConfig():
    auxiliar.EscribirFuncion("NetworkConfig")

    if hbl.NETWORK_activado == 1: 

        escribeParametros() 


def GSM_Modem_Init(): 
    auxiliar.EscribirFuncion("GSM_Modem_Init")

    if hbl.NETWORK_ppp0_activado == 1:  

        modemGSM = threading.Thread(target=startGSM, name='modemGSM')
        modemGSM.setDaemon(True)
        modemGSM.start()
                