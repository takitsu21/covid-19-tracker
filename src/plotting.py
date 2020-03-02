from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import src.utils as utils


month = mdates.MonthLocator()
days = mdates.DayLocator()


class LengthError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def plot_csv():
    x_c, y_c = make_courbe(utils._CONFIRMED_PATH)
    x_r, y_r = make_courbe(utils._RECOVERED_PATH)
    x_d, y_d = make_courbe(utils._DEATH_PATH)
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(MultipleLocator(7))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.plot(x_c, y_c, "k.-")
    ax.plot(x_r, y_r, "g.-")
    ax.plot(x_d, y_d, "r.-")

    ticks = [i for i in range(len(y_c)) if i % 7 == 0]
    plt.xticks(ticks)
    plt.grid(True)
    plt.title("Coronavirus COVID-19 " + utils.last_update())
    plt.ylabel("Total confirmed cases")
    plt.xlabel("Timeline (MM/DD/YYYY)")
    plt.legend(["Total confirmed", "Total recovered", "Total deaths"])
    plt.savefig("data/stats.png")
    plt.show()

def make_courbe(fpath: str) -> Tuple[List, List]:
    datas = utils.data_reader(fpath)
    d = {}
    x = []
    y = []
    for data in datas:
        i = 0
        for k, v in data.items():
            if i > 3: # we are only interested by numbers
                if k not in d:
                    d[k] = int(v)
                else:
                    d[k] += int(v)
            i += 1
    for parse_k, parse_v in d.items():
        x.append(parse_k)
        y.append(parse_v)
    if len(x) == len(y):
        return x, y
    raise LengthError(f"x, y have a different length, x = {len(x)}, y = {len(y)}")


if __name__ == "__main__":
    plot_csv()
