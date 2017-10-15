CREATE TABLE forum
(
    user_id INTEGER,
    title VARCHAR(128),
    slug VARCHAR(50),
    id INTEGER DEFAULT nextval('forum_id_seq'::regclass) PRIMARY KEY NOT NULL,
    count_threads INTEGER DEFAULT 0,
    count_posts INTEGER DEFAULT 0
);
CREATE TABLE thread
(
    user_id INTEGER,
    title VARCHAR(50),
    slug VARCHAR(50),
    message TEXT,
    id INTEGER DEFAULT nextval('thread_id_seq'::regclass) PRIMARY KEY NOT NULL,
    forum_id INTEGER,
    created TIMESTAMP
);
CREATE TABLE "user"
(
    nickname VARCHAR(50),
    id INTEGER DEFAULT nextval('user_id_seq'::regclass) PRIMARY KEY NOT NULL,
    fullname VARCHAR(50),
    email VARCHAR(50),
    about TEXT
);