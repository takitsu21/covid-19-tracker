import csv
import datetime as dt
import requests
from discord.ext import commands
from typing import List
import asyncio
import logging
import os
import discord
import time

import src.utils as utils
from src.plotting import plot_csv
from src.database import db
from src import up


logger = logging.getLogger("covid-19")


class AutoUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langfr-280px-COVID-19_Outbreak_World_Map.svg.png"
        self.author_thumb = "https://www.stickpng.com/assets/images/5bd08abf7aaafa0575d8502b.png"
        self.bot.loop.create_task(self.main())

    async def send_notifications(self, old_data, new_data):
        confirmed = new_data['total']['confirmed']
        recovered = new_data['total']['recovered']
        deaths = new_data['total']['deaths']
        channels_id = db.to_send()
        t, r, c = utils.difference_on_update(old_data, new_data)
        embed = discord.Embed(
            description="Below you can find the new stats for the past hour. (Data are updated ~ every 1 hour)\n`**Status** X`[current_update-last_hour_update]`",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.set_author(name="Notification Coronavirus COVID-19",
                         url="https://www.who.int/home",
                         icon_url=self.author_thumb)
        embed.set_thumbnail(url=self.thumb)
        embed.add_field(
            name="Confirmed",
            value=f"**{confirmed}** [+**{t}**]",
            inline=False
            )
        embed.add_field(
                    name="Recovered",
                    value=f"**{recovered}** ({utils.percentage(confirmed, recovered)}) [+**{r}**]",
                    inline=False
                    )
        embed.add_field(
            name="Deaths",
            value=f"**{deaths}** ({utils.percentage(confirmed, deaths)}) [+**{c}**]",
            inline=False
            )
        for _ in channels_id:
            try:
                with open("stats.png", "rb") as p:
                    img = discord.File(p, filename="stats.png")
                embed.set_image(url=f'attachment://stats.png')
                channel = self.bot.get_channel(int(_["channel_id"]))
                try:
                    guild = self.bot.get_guild(int(_["guild_id"]))
                    embed.set_footer(
                        text=utils.last_update(utils.DATA_PATH),
                        icon_url=guild.me.avatar_url
                    )
                except:
                    pass
                await channel.send(file=img, embed=embed)
            except Exception as e:
                pass
        logger.info("Notifications sended")

    async def send_tracker(self):
        data = utils.from_json(utils.DATA_PATH)
        tracked = db.send_tracker()
        embed = discord.Embed(
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        embed.set_author(name="Personal tracker for Coronavirus COVID-19",
                        url="https://www.who.int/home",
                        icon_url=self.author_thumb)
        embed.set_thumbnail(url=self.thumb)

        for t in tracked:
            try:
                dm = self.bot.get_user(int(t["user_id"]))
                header, text = utils.string_formatting(data, t["country"].split(" "))
                embed.description = "**Country** : X`[current_update-last_hour_update]`\n" + header + "\n" + text
                try:
                    guild = self.bot.get_guild(int(t["guild_id"]))
                    embed.set_footer(
                            text=utils.last_update(utils.DATA_PATH),
                            icon_url=guild.me.avatar_url
                        )
                except:
                    pass
                await dm.send(embed=embed)
            except:
                pass

    async def parse_and_update(self):
        await up.update()
        logger.info("New data downloaded")
        utils.csv_parse()
        plot_csv()
        logger.info("New plot generated")

    async def main(self):
        await self.bot.wait_until_ready()
        await self.parse_and_update()
        starting = True
        while True:
            before = time.time()
            if not starting:

                old_data = utils.from_json(utils.DATA_PATH)
                await self.parse_and_update()
                new_data = utils.from_json(utils.DATA_PATH)
                await self.send_notifications(old_data, new_data)
                await self.send_tracker()
            else:
                starting = False
            after = time.time()
            await asyncio.sleep(3600 - int(after - before))


def setup(bot):
    bot.add_cog(AutoUpdater(bot))
