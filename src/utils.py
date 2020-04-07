import csv
from typing import List, Dict, Tuple, IO
import functools
from discord.ext import commands
import datetime as dt
import time
import json
import os
import asyncio
from decouple import config
from aiohttp import ClientSession
import aiofiles
import discord


URI_DATA      = config("uri_data")
DATA_PATH     = "data/datas.json"
CSV_DATA_PATH = "data/parsed_csv.json"
NEWS_PATH     = "data/news.json"
BACKUP_PATH   = "backup/datas.json"

COLOR                    = 0xd6b360
DISCORD_LIMIT            = 2 ** 11 # 2048
MAX_SIZE_FIELD_VALUE     = 2 ** 10 # 1024
MAX_MAX_SIZE_FIELD_VALUE = 5000 # max embed size

USER_AGENT      = {'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/73.0'}
STATS_PATH      = "stats.png"
STATS_LOG_PATH  = "log_stats.png"


class CountryNotFound(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def get_region(country, region):
    data = from_json(DATA_PATH)
    is_code = True if len(country) == 2 else False
    for d in data["sorted"]:
        country_data = d["country"]["name"]
        code = d["country"]["code"]
        if country_data.lower() == country or code.lower() == country:
            for c in data["data"][code]["regions"]:
                if c['name'].lower() == region:
                    return c

    raise CountryNotFound(f"{region} not found for {country}")

def _get_country(data, country):
    for d in data["sorted"]:
        try:
            country_data = d["country"]["name"]
            code = d["country"]["code"]
            iso3 = d["country"]["iso3"]
        except:
            continue

        if country_data.lower() == country or code.lower() == country or iso3.lower() == country:
            return d
    raise CountryNotFound(f"{country} not found")

def matching_path(fpath: str):
    try:
        return fpath.split("-")[2].lower()[:-4]
    except:
        return fpath.split("_")[3].lower()

async def from_json(file: IO):
    async with aiofiles.open(file) as f:
        data = await f.read()
        return json.loads(data)

def string_formatting(data_parsed: dict, param: list=[]) -> Tuple[str, str]:
    tot = data_parsed["total"]
    max_length = DISCORD_LIMIT - 50
    length = 0
    old_text = ""
    text = ""
    d = {}
    truncated = ""
    header = mkheader(
        tot['confirmed'], tot["today"]["confirmed"],
        tot['recovered'], percentage(tot["confirmed"], tot["recovered"]),
        tot["today"]["recovered"], tot['deaths'], percentage(tot["confirmed"], tot["deaths"]), tot["today"]["deaths"], True
    )
    header_length = len(header)
    param_length = len(param)
    i = 0
    if param_length:
        check = []
        for p in param:
            p = p.lower()
            p_length = len(p)
            for k, v in data_parsed["data"].items():
                try:
                    country = v["country"]["name"] if v["country"]["name"] is not None else "Null"
                    code = v['country']['code'] if v["country"]["code"] is not None else "Null"
                    stats = v['statistics']
                    iso3 = v["country"]["iso3"]
                    if len(country) >= 15:
                        truncated = country[0:15] + "..."
                    else:
                        truncated = country
                    if country not in check:
                        if (p_length in range(2,4) and (p == code.lower()) or p == iso3.lower()) or (country.lower().startswith(p) and p_length not in range(2,4)):
                            if i % 2 == 0:
                                text += f"**{truncated} : {stats['confirmed']} <:confirmed:688686089548202004> [+{v['today']['confirmed']}], {stats['recovered']} cured [+{v['today']['recovered']}], {stats['deaths']} deaths [+{v['today']['deaths']}]**\n"
                            else:
                                text += f"{truncated} : {stats['confirmed']} <:confirmed:688686089548202004> [+{v['today']['confirmed']}], {stats['recovered']} cured [+{v['today']['recovered']}], {stats['deaths']} deaths [+{v['today']['deaths']}]\n"
                            check.append(country)
                            length = len(text) + header_length
                            i += 1
                except KeyError:
                    pass
            if length < max_length:
                old_text = text
    else:

        for v in data_parsed["sorted"]:
            try:
                confirmed = v['statistics']['confirmed']
                country = v['country']['name'] if v["country"]["name"] is not None else "Null"
                stats = v['statistics']
            except KeyError:
                continue

            if len(country) >= 15:
                truncated = country[0:15] + "..."
            else:
                truncated = country
            if stats['confirmed']:
                if i % 2 == 0:
                    text += f"**{truncated} : {confirmed} [+{v['today']['confirmed']}]**\n"
                else:
                    text += f"{truncated} : {confirmed} [+{v['today']['confirmed']}]\n"
                i += 1
                length = len(text) + header_length
            if length >= max_length:
                break
            else:
                old_text = text

    if length >= max_length:
        text = old_text
    return header, text

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

def last_update(fpath: str):
    lcu = dt.datetime.utcfromtimestamp(os.path.getctime(fpath))
    return f"Last update {lcu.strftime('%Y-%m-%d %H:%M:%S')} GMT +0000"

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

async def is_valid_json():
    try:
        j = await from_json(DATA_PATH)
        return True
    except:
        return False

def region_format(data, country, state):
    states = get_states(data, country)
    text = ""
    old_text = ""
    length = 0
    max_length = DISCORD_LIMIT- 50
    k = 0

    tot = data['total']
    header = mkheader(
        tot['confirmed'], tot["today"]["confirmed"],
        tot['recovered'], percentage(tot["confirmed"], tot["recovered"]),
        tot["today"]["recovered"], tot['deaths'], percentage(tot["confirmed"], tot["deaths"]), tot["today"]["deaths"], True
    )
    header_length = len(header)
    for s in states:
        state_name = s['name']
        statistics = s['statistics']
        if len(state_name) >= 15:
            state_name_trunc = state_name[0:15] + "..."
        else:
            state_name_trunc = state_name
        bold = "**" if k % 2 == 0 else ""

        if state == "all":
            text += f"{bold}{state_name_trunc} : {statistics['confirmed']} [+{s['today']['confirmed']}] confirmed - {statistics['recovered']} cured - {statistics['deaths']} deaths{bold}\n"
            k += 1

        elif state_name.lower() == state:
            text += f"{bold}{state_name_trunc} : {statistics['confirmed']} [+{s['today']['confirmed']}] confirmed - {statistics['recovered']} cured - {statistics['deaths']} deaths{bold}\n"
            k += 1
        length = len(text) + header_length
        if length >= max_length:
            break
        else:
            old_text = text
    if length >= max_length:
        text = old_text

    return header + "\n\n", text


def mkheader(confirmed, dfc, recov, dfr, pr, deaths, dfd, pd, is_on_mobile):
    header = "You can support me on <:kofi:693473314433138718>[Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot. <:github:693519776022003742> [Source code](https://github.com/takitsu21/covid-19-tracker)\n<:confirmed:688686089548202004> Confirmed **{}** [+**{}**]\n<:recov:688686059567185940> Recovered **{}** (**{}**) [+**{}**]\n<:_death:688686194917244928> Deaths **{}** (**{}**) [+**{}**]"
    return header.format(
        confirmed,
        dfc,
        recov,
        dfr,
        pr,
        deaths,
        dfd,
        pd
    )

def png_clean():
    for file in os.listdir("."):
        if file.endswith("png"):
            os.remove(file)

async def _from_json(fpath):
    async with aiofiles.open(fpath, "r") as f:
        jso = json.load(f)
    return jso

class UpdateHandler:
    def __init__(self, lang="en"):
        self.news_api_key = config("news_api")
        self.q = "coronavirus covid 19"
        self.lang = lang
        self.update_list = self.update_list()

    def update_list(self):
        return {
            f"http://newsapi.org/v2/top-headlines?apiKey={self.news_api_key}&language={self.lang}&q={self.q}": NEWS_PATH,
            config("uri_data"): DATA_PATH
        }

    async def fetch(self, url: str, session: ClientSession, **kwargs):
        resp = await session.request(
            method="GET",
            url=url,
            **kwargs
        )
        try:
            if resp.status >= 200 and resp.status <= 299:
                data = await resp.json()
            else:
                return None
        except Exception as e:
            return None
        return data

    async def parse(self, url: str, session: ClientSession, **kwargs):
        try:
            resp = await self.fetch(url=url, session=session, **kwargs)
            return json.dumps(resp)
        except Exception as e:
            return None

    async def store_as_backup(self, file: IO, old_data):
        async with aiofiles.open(file, "w+") as f:
            await f.write(old_data)

    async def _write(self, url:str, file: IO, session: ClientSession, **kwargs):
        try:
            to_write = await self.parse(url=url, session=session, **kwargs)
        except:
            return
        if to_write is None:
            return
        async with aiofiles.open(file, "w+") as f:
            await f.write(to_write)

    async def update(self, session: ClientSession, **kwargs):
        tasks = []
        for url, fpath in self.update_list.items():
            tasks.append(
                self._write(url=url, file=fpath, session=session, **kwargs)
            )
        await asyncio.gather(*tasks)