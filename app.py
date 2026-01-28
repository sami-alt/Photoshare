from flask import Flask
from flask import render_template, redirect
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('home.html')


#User auth functions

@app.route('/login')
def login():
    return render_template('login.html') 


@app.route('/logout')
def logout():
    return

@app.route('/add_user')
def add_user_page():
    pass

#picure functions

@app.route("/pictures")
def show_pictures():
    return render_template('pictures.html')

@app.route("/add_picture")
def add_picture_page():
    return render_template('add_picture.html')

@app.route('/add_new_picture', methods=["POST"])
def add_new_picture():
    return redirect('/')


#database and sql functions,

@app.route('/add_user_action')
def add_user():
    db = sqlite3.connect('database.db')
    db.execute('insert into user (name, password) values (??)',['käyttäjä', 'salasana'])
    db.commit()
    db.close()
    return

def add_picture_to_db():
    db = sqlite3.connect('database.db')
    db.execute('insert into ')
    return 