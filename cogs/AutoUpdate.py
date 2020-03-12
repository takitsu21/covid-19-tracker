import csv
import datetime as dt
import requests
from discord.ext import commands
from typing import List
import asyncio
import logging
import os
import discord

import src.utils as utils
from src.plotting import plot_csv
from src.database import db


logger = logging.getLogger("covid-19")


class AutoUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langfr-280px-COVID-19_Outbreak_World_Map.svg.png"
        self.author_thumb = "https://www.stickpng.com/assets/images/5bd08abf7aaafa0575d8502b.png"
        self.bot.loop.create_task(self.main())

    def cache(self) -> None:
        utils.cache_data()

    def _csv_update(self) -> None:
        with requests.Session() as s:
            for uri, fpath in utils.DICT.items():
                download = s.get(uri)
                decoded_content = download.content.decode('utf-8')
                with open(fpath, "w") as f:
                    f.write(decoded_content)
        utils.csv_parse()
        logger.info("CSV downloaded and parsed")

    async def send_notifications(self, old_data, new_data):
        confirmed = new_data['total']['confirmed']
        recovered = new_data['total']['recovered']
        deaths = new_data['total']['deaths']
        channels_id = db.to_send()
        t, r, c = utils.difference_on_update(old_data, new_data)
        embed = discord.Embed(
            description="Below you can find the new stats for the past hour. (Data are updated ~ every 1 hour)\n`[current_update-morning_update]`",
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
                embed.description = header + "\n" + text
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

    def diff_checker(self, csv_data: List[dict]) -> bool:
        """
        Return True if up to date else False
        """
        r = requests.get(utils._CONFIRMED_URI)
        if r.status_code >= 200 and r.status_code <= 299:
            decoded_content = r.content.decode('utf-8')
            cr = list(csv.DictReader(decoded_content.splitlines(), delimiter=','))
            return utils.last_key(csv_data) == utils.last_key(cr)
        raise requests.RequestException(f"Request error : {r.status_code}")

    async def main(self):
        await self.bot.wait_until_ready()
        starting = True
        while True:
            if not os.path.exists(utils._CONFIRMED_PATH):
                self._csv_update()
            elif self.diff_checker(utils.data_reader(utils._CONFIRMED_PATH)):
                logger.info("Datas are up to date")
            else:
                self._csv_update()
            old_data = utils.from_json(utils.DATA_PATH)
            self.cache()
            new_data = utils.from_json(utils.DATA_PATH)
            logger.info("New data downloaded")
            plot_csv()
            logger.info("New plot generated")
            if not starting:
                await self.send_notifications(old_data, new_data)
                await self.send_tracker()
            else:
                starting = False
            await asyncio.sleep(3600)


def setup(bot):
    bot.add_cog(AutoUpdater(bot))
