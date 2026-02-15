from flask import Flask
from flask import render_template, redirect, flash, request, make_response, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import users
import pictures
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    user_id = session.get('id')
    if user_id:
        user = users.get_user(user_id, None)
    else:
        user = None

    return render_template('home.html', user=user)


#User auth functions

def require_login():
    if 'id' not in session:
        print('login abort')
        abort(403)


def check_csrf():
    if 'csrf_token' not in session:
        print('csrf 1')
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        print('session token',session['csrf_token'])
        print('from form',request.form['csrf_token'])
        print('csrf 2')
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
    user = users.get_user(None, username)
    if not user or not check_password_hash(user['password'], password):
        flash('Username or password does not match')
        return redirect('/login')
    flash(f'Welcome {username}')
    print(user[0])

    session['id'] = user['id']
    session['username'] = user['username']
    session['csrf_token'] = secrets.token_hex(16)
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
    if not password1 == password2:
        flash('Password do not match!')
        return redirect('/signin')
    password = generate_password_hash(password1)
    users.create_user(username, password)
    flash('New user created')
    return redirect('/')

#picture functions

@app.route("/add_picture")
def add_picture_page():
    return render_template('add_picture.html')

@app.route('/add_new_picture', methods=['POST'])
def add_picture_to_db():
    require_login()
    check_csrf()
    #add validation
    file = request.files['image']
    name = request.form['name']
    description = request.form['description']
    date = request.form['date']
    image = file.read()
    categories = request.form.getlist('category')

    pictures.add_picture(session['id'], image, name, description, date)
    picture_id = db.last_insert_id()
    print('picture_id',picture_id)
    for category in categories:
        print('prii', category)
        pictures.add_to_category(category, picture_id)

    return redirect('/')


@app.route('/picture/<int:picture_id>')
def one_picture(picture_id):
    pic_info = pictures.get_picture(picture_id)
    results = pictures.get_comments_by_id(picture_id)
    comments = None
    print(len(results) if results else 'Empty')
    if results:
        comments = [{'comment':result['comment'], 'owner':users.get_user(result['user_id'],None)['username']} for result in results]
        for comment in comments:
            print(comment)
    
    return render_template('picture.html',id=picture_id, info=pic_info, comments=comments)

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
    print('pictures',pictures)
    send_obj = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in all]

    return render_template('pictures.html', pictures=send_obj)

@app.route('/my_pictures')
def my_pictures():
    pictures_by_user = pictures.get_pictures_by_user_id(session['id'])
    my_pics = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in pictures_by_user]
    return render_template("pictures.html", pictures=my_pics)

@app.route('/remove/<int:picture_id>', methods=['POST'])
def delete_picture(picture_id):
    pictures.delete_picture(picture_id)
    flash('Picture deleted','success')
    return redirect('/')

@app.route('/modify/<int:picture_id>', methods=['GET'])
def modify_picture(picture_id):
    info = None

    result = pictures.get_picture(picture_id)
    info = {'name':result[0], 'description':result[1], 'date':result[2]}
    print(info)
    return render_template('modify.html', info=info, id=picture_id)

@app.route('/modify_picture/<int:picture_id>', methods=['POST'])
def modify_picture_info(picture_id):
    require_login()
    check_csrf()
    name = request.form['name']
    description = request.form['description']
    date = request.form['date']
    pictures.modify_picture(name, description, date, picture_id)
    flash('Picture info modified')
    return redirect('/')




@app.route('/search')
def search_form():
    return render_template('search.html')

@app.route('/search_with_parameter', methods=['GET'])
def paramater_search():
    found = None
    parameter = request.args.get('parameter')

    results = pictures.search_pictures(parameter)
    found = [{'id':picture[0], 'name':picture[1], 'date':picture[2]} for picture in results]

    return render_template('pictures.html', pictures=found)

@app.route('/search_with_categories')
def category_search():
    found = []
    categories = request.args.getlist('category')

    for categody in categories:
        temp = []
        result = pictures.pictures_by_category(categody)
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
    comments = None
    comments = pictures.get_comment_by_user_id(session['id'])
    return render_template('my_comments.html', comments=comments)

@app.route('/statistics')
def show_statistics():
    statistics = None

    user_data = users.get_users()
    picture_data = pictures.get_all()
    comment_data = pictures.get_comments()

    statistics = {'users':len(user_data) if user_data else 0, 'pictures':len(picture_data)if picture_data else 0, 'comments':len(comment_data)if comment_data else 0}
    return render_template('/statistics.html', statistics=statistics)

#Admin functionalities

#to-do

#search on date
