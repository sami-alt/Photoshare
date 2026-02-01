from flask import Flask
from flask import render_template, redirect, flash, request, make_response, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import config
#import secrets

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

def require_login():
    if 'id' not in session:
        abort(403)

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
    if not user or check_password_hash(password, user[2]):
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
    hash = generate_password_hash(password1)
    db = sqlite3.connect('database.db')
    db.execute('insert into user (username, password) values (?,?)',[username, hash])
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
    require_login()
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
    db = sqlite3.connect('database.db')
    pic_info = db.execute('select name, description, date, user_id from picture where id = ?', [id]).fetchone()
    return render_template('picture.html',id=id, info=pic_info)

@app.route('/image/picture/<int:id>')
def show_picture(id):
    db = sqlite3.connect('database.db')
    image = db.execute('select image from picture where id = ?',[id]).fetchone()
    if not image:
        flash('Something went wrong')
        return redirect('/pictures')
    response = make_response(bytes(image[0]))
    response.headers.set('Content-Type', 'image/png')
    return response


@app.route('/pictures')
def pictures():
    db = sqlite3.connect('database.db')
    pictures = db.execute('select id, name, date from picture').fetchall()
    print('pictures',pictures)
    sendObj = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in pictures]
    
    return render_template('pictures.html', pictures=sendObj)

@app.route('/my_pictures')
def my_pictures():
    db = sqlite3.connect('database.db')
    pictures = db.execute('select id, name, description from picture where user_id = ?',[session['id']])
    my_pics = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in pictures]
    return render_template("pictures.html", pictures=my_pics)

@app.route('/remove/<int:id>', methods=['POST'])
def delete_picture(id):
    print('try to remove')
    db = sqlite3.connect('database.db')
    db.execute('delete from picture where id = ?',[id])
    db.commit()
    db.close()

    flash('Picture deleted','success')
    return redirect('/')

@app.route('/modify/<int:id>', methods=['GET'])
def modify_picture(id):
    info = None
    db = sqlite3.connect('database.db')
    result = db.execute('select name, description, date from picture where id = ?',[id]).fetchone()
    info = {'name':result[0], 'description':result[1], 'date':result[2]}
    print(info)
    return render_template('modify.html', info=info, id=id)

@app.route('/modify_picture/<int:id>', methods=['POST'])
def modify_picture_info(id):
    name = request.form['name']
    description = request.form['description']
    date = request.form['date']
    db = sqlite3.connect('database.db')
    db.execute('update picture set name = ?, description = ?, date = ? where id = ?',[name, description, date, id])
    db.commit()
    db.close()
    flash('Picture info modified')
    return redirect('/')


#searc function

@app.route('/search')
def search_form():
    return render_template('search.html')

@app.route('/search_with_parameter', methods=['GET'])
def paramater_search():
    found = None
    parameter = request.args.get('parameter')
    db = sqlite3.connect('database.db')

    pictures = db.execute('select id, name, date from picture where name like ? or description like ?', ["%"+parameter+"%", "%"+parameter+"%"] ).fetchall()
    
    found = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in pictures]

    print(found)

    return render_template('pictures.html', pictures=found)


#to-do

#search on name, date, description
#users own pictures
#verify login on adding removing and changing
