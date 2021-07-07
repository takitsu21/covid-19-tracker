import asyncio
import logging

import topgg
from decouple import config
from discord.ext import commands, tasks

logger = logging.getLogger("covid-19")


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""
    __slots__ = ("bot", "topgg")

    def __init__(self, bot):
        self.bot = bot
        self.topgg = topgg.DBLClient(bot, config('dbl_token'))
        if not self.bot.debug_token:
            self.bot.loop.create_task(self.update_stats())

    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""
        while True:
            try:
                await self.topgg.post_guild_count()
                logger.info(f"Posted server count ({self.topgg.guild_count})")
            except Exception as e:
                logger.error(
                    f"Failed to post server count\n{e.__class__.__name__}: {e}")
            await asyncio.sleep(30 * 60)


def setup(bot):
    bot.add_cog(TopGG(bot))
