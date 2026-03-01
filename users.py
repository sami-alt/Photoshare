import db


#Common user access
def get_user(user_id, username):
    if not username:
        user = db.query('select id, username, password from user where id = ?',[user_id])
    else:
        user = db.query('select id, username, password from user where username = ?',[username])
    return user

def create_user(username, password):
    db.execute('insert into user (username, password) values (?,?)',[username, password])
    return None

def get_users():
    users = db.query("select id, username, password from user", [], False)
    return users

def add_or_update_userpage_picture(user_id, user_picture):
    picture_exists = db.query('select id from user_picture where user_id = ?', [user_id])

    if picture_exists:
        db.execute('update user_picture set user_picture = ? where user_id = ?', [user_picture, user_id])
    else:
        db.execute('insert into user_picture (user_picture, user_id) values (?,?)', [user_picture, user_id])
    return None

def get_user_picture(user_id):
    user_picture = db.query('select user_picture from user_picture where user_id = ?', [user_id])
    return user_picture

