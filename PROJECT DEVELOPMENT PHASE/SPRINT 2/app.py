import flask
import joblib
import MySQLdb.cursors
import re
from flask import request, render_template, Flask, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_cors import CORS

app = flask.Flask(__name__, static_url_path="")
CORS(app)

app.secret_key = 'helloworld'

app.config['MYSQ_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Shreya@123'
app.config['MYSQL_DB'] = 'flightuserdata'

mysql = MySQL(app)

@app.route('/', methods=["GET"])
def sendHome():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        name = request.form['name']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE name = % s AND password= % s', (name, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            msg = 'Logged in successfully!'
            if session['pending'] == True:
                return render_template('details.html')
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username/Please try again'
    return render_template('login.html', msg=msg)

    
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form:
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        print(name)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE name = % s', (name, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers !'
        elif not name or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (name, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route('/predict', methods=["POST"])
def predictDelay():
    crsdt = float(request.form['crsdt'])
    deptime = float(request.form['deptime'])
    depdelay = float(request.form['depdelay'])
    crsat = float(request.form['crsat'])
    at = float(request.form['at'])
    ad = float(request.form['ad'])
    depdel = float(request.form['depdel'])
    cancel = float(request.form['cancel'])
    divert = float(request.form['divert'])
    crset = float(request.form['crset'])
    aet = float(request.form['aet'])
    X = [[crsdt,deptime,depdelay,depdel,crsat,
    at,ad,cancel,divert,crset,aet]]
    model = joblib.load('flight.pkl')
    predicted = model.predict(X)[0]
    return render_template('predict.html', predict=predicted)

@app.route('/details', methods=["GET"])
def get_form():
    if 'loggedin' in session.keys():
        return render_template("details.html")
    session['pending'] = True
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)