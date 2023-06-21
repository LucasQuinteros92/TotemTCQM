from email.message import EmailMessage
from threading import Thread
import modulos.auxiliar as auxiliar
import modulos.hbl as hbl
import modulos.log as log
import time
import smtplib
import datetime


'''
    COSAS PARA HACER:
        UN METODO UNICO PARA ENVIAR MAILS 
            PARAMS:    
                *MENSAJE
                *VIDEO/FOTO
        QUE EL HILO SEA CAPAZ DE ENVIAR MAILS GUARDADOS CUANDO HAYA CONEXION
        
                
            
'''


class SendMail(object):

    def __init__(self):
        self.pendientes = False
        self.remitente = hbl.Mail_remitente
        self.destinatario = hbl.Mail_destinatarios

        self.door = False
        self.user = hbl.Mail_user
        self.key = hbl.Mail_key
        
        self.count = 0
        if hbl.Mail_activado == 1:
            self.t = Thread(target = self.__run, daemon= False, name = "Mails")
            self.t.start()

    def sendIntrusoMail(self):
            self.count += 1
        
        
    def sendDoorMail(self):
        self.door = True   
        
    def add_intruso(self, date):
        myFile = open(hbl.Contador_IntrusosPendientesPath, 'a')

        with myFile:
            myFile.write(date + "\n")
            myFile.close() 
        self.pendientes = True 
        
    def __LogReport(self, texto):
        log.escribeSeparador(hbl.LOGS_hblMail)
        log.escribeLineaLog(hbl.LOGS_hblMail, texto)      
    
    def __run(self):
        if hbl.Mail_activado == 1:
            while True:
                
                    if self.count > 0:

                            self.email = EmailMessage()
                            
                            self.email["From"] = hbl.Mail_remitente
                            self.email["To"] = hbl.Mail_destinatarios
                            self.email["Subject"] = hbl.Contador_ID+ "  " + hbl.Mail_subject
                            

                            date = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                            try:
                                mensaje = "<html><body><h1> Se ha detectado un intruso en "+hbl.Contador_ID+"\
                                             a las : " + date + "</h1></body></html>"
                                self.email.set_content(mensaje)
                                smtp = smtplib.SMTP_SSL("smtp-relay.sendinblue.com")
                                
                                smtp.login(self.user, self.key)
                                smtp.sendmail(self.remitente, self.destinatario, self.email.as_string())
                                smtp.quit()
                                self.__LogReport(f"mail intruso enviado, quedan : {self.count} pendientes")
                                self.count -= 1
                                print("Intruso Enviado")
                            except Exception as e:
                                
                                self.__LogReport("No se pudo enviar el mail de intruso: %s\n" % e)
                                print("Pendiente agregado")
                                self.add_intruso(date)
                                self.pendientes = True
                                self.count -= 1
                            
                    elif self.pendientes :
                        if auxiliar.CheckInternet():
                            self.email = EmailMessage()
                            self.email["From"] = hbl.Mail_remitente
                            self.email["To"] = hbl.Mail_destinatarios
                            self.email["Subject"] = hbl.Contador_ID+ " " + "Intruso Pendiente"
                    
                            try:

                                with open(hbl.Contador_IntrusosPendientesPath) as file:
                                    lines = [line.strip() for line in file]
                                    file.close()
                                
                                with open(hbl.Contador_IntrusosPendientesPath,"w") as file:
                                    file.write("")
                                    file.close()
                                dates = ""
                                for date in lines:
                                    dates = dates + date.strip() + "\n"
                                if dates != "":
                                    mensaje = "<html><body><h1> Se ha detectado un intruso en "+hbl.Contador_ID+"\
                                            a las :  \n" + dates + "</h1></body></html>"
                                    
                                    self.email.set_content(mensaje)
                                    smtp = smtplib.SMTP_SSL("smtp-relay.sendinblue.com")
                                    smtp.login(self.user, self.key)
                                    smtp.sendmail(self.remitente, self.destinatario, self.email.as_string())
                                    smtp.quit()
                                    self.__LogReport(f"mail intruso pendiente enviado, fecha: {date}")
                                    time.sleep(0.5)
                                    self.pendientes = False
                                    print("pendientes enviados")
                                
                            except Exception as e:
                                
                                self.__LogReport("No se pudo enviar el mail de intruso pendiente : %s\n" % e)
                        else:
                            time.sleep(5)
                            
                    elif self.door:
                        if auxiliar.CheckInternet():
                            self.email = EmailMessage()
                            
                            self.email["From"] = hbl.Mail_remitente
                            self.email["To"] = hbl.Mail_destinatarios
                            self.email["Subject"] = hbl.Contador_ID + " "+ " Puerta abierta"
                            
                            date = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                            try:
                                mensaje = "<html><body><h1> Se ha detectado que la puerta "+hbl.Contador_ID+\
                                          " esta abierta a las : " + date + "</h1></body></html>"
                                self.email.set_content(mensaje)
                                smtp = smtplib.SMTP_SSL("smtp-relay.sendinblue.com")
                                
                                smtp.login(self.user, self.key)
                                smtp.sendmail(self.remitente, self.destinatario, self.email.as_string())
                                smtp.quit()
                                self.__LogReport(f"mail por puerta abierta enviado")
                                
                            except Exception as e:
                                self.__LogReport("No se pudo enviar el mail por puerta abierta : %s\n" % e)
                                
                            self.door = False
                        else:
                            time.sleep(5)
                    else:
                        self.HayIntrusosPendientes()
                        time.sleep(0.5)
                        
    def HayIntrusosPendientes(self):
        myFile = open(hbl.Contador_IntrusosPendientesPath, 'r')

        with myFile:
            if myFile.readline():
                self.pendientes = True 
            else:
                self.pendientes = False
            myFile.close() 
        