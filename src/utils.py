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

from src.country_code import CD


URI_DATA      = config("uri_data")
DATA_PATH     = "data/datas.json"
CSV_DATA_PATH = "data/parsed_csv.json"
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


def csv_parse():
    dic = {}
    t, r, d = 0, 0, 0
    confirmed_data = data_reader(_CONFIRMED_PATH)
    recovered_data = data_reader(_RECOVERED_PATH)
    deaths_data = data_reader(_DEATH_PATH)
    lk = last_key(confirmed_data)
    for data in confirmed_data:
        i = 0
        current_country = data["Country/Region"]
        if current_country not in dic:
            dic[current_country] = {
                "confirmed": int(data[lk]),
                "recovered": 0,
                "deaths": 0
            }
        else:
            dic[current_country]["confirmed"] += int(data[lk])
        t += int(data[lk])

    for data in recovered_data:
        i = 0
        current_country = data["Country/Region"]
        dic[current_country]["recovered"] += int(data[lk])
        r += int(data[lk])

    for data in deaths_data:
        i = 0
        current_country = data["Country/Region"]
        dic[current_country]["deaths"] += int(data[lk])
        d += int(data[lk])

    dic["total"] = {
        "confirmed": t,
        "recovered": r,
        "deaths": d
    }

    with open(CSV_DATA_PATH, "w") as f:
        f.write(json.dumps(dic, indent=4))

def cache_data(uri: str) -> None:
    r = requests.get(URI_DATA, headers=USER_AGENT)
    if r.status_code >= 200 and r.status_code <= 299:
        with open(DATA_PATH, "w") as f:
            f.write("{}".format(json.dumps(parse_data(r.json()), indent=4)))
    else:
        raise requests.RequestException("Status code error : {}".format(r.status_code))

def from_json(fpath: str) -> dict:
    with open(fpath, "r") as f:
        jso = json.load(f)
    return jso

def parse_data(data: dict) -> dict:
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

def difference_on_update(old_data: dict, new_data: dict):
    old_c = old_data["total"]["confirmed"]
    old_r = old_data["total"]["recovered"]
    old_d = old_data["total"]["deaths"]
    new_c = new_data["total"]["confirmed"]
    new_r = new_data["total"]["recovered"]
    new_d = new_data["total"]["deaths"]
    return new_c - old_c, new_r - old_r, new_d - old_d

def is_countryCode(v: str) -> bool:
    return len(v) == 2 and CD.get(v.upper()) is not None

def special_case(country):
    spec = {
            "us": "United States",
            "uk": "United Kingdom"
    }
    country = country.lower()
    if country in spec:
        return spec[country.lower()]
    return ' '.join(x.capitalize() for x in country.split(' '))

def country_verifier(k: str, param: str) -> str:
    if is_countryCode(param) and param.lower() not in ("us", "uk"):
        return CD[param.upper()]
    elif k.lower().startswith(param.lower()):
        return k.lower()
    return ""

def diff_confirmed(csv: dict, k: str, v: dict, key_getter: str) -> int:
    if type(csv) == list:
        return v[key_getter]
    for c, val in csv.items():
        if c == k:
            return int(v[key_getter]) - int(val[key_getter])
    return v[key_getter]

def string_formatting(data_parsed: dict, param: list=[]) -> Tuple[str, str]:
    tot = data_parsed["total"]
    max_length = DISCORD_LIMIT - 80
    length = 0
    old_text = ""
    text = ""
    d = {}
    header = "Country `[current_update-morning_update]`\nConfirmed **{}** [+**{}**]\nRecovered **{}** ({}) [+**{}**]\nDeaths **{}** ({}) [+**{}**]\n"
    header_length = len(header)
    param_length = len(param)
    my_csv = from_json(CSV_DATA_PATH)
    if param_length:
        buffer = []
        for p in param:
            for k, v in data_parsed.items():
                country_v = country_verifier(k, p)
                if k not in buffer and k.lower() == country_v.lower():
                    text += f"**{special_case(country_v)}** : {v['confirmed']} confirmed [+**{diff_confirmed(my_csv, k, v, 'confirmed')}**], {v['recovered']} recovered [+**{diff_confirmed(my_csv, k, v, 'recovered')}**], {v['deaths']} deaths [+**{diff_confirmed(my_csv, k, v, 'deaths')}**]\n"
                    buffer.append(k)
                length = len(text) + header_length
            if length < max_length:
                old_text = text
    else:
        for k, v in data_parsed.items():

            text += f"**{special_case(k)}** {v['confirmed']} [+{diff_confirmed(my_csv, k, v, 'confirmed')}]\n"
            length = len(text) + header_length
            if length > max_length:
                break
            else:
                old_text = text

    if length >= max_length:
        text = old_text
    t, r, c = difference_on_update(my_csv, data_parsed)
    header = header.format(
        tot["confirmed"],
        t,
        tot["recovered"],
        percentage(tot["confirmed"], tot["recovered"]),
        r,
        tot["deaths"],
        percentage(tot["confirmed"], tot["deaths"]),
        c
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
    return "{:.2f}%".format(x * 100 / total) if total > 0 else 0

