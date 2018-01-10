from models.dbmodel import DbModel
from models.forum import Forum
from models.thread import Thread
from models.user import User
from modules.dbconector import DbConnector


class Vote(DbModel):
    tbl_name = "votes"

    @classmethod
    def vote_for_thread(cls, user_id, voice, thread_id):
        sql = """
            SELECT FROM {tbl_thread} WHERE id = %(thread_id)s FOR UPDATE;
            DELETE FROM {tbl_name} WHERE user_id = %(user_id)s AND thread_id = %(thread_id)s;
            INSERT INTO {tbl_name} (user_id, thread_id, voice) 
            VALUES (%(user_id)s, %(thread_id)s, %(voice)s);
            UPDATE {tbl_thread} SET 
              votes = sub.votes
              FROM (SELECT SUM(voice) as votes FROM {tbl_name} WHERE thread_id = %(thread_id)s) as sub
            WHERE id=%(thread_id)s;
        """.format_map({
            'tbl_name': cls.tbl_name,
            'tbl_thread': Thread.tbl_name,
            # 'set_statement': 'votes = votes + %(voice)s' if int(voice) > 0 else 'votes = votes - %(voice)s'
        })

        sql += """
        SELECT
          u.nickname as author,
          t.created,
          f.slug as forum,
          t.id,
          t.message,
          t.slug as slug,
          t.title,
          t.votes as votes
        FROM "{0}" as t
        JOIN "{1}" as u ON u.id = t.user_id
        JOIN "{2}" as f ON t.forum_id = f.id
        WHERE t.id = %(thread_id)s
        """.format(Thread.tbl_name, User.tbl_name, Forum.tbl_name)
        variables = {
            'thread_id': thread_id,
            'voice': voice,
            'user_id': user_id,
        }
        return DbConnector.execute_set_and_get(sql, variables)[0]
