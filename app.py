from flask import Flask
from flask import render_template, redirect, flash, request, make_response, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import users
import pictures
import secrets

import sqlite3

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    user_id = session.get('id')
    if user_id:
        user = users.get_user(user_id, None)
    else:
        user = None

    comments_from_db = None
    pictures_from_db = None
    latest_pictures = []
    latest_comments = []

    pictures_from_db = pictures.get_pictures_by_quantity(5)
    if pictures_from_db:
        latest_pictures = [dict(picture) for picture in pictures_from_db]
    comments_from_db = pictures.get_comments_by_quantity(5)
    if comments_from_db:
        latest_comments = [dict(comment) for comment in comments_from_db]

    return render_template('home.html', user=user, comments=latest_comments, pictures=latest_pictures)


#User auth functions

def require_login():
    if 'id' not in session:
        abort(403)


def check_csrf():
    if 'csrf_token' not in session:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    require_login()
    del session['id']
    del session['username']
    del session['csrf_token']

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
    user = users.get_user(None, username)
    if not user or not check_password_hash(user['password'], password):
        flash('Username or password does not match', 'failure')
        return redirect('/login')
    flash(f'Welcome {username}', 'success')


    session['id'] = user['id']
    session['username'] = user['username']
    session['csrf_token'] = secrets.token_hex(16)
    


    return redirect('/user_page')


@app.route('/user_page')
def user_page():
    require_login()
    my_comments = None
    my_pictures = None
    image = None
    mini_stats = None


    pictures_from_db = pictures.get_pictures_by_user_id(session['id'])
    if pictures_from_db:
        my_pictures = [dict(picture) for picture in pictures_from_db]
    comments_from_db = pictures.get_comment_by_user_id(session['id'])
    if comments_from_db:
        my_comments = [dict(comment) for comment in comments_from_db]

    mini_stats = {'pictures': len(my_pictures), 'comments':len(my_comments)}

    exists = users.get_user_picture(session['id'])

    if exists:
        image = exists
    
    return render_template('user_page.html', pictures=my_pictures, comments=my_comments, image=image, mini_stats=mini_stats)

@app.route('/add_user_action', methods=['POST'])
def add_user():
    username = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    if len(username) < 1 or len(password1) < 1:
        flash('Empty username or password')
        return redirect('/signin')
    if not password1 == password2:
        flash('Password do not match!', 'failure')
        return redirect('/signin')
    password = generate_password_hash(password1)
    try:
        users.create_user(username, password)
    except sqlite3.IntegrityError:
        flash('Username already taken','failure')
        return render_template('signin.html')
    flash('New user created', 'success')
    return redirect('/')


@app.route('/add_or_update_userpage_pic/<int:user_id>', methods=['POST'])
def add_or_update_user_picture(user_id):
    require_login()
    check_csrf()
    
    ALLOWED_MIMES = {'image/jpeg', 'image/png'}

    
    file = request.files['image']

    if file.mimetype not in ALLOWED_MIMES:
        flash('Only JPEG or PNG images are allowed', 'failure')
        return redirect('/user_page')
    
    user_picture = file.read()

    users.add_or_update_userpage_picture(user_id, user_picture)

    return redirect('/user_page')

@app.route('/user_picture/<int:user_id>')
def get_user_image(user_id):
    image = users.get_user_picture(user_id)
    if not image:
        flash('Something went wrong')
        return redirect('/user_page')
    response = make_response(bytes(image['user_picture']))
    response.headers.set('Content-Type', 'image/jpg, image/png')
    return response
    
@app.route('/change_user_picture')
def change_user_picture_page():

    return render_template('change_user_picture.html')


#picture functions

@app.route("/add_picture")
def add_picture_page():
    return render_template('add_picture.html')

@app.route('/add_new_picture', methods=['POST'])
def add_picture_to_db():
    require_login()
    check_csrf()

    ALLOWED_MIMES = {'image/jpeg', 'image/png'}

    file = request.files['image']
    if file.mimetype not in ALLOWED_MIMES:
        flash('Only JPEG or PNG images are allowed', 'failure')
        return render_template('add_picture.html')
    name = request.form['name']
    description = request.form['description']
    date = request.form['date']
    image = file.read()
    categories = request.form.getlist('category')

    if not image:
        flash('Picture not provided', 'failure')
        return render_template('add_picture.html')

    if len(name) < 1 or len(name) > 255:
        flash('Name lenght must be between 1 and 255 characters')
        return render_template('add_picture.html')


    if len(description) < 1 or len(description) > 255:
        flash('Description lenght must be between 1 and 255 characters')
        return render_template('add_picture.html')
      

    if date:
        if not validate_date(date):
            flash('Date is not valid, follow the date format give', 'failure')
            return render_template('add_picture.html')
    

    pictures.add_picture(session['id'], image, name, description, date)
    picture_id = db.last_insert_id()
  
    for category in categories:
        pictures.add_to_category(category, picture_id)

    

    flash('Picture added', 'success')
    return redirect('/')

