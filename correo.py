from email.message import EmailMessage
import smtplib

def enviar_correo(destinatario,asunto,mensaje):
    remitente = "ananias.paredes@utec.edu.pe" #correo desde el que se enviará
    email = EmailMessage()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = asunto
    email.set_content(mensaje)
    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
    smtp.login(remitente, "ehddkkecntagjicz")#contraseña generada por Gmail para la cuenta creada
    
    smtp.sendmail(remitente, destinatario, email.as_string())
    smtp.quit()

# correo (<cuenta>,<asunto_de_correo>,<mensaje>)
# correo("ananias.paredes@utec.edu.pe","Desde Python","Hola mundo")