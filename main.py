import time,os
from dotenv import load_dotenv
load_dotenv(override=True)
from flask import Flask, render_template,request, redirect,make_response,jsonify
import pymongo
client = pymongo.MongoClient(os.getenv('MONGO_URL'))
userdb = client['userdb']
signupdb = client['signupdb']
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

def sendmail(sendto):
    #  主旨
    msg_title = 'Sign Up:Yulin NewTab sync services'
    #  寄件者，若參數有設置就不需再另外設置
    msg_sender = 'event@legendyang.me'
    #  收件者，格式為list，否則報錯
    msg_recipients = [sendto]
    #  郵件內容
    #  也可以使用html
    msg_html = '<h1>Hello, this is Yulin NewTab sync services. Please click the link below to verify your email address. https://newtab.yulin.tw/verify?email='+sendto+'</h1>'
    msg = Message(msg_title,
                  sender=msg_sender,
                  recipients=msg_recipients)
    msg.html = msg_html
    
    #  mail.send:寄出郵件
    mail.send(msg)

@app.route('/')
def test():
    return jsonify({'status':'ok'})

@app.route('/createacc', methods=['POST'])
def createacc():
    if request.method == 'POST':
        email = request.form['email']
        password = hash(request.form['password'])
        if userdb['user'].find_one({'email':email}) == None:
            userdb['user'].insert_one({'email':email,'password':password})
            sendmail(email)
            return jsonify({'status':'success'})
        
        else:
            return jsonify({'status':'alweady exist'})
        
if __name__ == '__main__':
    app.run()