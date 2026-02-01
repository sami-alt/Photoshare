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
    loggedIn = session.get('username')
    user = None
    if loggedIn:
        db = sqlite3.connect('database.db')
        user = db.execute('select id, username from user where username = ?',[loggedIn]).fetchone()


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

#picture functions

@app.route("/add_picture")
def add_picture_page():
    return render_template('add_picture.html')

@app.route('/add_new_picture', methods=['POST'])
def add_picture_to_db():
    #add validation
    file = request.files['image']
    name = request.form['name']
    description = request.form['description']
    date = request.form['date']
    image = file.read()
    #
    db = sqlite3.connect('database.db')
    db.execute('insert into picture (user_id, image, name, description, date) values (?,?,?,?,?)',[session['id'], image, name, description, date])
    db.commit()
    db.close()
    return redirect('/')


@app.route('/picture/<int:id>')
def one_picture(id):
    print('hui')
    return render_template('picture.html',picture=id)

@app.route('/image/picture/<int:id>')
def show_picture(id):
    db = sqlite3.connect('database.db')
    image = db.execute('select image from picture where id = ?',[id]).fetchone()
    if not image:
        print('wah')
        flash('Something went wrong')
        return redirect('/pictures')
    print('hai', image)
    response = make_response(bytes(image[0]))
    response.headers.set('Content-Type', 'image/png')
    return response


@app.route('/pictures')
def pictures():
    db = sqlite3.connect('database.db')
    pictures = db.execute('select id from picture').fetchall()
    sendObj = [i for i in range(1,len(pictures) + 1)]
    print(sendObj)
    return render_template('pictures.html', pictures=sendObj)

