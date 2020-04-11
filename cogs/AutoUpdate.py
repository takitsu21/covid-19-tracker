import datetime as dt
import requests
from discord.ext import commands
from typing import List
import asyncio
import logging
import os
import discord
import time
import uuid
import sys
from aiohttp import ClientSession
from decouple import config

import src.utils as utils
from src.plotting import plot_csv
from src.database import db
from src import up

logger = logging.getLogger("covid-19")


class AutoUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.interval_update = 0
        self.bot.loop.create_task(self.main())

    async def send_notifications(self):
        data = self.bot._data


        channels_id = db.to_send()

        for i, guild in enumerate(channels_id):
            # go next, didn't match interval for this guild
            if self.interval_update % guild["next_update"] != 0:
                continue
            try:
                version = utils.STATS_PATH
                if guild["country"] != "all":
                    stats = utils._get_country(data, guild["country"])
                    today = stats["today"]
                    confirmed = stats["statistics"]["confirmed"]
                    recovered = stats["statistics"]["recovered"]
                    deaths = stats["statistics"]["deaths"]
                    active = stats["statistics"]["active"]
                    country_name = stats["country"]["name"]
                    thumb = f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/png250px/{stats['country']['code'].lower()}.png"

                    version = stats["country"]["code"].lower() + utils.STATS_PATH

                    if not os.path.exists(version):
                        await plot_csv(version, country=guild["country"])

                elif guild["country"] == "all":
                    stats = data["total"]
                    today = stats["today"]
                    confirmed = stats["confirmed"]
                    recovered = stats["recovered"]
                    deaths = stats["deaths"]
                    active = stats["active"]
                    thumb = self.bot.author_thumb
                    country_name = "All"

                    if not os.path.exists(version):
                        await plot_csv(version)

                else:
                    continue

                embed = discord.Embed(
                    description="You can support me on [Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot.",
                    timestamp=dt.datetime.utcnow(),
                    color=utils.COLOR
                )
                embed.set_author(
                    name="Notification Coronavirus COVID-19",
                    icon_url=self.bot.author_thumb
                    )
                embed.set_author(
                    name=f"Coronavirus COVID-19 Notification - {country_name}",
                    icon_url=thumb
                )
                embed.add_field(
                    name="<:confirmed:688686089548202004> Confirmed",
                    value=f"{confirmed}"
                )
                embed.add_field(
                    name="<:recov:688686059567185940> Recovered",
                    value=f"{recovered} (**{utils.percentage(confirmed, recovered)}**)"
                )
                embed.add_field(
                    name="<:_death:688686194917244928> Deaths",
                    value=f"{deaths} (**{utils.percentage(confirmed, deaths)}**)"
                )

                embed.add_field(
                    name="<:_calendar:692860616930623698> Today confirmed",
                    value=f"+{today['confirmed']} (**{utils.percentage(confirmed, today['confirmed'])}**)"
                )
                embed.add_field(
                    name="<:_calendar:692860616930623698> Today recovered",
                    value=f"+{today['recovered']} (**{utils.percentage(confirmed, today['recovered'])}**)"
                )
                embed.add_field(
                    name="<:_calendar:692860616930623698> Today deaths",
                    value=f"+{today['deaths']} (**{utils.percentage(confirmed, today['deaths'])}**)"
                )
                embed.add_field(
                    name="<:bed_hospital:692857285499682878> Active",
                    value=f"{active} (**{utils.percentage(confirmed, active)}**)"
                )
                with open(version, "rb") as p:
                    img = discord.File(p, filename=version)
                embed.set_image(url=f'attachment://{version}')
                try:
                    embed.set_thumbnail(url=stats["country"]["map"])
                except:
                    embed.set_thumbnail(url=self.bot.thumb + str(uuid.uuid4()))
                channel = self.bot.get_channel(int(guild["channel_id"]))
                try:
                    guild = self.bot.get_guild(int(guild["guild_id"]))
                    embed.set_footer(
                        text=utils.last_update(utils.DATA_PATH),
                        icon_url=guild.me.avatar_url
                    )
                except Exception as e:
                    pass
                await channel.send(file=img, embed=embed)
            except Exception as e:
                pass
        logger.info("Notifications sended")

    @commands.command()
    async def manual(self, ctx):
        if ctx.author.id in (90184563405361152, 162200556234866688):
            await up._write(
                config("uri_data") + "?revalidate=true",
                utils.DATA_PATH,
                self.bot.http_session,
                headers={"Super-Secret": config("uri_key")}
            )
            try:
                tmp = await utils.from_json(utils.DATA_PATH)
                if tmp["success"]:
                    self.bot._data = tmp
                await ctx.send("Manual update is a success!")
            except Exception as e:
                await ctx.send(f"{type(e).__name__} : {e}")
        else:
            await ctx.send("If you know this command that mean you saw it on github haha :p But still, you're not allowed to do this.")

    async def send_tracker(self):
        DATA = await utils.from_json(utils.DATA_PATH)
        data = DATA["total"]

        embed = discord.Embed(
                description="You can support me on [Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot.\n[World Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)",
                timestamp=dt.datetime.utcnow(),
                color=utils.COLOR
                )
        embed.set_author(
            name="Personal tracker for Coronavirus COVID-19",
            icon_url=self.bot.author_thumb
            )
        embed.set_thumbnail(url=self.bot.thumb + str(uuid.uuid4()))
        embed.add_field(
            name="<:confirmed:688686089548202004> Confirmed",
            value=f"{data['confirmed']}"
            )
        embed.add_field(
                name="<:recov:688686059567185940> Recovered",
                value=f"{data['recovered']} (**{utils.percentage(data['confirmed'], data['recovered'])}**)"
            )
        embed.add_field(
            name="<:_death:688686194917244928> Deaths",
            value=f"{data['deaths']} (**{utils.percentage(data['confirmed'], data['deaths'])}**)"
        )

        embed.add_field(
            name="<:_calendar:692860616930623698> Today confirmed",
            value=f"{data['today']['confirmed']} (**{utils.percentage(data['confirmed'], data['today']['confirmed'])}**)"
        )
        embed.add_field(
            name="<:_calendar:692860616930623698> Today recovered",
            value=f"{data['today']['recovered']} (**{utils.percentage(data['confirmed'], data['today']['recovered'])}**)"
        )
        embed.add_field(
            name="<:_calendar:692860616930623698> Today deaths",
            value=f"{data['today']['deaths']} (**{utils.percentage(data['confirmed'], data['today']['deaths'])}**)"
        )
        embed.add_field(
                name="<:bed_hospital:692857285499682878> Active",
                value=f"{data['active']} (**{utils.percentage(data['confirmed'], data['active'])}**)"
            )
        tracked = db.send_tracker()
        for t in tracked:
            try:
                dm = self.bot.get_user(int(t["user_id"]))
                header, text = utils.string_formatting(DATA, t["country"].split(" "))
                embed.description = "You can support me on [Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot.\n[Wold Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)\n\n" + text

                with open("stats.png", "rb") as p:
                    img = discord.File(p, filename="stats.png")
                embed.set_image(url=f'attachment://stats.png')
                try:
                    guild = self.bot.get_guild(int(t["guild_id"]))
                    embed.set_footer(
                            text=utils.last_update(utils.DATA_PATH),
                            icon_url=guild.me.avatar_url
                        )
                except:
                    pass
                await dm.send(file=img, embed=embed)
            except Exception as e:
                pass

    async def parse_and_update(self):
        await up.update(self.bot.http_session)
        logger.info("New data downloaded")
        try:
            await plot_csv(utils.STATS_PATH)
            await plot_csv(utils.STATS_LOG_PATH, logarithmic=True)
        except Exception as e:
            logger.exception(e, exc_info=True)

        logger.info("New plot generated")

    async def main(self):
        self.bot.http_session = ClientSession()
        utils.png_clean()
        await self.parse_and_update()
        self.bot._data = await utils.from_json(utils.DATA_PATH)
        self.bot._backup = self.bot._data
        await self.bot.wait_until_ready()

        starting = True
        while True:
            try:
                before = time.time()
                if not starting:
                    self.interval_update += 1
                    try:
                        # if self.bot._data["success"]:
                        #     self.bot._backup = self.bot._data
                        utils.png_clean()
                        await self.parse_and_update()
                        tmp = await utils.from_json(utils.DATA_PATH)
                        if tmp["success"]:
                            self.bot._backup = tmp
                            self.bot._data = tmp
                    except:
                        try:
                            if self.bot._backup["success"]:
                                self.bot._data = self.bot._backup
                        except:
                            pass
                    finally:
                        await self.send_notifications()
                        await self.send_tracker()
                else:
                    starting = False

                after = time.time()
            except:
                pass
            await asyncio.sleep(3600 - int(after - before))


def setup(bot):
    bot.add_cog(AutoUpdater(bot))
