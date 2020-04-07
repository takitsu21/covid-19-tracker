import asyncio
import discord
from discord.ext import commands
import os
import datetime as dt

import src.utils as utils


class News(commands.Cog):
    """Help commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="news", aliases=["new", "n"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def news(self, ctx):
        news = await utils.from_json(utils.NEWS_PATH)
        embed = discord.Embed(
            title=":newspaper: Recent news about Coronavirus COVID-19 :newspaper:",
            timestamp=utils.discord_timestamp(),
            color=utils.COLOR
        )
        sources = []
        length = 0
        max_size = 5800
        for n in news["articles"]:
            source = n["source"]["name"]
            if source not in sources:
                sources.append(source)
            else:
                continue
            try:
                length += len(f"🞄 **{source}** : {n['title']} {n['description']}  [Link]({n['url']})")
                if length >= max_size:
                    break
                embed.add_field(name=f"🞄 **{source}** : {n['title']}",
                                value=f"{n['description']}  [Link]({n['url']})",
                                inline=False)
            except discord.errors.HTTPException:
                break
        embed.set_thumbnail(url="https://avatars2.githubusercontent.com/u/32527401?s=400&v=4")
        embed.set_footer(text=utils.last_update(utils.NEWS_PATH) + " | newsapi.org",
                        icon_url=ctx.guild.me.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(News(bot))