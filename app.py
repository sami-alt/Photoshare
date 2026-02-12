'''Modules'''
from flask import Flask
from flask import render_template, redirect, flash, request, make_response, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
#import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    '''
    Docstring for index
    
    :return: Description
    :rtype: str
    '''
    logged_in = session.get('username')
    user = None
    if logged_in:
        user = db.query('select id, username from user where username = ?',[logged_in])

    return render_template('home.html', user=user)


#User auth functions

def require_login():
    '''
    Docstring for require_login
    
    :return: Description
    :rtype: str
    '''
    if 'id' not in session:
        abort(403)

@app.route('/login')
def login():
    '''
    Docstring for login
    
    :return: Description
    :rtype: str
    '''
    return render_template('login.html')


@app.route('/logout')
def logout():
    '''
    Docstring for logout
    
    :return: Description
    :rtype: str
    '''
    del session['id']
    del session['username']
    return redirect('/')

@app.route('/signin')
def signin_page():
    '''
    Docstring for signin_page
    
    :return: Description
    :rtype: str
    '''
    return render_template('signin.html')

@app.route('/add_user')
def add_user_page():
    '''
    Docstring for add_user_page
    
    :return: Description
    :rtype: str
    '''
    return render_template('signin.html')

@app.route('/login_user', methods=['POST'])
def login_user():
    '''
    Docstring for login_user
    
    :return: Description
    :rtype: str
    '''
    username = request.form['username']
    password = request.form['password']
    user = db.query('select id, username, password from user where username = ?',[username])
    if not user or not check_password_hash(user['password'], password):
        flash('Username or password does not match')
        return redirect('/login')
    flash(f'Welcome {username}')
    print(user[0])

    session['id'] = user['id']
    session['username'] = user['username']
    print('sessions',session['username'], session['id'])

    return redirect('/')


@app.route('/add_user_action', methods=['POST'])
def add_user():
    '''
    Docstring for add_user
    
    :return: Description
    :rtype: str
    '''
    username = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    if len(username) < 1 or len(password1) < 1:
        flash('Empty username or password')
        return redirect('/signin')
    if not password1 == password2:
        flash('Password do not match!')
        return redirect('/signin')
    password = generate_password_hash(password1)
    db.execute('insert into user (username, password) values (?,?)',[username, password])
    flash('New user created')
    return redirect('/')

#picture functions

@app.route("/add_picture")
def add_picture_page():
    '''
    Docstring for add_picture_page
    
    :return: Description
    :rtype: str
    '''
    return render_template('add_picture.html')

@app.route('/add_new_picture', methods=['POST'])
def add_picture_to_db():
    '''
    Docstring for add_picture_to_db
    
    :return: Description
    :rtype: str
    '''
    require_login()
    #add validation
    file = request.files['image']
    name = request.form['name']
    description = request.form['description']
    date = request.form['date']
    image = file.read()

    db.execute('''insert into picture (user_id, image, name, description, date)
                values (?,?,?,?,?)''',[session['id'], image, name, description, date])

    return redirect('/')


@app.route('/picture/<int:picture_id>')
def one_picture(picture_id):
    '''
    Docstring for one_picture
    
    :param id: Description
    :return: Description
    :rtype: str
    '''
    pic_info = db.query('''select name, description, date, user_id from picture
                         where id = ?''', [picture_id])
    return render_template('picture.html',id=picture_id, info=pic_info)

@app.route('/image/picture/<int:picture_id>')
def show_picture(picture_id):
    '''
    Docstring for show_picture
    
    :param id: Description
    :return: Description
    :rtype: str
    '''
    image = db.query('select image from picture where id = ?',[picture_id])
    if not image:
        flash('Something went wrong')
        return redirect('/pictures')
    response = make_response(bytes(image[0]))
    response.headers.set('Content-Type', 'image/jpg, image/png')
    return response


@app.route('/pictures')
def get_pictures():
    '''
    Docstring for pictures
    
    :return: Description
    :rtype: str
    '''

    pictures = db.query('select id, name, date from picture',[], False)
    print('pictures',pictures)
    send_obj = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in pictures]

    return render_template('pictures.html', pictures=send_obj)

@app.route('/my_pictures')
def my_pictures():
    '''
    Docstring for my_pictures
    
    :return: Description
    :rtype: str
    '''

    pictures = db.query('select id, name, description from picture where user_id = ?',
                        [session['id']], False)
    my_pics = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in pictures]
    return render_template("pictures.html", pictures=my_pics)

@app.route('/remove/<int:picture_id>', methods=['POST'])
def delete_picture(picture_id):
    '''
    Docstring for delete_picture
    
    :param id: Description
    :return: Description
    :rtype: str
    '''
    print('try to remove')
    db.execute('delete from picture where id = ?',[picture_id])
    flash('Picture deleted','success')
    return redirect('/')

@app.route('/modify/<int:picture_id>', methods=['GET'])
def modify_picture(picture_id):
    '''
    Docstring for modify_picture
    
    :param id: Description
    :return: Description
    :rtype: str
    '''
    info = None

    result = db.query('select name, description, date from picture where id = ?',[picture_id])
    info = {'name':result[0], 'description':result[1], 'date':result[2]}
    print(info)
    return render_template('modify.html', info=info, id=picture_id)

@app.route('/modify_picture/<int:picture_id>', methods=['POST'])
def modify_picture_info(picture_id):
    '''
    Docstring for modify_picture_info
    
    :param id: Description
    :return: Description
    :rtype: str
    '''
    name = request.form['name']
    description = request.form['description']
    date = request.form['date']
    db.execute('update picture set name = ?, description = ?, date = ? where id = ?'
               ,[name, description, date, picture_id])
    flash('Picture info modified')
    return redirect('/')


#searc function

@app.route('/search')
def search_form():
    '''
    Docstring for search_form
    
    :return: Description
    :rtype: str
    '''
    return render_template('search.html')

@app.route('/search_with_parameter', methods=['GET'])
def paramater_search():
    '''
    Docstring for paramater_search
    
    :return: Description
    :rtype: str
    '''
    found = None
    parameter = request.args.get('parameter')

    pictures = db.query('''select id, name, date from picture
                          where name like ? or description like ?''',
                          ["%"+parameter+"%", "%"+parameter+"%"], False)
    found = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in pictures]

    print(found)

    return render_template('pictures.html', pictures=found)

#Comment functionalities

#Admin functionalities

#to-do

#search on date
