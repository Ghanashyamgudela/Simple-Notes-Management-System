import smtplib
from email.message import EmailMessage

def send_mail(to,body,subject):
    server = smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('ghana19183@gmail.com','jmwe kafu lmdp cmpr')
    msg = EmailMessage()  #creating obj for EmailMessage format
    msg['FROM'] = 'noreply.notes@gmail.com'
    msg['TO'] = to
    msg['SUBJECT'] = subject
    msg.set_content(body)
    server.send_message(msg)
    server.close()