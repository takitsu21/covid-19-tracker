import asyncio
import pymysql
from decouple import config
import logging
import functools


logger = logging.getLogger("covid-19")

class Database:
    def __init__(self, conn=None):
        self.conn = conn

    def to_send(self):
        self._ping()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM notification")
        r = cur.fetchall()
        cur.close()
        return r

    def insert_notif(self, guild_id, channel_id):
        self._ping()
        cur = conn.cursor()
        sql = """INSERT INTO notification(guild_id, channel_id) VALUES(%s, %s)"""
        cur.execute(sql, (guild_id, channel_id, ))
        conn.commit()
        cur.close()
        # logger.info(f"{guild_id} GUILD ID : {channel_id} CHANNEL ID | ADDED")

    def delete_notif(self, guild_id):
        self._ping()
        cur = conn.cursor()
        sql = """DELETE FROM notification WHERE guild_id=%s"""
        cur.execute(sql, (guild_id, ))
        logger.info(f'{guild_id} removed')
        conn.commit()
        cur.close()

    def update_notif(self, guild_id, channel_id):
        self._ping()
        cur = conn.cursor()
        sql = """UPDATE notification SET
                channel_id=%s
                WHERE guild_id=%s"""
        cur.execute(sql, (channel_id, guild_id, ))
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