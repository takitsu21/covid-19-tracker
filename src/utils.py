import asyncio
import datetime as dt
import functools
import logging
import os
import pickle
import time
from typing import IO, List, Tuple

import discord
from aiohttp import ClientSession
from decouple import config
from discord.ext import commands

logger = logging.getLogger("covid-19")

URI_DATA = config("uri_data")
DATA_PATH = "data/datas.pickle"
CSV_DATA_PATH = "data/parsed_csv.json"
NEWS_PATH = "data/news.pickle"
POP_PATH = "data/populations.csv"
BACKUP_PATH = "backup/datas.json"
API_ROOT = config("api_root")
NEWS_URL = f"http://newsapi.org/v2/top-headlines?apiKey={config('news_api')}&language=en&q=coronavirus covid 19"

COLOR = 0xd6b360
DISCORD_LIMIT = 2 ** 11  # 2048
MAX_SIZE_FIELD_VALUE = 2 ** 10  # 1024
MAX_MAX_SIZE_FIELD_VALUE = 5000  # max embed size

USER_AGENT = {'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/73.0'}
STATS_PATH = "stats.png"
STATS_LOG_PATH = "log_stats.png"

MAX_RETRIES = 10


class CountryNotFound(Exception):
    pass


class RegionNotFound(Exception):
    pass


def get_country_history(data, country):
    for k, v in data.items():
        if country.lower() in \
                (k.lower(), v['iso2'].lower(), v['iso3'].lower()):
            return v
    return None


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


def string_formatting(dataset: list, param: list = []) -> str:
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


def get_country(data, country):
    country = country.lower()
    for d in data:
        if country in \
                (d['country'].lower(), d['iso2'].lower(), d['iso3'].lower()):
            return d
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


def region_format(confirmed, recovered, deaths):
    overflow_text = text = ""
    header = mkheader()
    header_length = len(header)
    embeds = []
    i = 0
    if type(recovered) == int:
        for c, d in zip(confirmed, deaths):
            bold = "**" if i % 2 == 0 else ""
            total_cases = list(confirmed[c]["history"].values())[-1]
            total_deaths = list(deaths[d]["history"].values())[-1]
            overflow_text += f"{bold}{c} : {total_cases:,} confirmed - {total_deaths:,} deaths{bold}\n"
            if (len(overflow_text) + header_length) >= DISCORD_LIMIT:
                embed = discord.Embed(
                    description=text,
                    color=COLOR,
                    timestamp=discord_timestamp()
                )
                text = overflow_text
                overflow_text = ""
                embeds.append(embed)
            text = overflow_text
            i += 1
    else:
        for c, r, d in zip(confirmed, recovered, deaths):
            bold = "**" if i % 2 == 0 else ""
            total_cases = list(confirmed[c]["history"].values())[-1]
            try:
                total_recovered = list(recovered[r]["history"].values())[-1]
            except Exception as e:
                total_recovered = 0
            total_deaths = list(deaths[d]["history"].values())[-1]
            overflow_text += f"{bold}{c} : {total_cases:,} confirmed - {total_recovered:,} recovered - {total_deaths:,} deaths{bold}\n"
            if (len(overflow_text) + header_length) >= DISCORD_LIMIT:
                embed = discord.Embed(
                    description=text,
                    color=COLOR,
                    timestamp=discord_timestamp()
                )
                text = overflow_text
                overflow_text = ""
                embeds.append(embed)
            text = overflow_text
            i += 1
    if text:
        embed = discord.Embed(
            description=text,
            color=COLOR,
            timestamp=discord_timestamp()
        )

        embeds.append(embed)
    return embeds


def mkheader():
    header = "You can support me on <:kofi:693473314433138718>[Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot. <:github:693519776022003742> [Source code](https://github.com/takitsu21/covid-19-tracker), <:api:752610700177965146> [API](https://coronavirus.jessicoh.com/api/) the bot is using.\n\n"
    return header


def png_clean():
    for file in os.listdir("."):
        if file.endswith("png"):
            os.remove(file)


async def get(session: ClientSession, endpoint, **kwargs):
    url = API_ROOT + endpoint
    resp = await session.request(
        method="GET",
        url=url,
        headers={"Authorization": config("Authorization")},
        **kwargs
    )
    i = 0
    while resp.status == 503 and i < MAX_RETRIES:  # avoid cloudflare limit
        resp = await session.request(
            method="GET",
            url=url,
            headers={"Authorization": config("Authorization")},
            **kwargs
        )
        i += 1
        await asyncio.sleep(1)
    if resp.status not in range(200, 300):
        return resp.status
    data = await resp.json()
    return data


async def fetch(url: str, session: ClientSession, **kwargs):
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


async def _write(url: str, file: IO, session: ClientSession, **kwargs):
    try:
        fetcher = await fetch(url=url, session=session, **kwargs)
        with open(file, 'wb') as f:
            pickle.dump(fetcher, f, -1)
    except Exception as e:
        logger.exception(e, exc_info=True)
