import csv
from typing import List, Dict
import functools
from discord.ext import commands
import datetime as dt
import time
import os


_CONFIRMED_URI = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
_DEATH_URI = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
_RECOVERED_URI = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"

_CONFIRMED_PATH = "data/time_series_19-covid-Confirmed.csv"
_DEATH_PATH = "data/time_series_19-covid-Deaths.csv"
_RECOVERED_PATH = "data/time_series_19-covid-Recovered.csv"

DICT = {
    _CONFIRMED_URI: _CONFIRMED_PATH,
    _DEATH_URI: _DEATH_PATH,
    _RECOVERED_URI: _RECOVERED_PATH
    }

COLOR = 0x5A12DF


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

def last_update():
    last_csv_update = dt.datetime.utcfromtimestamp(os.path.getctime(_CONFIRMED_PATH))
    return f"Last update {last_csv_update.month}-{last_csv_update.day}-{last_csv_update.year} {last_csv_update.hour:0<2}:{last_csv_update.minute:0<2} GMT"

def percentage(total, x):
    return "{:.2f}%".format(x * 100 / total)

def format_csv(csv_confirmed, csv_recovered, csv_deaths) -> Dict[str, int]:
    lk = last_key(csv_confirmed)
    res = {}
    total_confirmed = 0
    total_deaths = 0
    total_recovered = 0
    for confirmed in csv_confirmed:
        if confirmed["Country/Region"] not in res:
            res[confirmed["Country/Region"]] = {}
            res[confirmed["Country/Region"]]["confirmed"] = int(confirmed[lk])
        else:
            res[confirmed["Country/Region"]]["confirmed"] += int(confirmed[lk])
        total_confirmed += int(confirmed[lk])

    for recovered in csv_recovered:
        if "recovered" not in res[recovered["Country/Region"]]:
            res[recovered["Country/Region"]]["recovered"] = int(recovered[lk])
        else:
            res[recovered["Country/Region"]]["recovered"] += int(recovered[lk])
        total_recovered += int(recovered[lk])

    for deaths in csv_deaths:
        if "deaths" not in res[deaths["Country/Region"]]:
            res[deaths["Country/Region"]]["deaths"] = int(deaths[lk])
        else:
            res[deaths["Country/Region"]]["deaths"] += int(deaths[lk])
        total_deaths += int(deaths[lk])

    res["total"] = {
        "total_confirmed": total_confirmed,
        "total_recovered": total_recovered,
        "total_deaths": total_deaths
    }
    return res

def string_formatting(formatted_data: Dict[str, int], param=None) -> str:
    total = formatted_data['total']
    p_r = percentage(total['total_confirmed'], total['total_recovered'])
    p_d = percentage(total['total_confirmed'], total['total_deaths'])
    header = f"Total confirmed : **{total['total_confirmed']}**\nTotal recovered : **{total['total_recovered']}** ({p_r})\nTotal deaths : **{total['total_deaths']}** ({p_d})\n"
    res = ""
    del formatted_data["total"]
    if param is not None:
        for country, data in formatted_data.items():
            if country.lower().startswith(param):
                res += f"**{country}** : {data['confirmed']} confirmed, {data['recovered']} recovered, {data['deaths']} deaths\n"
    else:
        for country, data in formatted_data.items():
            res += f"**{country}** : {data['confirmed']} Confirmed\n"
    return header, res
