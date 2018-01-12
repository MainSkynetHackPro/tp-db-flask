DROP INDEX IF EXISTS post_thread_id;
DROP INDEX IF EXISTS posts_path;
DROP INDEX IF EXISTS lower_user_name;
DROP INDEX IF EXISTS lower_thread_slug;
DROP INDEX IF EXISTS forum_user_id;
DROP INDEX IF EXISTS forum_slug_lower;
DROP INDEX IF EXISTS user_forum_forum_id;
DROP INDEX IF EXISTS post_created_flat;
DROP INDEX IF EXISTS post_thread_author;
DROP INDEX IF EXISTS post_path_thread_id;
DROP INDEX IF EXISTS thread_forum_author;
DROP INDEX IF EXISTS post_created_flat_sm;

DROP TABLE IF EXISTS forum;
DROP TABLE IF EXISTS thread;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS user_forum;

CREATE TABLE forum
(
  id            SERIAL PRIMARY KEY NOT NULL,
  user_id       INTEGER,
  title         VARCHAR(128),
  slug          VARCHAR(50),
  count_threads INTEGER DEFAULT 0,
  count_posts   INTEGER DEFAULT 0
);

CREATE TABLE thread
(
  id         SERIAL PRIMARY KEY NOT NULL,
  user_id    INTEGER,
  forum_id   INTEGER,
  forum_slug VARCHAR(50),
  slug       VARCHAR(50),
  title      VARCHAR(256),
  message    TEXT,
  created    TIMESTAMP WITH TIME ZONE,
  votes      INTEGER DEFAULT 0
);

CREATE TABLE member
(
  id       SERIAL PRIMARY KEY                  NOT NULL,
  nickname CITEXT COLLATE pg_catalog.ucs_basic NOT NULL CONSTRAINT User_nickname_unique UNIQUE,
  fullname VARCHAR(50),
  email    VARCHAR(50),
  about    TEXT
);

CREATE TABLE posts
(
  id        SERIAL PRIMARY KEY NOT NULL,
  user_id   INTEGER,
  thread_id INTEGER,
  parent_id INTEGER,
  is_edited BOOLEAN,
  created   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  message   TEXT,
  path      INTEGER [],
  root_id   INTEGER
);

CREATE TABLE votes
(
  id        SERIAL PRIMARY KEY NOT NULL,
  user_id   INTEGER,
  thread_id INTEGER,
  voice     INTEGER,
  UNIQUE (user_id, thread_id)
);

CREATE TABLE user_forum
(
  id            SERIAL PRIMARY KEY NOT NULL,
  forum_id      INTEGER,
  user_id       INTEGER,
  user_nickname VARCHAR(50),
  UNIQUE (forum_id, user_id)
);

CREATE INDEX post_thread_id
  ON posts (thread_id);
CREATE INDEX posts_path
  ON posts (path);
CREATE INDEX post_thread_author
  ON posts (thread_id, user_id, id);
CREATE INDEX lower_user_name
  ON member (lower(nickname));
CREATE INDEX lower_thread_slug
  ON thread (lower(slug));
CREATE INDEX forum_user_id
  ON forum (user_id);
CREATE INDEX forum_slug_lower
  ON forum (lower(slug));
CREATE INDEX user_forum_forum_id
  ON user_forum (forum_id);
CREATE INDEX post_path_thread_id
  ON posts (thread_id, path);
CREATE INDEX post_created_flat
  ON posts (thread_id, created, id);
CREATE INDEX post_created_flat_sm
  ON posts (thread_id, id);
CREATE INDEX thread_forum_author
  ON thread (forum_id, user_id);


DROP FUNCTION IF EXISTS create_parent_path();
CREATE FUNCTION create_parent_path()
  RETURNS TRIGGER AS
$create_parent_path$
DECLARE
  tmp_path    INTEGER [];
  tmp_root_id INTEGER;
BEGIN
  IF new.parent_id = 0
  THEN
    UPDATE posts
    SET path = ARRAY [0, new.id], root_id = new.id
    WHERE id = new.id;
  ELSE
    SELECT
      path,
      root_id
    INTO tmp_path, tmp_root_id
    FROM posts
    WHERE id = new.parent_id;
    UPDATE posts
    SET
      path = tmp_path || ARRAY [new.id], root_id = tmp_root_id
    WHERE id = new.id;
  END IF;
  RETURN new;
END;
$create_parent_path$ LANGUAGE plpgsql;

CREATE TRIGGER set_parent_path
AFTER INSERT ON posts
FOR EACH ROW EXECUTE PROCEDURE create_parent_path();
