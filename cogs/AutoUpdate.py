import csv
import datetime as dt
import requests
from discord.ext import commands
from typing import List
import asyncio
import logging
import os

import src.utils as utils


logger = logging.getLogger("covid-19")


class AutoUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.main())

    def _csv_update(self) -> None:
        with requests.Session() as s:
            for uri, fpath in utils.DICT.items():
                download = s.get(uri)
                decoded_content = download.content.decode('utf-8')
                with open(fpath, "w+") as f:
                    f.write(decoded_content)
        logger.info("csv downloaded")

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
        while True:
            if not os.path.exists(utils._CONFIRMED_PATH):
                self._csv_update()
            if self.diff_checker(utils.data_reader(utils._CONFIRMED_PATH)):
                logger.info("csv are up to date")
            else:
                self._csv_update()
            await asyncio.sleep(3600)


def setup(bot):
    bot.add_cog(AutoUpdater(bot))
