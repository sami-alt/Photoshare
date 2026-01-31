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
    date text
);