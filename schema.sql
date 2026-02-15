create table user(
    id integer primary key,
    username text,
    password text
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
    picture_id integer
);

create table picture_in_category(
    id integer primary key,
    category_id references categories(id),
    picture_id references picture(id)
);

create table categories(
    id integer primary key,
    category_name text
);




