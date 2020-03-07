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
        utils.cache_data(utils.URI_DATA)

    def _csv_update(self) -> None:
        with requests.Session() as s:
            for uri, fpath in utils.DICT.items():
                download = s.get(uri)
                decoded_content = download.content.decode('utf-8')
                with open(fpath, "w") as f:
                    f.write(decoded_content)
        logger.info("CSV downloaded")

    async def send_notifications(self, channels_id, old_data, new_data):
        __, text = utils.string_formatting(new_data)
        tot = new_data["total"]
        c, r, d = utils.difference_on_update(old_data, new_data)
        header = f"""Total Confirmed **{tot['confirmed']}** (+ {c})
        Total Recovered **{tot['recovered']}** (+ {r})
        Total Deaths **{tot['deaths']}** (+ {d})\n"""
        embed = discord.Embed(
            description=header + "\n" + text,
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.set_author(name="Current Region/Country affected by Coronavirus COVID-19",
                         url="https://www.who.int/home",
                         icon_url=self.author_thumb)
        embed.set_thumbnail(url=self.thumb)
        try:
            embed.set_footer(
                text=utils.last_update(utils.DATA_PATH),
                icon_url=self.bot.me.avatar_url
            )
        except: pass

        for _ in channels_id:
            with open("stats.png", "rb") as p:
                img = discord.File(p, filename="stats.png")
            channel = self.bot.get_channel(int(_["channel_id"]))
            embed.set_image(url=f'attachment://stats.png')
            await channel.send(file=img, embed=embed)
        logger.info("Notifications sended")

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
        starting = True
        while True:
            channels_id = db.to_send()
            if not os.path.exists(utils._CONFIRMED_PATH):
                self._csv_update()
            if self.diff_checker(utils.data_reader(utils._CONFIRMED_PATH)):
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
                await self.send_notifications(channels_id, old_data, new_data)
            else:
                starting = False
            await asyncio.sleep(3600)


def setup(bot):
    bot.add_cog(AutoUpdater(bot))
