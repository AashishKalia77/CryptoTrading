from flask import Flask,render_template,request,json,redirect
from flaskext.mysql import MySQL
import trading as td
app = Flask(__name__)
mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bucketlist'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()
app.debug = True
@app.route('/choosetrade',methods=['GET','POST'])
def showtrade():
    if request.method=='POST':
        tradecurr1=request.form['tradecurr1']
        tradecurr2=request.form['tradecurr2']
        tradecurr3=request.form['tradecurr3']
        currencies=[tradecurr1,tradecurr2,tradecurr3]
        for i in currencies:
            td.CrptoClass.currencies.append(i)
        # td.Mosbot._username=user_username
        print("MOsUserops: ", td.CrptoClass._username)
        z=td.CrptoClass()
        z.set_interval(z.returnTicker, 7)
        return render_template('hello.html',tradecurr1=tradecurr1,tradecurr2=tradecurr2,tradecurr3=tradecurr3)
    return render_template('choosetrade.html')
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')
@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')
@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    # try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
    # query ='''SELECT user_password FROM sigin WHERE user_name='%s';''' % (_username)
        td.CrptoClass._username=_username
        print("MOsUser: ", td.CrptoClass._username)
        # connect to mysql
        cursor.callproc('sp_validateLogin', (_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if str(data[0][2])==_password:
                # session['user'] = data[0][0]
                # return redirect('/userHome')
                return redirect('/choosetrade')
            else:
                return render_template('error.html')
        else:
            return render_template('error.html')


    # except Exception as e:
    #     return render_template('error.html')
    # finally:
    #     cursor.close()
    #     conn.close()
@app.route('/signUp', methods=['POST'])
def signUp():
    # read the posted values from the UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    # if _name and _email and _password:
    #     return json.dumps({'html': '<span>All fields good !!</span>'})
    # else:
    #     return json.dumps({'html': '<span>Enter the required fields</span>'})
    cursor.callproc('sp_createUser', (_name, _email,_password))
    data = cursor.fetchall()

    if len(data) is 0:
        conn.commit()
        return json.dumps({'message': 'User created successfully !'})
    else:
        return json.dumps({'error': str(data[0])})


if __name__ == '__main__':
    app.run(port=40)