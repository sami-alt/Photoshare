create table user(
    id integer primary key,
    name text
)

create table pictures(
    id integer primary key,
    user_id integer references user(id),
    image BLOB
)