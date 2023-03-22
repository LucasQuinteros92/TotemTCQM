#from escpos.printer import Usb
import time
        
def ImpresionTest():
    try:
        p = Usb(0x067b, 0x2305, 0, profile="TM-T88II")
    except Exception as e:
        print("No se encuentra la impresora. Verifique si esta conectada.")
    try:
        p.text(time.strftime("%d/%m/%y") + "  -  " + time.strftime("%H:%M:%S") + "\n")
        p.text("Hello World\n")
        p.barcode('1324354657687', 'EAN13', 64, 2, '', '')
        p.qr("https://www.jphlions.com/",size=8)
        p.image("/home/pi/Desktop/JPHLogo.gif")
        p.cut()
    except Exception as e:
        print("Error de Impresion")
