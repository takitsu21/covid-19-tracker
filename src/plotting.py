from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np
import datetime
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import src.utils as utils


month = mdates.MonthLocator()
days = mdates.DayLocator()


class LengthError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PlotEmpty(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def rearrange(timeline, confirmed, recovered, deaths, active):
    i = 0
    while confirmed[i] == 0:
        i += 1
    return timeline[i:], confirmed[i:], logarify(recovered[i:]), logarify(deaths[i:]), logarify(active[i:])

def logarify(y):
    for i in range(len(y)):
        if y[i] == 0:
            y[i] = 1
    return y

async def plot_csv(path, data, dark=True, logarithmic=False, country=None, region=None, continent=None):
    timeline, confirmed, recovered, deaths, active = await make_courbe(data, country, region, continent)
    fig, ax = plt.subplots()
    alpha = .2
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    if logarithmic:
        plt.yscale('log')

    ax.xaxis.set_major_locator(MultipleLocator(7))
    ax.plot(timeline, active, ".-", color="yellow", alpha=0.5)
    ax.plot(timeline, recovered, ".-", color="lightgreen")
    ax.plot(timeline, deaths, ".-", color="#e62712")
    ax.plot(timeline, confirmed, ".-", color="orange")

    # plt.fill_between(timeline, confirmed, recovered, color="orange", alpha=alpha)
    # plt.fill_between(timeline, recovered, deaths, color="lightgreen", alpha=alpha)
    # if not logarithmic:
    #     plt.fill_between(timeline, deaths, color="#e62712", alpha=alpha)

    ticks = [i for i in range(len(timeline)) if i % 15 == 0]
    plt.xticks(ticks, ha="center")
    ax.yaxis.grid(True)
    plt.ylabel("Total cases")
    plt.xlabel("Timeline (DD/MM)")

    if dark:
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        leg = plt.legend(["Actives", "Recovered", "Deaths", "Confirmed"], facecolor='0.1', loc="upper left")
        for text in leg.get_texts():
            text.set_color("white")

        if not logarithmic:
            ax.set_ylim(ymin=1)
        ylabs = []
        locs, _ = plt.yticks()

        if logarithmic:
            locs = list(map(lambda x: x * 100, locs[:-1]))
        for iter_loc in locs:
            ylabs.append(utils.human_format(int(iter_loc)))

        plt.yticks(locs, ylabs)
        plt.savefig(path, transparent=True)

    plt.close(fig)

async def make_courbe(data, country=None, region=None, continent=None) -> Tuple[List, List]:
    timeline = []
    confirmed = []
    recovered = []
    deaths = []
    active = []
    code_found = ""
    if continent is not None:
        for c in continent["data"]:
            timeline.append(c[:-3])
            confirmed.append(continent["data"][c]["confirmed"])
            recovered.append(continent["data"][c]["recovered"])
            deaths.append(continent["data"][c]["deaths"])
            active.append(continent["data"][c]["active"])

    elif country is None:
        for d in data["total"]["history"]:
            timeline.append(d[:-3])
            confirmed.append(data["total"]["history"][d]["confirmed"])
            recovered.append(data["total"]["history"][d]["recovered"])
            deaths.append(data["total"]["history"][d]["deaths"])
            active.append(data["total"]["history"][d]["active"])

    elif isinstance(region, dict):
        for h in region:
            timeline.append(h[:-3])
            confirmed.append(region[h]["confirmed"])
            recovered.append(region[h]["recovered"])
            deaths.append(region[h]["deaths"])
            active.append(region[h]["active"])
    else:

        for d in data["sorted"]:
            try:
                country_name = d["country"]["name"]
                code = d["country"]["code"]
                iso3 = d["country"]["iso3"]
            except:
                continue

            if country == country_name.lower() or code.lower() == country or iso3.lower() == country:
                for c in d["history"]:
                    timeline.append(c[:-3])
                    confirmed.append(d["history"][c]["confirmed"])
                    recovered.append(d["history"][c]["recovered"])
                    deaths.append(d["history"][c]["deaths"])
                    active.append(d["history"][c]["active"])
                break

    if not len(timeline):
        raise PlotEmpty(f"Plot empty, length : {len(timeline)}")

    return rearrange(timeline, confirmed, recovered, deaths, active)
