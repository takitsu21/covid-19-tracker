from discord.ext import commands

import src.utils as utils
from src.commands import data


class News(commands.Cog):
    """Help commands"""
    __slots__ = ("bot")

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="news", aliases=["new", "n"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def news(self, ctx: commands.Context):
        await data.news_command(self.bot, ctx)



def setup(bot):
    bot.add_cog(News(bot))
