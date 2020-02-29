import asyncio
import discord
from discord.ext import commands
import os
import datetime as dt

import src.utils as utils


class Datacmds(commands.Cog):
    """Help commands"""
    def __init__(self, bot):
        self.bot = bot
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langfr-280px-COVID-19_Outbreak_World_Map.svg.png"

    @commands.command(name="info")
    async def info(self, ctx):
        string_data = utils.string_formatting(
                utils.format_csv(
                    utils.data_reader(utils._CONFIRMED_PATH),
                    utils.data_reader(utils._RECOVERED_PATH),
                    utils.data_reader(utils._DEATH_PATH)
                )
            )
        embed = discord.Embed(
            description=string_data[0] + "\n" + string_data[1],
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.set_author(name="Current Region/Country affected by Coronavirus COVID-19",
                         url="https://www.who.int/home",
                         icon_url=ctx.guild.me.avatar_url)
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="country")
    async def country(self, ctx, *country):
        country = ' '.join(list(x.lower() for x in country))
        string_data = utils.string_formatting(
                utils.format_csv(
                    utils.data_reader(utils._CONFIRMED_PATH),
                    utils.data_reader(utils._RECOVERED_PATH),
                    utils.data_reader(utils._DEATH_PATH)
                ),
                country
            )
        last_csv_update = dt.datetime.utcfromtimestamp(os.path.getctime(utils._CONFIRMED_PATH))
        if len(string_data[1]) > 0:
            embed = discord.Embed(
                description=string_data[0] + "\n" + string_data[1],
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
                        icon_url=ctx.guild.me.avatar_url)
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Datacmds(bot))