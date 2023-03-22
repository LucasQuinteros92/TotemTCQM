from email.message import EmailMessage
from threading import Thread
import modulos.auxiliar as auxiliar
import modulos.hbl as hbl
import time
import smtplib
import datetime


class SendMail(object):

    def __init__(self):
        self.pendientes = False
        self.remitente = hbl.Mail_remitente
        self.destinatario = hbl.Mail_destinatarios


        self.user = hbl.Mail_user
        self.key = hbl.Mail_key
        
        self.count = 0
        if hbl.Mail_activado == 1:
            self.t = Thread(target = self.__run, daemon= False)
            self.t.start()

    def send(self):
        
        self.count += 1         
    
    def __run(self):
        if hbl.Mail_activado == 1:
            while True:
                if auxiliar.CheckInternet():
                    if self.count > 0:
                        self.count -= 1
                        self.email = EmailMessage()
                        
                        self.email["From"] = hbl.Mail_remitente
                        self.email["To"] = hbl.Mail_destinatarios
                        self.email["Subject"] = hbl.Mail_subject
                        

                        date = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                        try:
                            mensaje = "<html><body><h1> Se ha detectado un intrusoa a las : " + date + "</h1></body></html>"
                            self.email.set_content(mensaje)
                            smtp = smtplib.SMTP_SSL("smtp-relay.sendinblue.com")
                            smtp.login(self.user, self.key)
                            smtp.sendmail(self.remitente, self.destinatario, self.email.as_string())
                            smtp.quit()
                            #print(f"mail enviado, quedan: {self.count}")
                            
                            
                        except Exception as e:
                            print("No se pudo enviar el mail : %s\n" % e)
                            
                    elif self.pendientes :
                        self.email = EmailMessage()
                        self.email["From"] = hbl.Mail_remitente
                        self.email["To"] = hbl.Mail_destinatarios
                        self.email["Subject"] = "Intruso Pendiente"
                
                        try:

                            with open(hbl.Contador_IntrusosPendientesPath) as file:
                                lines = [line.strip() for line in file]
                                file.close()
                               
                            with open(hbl.Contador_IntrusosPendientesPath,"w") as file:
                                file.write("")
                                file.close()
                            
                            for date in lines:
                                mensaje = "<html><body><h1> Se ha detectado un intrusoa a las : " + date + "</h1></body></html>"
                                self.email.set_content(mensaje)
                                smtp = smtplib.SMTP_SSL("smtp-relay.sendinblue.com")
                                smtp.login(self.user, self.key)
                                smtp.sendmail(self.remitente, self.destinatario, self.email.as_string())
                                smtp.quit()
                                print(f"mail enviado, fecha: {date}")
                                time.sleep(0.5)
                            self.pendientes = False
                            
                            
                        except Exception as e:
                            print("No se pudo enviar el mail : %s\n" % e)
                        
                        
                
                else:
                    time.sleep(0.5)