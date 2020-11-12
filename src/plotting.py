from typing import List, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter, MultipleLocator

month = mdates.MonthLocator()
days = mdates.DayLocator()


class LengthError(Exception):
    pass


class PlotEmpty(Exception):
    pass


async def plot_csv(path,
    total_confirmed,
    total_recovered,
    total_deaths,
    logarithmic=False,
    is_us=False,
    is_daily=False):
    timeline, confirmed, recovered, deaths, active = await make_courbe(
        total_confirmed,
        total_recovered,
        total_deaths, is_us=is_us)
    alpha = .2
    fig, ax = plt.subplots()
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    if logarithmic:
        plt.yscale('log')

    ax.xaxis.set_major_locator(MultipleLocator(7))
    ax.plot(timeline, deaths, "-", color="#e62712")
    ax.plot(timeline, confirmed, "-", color="orange")
    if not is_us:
        ax.plot(timeline, active, "-", color="yellow", alpha=0.5)
        ax.plot(timeline, recovered, "-", color="lightgreen")
        leg = plt.legend(["Deaths", "Confirmed", "Active", "Recovered"], facecolor='0.1', loc="upper left")
    else:
        leg = plt.legend(["Deaths", "Confirmed"], facecolor='0.1', loc="upper left")

    for text in leg.get_texts():
        text.set_color("white")
    ticks = [i for i in range(len(timeline)) if i % 30 == 0]
    plt.xticks(ticks, ha="center")
    ax.yaxis.grid(True)
    plt.ylabel("Data")
    plt.xlabel("Timeline (mm/dd)")

    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')



    if not logarithmic:
        ax.set_ylim(ymin=1)
    locs, _ = plt.yticks()


    if logarithmic:
        locs = list(map(lambda x: x * 100, locs[:-1]))
    formatter = EngFormatter(locs)

    plt.yticks(locs, [formatter.format_eng(int(iter_loc)) for iter_loc in locs])
    plt.savefig(path, transparent=True)

    plt.close('all')

async def make_courbe(
    total_confirmed,
    total_recovered,
    total_deaths,
    is_us=False) -> Tuple[List, List]:

    timeline = list(x[:-3] for x in total_confirmed["history"].keys())
    confirmed = []
    recovered = []
    deaths = []
    active = []

    if not is_us:
        for c, r, d in zip(total_confirmed["history"],
                            total_recovered["history"],
                            total_deaths["history"]):
            try:
                confirmed.append(total_confirmed["history"][c])
                recovered.append(total_recovered["history"][r])
                deaths.append(total_deaths["history"][d])
                active.append(total_confirmed["history"][c] - total_recovered["history"][r])
            except TypeError:
                pass
    else:
        for c, d in zip(total_confirmed["history"],
                            total_deaths["history"]):
            try:
                confirmed.append(total_confirmed["history"][c])
                deaths.append(total_deaths["history"][d])
            except TypeError:
                pass

    timeline = timeline[0:len(confirmed)]
    return timeline, confirmed, recovered, deaths, active

def make_daily_courbe(data_confirmed, data_recovered, data_death):
    timeline, confirmed, recovered, deaths = [], [], [], []
    for c, r, d in zip(data_confirmed['daily'], data_recovered['daily'], data_death['daily']):
        timeline.append(c[:-3])
        confirmed.append(data_confirmed['daily'][c] if data_confirmed['daily'][c] >= 0 else 0)
        recovered.append(data_recovered['daily'][r] if data_recovered['daily'][r] >= 0 else 0)
        deaths.append(data_death['daily'][d] if data_death['daily'][d] >= 0 else 0)
    return timeline, confirmed, recovered, deaths


