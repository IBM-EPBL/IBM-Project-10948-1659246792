import flask
import joblib
import requests
import MySQLdb.cursors
import re
import pandas as pd
from flask import request, render_template, Flask, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_cors import CORS
import datetime

API_KEY = "tCzEer0P5KjeQ_Tu6f8W9HK24TQ1Ds_Wi311f1_mS5UI"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

# setting a new instance of Flask
app = flask.Flask(__name__, static_url_path="")
CORS(app)

# creating secret key for the app
app.secret_key = 'helloworld'

with open('secret.txt', 'r') as f:
    line = f.readline().split(',')
    user = line[0]
    password = line[1]

# setting config values
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = 'flights'

# creating instance of MySql
mysql = MySQL(app)

# home page route
@app.route('/', methods=["GET"])
def sendHome():
    return render_template('index.html', active_page="home", title="Welcome to FDP System!")

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # to display on the website
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        name = request.form['name']
        password = request.form['password']

        # connect to MYSQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE name = % s AND password= % s', (name, password))
        account = cursor.fetchone()

        # if account exists
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            msg = 'Logged in successfully!'
            # if predict was selected before
            if 'pending' in session.keys():
                redirect(url_for('predict'))
                return render_template('details.html', msg=session['name'], active_page='details', title="Flight Details")
            redirect(url_for('sendHome'))
            return render_template('index.html', msg=msg, active_page='home', title="Welcome to FDP System!")
        else:
            msg = 'Incorrect username/password. Please try again'
    redirect(url_for('login'))
    return render_template('login.html', msg=msg, active_page='login', title="Login")

# logout   
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    session.pop('pending', None)
    msg = 'Successfully Logged out!'
    redirect(url_for('sendHome'))
    return render_template('index.html', msg=msg, active_page='home', title="Welcome to FDP System!")

# register
@app.route('/register', methods = ['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form:

        # get details from form 
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']

        # mysql connection and retreival
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE name = % s', (name, ))
        account = cursor.fetchone()

        # check statements
        if account:
            msg = 'Account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers !'
        elif not name or not password or not email:
            msg = 'Please fill out the form !'
        else:
            # insert into table
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (name, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            redirect(url_for('login'))
            return render_template('login.html', msg = msg, active_page='login', title="Log In")

    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    redirect(url_for('register'))
    return render_template('register.html', msg = msg, active_page='register', title="Signup")

# predicting the labels
@app.route('/predict', methods=["POST"])
def predict():

    format_date = "%Y-%m-%d"
    dep_date = datetime.datetime.strptime(request.form['dep_date'], format_date)
    month = int(dep_date.date().month)
    day_of_month = int(dep_date.date().day)

    format_time = "%H:%M"
    crs_dep_time = datetime.datetime.strptime(request.form['crs_dep_time'], format_time)
    hour = crs_dep_time.time().hour
    minute = crs_dep_time.time().minute
    crs_departure_time = hour*100+minute

    format_time = "%H:%M"
    crs_arr_time = datetime.datetime.strptime(request.form['crs_arr_time'], format_time)
    hour = crs_arr_time.time().hour
    minute = crs_arr_time.time().minute
    crs_arrival_time = hour*100+minute

    format_time = "%H:%M"
    dep_time = datetime.datetime.strptime(request.form['dep_time'], format_time)
    hour = dep_time.time().hour
    minute = dep_time.time().minute
    departure_time = hour*100+minute

    departure_delay = crs_departure_time - departure_time
    if(departure_delay>15):
        dep_del15 = 1
    else:
        dep_del15 = 0
    
    cancelled = request.form['cancelled']
    if(cancelled == 'Yes'):
        cancelled = 1
    else:
        cancelled = 0
    
    diverted = request.form['diverted']
    if(diverted == 'Yes'):
        diverted = 1
    else:
        diverted = 0

    X = [[month, day_of_month, crs_departure_time, departure_time, departure_delay, 
         dep_del15, crs_arrival_time, cancelled, diverted]]
    payload_scoring = {"input_data": [{"field": [['month', 'day_of_month', 'crs_departure_time', 'departure_time', 'departure_delay', 
         'dep_del15', 'crs_arrival_time', 'cancelled', 'diverted']], "values": X}]}

    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/0b4a580c-18db-4a71-92a9-0d006bd0c06d/predictions?version=2022-11-13', json=payload_scoring,
    headers={'Authorization': 'Bearer ' + mltoken})
    print(response_scoring)
    predictions = response_scoring.json()
    predicted = predictions['predictions'][0]['values'][0][0]

    # model = joblib.load('flight.pkl')
    # predicted = model.predict(X)[0]
    redirect(url_for('details'))
    return render_template("details.html", active_page='details', title="Details", predict=predicted, msg=session['name'])

@app.route('/details', methods=["GET"])
def details():
    msg = 'Please log in or signup to continue!'
    if 'loggedin' in session.keys():
        redirect(url_for('details'))
        return render_template("details.html", active_page='details', title="Details", msg=session['name'])
    session['pending'] = True
    redirect(url_for('login'))
    return render_template('login.html', msg=msg, active_page='login', title="Login")

if __name__ == '__main__':
    app.run(debug=True)