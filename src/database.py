import asyncio
import logging

import pymysql
from decouple import config

# import aiomysql


logger = logging.getLogger("covid-19")

# class Poll(object):
#     def __init__(self):
#         self._pool = None
#         self._loop_pool = asyncio.get_event_loop()

#     async def create_pool(self):
#         if not self._pool:
#             self._pool = await aiomysql.connect(
#                 host=config("db_host"),
#                 port=3306,
#                 user=config("db_user"),
#                 password=config("db_token"),
#                 db=config("db"),
#                 loop=self._loop_pool
#             )
#         cur = await conn.cursor()
#         await cur.execute("SELECT * FROM notification")
#         r = await cur.fetchall()
#         print(r)
#         await cur.close()

class Database:
    def __init__(self, conn=None):
        self.conn = conn

    def get_prefix(self, guild_id):
        self._ping()
        cur = self.conn.cursor()
        cur.execute("SELECT prefix FROM guild_setting WHERE guild_id=%s", (guild_id, ))
        r = cur.fetchall()
        cur.close()
        return r

    def set_prefix(self, guild_id, prefix):
        self._ping()
        cur = conn.cursor()
        sql = """INSERT INTO guild_setting(guild_id, prefix) VALUES(%s, %s)"""
        cur.execute(sql, (guild_id, prefix, ))
        conn.commit()
        cur.close()

    def update_prefix(self, guild_id, prefix):
        self._ping()
        cur = conn.cursor()
        sql = """UPDATE guild_setting SET
                prefix=%s
                WHERE guild_id=%s"""
        cur.execute(sql, (prefix, guild_id, ))
        conn.commit()
        cur.close()

    def delete_prefix(self, guild_id):
        self._ping()
        cur = conn.cursor()
        sql = """DELETE FROM guild_setting WHERE guild_id=%s"""
        cur.execute(sql, (guild_id, ))
        conn.commit()
        cur.close()

    def to_send(self):
        self._ping()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM notification")
        r = cur.fetchall()
        cur.close()
        return r

    def insert_notif(self, guild_id, channel_id, country, next_update):
        self._ping()
        cur = conn.cursor()
        sql = """INSERT INTO notification(guild_id, channel_id, country, next_update) VALUES(%s, %s, %s, %s)"""
        cur.execute(sql, (guild_id, channel_id, country.lower(), next_update, ))
        conn.commit()
        cur.close()


    def delete_notif(self, guild_id):
        self._ping()
        cur = conn.cursor()
        sql = """DELETE FROM notification WHERE guild_id=%s"""
        cur.execute(sql, (guild_id, ))
        conn.commit()
        cur.close()

    def update_notif(self, guild_id, channel_id, country, next_update):
        self._ping()
        cur = conn.cursor()
        sql = """UPDATE notification SET
                channel_id=%s,
                country=%s,
                next_update=%s
                WHERE guild_id=%s"""
        cur.execute(sql, (channel_id, country.lower(), next_update, guild_id, ))
        conn.commit()
        cur.close()

    def update_graph_background(self, guild_id, is_dark):
        self._ping()
        cur = conn.cursor()
        sql = """UPDATE notification SET
                dark=%s
                WHERE guild_id=%s"""
        cur.execute(sql, (is_dark, guild_id, ))
        conn.commit()
        cur.close()

    def insert_tracker(self, user_id, guild_id, country):
        self._ping()
        cur = conn.cursor()
        sql = """INSERT INTO tracker(user_id, guild_id, country) VALUES(%s, %s, %s)"""
        cur.execute(sql, (user_id, guild_id, country, ))
        conn.commit()
        cur.close()

    def delete_tracker(self, user_id):
        self._ping()
        cur = conn.cursor()
        sql = """DELETE FROM tracker WHERE user_id=%s"""
        cur.execute(sql, (user_id, ))
        conn.commit()
        cur.close()

    def update_tracker(self, user_id, country):
        self._ping()
        cur = conn.cursor()
        sql = """UPDATE tracker SET
                country=%s
                WHERE user_id=%s"""
        cur.execute(sql, (country, user_id, ))
        conn.commit()
        cur.close()

    def send_tracker(self):
        self._ping()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tracker")
        r = cur.fetchall()
        cur.close()
        return r

    def select_tracker(self, user_id):
        self._ping()
        cur = self.conn.cursor()
        cur.execute("SELECT country FROM tracker WHERE user_id=%s", (user_id, ))
        r = cur.fetchall()
        cur.close()
        return r

    def _ping(self):
        self.conn.ping(reconnect=True)

    def _close(self):
        self.conn.close()
        logger.info("MySQL connexion closed")

try:
    conn = pymysql.connect(
                host=config("db_host"),
                user=config("db_user"),
                port=3306,
                password=config("db_token"),
                db=config("db"),
                cursorclass=pymysql.cursors.DictCursor
                )
    db = Database(conn=conn)
except pymysql.Error as error:
    try:
        db._close()
    except:
        pass
    logger.error(error, exc_info=True)
    logger.info('Connection closed')
