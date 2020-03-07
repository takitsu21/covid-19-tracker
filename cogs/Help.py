import asyncio
import discord
from discord.ext import commands
import os
import datetime as dt

import src.utils as utils


class Help(commands.Cog):
    """Help commands"""
    def __init__(self, bot):
        self.bot = bot
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langfr-280px-COVID-19_Outbreak_World_Map.svg.png"

    @commands.command(name="help", aliases=["h"])
    @utils.trigger_typing
    async def help(self, ctx):
        embed = discord.Embed(
            title=":newspaper: Coronavirus COVID-19 Commands",
            description="[Wold Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.add_field(
            name="**`c!info`**",
            value="Views every confirmed cases, deaths and recovery.",
            inline=False
        )
        embed.add_field(
            name="**`c!country [COUNTRY]`**",
            value="Views information about multiples country/region choosen, Valid country/region are listed with **`c!info`** command. Example : **`c!country fr ita`** will only show you France and Italy datas (it's an infinite filter and work like an autcompleter)",
            inline=False
        )
        embed.add_field(
            name="**`c!<stats | s>`**",
            value="Views graphical statistics",
            inline=False
        )
        embed.add_field(
            name="**`c!about`**",
            value="Views informations about the bot",
            inline=False
        )
        embed.add_field(
            name="**`c!source`**",
            value="Views source data which the bot is based on.",
            inline=False
        )
        embed.add_field(
            name="**`c!notification <enable | disable>`**",
            value="(Only administrator) When new datas are downloaded the bot will send you a notification where you typed the command."
        )
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )

        await ctx.send(embed=embed)

    @commands.command(name="about")
    @utils.trigger_typing
    async def about(self, ctx):
        DATA = utils.from_json(utils.DATA_PATH)
        embed = discord.Embed(
                description="[Wold Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)",
                timestamp=utils.discord_timestamp(),
                color=utils.COLOR
            )
        embed.set_author(name="Coronavirus COVID-19 Tracker", icon_url=ctx.guild.me.avatar_url)
        embed.set_thumbnail(url=self.thumb)
        embed.add_field(name="Vote",
                        value="[Click here](https://top.gg/bot/682946560417333283/vote)")
        embed.add_field(name="Invite Coronavirus COVID-19",
                        value="[Click here](https://discordapp.com/oauth2/authorize?client_id=682946560417333283&scope=bot&permissions=313408)")
        embed.add_field(name="Discord Support",
                        value="[Click here](https://discordapp.com/invite/wTxbQYb)")
        embed.add_field(name = "Source code", value="[Click here](https://github.com/takitsu21/covid-19-tracker)")
        embed.add_field(name="Help command",value="c!help")
        embed.add_field(name="Prefix",value="c!")
        nb_users = 0
        for s in self.bot.guilds:
            nb_users += len(s.members)
        embed.add_field(name="Confirmed", value=DATA["total"]["confirmed"])
        embed.add_field(name="Recovered", value=DATA["total"]["recovered"])
        embed.add_field(name="Deaths", value=DATA["total"]["deaths"])
        embed.add_field(name="Servers", value=len(self.bot.guilds))
        embed.add_field(name="Members", value=nb_users)
        embed.set_footer(text="Made by Taki#0853 (WIP) " + utils.last_update(utils.DATA_PATH),
                        icon_url=ctx.guild.me.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="sources", aliases=["source"])
    @utils.trigger_typing
    async def sources(self, ctx):
        embed = discord.Embed(
            description="[CSSEGISandData](https://github.com/CSSEGISandData/COVID-19)",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
            )
        embed.set_author(
            name="Source used for stats",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Octicons-mark-github.svg/1200px-Octicons-mark-github.svg.png"
        )
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text="Made by Taki#0853 (WIP)",
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="reload")
    @commands.is_owner()
    async def r(self, ctx):
        self.bot._unload_extensions()
        self.bot._load_extensions()
        await ctx.send("Reloaded")

def setup(bot):
    bot.add_cog(Help(bot))