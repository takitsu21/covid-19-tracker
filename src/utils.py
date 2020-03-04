import csv
from typing import List, Dict, Tuple
import functools
from discord.ext import commands
import datetime as dt
import time
import os
import requests
from data.datas import DATA
from decouple import config


URI_DATA      = config("uri_data")
DATA_PATH     = "data/datas.py"
COLOR         = 0x5A12DF
DISCORD_LIMIT = 2 ** 11 # discord limit
USER_AGENT    = {'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/73.0'}


def cache_data(uri):
    r = requests.get(URI_DATA, headers=USER_AGENT)
    if r.status_code >= 200 and r.status_code <= 299:
        with open("data/datas.py", "w") as f:
            f.write("DATA = {}".format(parse_data(r.json())))

def parse_data(data):
    d = {}
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
    return d

def string_formatting(data_parsed: dict) -> Tuple[str, str]:
    total_confirmed = 0
    total_recovered = 0
    total_deaths = 0
    max_length = DISCORD_LIMIT - 50
    old_text = ""
    text = ""
    d = {}
    header = "Total confirmed **{}**\nTotal recovered **{}** ({})\nTotal deaths **{}** ({})"
    length = len(header)
    basic_length = 16
    for k, v in data_parsed.items():
        length += len(str(k)) + len(str(v['confirmed'])) + basic_length
        total_confirmed += v['confirmed']
        total_recovered += v['recovered']
        total_deaths += v['deaths']
        if length < max_length:
            text += f"**{k}** {v['confirmed']} Confirmed\n"
            old_text = text

    if length > max_length:
        text = old_text + "...Too many country to show"
    header = header.format(
        total_confirmed,
        total_recovered,
        percentage(total_confirmed, total_recovered),
        total_deaths,
        percentage(total_confirmed, total_deaths)
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
    last_csv_update = dt.datetime.utcfromtimestamp(os.path.getctime(fpath))
    return f"Last update {last_csv_update.month}-{last_csv_update.day}-{last_csv_update.year} {last_csv_update.hour:0<2}:{last_csv_update.minute} GMT"

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

if __name__ == "__main__":
    # print(DATA["objectIdFieldName"])
    # cache_data(URI_DATA)
    print(string_formatting(DATA))