from flask import Flask
from flask import render_template, redirect, flash, request, make_response, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import config
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    user = session.get('username')
    if not user:
        print('is not')
    return render_template('home.html', user=user)


#User auth functions

@app.route('/login')
def login():
    return render_template('login.html') 


@app.route('/logout')
def logout():
    del session['id']
    del session['username']
    return redirect('/')

@app.route('/signin')
def signin_page():
    return render_template('signin.html')

@app.route('/add_user')
def add_user_page():
    return render_template('signin.html')


#database and sql functions,

@app.route('/login_user', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']
    db = sqlite3.connect('database.db')
    user = db.execute('select id, username, password from user where username = ?',[username]).fetchone()
    if not user or password != user[2]:
        flash('Username or password does not match')
        return redirect('/login')
    flash(f'Welcome {username}')
    print(user[0])
    
    session['id'] = user[0]
    session['username'] = user[1]
    print('sessions',session['username'], session['id'])
    
    return redirect('/') 


@app.route('/add_user_action', methods=['POST'])
def add_user():
    username = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    if len(username) < 1 or len(password1) < 1:
        flash('Empty username or password')
        return redirect('/signin')
    if not (password1 == password2):
        flash('Password do not match!')
        return redirect('/signin')
    db = sqlite3.connect('database.db')
    db.execute('insert into user (username, password) values (?,?)',[username, password1])
    db.commit()
    db.close()
    flash('User added sucsesfully')
    return redirect('/')

