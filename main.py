import discord
import os
import asyncio
import logging
import decouple
import datetime
import time
import random
from discord.utils import find
from discord.ext import commands
from discord.ext.commands import when_mentioned_or

import src.utils as utils
from src.database import db


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


class Covid(commands.AutoShardedBot):
    def __init__(self, *args, loop=None, **kwargs):
        super().__init__(
            command_prefix=when_mentioned_or("c!"),
            activity=discord.Game(name="Starting..."),
            status=discord.Status.dnd
        )
        self.remove_command("help")
        self._load_extensions()
        data = utils.from_json(utils.DATA_PATH)

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


    async def on_guild_join(self, guild: discord.Guild):
        general = find(lambda x: x.name == "general", guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            data = utils.from_json(utils.DATA_PATH)
            embed = discord.Embed(
                    title="Coronavirus COVID-19 Tracker",
                    description="[Wold Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)",
                    timestamp=datetime.datetime.utcfromtimestamp(time.time()),
                    color=utils.COLOR
                )
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langfr-280px-COVID-19_Outbreak_World_Map.svg.png")
            embed.add_field(name="Vote",
                            value="[Click here](https://top.gg/bot/682946560417333283/vote)")
            embed.add_field(name="Invite Coronavirus COVID-19",
                            value="[Click here](https://discordapp.com/oauth2/authorize?client_id=682946560417333283&scope=bot&permissions=313408)")
            embed.add_field(name="Discord Support",
                            value="[Click here](https://discordapp.com/invite/wTxbQYb)")
            embed.add_field(name = "Source code and commands", value="[Click here](https://github.com/takitsu21/covid-19-tracker)")
            embed.add_field(name="Help command",value="c!help")
            embed.add_field(name="Prefix",value="c!")
            nb_users = 0
            for s in self.guilds:
                nb_users += len(s.members)
            embed.add_field(name="Total confirmed", value=data["total"]["confirmed"], inline=False)
            embed.add_field(name="Total recovered", value=data["total"]["recovered"], inline=False)
            embed.add_field(name="Total deaths", value=data["total"]["deaths"], inline=False)
            embed.add_field(name="Servers", value=len(self.guilds))
            embed.add_field(name="Members", value=nb_users)
            embed.set_footer(text="Made by Taki#0853 (WIP)",
                            icon_url=guild.me.avatar_url)
            await general.send(embed=embed)

    async def on_guild_remove(self, guild: discord.Guild):
        db.delete_notif(guild.id)

    async def on_ready(self):
        # waiting internal cache to be ready
        await self.wait_until_ready()
        i = 0
        while True:
            try:
                data = utils.from_json(utils.DATA_PATH)
                if i == 0:
                    confirmed = data["total"]["confirmed"]
                    await self.change_presence(
                        activity=discord.Game(
                            name="[c!help] | Total confirmed {}".format(confirmed)
                            )
                        )
                elif i == 1:
                    deaths = data["total"]["deaths"]
                    await self.change_presence(
                        activity=discord.Game(
                            name="[c!help] | Total deaths {}".format(deaths)
                            )
                        )
                else:
                    recovered = data["total"]["recovered"]
                    await self.change_presence(
                        activity=discord.Game(
                            name="[c!help] | Total recovered {}".format(recovered)
                            )
                        )
                i = (i + 1) % 3

            except Exception as e:
                logger.exception(e, exc_info=True)
                await self.change_presence(
                        activity=discord.Game(
                            name="[c!help] | Updating data..."
                            )
                        )
            await asyncio.sleep(random.randint(5, 10))

    def run(self, *args, **kwargs):
        try:
            self.loop.run_until_complete(self.start(decouple.config("debug")))
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.logout())
            for task in asyncio.all_tasks(self.loop):
                task.cancel()
            try:
                self.loop.run_until_complete(
                    asyncio.gather(*asyncio.all_tasks(self.loop))
                )
            except asyncio.CancelledError:
                logger.debug("Pending tasks has been cancelled.")
            finally:
                db._close()
                logger.info("Shutting down")

if __name__ == "__main__":
    bot = Covid()
    bot.run()