import datetime as dt
import time
from typing import Union

import discord
from discord.ext import commands
from discord_slash.context import SlashContext
from pymysql import IntegrityError

import src.utils as utils


async def help_command(bot, ctx: Union[commands.Context, SlashContext], help_type=""):
    try:
        prefix = await bot.getg_prefix(ctx.guild.id)
    except:
        prefix = "c!"
    if help_type and help_type in ("stats", "utilities"):
        embed = discord.Embed(
            title=":newspaper: Coronavirus COVID-19 Commands",
            description="""[World Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)
            **`<something>`** something is required
            **`[something]`** something is optional
            **`arg1 | arg2`** mean arg1 or arg2
            __Stats are updated every 30 minutes.__""",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        if help_type == "stats":
            embed.add_field(
                name=f"📈 **`{prefix}info`**",
                value="Views every countries affected.",
                inline=False
            )
            embed.add_field(
                name=f"📈 **`{prefix}list`**",
                value="Views every country available.",
                inline=False
            )
            embed.add_field(
                name=f"📈 **`{prefix}<s | stats> [log | country | log [country]]`**",
                value=f"Views graphical statistics. If no args provided return linear graph for total cases. You can find countries with **full name** or **[ISO-3166-1](https://fr.wikipedia.org/wiki/ISO_3166-1)**.\n __Examples__ : `{prefix}stats us`, `{prefix}s log usa`, `{prefix}stats log`, `{prefix}s`",
                inline=False
            )
            embed.add_field(
                name=f"📊 **`{prefix}<d | daily> [country]`**",
                value=f"Views daily graphical statistics. If no args provided return World graph. You can find countries with **full name** or **[ISO-3166-1](https://fr.wikipedia.org/wiki/ISO_3166-1)**.\n __Examples__ : `{prefix}daily us`, `{prefix}daily`, `{prefix}daily italy`",
                inline=False
            )
            # embed.add_field(
            #     name=f"📈 **`{prefix}<g | graph> <proportion> <deaths | confirmed | recovered | active> <top | country[]>`**",
            #     value=f"Views graphical statistics. You can find countries with **full name** or **[ISO-3166-1](https://fr.wikipedia.org/wiki/ISO_3166-1)**.\n\n **Proportion**: This is the value / population * 100 \n\n __Examples__ : `{prefix}graph proportion top`, `{prefix}g proportion deaths us gb it es mx fr`, `{prefix}g proportion active gb`",
            #     inline=False
            # )
            embed.add_field(
                name=f"📈 **`{prefix}<c | country> <country>`**",
                value=f"Views information about multiple chosen country. You can either use **autocompletion** or **[ISO-3166-1](https://fr.wikipedia.org/wiki/ISO_3166-1)**.\n __Examples__ : `{prefix}country fr usa it gb`",
                inline=False
            )
            embed.add_field(
                name=f"📈 **`{prefix}<r | region> <state/province | all> in <country>`**",
                value=f"Certain regions are not supported yet.\nThe `in` (mandatory symbol) is interpreted as separator between the country and the region/province so don't forget it.\n __Examples__ : `{prefix}r new york in us`, `{prefix}region all in china`",
                inline=False
            )
            # embed.add_field(
            #     name=f"📈 **`{prefix}continent <continent>`**",
            #     value="Views graph start according to the given continent, available (**AF, AS, EU, NA, SA, OC**)",
            #     inline=False
            # )
            embed.add_field(
                name=f"📈 **`{prefix}track <country | disable>`**",
                value=f"Track country (bot will DM you update) the command needs to be typed in a server channel not DM.\n__Examples__ : `{prefix}track us`, `{prefix}track disable`",
                inline=False
            )
            embed.add_field(
                name=f"📈 **`{prefix}notification <country | disable> <every NUMBER> <hours | days | weeks>`**",
                value=f"(Only administrator) When new data is found, the bot will send you a notification where you typed the command, server only.\n __Examples__ : `{prefix}notification usa every 3 hours`, `{prefix}notification disable`"
            )

        elif help_type == "utilities":
            embed.add_field(
                name=f"⚙️ **`{prefix}setprefix <new_prefix>`**",
                value="Change your guild prefix.(Server - Only admins)",
                inline=False
            )
            embed.add_field(
                name=f"⚙️ **`@Coronavirus COVID-19 getprefix`**",
                value="View current guild prefix.(Server)",
                inline=False
            )
            embed.add_field(
                name=f"⚙️ **`{prefix}source`**",
                value="Views source data which the bot is based on.",
                inline=False
            )
            embed.add_field(
                name=f"⚙️ **`{prefix}ping`**",
                value="Views bot ping.",
                inline=False
            )
            embed.add_field(
                name=f"⚙️ **`{prefix}invite`**",
                value="Views bot link invite.",
                inline=False
            )
            embed.add_field(
                name=f"⚙️ **`{prefix}suggestion <MESSAGE>`**",
                value="Send suggestion feedback.",
                inline=False
            )
            embed.add_field(
                name=f"⚙️ **`{prefix}bug <MESSAGE>`**",
                value="Send bug feedback.",
                inline=False
            )
            embed.add_field(
                name=f"⚙️ **`{prefix}about`**",
                value="Views information about the bot.",
                inline=False
            )
            embed.add_field(
                name=f"⚙️ **`{prefix}vote`**",
                value="Views bot link vote.",
                inline=False
            )
    else:
        embed = discord.Embed(
            title=":newspaper: Coronavirus COVID-19 Commands",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.add_field(
            name=f"📈 **`{prefix}help stats`**",
            value="Every commands for COVID 19 stats. (8 commands)",
            inline=False
        )
        embed.add_field(
            name=f"⚙️ **`{prefix}help utilities`**",
            value="Bot utilities. (9 commands)",
            inline=False
        )
        embed.add_field(
            name=f"📰 **`{prefix}news`**",
            value="Views recent news about COVID-19.",
            inline=False
        )

    embed.set_footer(
        text="coronavirus.jessicoh.com/api/",
        icon_url=bot.user.avatar_url
    )
    embed.set_thumbnail(url=bot.thumb)

    await ctx.send(embed=embed)


async def vote_command(bot, ctx: Union[commands.Context, SlashContext]):
    embed = discord.Embed(
        description="[Click here](https://top.gg/bot/682946560417333283/vote)",
        timestamp=utils.discord_timestamp(),
        color=utils.COLOR
    )
    embed.set_author(name="Coronavirus COVID-19 Vote link",
                     icon_url=bot.user.avatar_url)
    embed.set_thumbnail(url=bot.thumb)
    embed.set_footer(text="coronavirus.jessicoh.com/api/",
                     icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)


async def invite_command(bot, ctx: Union[commands.Context, SlashContext]):
    embed = discord.Embed(
        description="[Click here](https://discordapp.com/oauth2/authorize?client_id=682946560417333283&scope=bot&permissions=313408)",
        timestamp=utils.discord_timestamp(),
        color=utils.COLOR
    )
    embed.set_author(name="Coronavirus COVID-19 Invite link",
                     icon_url=bot.user.avatar_url)
    embed.set_thumbnail(url=bot.thumb)
    embed.set_footer(text="coronavirus.jessicoh.com/api/",
                     icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)


async def about_command(bot, ctx: Union[commands.Context, SlashContext]):
    try:
        prefix = await bot.getg_prefix(ctx.guild.id)
    except:
        prefix = "c!"
    embed = discord.Embed(
        description=utils.mkheader(),
        timestamp=utils.discord_timestamp(),
        color=utils.COLOR
    )
    embed.set_author(name="Coronavirus COVID-19 Tracker",
                     icon_url=bot.user.avatar_url)
    embed.set_thumbnail(url=bot.thumb)
    embed.add_field(name="Vote",
                    value="[Click here](https://top.gg/bot/682946560417333283/vote)")
    embed.add_field(name="Invite Coronavirus COVID-19",
                    value="[Click here](https://discordapp.com/oauth2/authorize?client_id=682946560417333283&scope=bot&permissions=313408)")
    embed.add_field(name="Discord Support",
                    value="[Click here](https://discordapp.com/invite/wTxbQYb)")
    embed.add_field(name="Source code",
                    value="[Click here](https://github.com/takitsu21/covid-19-tracker)")
    embed.add_field(name="Help command",
                    value=f"`{prefix}help` or `@mention help`")
    embed.add_field(name="Prefix", value=f"`{prefix}` or `@mention`")

    nb_users = 0
    channels = 0
    for s in bot.guilds:
        nb_users += len(s.members)
        channels += len(s.channels)
    data = await utils.get(bot.http_session, "/all/world")
    embed.add_field(
        name="<:confirmed:688686089548202004> Confirmed", value=data["totalCases"])
    embed.add_field(name="<:recov:688686059567185940> Recovered",
                    value=data["totalRecovered"])
    embed.add_field(name="<:_death:688686194917244928> Deaths",
                    value=data["totalDeaths"])
    embed.add_field(name="<:servers:693053697453850655> Servers",
                    value=len(bot.guilds))
    embed.add_field(name="<:users:693053423494365214> Members", value=nb_users)
    embed.add_field(
        name="<:hashtag:693056105076621342> Channels", value=channels)
    embed.add_field(name="<:stack:693054261512110091> Shards",
                    value=f"{ctx.guild.shard_id + 1}/{bot.shard_count}")
    embed.set_footer(text="Made by Taki#0853 (WIP) " + utils.last_update(data['lastUpdate']),
                     icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)


async def ping_command(bot, ctx: Union[commands.Context, SlashContext]):
    """Ping's Bot"""
    before = time.monotonic()
    message = await ctx.send("🏓Ping!")
    ping = (time.monotonic() - before) * 1000
    embed = discord.Embed(
        color=utils.COLOR,
        title="Ping",
        description="🏓 Pong!\n**`{0}`** ms".format(int(ping))
    )
    embed.set_thumbnail(url=bot.thumb)
    embed.set_footer(
        text="coronavirus.jessicoh.com/api/",
        icon_url=bot.user.avatar_url
    )
    await message.edit(content="", embed=embed)


async def suggestion_command(bot, ctx: Union[commands.Context, SlashContext], message):
    if len(message) < 3:
        embed = discord.Embed(title="Suggestion",
                              color=utils.COLOR,
                              description="Message too short at least 3 words required.".format(
                                  ctx.author.mention),
                              icon_url=bot.user.avatar_url)
        embed.set_thumbnail(url=bot.user.avatar_url)
        embed.set_footer(text="coronavirus.jessicoh.com/api/",
                         icon_url=bot.user.avatar_url)
        return await ctx.send(embed=embed)
    dm = bot.get_user(bot._id)
    message = ' '.join(message)
    await dm.send(f"[{ctx.author} - SUGGEST] -> {message}")
    embed = discord.Embed(title="Suggestion",
                          color=utils.COLOR,
                          description="{} Your suggestion has been sent @Taki#0853.\nThank you for the feedback!".format(
                                ctx.author.mention),
                          icon_url=bot.user.avatar_url)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text="coronavirus.jessicoh.com/api/",
                     icon_url=bot.user.avatar_url)
    return await ctx.send(embed=embed)


async def bug_command(bot, ctx: Union[commands.Context, SlashContext], message):
    if len(message) < 3:
        embed = discord.Embed(title="Bug report",
                              color=utils.COLOR,
                              description="{} Message too short at least 3 words required.".format(
                                    ctx.author.mention),
                              icon_url=bot.user.avatar_url)
        embed.set_thumbnail(url=bot.user.avatar_url)
        embed.set_footer(text="coronavirus.jessicoh.com/api/",
                         icon_url=bot.user.avatar_url)
        return await ctx.send(embed=embed)
    dm = bot.get_user(bot._id)
    message = ' '.join(message)
    await dm.send(f"[{ctx.author} - BUG] -> {message}")
    embed = discord.Embed(title="Bug report",
                          color=utils.COLOR,
                          description="Your bug report has been sent @Taki#0853.\nThank you for the feedback!".format(
                                ctx.author.mention),
                          icon_url=bot.user.avatar_url)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text="coronavirus.jessicoh.com/api/",
                     icon_url=bot.user.avatar_url)
    return await ctx.send(embed=embed)


