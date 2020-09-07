import asyncio
import csv
import datetime as dt
import functools
import json
import logging
import os
import pickle
import time
from typing import IO, Dict, List, Tuple

import aiofiles
import discord
from aiohttp import ClientSession
from decouple import config
from discord.ext import commands


logger = logging.getLogger("covid-19")

URI_DATA      = config("uri_data")
DATA_PATH     = "data/datas.pickle"
CSV_DATA_PATH = "data/parsed_csv.json"
NEWS_PATH     = "data/news.pickle"
POP_PATH      = "data/populations.csv"
BACKUP_PATH   = "backup/datas.json"
API_ROOT = config("api_root")


COLOR                    = 0xd6b360
DISCORD_LIMIT            = 2 ** 11 # 2048
MAX_SIZE_FIELD_VALUE     = 2 ** 10 # 1024
MAX_MAX_SIZE_FIELD_VALUE = 5000 # max embed size

USER_AGENT      = {'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/73.0'}
STATS_PATH      = "stats.png"
STATS_LOG_PATH  = "log_stats.png"


class CountryNotFound(Exception):
    pass


class RegionNotFound(Exception):
    pass

def _get_country(data, country):
    for d in data["sorted"]:
        try:
            country_data = d["country"]["name"]
            code = d["country"]["code"]
            iso3 = d["country"]["iso3"]
        except:
            continue
        try:
            if country_data.lower() == country or code.lower() == country or iso3.lower() == country:
                return d
        except:
            continue
    raise CountryNotFound(f"{country} not found")

def matching_path(fpath: str):
    try:
        return fpath.split("-")[2].lower()[:-4]
    except:
        return fpath.split("_")[3].lower()

def iteritems(d):
    for k in d.keys():
        yield k, d[k]

def load_news():
    with open(NEWS_PATH, 'rb') as f:
        return pickle.load(f)

def load_pickle():
    with open(DATA_PATH, 'rb') as f:
        return pickle.load(f)

def load_populations():
    d = {}
    with open(POP_PATH, 'r', encoding='utf-8-sig') as f:
        for line in f:
            (key, val) = line.rsplit(',', 1)
            d[key] = int(val)
        return d

def string_formatting(dataset: list, param: list=[]) -> str:
    max_length = DISCORD_LIMIT - 50
    overflow_string = ""
    rows = ""
    truncated = ""
    header = mkheader()
    header_length = len(header)
    param_length = len(param)
    bold = ""
    for i, d in enumerate(dataset, start=1):
        bold = "**" if i % 2 == 0 else ""
        total_cases = f"{d['totalCases']:,}".replace(",", " ")
        new_cases = f"{d['newCases']:,}".replace(",", " ")
        truncated = d['country'][0:15] + "..." if len(d['country']) >= 18 \
            else d['country']

        overflow_string += f"{bold}{truncated} : {total_cases} [+{new_cases}]{bold}\n"

        if (len(overflow_string) + header_length) >= max_length:
            break
        rows = overflow_string
    return header + rows

def get_country(data, country, type, value=True):
    country = country.lower()
    for d in data['sorted']:
        try:
            country_n = d['country']['name']
            country_code = d['country']['code']
            stats = d['statistics']
            if value:
                if country_n.lower() == country or country == country_code.lower():
                    return stats[type]
            else:
                if not isinstance(country_code, int) and country == country_code.lower():
                    return country_n
        except:
            pass
    return None

def trigger_typing(func):
    @functools.wraps(func)
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        await ctx.trigger_typing()
        return await func(self, ctx, *args, **kwargs)
    return wrapper

def discord_timestamp():
    return dt.datetime.utcfromtimestamp(time.time())

def last_key(csv_data: List[dict]) -> int:
    return list(csv_data[0].keys())[-1]

def last_update(t: int):
    return f"Last update {dt.datetime.utcfromtimestamp(t).strftime('%m/%d/%Y %H:%M:%S')} UTC"

def percentage(total, x):
    return "{:.2f}%".format(x * 100 / total) if total > 0 else 0

def get_states(data: dict, country: str) -> list:
    for v in data["sorted"]:
        try:
            dc_name = v['country']['name'] if v['country']['name'] is not None else "."
            code = v['country']['code'] if v['country']['code'] is not None else "."
            iso3 = v['country']['iso3'] if v['country']['iso3'] is not None else "."
        except Exception as e:
            continue
        if dc_name.lower() == country or code.lower() == country or iso3.lower() == country:
            try:
                return v['regions']
            except KeyError:
                return []
    return []

def parse_state_input(*params: list) -> Tuple[str, str]:
    country = ""
    state = ""
    sep_found = False
    for c in params:
        if "in" == c:
            sep_found = True
            continue
        if sep_found:
            country += c + " "
        else:
            state += c + " "
    return country.rstrip(" ").lower(), state.rstrip(" ").lower()

