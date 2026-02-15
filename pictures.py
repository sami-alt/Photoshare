import db

#Common user features

def add_picture(user_id, image, name, description, date):
    db.execute('''insert into picture (user_id, image, name, description, date)
                values (?,?,?,?,?)''',[user_id, image, name, description, date])

def get_picture(picture_id):
    picture = db.query('''select name, description, date, user_id, image from picture
                         where id = ?''', [picture_id])
    return picture

def pictures_by_category(category_id):
    pictures = db.query('''select p.id, p.user_id, p.image, p.name, p.description, date from picture p 
                             left join picture_in_category pic on p.id = pic.picture_id join categories c on c.id = pic.category_id
                             where c.id = ?''',[category_id], False)
    return pictures

def get_all():
    pictures = db.query('select id, name, date from picture',[], False)
    return pictures

def get_pictures_by_user_id(user_id):
    pictures =  db.query('select id, name, description from picture where user_id = ?',
                        [user_id], False)
    return pictures

def delete_picture(picture_id):
    db.execute('delete from picture where id = ?',[picture_id])


def modify_picture(name, description, date, picture_id):
        db.execute('update picture set name = ?, description = ?, date = ? where id = ?'
               ,[name, description, date, picture_id])

def search_pictures(parameter):
    found = db.query('''select id, name, date from picture
                          where name like ? or description like ?''',
                          ["%"+parameter+"%", "%"+parameter+"%"], False)
    return found

def add_comment_by_id(picture_id, user_id, comment):
     db.execute('insert into comment (comment, user_id, picture_id) values  (?,?,?) ',[comment, user_id, picture_id])

def get_comments():
    comments = db.query('select comment, user_id from comment',[],False)
    return comments

def get_comments_by_id(picture_id):
    comments = db.query('select comment,user_id from comment where picture_id = ?', [picture_id], False)
    return comments

def get_comment_by_user_id(user_id):
    comments = db.query('select comment, picture_id from comment where user_id = ?',[user_id], False)
    return comments

def add_to_category(category_id,picture_id):
     db.execute('insert into picture_in_category (category_id, picture_id) values (?,?)',[category_id, picture_id])

#Admin features