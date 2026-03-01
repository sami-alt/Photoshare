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

def get_pictures_by_quantity(num_of_pictures):
    pictures = db.query('select id, name from picture limit ?',[num_of_pictures], False)
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
     db.execute('insert into comment (comment, user_id, picture_id) values  (?,?,?) '
                ,[comment, user_id, picture_id])

def get_comments():
    comments = db.query('select comment, user_id from comment'
                        ,[],False)
    return comments

def get_comments_by_id(picture_id):
    comments = db.query('select comment,user_id from comment where picture_id = ?',
                        [picture_id], False)
    return comments

def get_comment_by_user_id(user_id):
    comments = db.query('select comment, picture_id from comment where user_id = ?',
                        [user_id], False)
    return comments

def get_comments_by_quantity(num_of_comments):
    comments = db.query('select comment, picture_id from comment limit ?',
                        [num_of_comments], False)
    return comments

def add_to_category(category_id,picture_id):
     db.execute('insert into picture_in_category (category_id, picture_id) values (?,?)',
                [category_id, picture_id])


def count_pictures():
    res = db.query('select count(*) as cnt from picture', [], True)
    return res['cnt'] if res else 0

def count_comments():
    res = db.query('select count(*) as cnt from comment', [], True)
    return res['cnt'] if res else 0

def count_users():
    res = db.query('select count(*) as cnt from user', [], True)
    return res['cnt'] if res else 0

def most_popular_category():

    sql = '''
        select c.id, c.category_name, count(pic.id) as pic_count
        from categories c
        left join picture_in_category pic on pic.category_id = c.id
        group by c.id, c.category_name
        order by pic_count desc, c.category_name asc
        limit 1
    '''
    row = db.query(sql, [], True)
    if not row:
        return None
    return {'id': row['id'], 'name': row['category_name'], 'count': row['pic_count']}

def date_with_most_pictures():
    
    sql = '''
        select date, count(*) as cnt
        from picture
        where date is not null and date <> ''
        group by date
        order by cnt desc, date asc
        limit 1
    '''
    row = db.query(sql, [], True)
    if not row:
        return None
    return {'date': row['date'], 'count': row['cnt']}

def user_with_most_pictures():
    sql = '''
        select u.id, u.username, count(p.id) as pic_count
        from user u
        left join picture p on p.user_id = u.id
        group by u.id, u.username
        order by pic_count desc, u.username asc
        limit 1
    '''
    row = db.query(sql, [], True)
    if not row:
        return None
    return {'id': row['id'], 'username': row['username'], 'count': row['pic_count']}

def user_who_commented_most():
    sql = '''
        select u.id, u.username, count(c.id) as comment_count
        from user u
        left join comment c on c.user_id = u.id
        group by u.id, u.username
        order by comment_count desc, u.username asc
        limit 1
    '''
    row = db.query(sql, [], True)
    if not row:
        return None
    return {'id': row['id'], 'username': row['username'], 'count': row['comment_count']}

def user_who_got_most_comments():
    
    sql = '''
        select u.id, u.username, count(c.id) as comment_count
        from user u
        join picture p on p.user_id = u.id
        left join comment c on c.picture_id = p.id
        group by u.id, u.username
        order by comment_count desc, u.username asc
        limit 1
    '''
    row = db.query(sql, [], True)
    if not row:
        return None
    return {'id': row['id'], 'username': row['username'], 'count': row['comment_count']}

def picture_with_most_comments():
    sql = '''
        select p.id, p.name, count(c.id) as comment_count
        from picture p
        left join comment c on c.picture_id = p.id
        group by p.id, p.name
        order by comment_count desc, p.name asc
        limit 1
    '''
    row = db.query(sql, [], True)
    if not row:
        return None
    return {'id': row['id'], 'name': row['name'], 'count': row['comment_count']}
