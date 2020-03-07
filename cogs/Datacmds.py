import asyncio
import discord
from discord.ext import commands
import os
import datetime as dt
from pymysql.err import IntegrityError

import src.utils as utils
from src.database import db


class Datacmds(commands.Cog):
    """Help commands"""
    def __init__(self, bot):
        self.bot = bot
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langfr-280px-COVID-19_Outbreak_World_Map.svg.png"
        self.author_thumb = "https://www.stickpng.com/assets/images/5bd08abf7aaafa0575d8502b.png"

    @commands.command(name="info")
    @utils.trigger_typing
    async def info(self, ctx):
        DATA = utils.from_json(utils.DATA_PATH)
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
        with open("stats.png", "rb") as p:
            img = discord.File(p, filename="stats.png")
        embed.set_image(url=f'attachment://stats.png')
        await ctx.send(file=img, embed=embed)

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
            DATA = utils.from_json(utils.DATA_PATH)
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
        DATA = utils.from_json(utils.DATA_PATH)
        confirmed = DATA['total']['confirmed']
        recovered = DATA['total']['recovered']
        deaths = DATA['total']['deaths']
        embed = discord.Embed(
                            timestamp=utils.discord_timestamp(),
                            color=utils.COLOR,
                            )
        embed.set_author(
            name="Coronavirus COVID-19 Stats",
            icon_url=self.author_thumb
            )
        embed.set_thumbnail(
            url=self.thumb
            )
        embed.add_field(
            name="Confirmed",
            value=f"**{confirmed}**"
            )
        embed.add_field(
                    name="Recovered",
                    value=f"**{recovered}** ({utils.percentage(confirmed, recovered)})"
                    )
        embed.add_field(
            name="Deaths",
            value=f"**{deaths}** ({utils.percentage(confirmed, deaths)})"
            )
        embed.set_footer(
            text=utils.last_update("stats.png"),
            icon_url=ctx.guild.me.avatar_url
            )
        with open("stats.png", "rb") as p:
            img = discord.File(p, filename="stats.png")
        embed.set_image(url=f'attachment://stats.png')
        await ctx.send(file=img, embed=embed)

    @commands.command(name="notification", aliases=["notif", "notifications"])
    @commands.has_permissions(administrator=True)
    @utils.trigger_typing
    async def notification(self, ctx, state=None):
        if state is None:
            embed = discord.Embed(
                title="c!notification",
                description="c!nofitication <enable | disable>"
            )
        elif state.lower() == "enable":
            try:
                db.insert_notif(str(ctx.guild.id), str(ctx.channel.id))
            except IntegrityError:
                db.update_notif(str(ctx.guild.id), str(ctx.channel.id))
            embed = discord.Embed(
                title="Notifications successfully enabled",
                description="You will receive a notification in this channel on data update."
            )
        elif state.lower() == "disable":
            db.delete_notif(str(ctx.guild.id))
            embed = discord.Embed(
                title="Notifications successfully disabled",
                description="Notifications are now interrupted in this channel."
            )

        embed.color = color=utils.COLOR
        embed.timestamp = utils.discord_timestamp()
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Datacmds(bot))