def validate_date(date):
    if not isinstance(date, str):
        return False
    
    if len(date) != 10:
        return False

    if date[2] != '.' or date[5] != '.':
        return False

    for i in range(10):
        if i in (2, 5):
            continue
        if not date[i].isdigit():
            return False

    day = int(date[0:2])
    month = int(date[3:5])
    year = int(date[6:10])

    if month < 1 or month > 12:
        return False

    if day < 1 or day > 31:
        return False

    if year < 0 or year > 9999:
        return False

    return True


@app.route('/picture/<int:picture_id>')
def one_picture(picture_id):
    pic_info = pictures.get_picture(picture_id)
    results = pictures.get_comments_by_id(picture_id)
    comments = None
   
    if results:
        comments = [{'comment':result['comment'], 'owner':users.get_user(result['user_id'],None)['username']} for result in results]

    return render_template('picture.html',id=picture_id, info=dict(pic_info), comments=comments)

@app.route('/image/picture/<int:picture_id>')
def show_picture(picture_id):
    image = pictures.get_picture(picture_id)
    if not image:
        flash('Something went wrong')
        return redirect('/pictures')
    response = make_response(bytes(image[4]))
    response.headers.set('Content-Type', 'image/jpg, image/png')
    return response


@app.route('/pictures')
def get_pictures():
    all = pictures.get_all()
    send_obj = None
    if all:
        send_obj = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in all]

    return render_template('pictures.html', pictures=send_obj)

@app.route('/my_pictures')
def my_pictures():
    require_login()
    pictures_by_user = pictures.get_pictures_by_user_id(session['id'])
    my_pics = None
    if pictures_by_user:
        my_pics = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in pictures_by_user]
    return render_template("pictures.html", pictures=my_pics)

@app.route('/remove/<int:picture_id>', methods=['POST'])
def delete_picture(picture_id):
    require_login()
    check_csrf()
    user_id = pictures.get_picture(picture_id)
    if user_id['user_id'] == session['id']:
        pictures.delete_picture(picture_id)
        flash('Picture deleted','success')
    return redirect('/')

@app.route('/modify/<int:picture_id>', methods=['GET'])
def modify_picture(picture_id):
    require_login()
    info = None

    result = pictures.get_picture(picture_id)

    if result['user_id'] != session['id']:
        flash('You are not owner of this post')
        return redirect('/')

    info = {'name':result[0], 'description':result[1], 'date':result[2]}



    return render_template('modify.html', info=info, id=picture_id)

@app.route('/modify_picture/<int:picture_id>', methods=['POST'])
def modify_picture_info(picture_id):
    require_login()
    check_csrf()

    name = request.form['name']
    description = request.form['description']
    date = request.form['date']
    pictures.modify_picture(name, description, date, picture_id)
    flash('Picture info modified', 'success')
    return redirect('/')




@app.route('/search')
def search_form():
    return render_template('search.html')

@app.route('/search_with_parameter', methods=['GET'])
def paramater_search():
    found = None
    parameter = request.args.get('parameter')

    results = pictures.search_pictures(parameter)
    if results:
        found = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in results]

    return render_template('pictures.html', pictures=found)

@app.route('/search_with_categories')
def category_search():
    found = []
    categories = request.args.getlist('category')

    for categody in categories:
        temp = []
        result = pictures.pictures_by_category(categody)
        if result:
            temp = [dict(picture) for picture in  result]
        found.extend(temp)

    return render_template('pictures.html', pictures=found)

#Comment functionalities

@app.route('/add_comment_to/<int:picture_id>', methods=['POST'])
def add_comment_to_picture(picture_id):
    require_login()
    check_csrf()
    comment = request.form['comment']
    pictures.add_comment_by_id(picture_id, session['id'],comment)
    return redirect('/picture/' + str(picture_id))


@app.route('/my_comments')
def my_comments():
    require_login()
    comments = None
    comments = pictures.get_comment_by_user_id(session['id'])
    return render_template('my_comments.html', comments=comments)

# app.py
@app.route('/statistics')
def show_statistics():

    total_users = pictures.count_users()
    total_pictures = pictures.count_pictures()
    total_comments = pictures.count_comments()

    
    popular_category = pictures.most_popular_category()
    busiest_date = pictures.date_with_most_pictures()
    top_uploader = pictures.user_with_most_pictures()
    top_commenter = pictures.user_who_commented_most()
    most_commented_owner = pictures.user_who_got_most_comments()
    most_commented_picture = pictures.picture_with_most_comments()

    statistics = {
        'users': total_users,
        'pictures': total_pictures,
        'comments': total_comments,
        'popular_category': popular_category,
        'busiest_date': busiest_date,
        'top_uploader': top_uploader,
        'top_commenter': top_commenter,
        'most_commented_owner': most_commented_owner,
        'most_commented_picture': most_commented_picture
    }
    return render_template('statistics.html', statistics=statistics)

