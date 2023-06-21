import os
from modulos import hbl as hbl
from modulos import log as log
from modulos import auxiliar as auxiliar

def inicializacion():
    auxiliar.EscribirFuncion("inicializacion")

    if hbl.KIOSCO_activado:
        URL = "XAUTHORITY=/root/Xauthority firefox -kiosk -printing -private-window " + "'" + hbl.KIOSCO_URL + "' "

        if hbl.KIOSCO_width != "":
            URL = URL + "-width " + hbl.KIOSCO_width 
        if hbl.KIOSCO_height != "":
            URL = URL + " -height " + hbl.KIOSCO_height

        URL = URL + " &"    

        log.escribeLineaLog(hbl.LOGS_hblKiosco,"Abriendo: " + hbl.KIOSCO_URL)
        try:
            os.system("xhost +SI:localuser:root")
            os.system("xset -dpms")
            os.system("xset s off")
            os.system("xset s noblank")
            os.system(URL)
            log.escribeLineaLog(hbl.LOGS_hblKiosco,"URL abierta exitosamente")
        except Exception as e:
            log.escribeLineaLog(hbl.LOGS_hblKiosco,"No se pudo abrir la URL")