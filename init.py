from flask import Flask, render_template
import os
from flask_mail import Mail,Message
app = Flask(__name__)
app.config.update(
    DEBUG=False,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
)
mail = Mail(app)
mail.init_app(app)

def sendmail(sendto,randomkey):
    #  主旨
    msg_title = 'Sign Up:Yulin NewTab sync services'
    #  寄件者，若參數有設置就不需再另外設置
    msg_sender = 'Yulin NewTab Sync Services','yulinnewtab_signup@legendyang.me'
    #  收件者，格式為list，否則報錯
    msg_recipients = [sendto]
    #  郵件內容
    #  也可以使用html
    msg_html = render_template('signupemail.html',randomkey=randomkey)
    msg = Message(msg_title,
                  sender=msg_sender,
                  recipients=msg_recipients)
    msg.html = msg_html
    
    #  mail.send:寄出郵件
    
    mail.send(msg)
    return 'email sent successfully if the email is correct'

def resetrequest(sendto,randomkey):
    #  主旨
    msg_title = 'Forget Password:Yulin NewTab sync services'
    #  寄件者，若參數有設置就不需再另外設置
    msg_sender = 'Yulin NewTab Sync Services','yulinnewtab_signup@legendyang.me'
    #  收件者，格式為list，否則報錯
    msg_recipients = [sendto]
    #  郵件內容
    #  也可以使用html
    msg_html = render_template('resetpass.html',randomkey=randomkey)
    msg = Message(msg_title,
                  sender=msg_sender,
                  recipients=msg_recipients)
    msg.html = msg_html
    
    #  mail.send:寄出郵件
    
    mail.send(msg)
    return 'reset request sent'    

def deleteacc(sendto,randomkey):
    #  主旨
    msg_title = 'Delete Account:Yulin NewTab sync services'
    #  寄件者，若參數有設置就不需再另外設置
    msg_sender = 'Yulin NewTab Sync Services','yulinnewtab_signup@legendyang.me'
    #  收件者，格式為list，否則報錯
    msg_recipients = [sendto]
    #  郵件內容
    #  也可以使用html
    msg_html = render_template('deletemail.html',randomkey=randomkey)
    msg = Message(msg_title,
                  sender=msg_sender,
                  recipients=msg_recipients)
    msg.html = msg_html
    
    #  mail.send:寄出郵件
    
    mail.send(msg)
    return 'delete request sent'    
