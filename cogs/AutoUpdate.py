import csv
import datetime as dt
import requests
from discord.ext import commands
from typing import List
import asyncio
import logging
import os

import src.utils as utils
from src.plotting import plot_csv


logger = logging.getLogger("covid-19")


class AutoUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.main())

    def cache(self) -> None:
        utils.cache_data(utils.URI_DATA)

    async def send_notifications(self, channels_id):
        for id in channels_id:
            channel = self.bot.get_channel(id)
            embed = discord.Embed()
            await channel.send(embed=embed)
        logger.info("Notifications sended")
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

    async def update(self, channels_id):
        self.cache()
        logger.info("New data downloaded")
        plot_csv()
        logger.info("New plot generated")
        await self.send_notifications(channels_id)

    async def main(self):
        while True:
            if not os.path.exists(utils.DATA_PATH):
                channels_id = []
                await self.update(channels_id)
            if self.diff_checker(utils.data_reader(utils.DATA_PATH)):
                logger.info("Datas are up to date")
            else:
                channels_id = []
                await self.update(channels_id)
            await asyncio.sleep(3600)


def setup(bot):
    bot.add_cog(AutoUpdater(bot))
