import asyncio
import discord
from discord.ext import commands
import os
import datetime as dt

import src.utils as utils
from data.datas import DATA


class Datacmds(commands.Cog):
    """Help commands"""
    def __init__(self, bot):
        self.bot = bot
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langfr-280px-COVID-19_Outbreak_World_Map.svg.png"
        self.author_thumb = "https://www.stickpng.com/assets/images/5bd08abf7aaafa0575d8502b.png"

    @commands.command(name="info")
    @utils.trigger_typing
    async def info(self, ctx):
        header, text = utils.string_formatting(DATA)
        embed = discord.Embed(
            description=header + "\n" + text,
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.set_author(name="Current Region/Country affected by Coronavirus COVID-19",
                         url="https://www.who.int/home",
                         icon_url=self.author_thumb)
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="country")
    @utils.trigger_typing
    async def country(self, ctx, *country):
        if not len(country):
            embed = discord.Embed(
                    description="No args provided, I can't tell you which country/region is affected if you won't tell me everything!",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        else:
            header, text = utils.string_formatting(
                    DATA,
                    country
                )
            if len(text) > 0:
                embed = discord.Embed(
                    description=header + "\n" + text,
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
            else:
                embed = discord.Embed(
                    description="Wrong country selected retry with a valid one!",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        embed.set_author(name="Current Region/Country affected by Coronavirus COVID-19",
                        url="https://www.who.int/home",
                        icon_url=self.author_thumb)
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="stats", aliases=["stat", "statistic", "s"])
    @utils.trigger_typing
    async def stats(self, ctx):
        with open("data/stats.png", "rb") as p:
            await ctx.send(file=discord.File(p, "data/stats.png"))


def setup(bot):
    bot.add_cog(Datacmds(bot))