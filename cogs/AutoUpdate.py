import asyncio
import datetime as dt
import logging
import os
import sys
import time
import uuid
from typing import List

import discord
import requests
from aiohttp import ClientSession
from decouple import config
from discord.ext import commands

import src.utils as utils
from src.plotting import plot_csv

logger = logging.getLogger("covid-19")


class AutoUpdater(commands.Cog):
    __slots__ = ("bot", "interval_update")
    def __init__(self, bot):
        self.bot = bot
        self.interval_update = 0
        self.bot.loop.create_task(self.main())

    async def send_notifications(self):
        channels_id = await self.bot.to_send()
        total_history_confirmed = await utils.get(self.bot.http_session, "/history/confirmed/total/")
        total_history_recovered = await utils.get(self.bot.http_session, "/history/recovered/total/")
        total_history_deaths = await utils.get(self.bot.http_session, "/history/deaths/total/")

        history_confirmed = await utils.get(self.bot.http_session, "/history/confirmed/")
        history_recovered = await utils.get(self.bot.http_session, "/history/recovered/")
        history_deaths = await utils.get(self.bot.http_session, "/history/deaths/")

        all_data = await utils.get(self.bot.http_session, "/all/")

        for guild in channels_id:
            # go next, didn't match interval for this guild
            if self.interval_update % guild["next_update"] != 0:
                continue
            try:
                embed = discord.Embed(
                    description=utils.mkheader(),
                    timestamp=dt.datetime.utcnow(),
                    color=utils.COLOR
                )

                if guild["country"] == "all":
                    country = "World"
                else:
                    country = guild["country"]
                data = utils.get_country(all_data, country)
                if data is None:
                    continue

                path = (country.replace(" ", "_") + utils.STATS_PATH).lower()
                confirmed = data["totalCases"]
                recovered = data["totalRecovered"]
                deaths = data["totalDeaths"]
                active = data["activeCases"]
                embed.set_author(
                    name=f"Coronavirus COVID-19 Notification - {data['country']}",
                    icon_url=f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/png250px/{data['iso2'].lower()}.png"
                )
                embed.add_field(
                    name="<:confirmed:688686089548202004> Confirmed",
                    value=f"{confirmed:,}"
                )
                embed.add_field(
                    name="<:recov:688686059567185940> Recovered",
                    value=f"{recovered:,} (**{utils.percentage(confirmed, recovered)}**)"
                )
                embed.add_field(
                    name="<:_death:688686194917244928> Deaths",
                    value=f"{deaths:,} (**{utils.percentage(confirmed, deaths)}**)"
                )

                embed.add_field(
                    name="<:_calendar:692860616930623698> Today confirmed",
                    value=f"+{data['newCases']:,} (**{utils.percentage(confirmed, data['newCases'])}**)"
                )
                embed.add_field(
                    name="<:_calendar:692860616930623698> Today deaths",
                    value=f"+{data['newDeaths']:,} (**{utils.percentage(confirmed, data['newDeaths'])}**)"
                )
                embed.add_field(
                    name="<:bed_hospital:692857285499682878> Active",
                    value=f"{active:,} (**{utils.percentage(confirmed, active)}**)"
                )
                embed.add_field(
                    name="<:critical:752228850091556914> Serious critical",
                    value=f"{data['seriousCritical']:,} (**{utils.percentage(confirmed, data['seriousCritical'])}**)"
                )
                if data["totalTests"]:
                    percent_pop = ""
                    if data["population"]:
                        percent_pop = f"(**{utils.percentage(data['population'], data['totalTests'])}**)"

                    embed.add_field(
                        name="<:test:752252962532884520> Total test",
                        value=f"{data['totalTests']:,} {percent_pop}"
                    )


                if not os.path.exists(path) and country != "World":
                    await plot_csv(
                        path,
                        utils.get_country_history(history_confirmed, country),
                        utils.get_country_history(history_recovered, country),
                        utils.get_country_history(history_deaths, country))
                elif not os.path.exists(path):
                    await plot_csv(
                        path,
                        total_history_confirmed,
                        total_history_recovered,
                        total_history_deaths)


                with open(path, "rb") as p:
                    img = discord.File(p, filename=path)
                embed.set_image(url=f'attachment://{path}')
                embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
                channel = self.bot.get_channel(int(guild["channel_id"]))
                try:
                    embed.set_footer(
                        text="coronavirus.jessicoh.com/api/ | " + utils.last_update(all_data[0]['lastUpdate'])
                    )
                except Exception as e:
                    pass
                await channel.send(file=img, embed=embed)
            except Exception as e:
                pass
        logger.info("Notifications sent")

    async def send_tracker(self):
        total_history_confirmed = await utils.get(self.bot.http_session, "/history/confirmed/total/")
        total_history_recovered = await utils.get(self.bot.http_session, "/history/recovered/total/")
        total_history_deaths = await utils.get(self.bot.http_session, "/history/deaths/total/")

        history_confirmed = await utils.get(self.bot.http_session, "/history/confirmed/")
        history_recovered = await utils.get(self.bot.http_session, "/history/recovered/")
        history_deaths = await utils.get(self.bot.http_session, "/history/deaths/")

        all_data = await utils.get(self.bot.http_session, "/all/")
        tracked = await self.bot.send_tracker()
        for t in tracked:
            try:
                embed = discord.Embed(
                    description=utils.mkheader(),
                    timestamp=dt.datetime.utcnow(),
                    color=utils.COLOR
                )
                path = utils.STATS_PATH
                if t["country"].lower() == "all":
                    country = "World"
                else:
                    country = t["country"]
                    path = (country.replace(" ", "_") + utils.STATS_PATH).lower()
                data = utils.get_country(all_data, country)
                if data is None:
                    continue


                confirmed = data["totalCases"]
                recovered = data["totalRecovered"]
                deaths = data["totalDeaths"]
                active = data["activeCases"]
                embed.set_author(
                    name=f"Coronavirus COVID-19 Personnal Tracker - {data['country']}",
                    icon_url=f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/png250px/{data['iso2'].lower()}.png"
                )
                embed.add_field(
                    name="<:confirmed:688686089548202004> Confirmed",
                    value=f"{confirmed:,}"
                )
                embed.add_field(
                    name="<:recov:688686059567185940> Recovered",
                    value=f"{recovered:,} (**{utils.percentage(confirmed, recovered)}**)"
                )
                embed.add_field(
                    name="<:_death:688686194917244928> Deaths",
                    value=f"{deaths:,} (**{utils.percentage(confirmed, deaths)}**)"
                )

                embed.add_field(
                    name="<:_calendar:692860616930623698> Today confirmed",
                    value=f"+{data['newCases']:,} (**{utils.percentage(confirmed, data['newCases'])}**)"
                )
                embed.add_field(
                    name="<:_calendar:692860616930623698> Today deaths",
                    value=f"+{data['newDeaths']:,} (**{utils.percentage(confirmed, data['newDeaths'])}**)"
                )
                embed.add_field(
                    name="<:bed_hospital:692857285499682878> Active",
                    value=f"{active:,} (**{utils.percentage(confirmed, active)}**)"
                )
                embed.add_field(
                    name="<:critical:752228850091556914> Serious critical",
                    value=f"{data['seriousCritical']:,} (**{utils.percentage(confirmed, data['seriousCritical'])}**)"
                )
                if data["totalTests"]:
                    percent_pop = ""
                    if data["population"]:
                        percent_pop = f"(**{utils.percentage(data['population'], data['totalTests'])}**)"

                    embed.add_field(
                        name="<:test:752252962532884520> Total test",
                        value=f"{data['totalTests']:,} {percent_pop}"
                    )


                if not os.path.exists(path) and country != "World":
                    await plot_csv(
                        path,
                        utils.get_country_history(history_confirmed, country),
                        utils.get_country_history(history_recovered, country),
                        utils.get_country_history(history_deaths, country))
                elif not os.path.exists(path):
                    await plot_csv(
                        path,
                        total_history_confirmed,
                        total_history_recovered,
                        total_history_deaths)

                channel = self.bot.get_user(int(t["user_id"]))
                with open(path, "rb") as p:
                    img = discord.File(p, filename=path)
                embed.set_image(url=f'attachment://{path}')
                embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
                try:
                    embed.set_footer(
                        text="coronavirus.jessicoh.com/api/ | " + utils.last_update(all_data[0]['lastUpdate'])
                    )
                except Exception as e:
                    pass
                await channel.send(file=img, embed=embed)
            except Exception as e:
                pass
        logger.info("Tracker sent")

    async def main(self):
        if self.bot.auto_update_running:
            return
        self.bot.news = utils.load_news()
        if self.bot.http_session is None:
            self.bot.http_session = ClientSession(loop=self.bot.loop)
        await self.bot.wait_until_ready()
        utils.png_clean()
        starting = True
        self.bot.auto_update_running = True
        while True:
            before = time.time()
            if not starting:
                self.interval_update += 1
                await utils._write(utils.NEWS_URL, utils.NEWS_PATH, self.bot.http_session)
                self.bot.news = utils.load_news()
                utils.png_clean()

                await self.send_notifications()
                await self.send_tracker()
            else:
                starting = False

            after = time.time()

            await asyncio.sleep(3600 - int(after - before))


def setup(bot):
    bot.add_cog(AutoUpdater(bot))