async def plot_bar_daily(path, confirmed, recovered, deaths):
    timeline, confirmed, recovered, deaths = make_daily_courbe(confirmed, recovered, deaths)
    ticks = [i for i in range(len(timeline)) if i % 30 == 0]
    legs = []

    ax1 = plt.subplot(3, 1, 1)
    ax1.xaxis.label.set_color('white')
    ax1.yaxis.label.set_color('white')

    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.axes.get_xaxis().set_visible(False)
    plt.xticks(ticks, ha="center")
    labels = ["Confirmed"]
    handles = [plt.Rectangle((0,0),1,1, color="orange") for label in labels]
    legs.append(plt.legend(handles, labels, facecolor='0.1', loc="upper left", prop={"size": 8}))
    ax1.bar(timeline, confirmed, color="orange")
    locs, _ = plt.yticks()
    formatter = EngFormatter(locs)
    plt.yticks(locs, [formatter.format_eng(int(iter_loc)) for iter_loc in locs])

    ax2 = plt.subplot(3, 1, 2)
    ax2.xaxis.label.set_color('white')
    ax2.yaxis.label.set_color('white')
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')
    plt.xticks(ticks, ha="center")
    labels = ["Recovered"]
    handles = [plt.Rectangle((0,0),1,1, color="lightgreen") for label in labels]
    legs.append(plt.legend(handles, labels, facecolor='0.1', loc="upper left", prop={"size": 8}))
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.axes.get_xaxis().set_visible(False)
    ax2.bar(timeline, recovered, color="lightgreen")
    locs, _ = plt.yticks()
    formatter = EngFormatter(locs)
    plt.yticks(locs, [formatter.format_eng(int(iter_loc)) for iter_loc in locs])

    ax3 = plt.subplot(3, 1, 3)
    ax3.xaxis.label.set_color('white')
    ax3.yaxis.label.set_color('white')
    ax3.tick_params(axis='x', colors='white')
    ax3.tick_params(axis='y', colors='white')
    plt.xticks(ticks, ha="center")
    labels = ["Deaths"]
    handles = [plt.Rectangle((0, 0), 1, 1, color="#e62712") for label in labels]
    legs.append(plt.legend(handles, labels, facecolor='0.1', loc="upper left", prop={"size": 8}))
    ax3.spines['bottom'].set_visible(False)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    ax3.bar(timeline, deaths, color="#e62712")
    locs, _ = plt.yticks()
    formatter = EngFormatter(locs)
    plt.yticks(locs, [formatter.format_eng(int(iter_loc)) for iter_loc in locs])
    plt.xlabel("Timeline (mm/dd)")
    for leg in legs:
        for text in leg.get_texts():
            text.set_color("white")
    plt.savefig(path, transparent=True)
    plt.close('all')

# function to plot data from the c!graph command
async def plot_graph(path, data, value, measure, dark=True):
    # value is the name of the value to be graphed

    # the number of days to graph
    max_days_back = 76

    days_back = 10000
    shortest = {}
    timeline = []
    for c in data:
        l = len(c['history'])
        if l < days_back:
            days_back = l
            shortest = c['history']
    for s in shortest:
        timeline.append(s[:-3])

    if days_back > max_days_back:
        days_back = max_days_back

    timeline = timeline[-days_back:]

    # get yvalue data from data
    yvalues = []
    for c in data:
        p = []
        for d in c['history']:
            p.append(c['history'][d]['proportion'])
        yvalues.append(p[-days_back:])

    fig, ax = plt.subplots()
    alpha = .2
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.xaxis.set_major_locator(MultipleLocator(7))
    # plot lines
    # TODO: implement all countries
    for c in range(len(yvalues)):
        ax.plot(timeline, yvalues[c], ".-", alpha=0.5)

    ticks = [i for i in range(len(timeline)) if i % int(days_back / 5) == 0]
    plt.xticks(ticks, ha="center")
    ax.yaxis.grid(True)
    plt.ylabel(f"{value.capitalize()} of {measure.capitalize()} (%)")
    plt.xlabel("Timeline (DD/MM)")

    if dark:
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        leg = plt.legend([name['country']['name'] for name in data ], facecolor='0.1', loc="upper left")
        for text in leg.get_texts():
            text.set_color("white")

        plt.savefig(path, transparent=True)

    plt.close(fig)
