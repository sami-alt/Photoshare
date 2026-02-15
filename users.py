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
    users = db.query("select id, username, password from user", [],True)
    return users

#Admin access


def remove_user():
    return 

def null_password():
    return