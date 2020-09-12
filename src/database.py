import asyncio
import logging

from decouple import config

import aiomysql


logger = logging.getLogger("covid-19")

class Pool:
    async def set_prefix(self, guild_id, prefix):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:

                await cur.execute("INSERT INTO guild_setting(guild_id, prefix) VALUES(%s, %s)", (guild_id, prefix, ))
                await conn.commit()
                await cur.close()

    async def getg_prefix(self, guild_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT prefix FROM guild_setting WHERE guild_id=%s", (guild_id, ))
                r, = await cur.fetchone()
                await cur.close()
                return r

    async def update_prefix(self, guild_id, prefix):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:

                await cur.execute("UPDATE guild_setting SET prefix=%s WHERE guild_id=%s", (prefix, guild_id, ))
                await conn.commit()
                await cur.close()

    async def delete_prefix(self, guild_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:

                await cur.execute("DELETE FROM guild_setting WHERE guild_id=%s", (guild_id, ))
                await conn.commit()
                await cur.close()

    async def to_send(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:

                await cur.execute("SELECT * FROM notification")
                r = await cur.fetchall()
                await cur.close()

                return r

    async def insert_notif(self, guild_id, channel_id, country, next_update):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:

                sql = """INSERT INTO notification(guild_id, channel_id, country, next_update) VALUES(%s, %s, %s, %s)"""
                await cur.execute(sql, (guild_id, channel_id, country.lower(), next_update, ))
                await conn.commit()
                await cur.close()

    async def delete_notif(self, guild_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:

                await cur.execute("DELETE FROM notification WHERE guild_id=%s", (guild_id, ))
                await conn.commit()
                await cur.close()

    async def update_notif(self, guild_id, channel_id, country, next_update):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """UPDATE notification SET
                channel_id=%s,
                country=%s,
                next_update=%s
                WHERE guild_id=%s"""
                await cur.execute(sql, (channel_id, country.lower(), next_update, guild_id, ))
                await conn.commit()
                await cur.close()

    async def insert_tracker(self, user_id, guild_id, country):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:

                sql = """INSERT INTO notification(guild_id, channel_id, country, next_update) VALUES(%s, %s, %s, %s)"""
                await cur.execute("INSERT INTO tracker(user_id, guild_id, country) VALUES(%s, %s, %s)", (user_id, guild_id, country, ))
                await conn.commit()
                await cur.close()

    async def delete_tracker(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:

                await cur.execute("DELETE FROM tracker WHERE user_id=%s", (user_id, ))
                await conn.commit()
                await cur.close()

    async def update_tracker(self, user_id, country):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """UPDATE tracker SET
                country=%s
                WHERE user_id=%s"""
                await cur.execute(sql, (country, user_id, ))
                await conn.commit()
                await cur.close()

    async def send_tracker(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:

                await cur.execute("SELECT * FROM tracker")
                r = await cur.fetchall()
                await cur.close()

                return r

    async def select_tracker(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:

                await cur.execute("SELECT country FROM tracker WHERE user_id=%s", (user_id, ))
                r = await cur.fetchone()
                await cur.close()

                return r

    async def _close(self):
        self.pool.terminate()
        await self.pool.wait_closed()

