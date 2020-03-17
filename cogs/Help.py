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
            **NOTE: DATA MAY NOT BE FULLY ACCURATE**""",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.add_field(
            name="**`c!info`**",
            value="Views every confirmed, recovered, deaths cases",
            inline=False
        )
        embed.add_field(
            name="**`c!news`**",
            value="Views recent news about COVID-19 (update every 1 hour).",
            inline=False
        )
        embed.add_field(
            name="**`c!country <COUNTRY>`**",
            value="Views information about multiple chosen country/region. You can either use **autocompletion** or **country code**. Valid country/region are listed in `c!info`.\nExample : `c!country fr germ it poland`",
            inline=False
        )
        embed.add_field(
            name="**`c!<r | region> <STATE/PROVINCE | all> in <COUNTRY>`**",
            value="Supported countries (**China, Canada, United States, Australia, Cruise Ship**).\nViews regions infected in specific country or in all state with `all` arg.\nThe `in` (mandatory symbol) is interpreted as separator between the country and the region/province so don't forget it.\nExample 1 : `c!r new york in us`\nExample 2 : `c!region all in china`",
            inline=False
        )
        embed.add_field(
            name="**`c!stats`**",
            value="Views graphical statistics",
            inline=False
        )
        embed.add_field(
            name="**`c!track <COUNTRY | disable>`**",
            value="Track multiple country (bot will DM you update). `c!track <COUNTRY>` work like `c!country <COUNTRY>` (**country code** / **autocompletion**) see `c!help`. `c!track disable` will disable the tracker.\nExample 1 : `c!track fr it us gb`\nExample 2 : `c!track disable`",
            inline=False
        )
        embed.add_field(
            name="**`c!notification <enable | disable>`**",
            value="(Only administrator) When new datas are downloaded the bot will send you a notification where you typed the command."
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
            value="Views informations about the bot",
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
        embed.add_field(name="Donate", value="[Patreon](https://www.patreon.com/takitsu)\nBuy me a [Ko-fi](https://ko-fi.com/takitsu)")
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
    async def sources(self, ctx):
        embed = discord.Embed(
            description="[CSSEGISandData](https://github.com/CSSEGISandData/COVID-19)\n[World Health Organization (WHO)](https://www.who.int/)",
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

    @commands.command()
    async def test(self, ctx):
        await ctx.send(f"{ctx.author.status} mobile : {ctx.author.mobile_status}  desktop : {ctx.author.desktop_status} is on mobile : {ctx.author.is_on_mobile()}")

    @commands.command(name="bug")
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