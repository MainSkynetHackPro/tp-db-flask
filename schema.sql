DROP TABLE IF EXISTS "user";

CREATE TABLE "user" (
  id       SERIAL PRIMARY KEY,
  nickname CHAR(25),
  fullname CHAR(50),
  about    TEXT
);

DROP TABLE IF EXISTS "forum";

CREATE TABLE "forum" (
  id            SERIAL PRIMARY KEY,
  user_id       INT,
  slug          CHAR(25),
  count_posts   INT,
  count_threads INT
);

DROP TABLE IF EXISTS "thread";

CREATE TABLE "thread" (
  id          SERIAL PRIMARY KEY,
  user_id     INT,
  forum_id    INT,
  title       CHAR(50),
  slug        CHAR(25),
  message     TEXT,
  votes       INT,
  date_create TIME

);

DROP TABLE IF EXISTS "vote";

CREATE TABLE "vote" (
  id        SERIAL PRIMARY KEY,
  user_id   INT,
  thread_id INT,
  vote      INT
);

DROP TABLE IF EXISTS "post";

CREATE TABLE "post" (
  id          SERIAL PRIMARY KEY,
  user_id     INT,
  parent_id   INT,
  thread_id   INT,
  message     TEXT,
  date_create TIME
);

