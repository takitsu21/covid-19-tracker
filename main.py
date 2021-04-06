import datetime
import logging
import os

import aiomysql
import discord
from aiohttp import ClientSession
from decouple import config
from discord.ext import commands
from discord.ext.commands import when_mentioned_or
from discord.utils import find

import src.utils as utils
from src.database import Pool

logger = logging.getLogger('covid-19')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='covid-19.log',
    encoding='utf-8',
    mode='w'
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
)
)
logger.addHandler(handler)


class Covid(commands.AutoShardedBot, Pool):
    __slots__ = (
        "thumb",
        "http_session",
        "author_thumb",
        "news",
        "pool",
        "auto_update_running",
        "msg_read",
        "commands_used",
        "script_start_dt"
    )

    def __init__(self, *args, loop=None, **kwargs):
        super().__init__(
            command_prefix=self._get_prefix,
            activity=discord.Game(name="c!help | Loading shards..."),
            status=discord.Status.dnd
        )
        super(Pool, self).__init__()
        self.remove_command("help")
        self._load_extensions()
        self.news = None
        self.http_session = None
        self.pool = None
        self.auto_update_running = False
        self.msg_read = 0
        self.commands_used = 0
        self.script_start_dt = datetime.datetime.now()
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langfr-1000px-COVID-19_Outbreak_World_Map.svg.png?t="
        self.author_thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/International_Flag_of_Planet_Earth.svg/1200px-International_Flag_of_Planet_Earth.svg.png"
        self.loop.create_task(self.init_async())

    async def _get_prefix(self, bot, message):
        try:
            prefix = await self.getg_prefix(message.guild.id)
        except:
            if message.content[0:2] == "C!":
                prefix = "C!"
            else:
                prefix = "c!"
        return when_mentioned_or(prefix)(bot, message)

    def _load_extensions(self):
        for file in os.listdir("cogs/"):
            try:
                if file.endswith(".py"):
                    self.load_extension(f'cogs.{file[:-3]}')
                    logger.info(f"{file} loaded")
            except Exception:
                logger.exception(f"Fail to load {file}")

    def _unload_extensions(self):
        for file in os.listdir("cogs/"):
            try:
                if file.endswith(".py"):
                    self.unload_extension(f'cogs.{file[:-3]}')
                    logger.info(f"{file} unloaded")
            except Exception:
                logger.exception(f"Fail to unload {file}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                f"That command does not exist :confused:\n"+
                f"Please use `{self.command_prefix}help` for a list of commands"
            )
            # Handling Command Not Found Errors
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('{}'.format(ctx.author.mention),embed=discord.Embed(title=f":alarm_clock: Cooldown Error",
                                  description=f'Please cooldown a little, try again in `{error.retry_after:.2}s`',
                                  color=utils.COLOR),delete_after=5)
            # A little artistic touch won't hurt, I'll attach a screenshot in the PR description
        else:
            # raise error
            embed = discord.Embed(
                title="Error",
                description=f"{error} Invalid command see `c!help`.\nIf you think that is a bot error, report this issue on my discord [here](https://discordapp.com/invite/wTxbQYb) thank you.",
                timestamp=datetime.datetime.utcnow(),
                color=utils.COLOR
            )
            await ctx.send(embed=embed)

    async def on_guild_join(self, guild: discord.Guild):
        await self.wait_until_ready()
        chan_logger = self.get_channel(692815717078270052)
        try:
            general = find(lambda x: x.name == "general", guild.text_channels)
            if general and general.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    description="You can support me on <:kofi:693473314433138718>[Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot. <:github:693519776022003742> [Source code](https://github.com/takitsu21/covid-19-tracker)",
                    timestamp=utils.discord_timestamp(),
                    color=utils.COLOR
                )
                embed.set_author(
                    name="Coronavirus COVID-19 Tracker", icon_url=guild.me.avatar_url)
                embed.set_thumbnail(url=self.thumb)
                embed.add_field(name="Vote",
                                value="[Click here](https://top.gg/bot/682946560417333283/vote)")
                embed.add_field(name="Invite Coronavirus COVID-19",
                                value="[Click here](https://discordapp.com/oauth2/authorize?client_id=682946560417333283&scope=bot&permissions=313408)")
                embed.add_field(name="Discord Support",
                                value="[Click here](https://discordapp.com/invite/wTxbQYb)")
                embed.add_field(
                    name="Source code", value="[Click here](https://github.com/takitsu21/covid-19-tracker)")
                embed.add_field(name="Help command", value="c!help")
                embed.add_field(name="Prefix", value="c!")
                nb_users = 0
                channels = 0
                for s in self.guilds:
                    nb_users += len(s.members)
                    channels += len(s.channels)
                embed.add_field(name="<:confirmed:688686089548202004> Confirmed",
                                value=self._data["total"]["confirmed"])
                embed.add_field(name="<:recov:688686059567185940> Recovered",
                                value=self._data["total"]["recovered"])
                embed.add_field(
                    name="<:_death:688686194917244928> Deaths", value=self._data["total"]["deaths"])
                embed.add_field(
                    name="<:servers:693053697453850655> Servers", value=len(self.guilds))
                embed.add_field(
                    name="<:users:693053423494365214> Members", value=nb_users)
                embed.add_field(
                    name="<:hashtag:693056105076621342> Channels", value=channels)
                embed.add_field(name="<:stack:693054261512110091> Shards",
                                value=f"{ctx.guild.shard_id + 1}/{self.bot.shard_count}")
                embed.set_footer(text="Made by Taki#0853 (WIP) " + utils.last_update(utils.DATA_PATH),
                                 icon_url=guild.me.avatar_url)
                await general.send(embed=embed)
        except:
            pass

        embed = discord.Embed(
            title="Bot added to " + guild.name,
            timestamp=datetime.datetime.utcnow(),
            color=utils.COLOR
        )
        embed.add_field(
            name="<:users:693053423494365214> Members",
            value=len(guild.members)
        )
        embed.add_field(
            name="<:hashtag:693056105076621342> Channels",
            value=len(guild.channels)
        )
        embed.set_thumbnail(url=guild.icon_url)
        embed.set_footer(icon_url=guild.me.avatar_url)
        await chan_logger.send(embed=embed)

    async def on_guild_remove(self, guild: discord.Guild):
        try:
            await self.delete_notif(guild.id)
        except:
            pass
        try:
            await self.delete_prefix(guild.id)
        except:
            pass

    async def init_async(self):
        if self.http_session is None:
            self.http_session = ClientSession(loop=self.loop)
        if self.pool is None:
            try:
                self.pool = await aiomysql.create_pool(
                    host=config("db_host"),
                    port=3306,
                    user=config("db_user"),
                    password=config("db_token"),
                    db=config("db_user"),
                    minsize=5,
                    maxsize=10,
                    loop=self.loop,
                    autocommit=True
                )
                logger.info("pool created")
            except Exception as e:
                logger.exception(e, exc_info=True)

    async def on_ready(self):
        await self.init_async()
        await self.change_presence(
            activity=discord.Game(
                name=f"c!help | coronavirus.jessicoh.com/api/"
            )
        )

    async def on_command(self, ctx):
        self.commands_used += 1

    async def on_message(self, message):
        self.msg_read += 1
        return await self.process_commands(message)

    def run(self, token, *args, **kwargs):
        try:
            super().run(token, *args, **kwargs)
        except KeyboardInterrupt:
            try:
                self.loop.run_until_complete(self._close())
                self.loop.run_until_complete(self.http_session.close())
                logger.info("Shutting down")
                exit(0)
            except Exception as e:
                logger.exception(e, exc_info=True)
                exit(1)


if __name__ == "__main__":
    import sentry_sdk
    from sentry_sdk.integrations.aiohttp import AioHttpIntegration

    sentry_sdk.init(
        config("SENTRY_TOKEN"),
        traces_sample_rate=1.0,
        integrations=[AioHttpIntegration()]
    )
    bot = Covid()
    bot.run(config("token"), reconnect=True)
