import csv
from typing import List, Dict, Tuple
import functools
from discord.ext import commands
import datetime as dt
import time
import json
import os
import requests
from decouple import config


URI_DATA      = config("uri_data")
DATA_PATH     = "data/datas.json"
COLOR         = 0x5A12DF
DISCORD_LIMIT = 2 ** 11 # discord limit 2048
USER_AGENT    = {'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/73.0'}

_CONFIRMED_URI  = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
_DEATH_URI      = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
_RECOVERED_URI  = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"
_CONFIRMED_PATH = "data/time_series_19-covid-Confirmed.csv"
_DEATH_PATH     = "data/time_series_19-covid-Deaths.csv"
_RECOVERED_PATH = "data/time_series_19-covid-Recovered.csv"
DICT            = {
        _CONFIRMED_URI: _CONFIRMED_PATH,
        _DEATH_URI: _DEATH_PATH,
        _RECOVERED_URI: _RECOVERED_PATH
    }


def cache_data(uri: str) -> None:
    r = requests.get(URI_DATA, headers=USER_AGENT)
    if r.status_code >= 200 and r.status_code <= 299:
        with open(DATA_PATH, "w") as f:
            f.write("{}".format(json.dumps(parse_data(r.json()), indent=4)))
    else:
        raise requests.RequestException("Status code error : {}".format(r.status_code))

def from_json(fpath: str) -> dict:
    with open(DATA_PATH, "r") as f:
        jso = json.load(f)
    return jso


def parse_data(data):
    d = {}
    t_c = 0
    t_r = 0
    t_d = 0
    for iter in data["features"]:
        f = iter["attributes"]
        if f["Country_Region"] not in d:
            d[f["Country_Region"]] = {
                "confirmed": f["Confirmed"],
                "recovered": f["Recovered"],
                "deaths": f["Deaths"]
            }
        else:
            d[f["Country_Region"]]["confirmed"] += f["Confirmed"]
            d[f["Country_Region"]]["recovered"] += f["Recovered"]
            d[f["Country_Region"]]["deaths"] += f["Deaths"]
        t_c += f["Confirmed"]
        t_r += f["Recovered"]
        t_d += f["Deaths"]
    d["total"] = {
        "confirmed": t_c,
        "recovered": t_r,
        "deaths": t_d
    }
    return d

def difference_on_update(old_data, new_data):
    old_c = old_data["total"]["confirmed"]
    old_r = old_data["total"]["recovered"]
    old_d = old_data["total"]["deaths"]
    new_c = new_data["total"]["confirmed"]
    new_r = new_data["total"]["recovered"]
    new_d = new_data["total"]["deaths"]
    return new_c - old_c, new_r - old_r, new_d - old_d

def string_formatting(data_parsed: dict, param=[]) -> Tuple[str, str]:
    tot = data_parsed["total"]
    max_length = DISCORD_LIMIT - 80
    old_text = ""
    text = ""
    d = {}
    header = "Total confirmed **{}**\nTotal recovered **{}** ({})\nTotal deaths **{}** ({})\n"
    length = len(header)
    basic_length = 16 if not len(param) else 38
    param_length = len(param)
    for k, v in data_parsed.items():
        if param_length and True in [k.lower().startswith(z.lower()) for z in param]:
            text += f"**{k}** : {v['confirmed']} confirmed, {v['recovered']} recovered, {v['deaths']} deaths\n"
            length += len(str(k)) + len(str(v['confirmed'])) + basic_length
        elif not param_length:
            text += f"**{k}** {v['confirmed']} Confirmed\n"
            length += len(str(k)) + len(str(v['confirmed'])) + basic_length


        if length < max_length:
            old_text = text


    if length > max_length:
        text = old_text + "...Too many country to show"
    header = header.format(
        tot["confirmed"],
        tot["recovered"],
        percentage(tot["confirmed"], tot["recovered"]),
        tot["deaths"],
        percentage(tot["confirmed"], tot["deaths"])
    )
    return header, text

def trigger_typing(func):
    @functools.wraps(func)
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        await ctx.trigger_typing()
        return await func(self, ctx, *args, **kwargs)
    return wrapper

def data_reader(fpath: str) -> List[dict]:
    with open(fpath, "r") as f:
        cr = csv.DictReader(f.read().splitlines(), delimiter=',')
    return list(cr)

def discord_timestamp():
    return dt.datetime.utcfromtimestamp(time.time())

def last_key(csv_data: List[dict]) -> int:
    return list(csv_data[0].keys())[-1]

def last_update(fpath: str):
    lcu = dt.datetime.utcfromtimestamp(os.path.getctime(fpath))
    return f"Last update {lcu.strftime('%Y-%m-%d %H:%M:%S')} GMT"

def percentage(total, x):
    return "{:.2f}%".format(x * 100 / total)

# def format_csv(csv_confirmed, csv_recovered, csv_deaths) -> Dict[str, int]:
#     lk = last_key(csv_confirmed)
#     res = {}
#     total_confirmed = 0
#     total_deaths = 0
#     total_recovered = 0
#     for confirmed in csv_confirmed:
#         if confirmed["Country/Region"] not in res:
#             res[confirmed["Country/Region"]] = {}
#             res[confirmed["Country/Region"]]["confirmed"] = int(confirmed[lk])
#         else:
#             res[confirmed["Country/Region"]]["confirmed"] += int(confirmed[lk])
#         total_confirmed += int(confirmed[lk])

#     for recovered in csv_recovered:
#         if "recovered" not in res[recovered["Country/Region"]]:
#             res[recovered["Country/Region"]]["recovered"] = int(recovered[lk])
#         else:
#             res[recovered["Country/Region"]]["recovered"] += int(recovered[lk])
#         total_recovered += int(recovered[lk])

#     for deaths in csv_deaths:
#         if "deaths" not in res[deaths["Country/Region"]]:
#             res[deaths["Country/Region"]]["deaths"] = int(deaths[lk])
#         else:
#             res[deaths["Country/Region"]]["deaths"] += int(deaths[lk])
#         total_deaths += int(deaths[lk])

#     res["total"] = {
#         "total_confirmed": total_confirmed,
#         "total_recovered": total_recovered,
#         "total_deaths": total_deaths
#     }
#     return res

# def string_formatting(formatted_data: Dict[str, int], param=None) -> str:
#     total = formatted_data['total']
#     p_r = percentage(total['total_confirmed'], total['total_recovered'])
#     p_d = percentage(total['total_confirmed'], total['total_deaths'])
#     header = f"Total confirmed : **{total['total_confirmed']}**\nTotal recovered : **{total['total_recovered']}** ({p_r})\nTotal deaths : **{total['total_deaths']}** ({p_d})\n"
#     res = ""
#     del formatted_data["total"]
#     if param is not None:
#         for country, data in formatted_data.items():
#             if country.lower().startswith(param):
#                 res += f"**{country}** : {data['confirmed']} confirmed, {data['recovered']} recovered, {data['deaths']} deaths\n"
#     else:
#         for country, data in formatted_data.items():
#             res += f"**{country}** : {data['confirmed']} Confirmed\n"
#     return header, res

