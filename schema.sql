DROP TABLE IF EXISTS forum;
CREATE TABLE forum
(
  id            SERIAL PRIMARY KEY NOT NULL,
  user_id       INTEGER,
  title         VARCHAR(128),
  slug          VARCHAR(50),
  count_threads INTEGER DEFAULT 0,
  count_posts   INTEGER DEFAULT 0
);

DROP TABLE IF EXISTS thread;
CREATE TABLE thread
(
  id       SERIAL PRIMARY KEY NOT NULL,
  user_id  INTEGER,
  forum_id INTEGER,
  slug     VARCHAR(50),
  title    VARCHAR(256),
  message  TEXT,
  created  TIMESTAMP WITH TIME ZONE,
  votes    INTEGER DEFAULT 0
);

DROP TABLE IF EXISTS member;
CREATE TABLE member
(
  id       SERIAL PRIMARY KEY NOT NULL,
  nickname CITEXT COLLATE pg_catalog.ucs_basic NOT NULL CONSTRAINT User_nickname_unique UNIQUE,
  fullname VARCHAR(50),
  email    VARCHAR(50),
  about    TEXT
);

DROP TABLE IF EXISTS posts;
CREATE TABLE posts
(
  id        SERIAL PRIMARY KEY NOT NULL,
  user_id   INTEGER,
  thread_id INTEGER,
  parent_id INTEGER,
  is_edited BOOLEAN,
  created   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  message   TEXT
);

DROP TABLE IF EXISTS votes;
CREATE TABLE votes
(
  id        SERIAL PRIMARY KEY NOT NULL,
  user_id   INTEGER,
  thread_id INTEGER,
  voice     INTEGER,
  UNIQUE (user_id, thread_id)
)
