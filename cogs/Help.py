import asyncio
import discord
from discord.ext import commands
import os
import datetime as dt
import time
import random

import src.utils as utils


class Help(commands.Cog):
    """Help commands"""
    def __init__(self, bot):
        self.bot = bot
        self._id = 162200556234866688
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langen-1000px-COVID-19_Outbreak_World_Map.svg.png"

    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx):
        embed = discord.Embed(
            title=":newspaper: Coronavirus COVID-19 Commands",
            description="""[Wold Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)
            **`<something>`** something is required
            **`[something]`** something is optional
            **`arg1 | arg2`** mean arg1 or arg2
            **NOTE: DATA MAY NOT BE FULLY ACCURATE**\n__Stats are updated every 1 hour.__""",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.add_field(
            name="**`c!info`**",
            value="Views every confirmed cases",
            inline=False
        )
        embed.add_field(
            name="**`c!list`**",
            value="Views every country available to be chosen with other commands.",
            inline=False
        )
        embed.add_field(
            name="**`c!<s | stats> [log | country | log [country]]`**",
            value="Views graphical statistics. If no args provided return linear graph for total cases.You can find countries with **full name** or **[ISO-3166-1](https://fr.wikipedia.org/wiki/ISO_3166-1)**.\n __Examples__ : `c!stats us`, `c!s log usa`, `c!stats log`",
            inline=False
        )
        embed.add_field(
            name="**`c!country <country>`**",
            value="Views information about multiple chosen country/region. You can either use **autocompletion** or **[ISO-3166-1](https://fr.wikipedia.org/wiki/ISO_3166-1)**.\n __Examples__ : `c!country fr usa it gb`",
            inline=False
        )
        embed.add_field(
            name="**`c!<r | region> <state/province | all> in <country>`**",
            value="Certains region are not supported yet.\nThe `in` (mandatory symbol) is interpreted as separator between the country and the region/province so don't forget it.\n __Examples__ : `c!r new york in us`, `c!region all in china`",
            inline=False
        )
        embed.add_field(
            name="**`c!track <country | disable>`**",
            value="Track country (bot will DM you update) the command needs to be typed in a server channel not DM.\n__Examples__ : `c!track us`, `c!track disable`",
            inline=False
        )
        embed.add_field(
            name="**`c!nofitication <country | disable> <every NUMBER> <hours | days | weeks>`**",
            value="(Only administrator) When new datas are found, the bot will send you a notification where you typed the command, server only.\n __Examples__ : `c!notification usa every 3 hours`, `c!notification disable`"
        )
        embed.add_field(
            name="**`c!news`**",
            value="Views recent news about COVID-19.",
            inline=False
        )
        embed.add_field(
            name="**`c!source`**",
            value="Views source data which the bot is based on.",
            inline=False
        )
        embed.add_field(
            name="**`c!ping`**",
            value="Views bot ping.",
            inline=False
        )
        embed.add_field(
            name="**`c!invite`**",
            value="Views bot link invite.",
            inline=False
        )
        embed.add_field(
            name="**`c!suggestion <MESSAGE>`**",
            value="Send suggestion feedback.",
            inline=False
        )
        embed.add_field(
            name="**`c!bug <MESSAGE>`**",
            value="Send bug feedback.",
            inline=False
        )
        embed.add_field(
            name="**`c!about`**",
            value="Views informations about the bot.",
            inline=False
        )
        embed.add_field(
            name="**`c!vote`**",
            value="Views bot link vote.",
            inline=False
        )
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        embed.set_thumbnail(url=self.thumb)

        await ctx.send(embed=embed)

    @commands.command(name="vote")
    async def vote(self, ctx):
        embed = discord.Embed(
                description="[Click here](https://top.gg/bot/682946560417333283/vote)",
                timestamp=utils.discord_timestamp(),
                color=utils.COLOR
            )
        embed.set_author(name="Coronavirus COVID-19 Vote link", icon_url=ctx.guild.me.avatar_url)
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(text="Made by Taki#0853", icon_url=ctx.guild.me.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="invite")
    async def invite(self, ctx):
        embed = discord.Embed(
                description="[Click here](https://discordapp.com/oauth2/authorize?client_id=682946560417333283&scope=bot&permissions=313408)",
                timestamp=utils.discord_timestamp(),
                color=utils.COLOR
            )
        embed.set_author(name="Coronavirus COVID-19 Invite link", icon_url=ctx.guild.me.avatar_url)
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(text="Made by Taki#0853", icon_url=ctx.guild.me.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    @commands.is_owner()
    async def avatar(self, ctx):
        with open("corona.png", "rb") as f:
            await self.bot.user.edit(avatar=f.read())

    @commands.command(name="about")
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def about(self, ctx):
        DATA = self.bot._data
        embed = discord.Embed(
                description="You can support me on <:kofi:693473314433138718>[Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot. <:github:693519776022003742> [Source code](https://github.com/takitsu21/covid-19-tracker)\n[Wold Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)",
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
        embed.add_field(name="Help command",value="`c!help` or `@mention help`")
        embed.add_field(name="Prefix",value="`c!` or `@mention`")

        nb_users = 0
        channels = 0
        for s in self.bot.guilds:
            nb_users += len(s.members)
            channels += len(s.channels)
        embed.add_field(name="<:confirmed:688686089548202004> Confirmed", value=DATA["total"]["confirmed"])
        embed.add_field(name="<:recov:688686059567185940> Recovered", value=DATA["total"]["recovered"])
        embed.add_field(name="<:_death:688686194917244928> Deaths", value=DATA["total"]["deaths"])
        embed.add_field(name="<:servers:693053697453850655> Servers", value=len(self.bot.guilds))
        embed.add_field(name="<:users:693053423494365214> Members", value=nb_users)
        embed.add_field(name="<:hashtag:693056105076621342> Channels", value=channels)
        embed.add_field(name="<:stack:693054261512110091> Shards", value=f"{ctx.guild.shard_id + 1}/{self.bot.shard_count}")
        embed.set_footer(text="Made by Taki#0853 (WIP) " + utils.last_update(utils.DATA_PATH),
                        icon_url=ctx.guild.me.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="sources", aliases=["source"])
    async def sources(self, ctx):
        embed = discord.Embed(
            description="[CSSEGISandData](https://github.com/CSSEGISandData/COVID-19)\n[World Health Organization (WHO)](https://www.who.int/)\nThis bot does not use Worldometer's data as it is not accurate and only statistics on the potential cases, recoveries and deaths. The data used by the bot comes directly from the World Health Organisation and Johns Hopkins University as there are more trustworthy. The data is updated once every hour.",
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

    @commands.command(name="ping")
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def ping(self, ctx):
        """Ping's Bot"""
        before = time.monotonic()
        message = await ctx.send("🏓Ping!")
        ping = (time.monotonic() - before) * 1000
        embed = discord.Embed(
                        color=utils.COLOR,
                        title="Ping",
                        description="🏓 Pong!\n**`{0}`** ms".format(int(ping))
                        )
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text="Made by Taki#0853 (WIP)",
            icon_url=ctx.guild.me.avatar_url
        )
        await message.edit(content="", embed=embed)

    @commands.command(name="suggestion")
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def suggestion(self, ctx, *message):
        if len(message) < 3:
            embed = discord.Embed(title="Suggestion",
                                color=utils.COLOR,
                                description="Message too short at least 3 words required.".format(ctx.author.mention),
                                icon_url=ctx.guild.me.avatar_url)
            embed.set_thumbnail(url=ctx.guild.me.avatar_url)
            embed.set_footer(text="Made by Taki#0853 (WIP)",
                            icon_url=ctx.guild.me.avatar_url)
            return await ctx.send(embed=embed)
        dm = self.bot.get_user(self._id)
        message = ' '.join(message)
        await dm.send(f"[{ctx.author} - SUGGEST] -> {message}")
        embed = discord.Embed(title="Suggestion",
                            color=utils.COLOR,
                            description="{} Your suggestion has been sent @Taki#0853.\nThank you for the feedback!".format(ctx.author.mention),
                            icon_url=ctx.guild.me.avatar_url)
        embed.set_thumbnail(url=ctx.guild.me.avatar_url)
        embed.set_footer(text="Made by Taki#0853 (WIP)",
                        icon_url=ctx.guild.me.avatar_url)
        return await ctx.send(embed=embed)

    @commands.command(name="bug")
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def bug(self, ctx, *message):
        if len(message) < 3:
            embed = discord.Embed(title="Bug report",
                    color=utils.COLOR,
                    description="{} Message too short at least 3 words required.".format(ctx.author.mention),
                    icon_url=ctx.guild.me.avatar_url)
            embed.set_thumbnail(url=ctx.guild.me.avatar_url)
            embed.set_footer(text="Made by Taki#0853 (WIP)",
                            icon_url=ctx.guild.me.avatar_url)
            return await ctx.send(embed=embed)
        dm = self.bot.get_user(self._id)
        message = ' '.join(message)
        await dm.send(f"[{ctx.author} - BUG] -> {message}")
        embed = discord.Embed(title="Bug report",
                            color=utils.COLOR,
                            description="Your bug report has been sent @Taki#0853.\nThank you for the feedback!".format(ctx.author.mention),
                            icon_url=ctx.guild.me.avatar_url)
        embed.set_thumbnail(url=ctx.guild.me.avatar_url)
        embed.set_footer(text="Made by Taki#0853 (WIP)",
                        icon_url=ctx.guild.me.avatar_url)
        return await ctx.send(embed=embed)

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx):
        self.bot._unload_extensions()
        self.bot._load_extensions()
        await ctx.send("Reloaded")

def setup(bot):
    bot.add_cog(Help(bot))