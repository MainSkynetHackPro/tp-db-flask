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
  title    VARCHAR(50),
  message  TEXT,
  created  TIMESTAMP
);
DROP TABLE IF EXISTS "user";

CREATE TABLE "user"
(
  id       SERIAL PRIMARY KEY NOT NULL,
  nickname VARCHAR(50),
  fullname VARCHAR(50),
  email    VARCHAR(50),
  about    TEXT
);