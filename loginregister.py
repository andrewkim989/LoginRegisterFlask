from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z]+$')

mysql = connectToMySQL('registerdb')

app = Flask(__name__)
app.secret_key = "Secretloginregister"

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    if not session:
        session['whereto'] = 'here'
    return render_template("lrindex.html")

@app.route('/rprocess', methods = ['POST'])
def register():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    password_con = request.form['password_con']
    
    if len(firstname) < 2:
        flash(u"The first name should be two or more characters long.", 'firstname')
    elif not name_regex.match(firstname):
        flash(u"The first name should not contain any numbers"
        " or any special characters.", 'firstname')
    
    if len(lastname) < 2:
        flash(u"The last name should be two or more characters long.", 'lastname')
    elif not name_regex.match(lastname):
        flash(u"The last name should not contain any numbers"
        " or any special characters.", 'lastname')
    
    query = "SELECT EXISTS (SELECT * FROM register WHERE email = %(email)s) AS email"
    data = {
        'email': email
    }
    emailisthere = mysql.query_db(query, data)
        
    if len(email) < 1:
        flash(u"Email cannot be blank.", 'email')
    elif not EMAIL_REGEX.match(email):
        flash(u"Invalid Email Address.", 'email')
    elif emailisthere[0]['email'] != 0:
        flash("The email already exists in the system. Please type another one.")
    
    if len(password) < 1:
        flash(u"Please enter your password.", 'password')
    elif len(password) < 8:
        flash(u"Password should be more than 8 characters long.", 'password')
    elif re.search('[0-9]', password) is None:
        flash(u"Make sure that your password has a number in it", 'password')
    elif re.search('[A-Z]', password) is None: 
        flash(u"Make sure that your password has a capital letter in it", 'password')

    if len(password_con) < 1:
        flash(u"Please verify your password.", 'password_con')
    elif password != password_con:
        flash(u"Password does not match.", 'password_con')
    
    if '_flashes' in session.keys():
        return redirect("/")
    else:
        query = "INSERT INTO register (email, password) VALUES (%(email)s, %(password)s);"
        data = {
            'email': email,
            'password': bcrypt.generate_password_hash(password)
        }
        mysql.query_db(query, data)
        session['email'] = email

        session['whereto'] = 'register'
        return redirect("/success")

@app.route('/lprocess', methods = ['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    query1 = "SELECT * FROM register;"
    entries = mysql.query_db(query1)

    emailexists = False

    for entry in entries:
        if entry['email'] == email:
            emailexists = True
            if bcrypt.check_password_hash(bcrypt.generate_password_hash(password), password):
                session['whereto'] = 'login'
                return redirect("/success")
            else:
                flash(u"Incorrect password. Please try again.", 'password')
            break
    if emailexists is False:
        flash("The email does not exist in the system. Please type another one.", 'email')
    
    if '_flashes' in session.keys():
        return redirect("/")
    else:
        session['whereto'] = 'login'
        return redirect("/success")

@app.route('/success')
def success():
    return render_template('lrsuccess.html')

@app.route('/delete_all')
def delete_all():
    query = "TRUNCATE TABLE register;"
    mysql.query_db(query)
    return redirect("/")

if __name__=="__main__":
    app.run(debug = True) 