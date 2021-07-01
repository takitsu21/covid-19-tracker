import datetime as dt
import logging
import os
import time
import traceback

import discord
import psutil
from discord.ext import commands
from pymysql.err import IntegrityError

import src.utils as utils
from src.commands import data
from src.plotting import plot_bar_daily, plot_csv

logger = logging.getLogger("covid-19")


class Statistics(commands.Cog):
    """Statistics Class commands"""
    __slots__ = ("bot", "continent_code")

    def __init__(self, bot):
        self.bot = bot
        self.continent_code = [
            "af",
            "as",
            "eu",
            "na",
            "oc",
            "sa"
        ]

    @commands.command(name="list")
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def list_countries(self, ctx):
        await data.list_countries_command(self.bot, ctx)

    @commands.command(name="info")
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def info(self, ctx):
        await data.info_command(self.bot, ctx)

    @commands.command(name="country", aliases=["c"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def country(self, ctx, *countries):
        # TODO: use (, *, countries) trick instead
        # also remind to fix the slash command
        await data.country_command(self.bot, ctx, *countries)


    @commands.command(name="stats", aliases=["stat", "statistic", "s"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def stats(self, ctx, *country):
        await data.stats_command(self.bot, ctx, country)


    # @commands.command(name="graph", aliases=["g"])
    # @commands.cooldown(3, 30, commands.BucketType.user)
    # async def graph(self, ctx, *args):
    #     embed = discord.Embed(
    #         title="API REWORK",
    #         description="This command is down for now, sorry (all the command left in c!help are still available)",
    #         color=utils.COLOR,
    #         timestamp=utils.discord_timestamp()
    #     )
    #     embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
    #     embed.set_footer(
    #         text="coronavirus.jessicoh.com/api/",
    #         icon_url=ctx.me.avatar_url
    #     )
    #     await ctx.send(embed=embed)

    #     #c!graph <proportion | ...> <confirmed/recovered/deaths/active> <top | country[]>

    #     # graph is going to be store in files with names:
    #     # es_it_gb_us-proportion-deaths.png
    #     # most-proportion-confirmed.png

    #     types = ['proportion']

    #     description = {
    #         'proportion': "This shows the **percentage of the population** who have confirmed/recovered/died/active."
    #     }

    #     img = None

    #     ## START WITH INPUT VALIDATION
    #     if len(args) < 3:
    #         embed = discord.Embed(
    #                 description=f"Not enough args provided, I can't tell you which country/region/graph type if you won't tell me everything!\n\n__Examples:__\n `{ctx.prefix}g proportion deaths gb us it de fr`\n`{ctx.prefix}g proportion confirmed top`",
    #                 color=utils.COLOR,
    #                 timestamp=utils.discord_timestamp()
    #             )
    #         embed.set_author(name=f"Coronavirus COVID-19 Graphs",
    #                     url="https://www.who.int/home",
    #                     icon_url=self.bot.author_thumb)
    #     else:
    #         # at least 2 arguments have been provided
    #         if args[0] not in types:
    #             # 1st argument is not an available graph type
    #             embed = discord.Embed(
    #                 description="Your first argument should tell me which kind of graph you would like to see. (proportion/[WIP])",
    #                 color=utils.COLOR,
    #                 timestamp=utils.discord_timestamp()
    #             )
    #         elif args[1] not in ['confirmed', 'recovered', 'deaths', 'active']:
    #             # 2nd argument is not an available measure
    #             embed = discord.Embed(
    #                 description="Your second argument should tell me which kind of measure you would like to graph. (confirmed/recovered/deaths/active)",
    #                 color=utils.COLOR,
    #                 timestamp=utils.discord_timestamp()
    #             )
    #         else:
    #             # 1st and 2nd arguments are all good
    #             if args[2] == "top":
    #                 # user has requested a graph with the most or lease countries for that type
    #                 stats = self.bot._data["sorted"]
    #                 pop = self.bot._populations

    #                 calculatedData = {}

    #                 # loop through all stats
    #                 for i in range(len(stats)):
    #                     if args[0] == "proportion":
    #                         if pop[stats[i]["country"]["name"]] == 0:
    #                             continue
    #                         # calculate current proportion and add to dictionary
    #                         calculatedData[stats[i]["country"]["code"]] = int(stats[i]['statistics'][args[1]]) / pop[stats[i]["country"]["name"]] * 100

    #                 # sort dictionary smallest to largest value
    #                 calculatedData = {k: v for k, v in sorted(calculatedData.items(), key=lambda item: item[1], reverse=True)}

    #                 # get history stats for first x countries in the dict
    #                 graph = []

    #                 count = 6
    #                 for c in calculatedData:
    #                     if count > 0:
    #                         check = utils._get_country(self.bot._data, c.lower())
    #                         if check:
    #                             graph.append(check)
    #                     else:
    #                         break
    #                     count -= 1
    #                 for i in range(len(graph)):
    #                     if (args[0] == "proportion"):
    #                         for j in graph[i]['history']:
    #                             graph[i]['history'][j][args[0]] = int(graph[i]['history'][j][args[1]]) / pop[graph[i]["country"]["name"]] * 100
    #                         graph[i]['statistics'][args[0]] = int(graph[i]['statistics'][args[1]]) / pop[graph[i]["country"]["name"]] * 100
    #                     else:
    #                         await ctx.send("Not yet implemented: cogs/Datacmds.py:383")

    #                 path = args[2] + "-" + args[0] + "-" + args[1] + "-" + utils.STATS_PATH

    #                 embed = discord.Embed(
    #                     description=f"Here is a graph of the **{args[0].capitalize()}** of **{args[1].capitalize()}** of COVID-19. " + description[args[0]],
    #                     timestamp=dt.datetime.utcnow(),
    #                     color=utils.COLOR
    #                 )

    #                 for c in graph:
    #                     embed.add_field(
    #                         name=c['country']['name'],
    #                         value=str(round(c['statistics'][args[0]], 5)) + "%"
    #                     )

    #                 if not os.path.exists(path):
    #                     await plot_graph(path, graph, args[0], args[1])

    #                 with open(path, "rb") as p:
    #                     img = discord.File(p, filename=path)

    #                 embed.set_image(url=f'attachment://{path}')

    #             else:
    #                 # presumably the user has entered one or more countries
    #                 pop = self.bot._populations
    #                 # check all countries are valid
    #                 stats = []
    #                 for c in args[2:]:
    #                     check = utils._get_country(self.bot._data, c.lower())
    #                     if check:
    #                         stats.append(check)

    #                 for i in range(len(stats)):
    #                     # calculate proportion and store
    #                     ##print(stats[i]['history'])
    #                     if (args[0] == "proportion"):
    #                         for j in stats[i]['history']:
    #                             stats[i]['history'][j][args[0]] = int(stats[i]['history'][j][args[1]]) / pop[stats[i]["country"]["name"]] * 100
    #                         stats[i]['statistics'][args[0]] = int(stats[i]['statistics'][args[1]]) / pop[stats[i]["country"]["name"]] * 100
    #                     else:
    #                         await ctx.send("Not yet implemented: cogs/Datacmds.py:410")

    #                 # sort the stats in order of highest proportion
    #                 n = len(stats)
    #                 swapped = True
    #                 while swapped:
    #                     swapped = False
    #                     for i in range(0, n-1):
    #                         if stats[i]['statistics'][args[0]] > stats[i+1]['statistics'][args[0]]:
    #                             swapped = True
    #                             temp = stats[i]
    #                             stats[i] = stats[i+1]
    #                             stats[i+1] = temp
    #                 n = n-1

    #                 stats.reverse()

    #                 embed = discord.Embed(
    #                     description=f"Here is a graph of the **{args[0].capitalize()}** of **{args[1].capitalize()}** of COVID-19. " + description[args[0]],
    #                     timestamp=dt.datetime.utcnow(),
    #                     color=utils.COLOR
    #                 )

    #                 # add field with the data
    #                 # also create file path for graph
    #                 path = ""
    #                 for c in stats:
    #                     embed.add_field(
    #                         name=c['country']['name'],
    #                         value=str(round(c['statistics'][args[0]], 5)) + "%"
    #                     )

    #                     path += f"{c['country']['code'].lower()}_"
    #                 path += f"{args[0]}-{args[1]}-{utils.STATS_PATH}"

    #                 if not os.path.exists(path):
    #                     await plot_graph(path, stats, args[0], args[1])

    #                 with open(path, "rb") as p:
    #                     img = discord.File(p, filename=path)

    #                 embed.set_image(url=f'attachment://{path}')

    #     embed.set_author(name=f"Coronavirus COVID-19 Graphs - {args[0].capitalize()} of {args[1].capitalize()}",
    #                 url="https://www.who.int/home",
    #                 icon_url=self.bot.author_thumb)
    # embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
    # embed.set_footer(
    #     text=utils.last_update(utils.DATA_PATH),
    #     icon_url=ctx.me.avatar_url
    # )
    # if img != None:
    #     await ctx.send(file=img, embed=embed)
    # else:
    #     await ctx.send(embed=embed)

    @commands.command(name="notification", aliases=["notif", "notifications"])
    @commands.has_permissions(administrator=True)
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def notification(self, ctx: commands.Context, *state):
        await data.notification_command(self.bot, ctx, state)

    @commands.command(name="track", aliases=["tracker"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def track(self, ctx, *country):
        await data.track_command(self.bot, ctx, country)

    @commands.command(name="region", aliases=["r"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def region(self, ctx, *params):
        await data.region_command(self.bot, ctx, params)

    @commands.command(aliases=["d"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def daily(self, ctx: commands.Context, *country):
        await data.daily_command(self.bot, ctx, *country)

    @commands.command()
    async def messages_stats(self, ctx):
        embed = discord.Embed(
            title="Some discord stats",
            timestamp=utils.discord_timestamp(),
            description=f"Since script start {self.bot.script_start_dt}"
        )
        embed.add_field(
            name="Message read",
            value=self.bot.msg_read
        )
        embed.add_field(
            name="Command used",
            value=self.bot.commands_used
        )
        embed.add_field(
            name="Memory usage",
            value=f"{psutil.virtual_memory().percent}%"
        )
        embed.add_field(
            name="CPU usage",
            value=f"{psutil.cpu_percent()}%"
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Statistics(bot))
