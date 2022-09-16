import time,os
import random, string
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

def sendmail(sendto,randomkey):
    #  主旨
    msg_title = 'Sign Up:Yulin NewTab sync services'
    #  寄件者，若參數有設置就不需再另外設置
    msg_sender = 'event@legendyang.me'
    #  收件者，格式為list，否則報錯
    msg_recipients = [sendto]
    #  郵件內容
    #  也可以使用html
    msg_html = render_template('mail.html',randomkey=randomkey)
    msg = Message(msg_title,
                  sender=msg_sender,
                  recipients=msg_recipients)
    msg.html = msg_html
    
    #  mail.send:寄出郵件
    
    mail.send(msg)
    return 'email sent successfully if the email is correct'

@app.route('/')
def test():
    return jsonify({'status':'ok'})

@app.route('/createacc', methods=['POST'])
def createacc():
    if request.method == 'POST':
        email = request.values['email']
        password = hash(request.values['password'])
        if password == False:
            return jsonify({'status':'error','msg':'where is your password????'})
        if email == False:
            return jsonify({'status':'error','msg':'where is your email????'})
        if '@' not in email:
            return jsonify({'status':'error','msg':'email is not valid'})
        if len(str(request.values['password'])) < 5:
            return jsonify({'status':'error','msg':'password is too short'})
        if userdb['user'].find_one({'email':email}) == None:
            randomkey = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(999))
            signupdb['signup'].insert_one({'email':email,'password':password,'randomkey':randomkey,'time':time.time()})
            result = sendmail(email,randomkey)
            return jsonify({'status':'success','msg':str(result)})
        else:
            return jsonify({'status':'erorr','msg':'account alweady exist'})
        
if __name__ == '__main__':
    app.run(port=80,host='0.0.0.0')