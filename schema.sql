create table user(
    id integer primary key,
    username text unique,
    password text
);

create table user_picture(
    id integer primary key,
    user_picture BLOB,
    user_id references user(id)
);

create table picture(
    id integer primary key,
    user_id integer references user(id),
    image BLOB,
    name text,
    description text,
    date text,
    category_id references categories(id)
);

create table comment(
    id integer primary key,
    comment text,
    user_id integer,
    picture_id integer references picture(id) on delete cascade
);

create table picture_in_category(
    id integer primary key,
    category_id references categories(id),
    picture_id references picture(id) on delete cascade
);

create table categories(
    id integer primary key,
    category_name text
);