async def get_guild_prefix_command(bot, ctx: Union[commands.Context, SlashContext]):
    embed = discord.Embed(
        title=f"Guild prefix",
        timestamp=dt.datetime.utcnow(),
        color=utils.COLOR
    )
    try:
        prefix = await bot.getg_prefix(ctx.guild.id)
    except:
        prefix = "c!"
    embed.add_field(
        name=f"**{ctx.guild.name}**",
        value=f"`{prefix}`"
    )
    embed.set_thumbnail(url=ctx.guild.icon_url)
    await ctx.send(embed=embed)


async def sources_command(bot, ctx: Union[commands.Context, SlashContext]):
    embed = discord.Embed(
        description="<:api:752610700177965146> [API](coronavirus.jessicoh.com/api)\nFor now sources comes from [JHU](https://github.com/CSSEGISandData/COVID-19/) and [worldometer](https://www.worldometers.info/coronavirus/). The API will be improved day by day and surely use other sources.\nYou can access to the API <:github:693519776022003742> [source code](https://github.com/takitsu21/covid19-api).",
        color=utils.COLOR,
        timestamp=utils.discord_timestamp()
    )
    embed.set_author(
        name="Sources used for stats",
        icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Octicons-mark-github.svg/1200px-Octicons-mark-github.svg.png"
    )
    embed.set_thumbnail(url=bot.thumb)
    embed.set_footer(
        text="coronavirus.jessicoh.com/api/",
        icon_url=bot.user.avatar_url
    )
    await ctx.send(embed=embed)

async def setprefix_command(bot, ctx: Union[commands.Context, SlashContext], new_prefix):
    if isinstance(ctx, SlashContext):
        guild_permissions = ctx.author.guild_permissions
    else:
        guild_permissions = ctx.message.author.guild_permissions
    if not guild_permissions.administrator:
        return await ctx.send("You need to have Administrator permission to set a new prefix !")
    if len(new_prefix):
        try:
            await bot.set_prefix(str(ctx.guild.id), new_prefix)
        except IntegrityError:
            await bot.update_prefix(str(ctx.guild.id), new_prefix)
        finally:
            await ctx.send(f"New prefix : `{new_prefix}`")
    else:
        try:
            prefix = await bot.getg_prefix(ctx.guild.id)
        except:
            prefix = "c!"
        await ctx.send(f"Missing prefix arg.\n`{prefix}setprefix <new_prefix>`")