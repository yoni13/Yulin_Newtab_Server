import time,os
import random, string
from dotenv import load_dotenv
load_dotenv(override=True)
from flask import Flask, abort, render_template,request, redirect,make_response,jsonify
import pymongo
client = pymongo.MongoClient(os.getenv('MONGO_URL'))
userdb = client['userdb']
signupdb = client['signupdb']
forgetpassdb = client['forgetpass']
deleteaccdb = client['deleteacc']
from flask import Flask, render_template
app = Flask(__name__)
from init import sendmail,resetrequest,deleteacc
@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    return jsonify({'error': 'Oh,well.Some Erorr happend on the server side,Try again later'}), 500

@app.route('/')
def test():
    now = round(time.time())
    expires = now - 1800
    for i in signupdb['signup'].find({'time':{'$lt':expires}}):#sign up request expired
        signupdb['signup'].delete_many({'_id':i['_id']})
    for i in forgetpassdb['forgetpass'].find({'time':{'$lt':expires}}):#sign up request expired
        forgetpassdb['forgetpass'].delete_many({'_id':i['_id']})
    for i in deleteaccdb['deleteacc'].find({'time':{'$lt':expires}}):#sign up request expired
        deleteaccdb['deleteacc'].delete_many({'_id':i['_id']})
    return jsonify({'status':'ok'}),200

@app.route('/reset',methods=['GET','POST'])  # type: ignore
def reset():
    if forgetpassdb['forgetpass'].find_one({'randomkey':request.args.get('key')}) != None:
        for i in forgetpassdb['forgetpass'].find({'randomkey':request.args.get('key')}):
            if round (time.time()) - i['time'] < 1800:
                if request.method == 'GET':
                    return render_template('reset.html')
                elif request.method == 'POST':
                    if len(request.form['password']) < 5:
                        return '''<script>alert('Password too short')</script>''' + render_template('reset.html')
                    else:
                        userdb['user'].update_one({'email':i['email']},{'$set':{'password':hash(request.form['password'])}})
                        forgetpassdb['forgetpass'].delete_one({'email':i['email']})
                        return render_template('resetdone.html')
            else:
                forgetpassdb['forgetpass'].delete_one({'email':i['email']})
                return render_template('timeout.html')
    else:
        return abort(404)




@app.route('/vertify',methods=['GET'])  # type: ignore
def vertify():
    if signupdb['signup'].find_one({'randomkey':request.args.get('key')}) != None:
        for i in signupdb['signup'].find({'randomkey':request.args.get('key')}):
            if round (time.time()) - i['time'] < 1800:
                userid = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(50))
                userdb['user'].insert_one({'email':i['email'],'password':i['password'],'userid':userid,'acc_create_t':time.time(),'top':'','middle':'','bottom':'','topcolor':'','middlecolor':'','bottomcolor':'','searchprovider':''})
                signupdb['signup'].delete_one({'email':i['email']})
                return render_template('success.html')
            else:
                signupdb['signup'].delete_one({'email':i['email']})
                return render_template('timeout.html')
    else:
        return abort(404)

@app.route('/createacc',methods=['POST'])  # type: ignore
def createacc():
    if request.method == 'POST':
        email = request.values['email']
        password = hash(request.values['password'])
        if password == '':
            return jsonify({'status':'error','msg':'where is your password????'})
        if email == '':
            return jsonify({'status':'error','msg':'where is your email????'})
        if '@' not in email:
            return jsonify({'status':'error','msg':'email is not valid'})
        if len(str(request.values['password'])) < 5:
            return jsonify({'status':'error','msg':'password is too short'})
        if userdb['user'].find_one({'email':email}) == None:
            randomkey = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(999))
            signupdb['signup'].delete_one({'email':email})
            signupdb['signup'].insert_one({'email':email,'password':password,'randomkey':randomkey,'time':time.time()})
            result = sendmail(email,randomkey)
            return jsonify({'status':'success','msg':str(result)})
        else:
            return jsonify({'status':'erorr','msg':'account alweady exist'})

@app.route('/forgetpass',methods=['POST'])  # type: ignore
def forgetpass():
    email = request.values['email']
    if email == '':
        return jsonify({'status':'error','msg':'where is your email????'})
    if '@' not in email:
        return jsonify({'status':'error','msg':'email is not valid'})
    if userdb['user'].find_one({'email':email}) == None:
        return jsonify({'status':'error','msg':'account not found'})
    else:
        forgetpassdb['forgetpass'].delete_one({'email':email})
        randomkey = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(999))
        forgetpassdb['forgetpass'].insert_one({'email':email,'randomkey':randomkey,'time':time.time()})
        response = resetrequest(email,randomkey)
        return jsonify({'status':'success','msg':response})
    
@app.route('/deleteacc',methods=['POST'])  # type: ignore
def deletea():
    email = request.values['email']
    password = request.values['password']
    if email == '':
        return jsonify({'status':'error','msg':'where is your email????'})
    if password == '':
        return jsonify({'status':'error','msg':'where is your password????'})
    if '@' not in email:
        return jsonify({'status':'erorr','msg':'email is not vaid'})
    if userdb['user'].find_one({'email':email}) == None:
        return jsonify({'status':'error','msg':'account not found'})
    for i in userdb['user'].find({'email':email}):
        print(i['password'])
        print(password)
        print(hash(password))
        if i['password'] == hash(password):
            randomkey = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(999))
            deleteaccdb['deleteacc'].insert_one({'email':email,'randomkey':randomkey,'time':time.time()})
            response = deleteacc(email,randomkey)
            return jsonify({'status':'success','msg':response})
        else:
            return jsonify({'status':'error','msg':'password is wrong'})


@app.route('/delete',methods=['GET'])  # type: ignore
def deletesuccess():
    if deleteaccdb['deleteacc'].find_one({'randomkey':request.args.get('key')}) != None:
        for i in deleteaccdb['deleteacc'].find({'randomkey':request.args.get('key')}):
            if round(time.time()) - i['time'] < 1800:
                userdb['user'].delete_one({'email':i['email']})
                deleteaccdb['deleteacc'].delete_one({'email':i['email']})
                return render_template('deleterequest.html')
            else:
                deleteaccdb['deleteacc'].delete_one({'email':i['email']})
                return render_template('timeout.html')
    else:
        return abort(404)


if __name__ == '__main__':
    app.run(port=80,host='0.0.0.0')