def human_format(num: int) -> str:
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000
    try:
        if f"{num:.1f}".split(".")[1] != "0":
            return '{:.1f}{}'.format(num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
    except:
        pass
    return '{}{}'.format(int(num), ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

# def region_format(data, country, state):
#     states = get_states(data, country)
#     text = ""
#     overlflow_text = ""
#     length = 0
#     max_length = DISCORD_LIMIT- 50
#     k = 0

#     tot = data['total']
#     header = mkheader()
#     header_length = len(header)
#     for r in data:
#         if len(r[]) >= 18:
#             state_name_trunc = state_name[0:15] + "..."
#         else:
#             state_name_trunc = state_name
#         bold = "**" if k % 2 == 0 else ""

#         if state == "all":
#             text += f"{bold}{state_name_trunc} : {statistics['confirmed']:,} [+{s['today']['confirmed']:,}] confirmed - {statistics['recovered']:,} recovered - {statistics['deaths']:,} deaths{bold}\n"
#             k += 1

#         elif state_name.lower() == state:
#             text += f"{bold}{state_name_trunc} : {statistics['confirmed']:,} [+{s['today']['confirmed']:,}] confirmed - {statistics['recovered']:,} recovered - {statistics['deaths']:,} deaths{bold}\n"
#             k += 1
#         length = len(text) + header_length
#         if length >= max_length:
#             break
#         else:
#             old_text = text
#     if length >= max_length:
#         text = old_text

#     return header + "\n\n", text


def mkheader():
    header = "You can support me on <:kofi:693473314433138718>[Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot. <:github:693519776022003742> [Source code](https://github.com/takitsu21/covid-19-tracker), <:api:752610700177965146> [API](https://coronavirus.jessicoh.com/api/) the bot is using.\n\n"
    return header


def png_clean():
    for file in os.listdir("."):
        if file.endswith("png"):
            os.remove(file)

def filter_continent(data, continent):
    continents = {"data":{}}
    confirmed = 0
    recovered = 0
    deaths = 0
    active = 0
    today_confirmed = 0
    today_recovered = 0
    today_deaths = 0
    for d in data["sorted"]:
        try:
            if d["country"]["continent"].lower() == continent:
                today_confirmed += d["today"]["confirmed"]
                today_recovered += d["today"]["recovered"]
                today_deaths += d["today"]["deaths"]

                active += d["statistics"]["active"]
                confirmed += d["statistics"]["confirmed"]
                recovered += d["statistics"]["recovered"]
                deaths += d["statistics"]["deaths"]
                for h in d["history"]:
                    if h not in continents["data"]:
                        continents["data"][h] = {
                            "confirmed": 0,
                            "recovered": 0,
                            "deaths": 0,
                            "active": 0
                        }
                    continents["data"][h]["confirmed"] += d["history"][h]["confirmed"]
                    continents["data"][h]["recovered"] += d["history"][h]["recovered"]
                    continents["data"][h]["deaths"] += d["history"][h]["deaths"]
                    continents["data"][h]["active"] += d["history"][h]["active"]
        except:
            pass

    continents["total"] = {
        "confirmed": confirmed,
        "recovered": recovered,
        "deaths": deaths,
        "active": active
    }
    continents["today"] = {
        "confirmed": today_confirmed,
        "recovered": today_recovered,
        "deaths": today_deaths
    }

    return continents

async def get(session: ClientSession, endpoint, **kwargs):
    url = API_ROOT + endpoint
    resp = await session.request(
            method="GET",
            url=url,
            headers={"Authorization": config("Authorization")},
            **kwargs
        )
    while resp.status not in range(200, 300):
            try:
                resp = await session.request(
                    method="GET",
                    url=url,
                    headers={"Authorization": config("Authorization")},
                    **kwargs
                )
                logger.info(resp.status)
            except Exception as e:
                logger.exception(e, exc_info=True)
    data = await resp.json()
    return data

async def _get(endpoint, **kwargs):
    url = API_ROOT + endpoint
    session = ClientSession()
    resp = await session.request(
            method="GET",
            url=url,
            headers={"Authorization": config("Authorization")},
            **kwargs
        )
    while resp.status not in range(200, 300):
            try:
                resp = await session.request(
                    method="GET",
                    url=url,
                    headers={"Authorization": config("Authorization")},
                    **kwargs
                )
                logger.info(resp.status)
            except Exception as e:
                logger.exception(e, exc_info=True)
    data = await resp.json()
    return data

class UpdateHandler:
    def __init__(self, lang="en"):
        self.news_api_key = config("news_api")
        self.q = "coronavirus covid 19"
        self.lang = lang
        self.update_list = {
            f"http://newsapi.org/v2/top-headlines?apiKey={self.news_api_key}&language={self.lang}&q={self.q}": NEWS_PATH,
            config("uri_data"): DATA_PATH
        }

    async def fetch(self, url: str, session: ClientSession, **kwargs):
        resp = await session.request(
            method="GET",
            url=url,
            **kwargs
        )

        while resp.status not in range(200, 300):
            try:
                resp = await session.request(
                    method="GET",
                    url=url,
                    **kwargs
                )
                logger.info(resp.status)
            except Exception as e:
                logger.exception(e, exc_info=True)
        data = await resp.json()
        return data

    async def _write(self, url:str, file: IO, session: ClientSession, **kwargs):
        try:
            fetcher = await self.fetch(url=url, session=session, **kwargs)
            with open(file, 'wb') as f:
                pickle.dump(fetcher, f, -1)
            png_clean()
        except Exception as e:
            logger.exception(e, exc_info=True)


    async def update(self, session: ClientSession, **kwargs):
        tasks = []
        for url, fpath in self.update_list.items():
            if fpath == DATA_PATH:
                tasks.append(
                    self._write(url=url, file=fpath, session=session, headers={"Super-Secret": config("uri_key")}, **kwargs)
                )
            else:
                tasks.append(
                    self._write(url=url, file=fpath, session=session)
                )
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_get("/all/france"))