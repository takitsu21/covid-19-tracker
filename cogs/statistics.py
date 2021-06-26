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
from src.plotting import plot_bar_daily, plot_csv
from src.commands import data


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
    async def notification(self, ctx, *state):
        await data.notification_command(self.bot, ctx, state)

    @commands.command(name="track", aliases=["tracker"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def track(self, ctx, *country):
        if not len(country):
            embed = discord.Embed(
                description=f"No country provided. **`{ctx.prefix}track <COUNTRY>`** work like **`{ctx.prefix}country <COUNTRY>`** see `{ctx.prefix}help`",
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
            embed.set_author(
                name=f"{ctx.prefix}track",
                icon_url=self.bot.author_thumb
            )
        elif ''.join(country) == "disable":
            embed = discord.Embed(
                description=f"If you want to reactivate the tracker : **`{ctx.prefix}track <COUNTRY>`**",
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
            embed.set_author(
                name="Tracker has been disabled!",
                icon_url=self.bot.author_thumb
            )
            try:
                await self.bot.delete_tracker(str(ctx.author.id))
            except:
                pass
        else:

            all_data = await utils.get(self.bot.http_session, "/all/")
            country = ' '.join(country)
            data = utils.get_country(all_data, country)
            if data is not None:
                try:
                    await self.bot.insert_tracker(str(ctx.author.id), str(ctx.guild.id), country)
                except IntegrityError:
                    await self.bot.update_tracker(str(ctx.author.id), country)
                embed = discord.Embed(
                    description=f"{utils.mkheader()}You will receive stats about {data['country']} in DM",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
                embed.set_author(
                    name="Tracker has been set up!",
                    icon_url=f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/png250px/{data['iso2'].lower()}.png"
                )
            else:
                embed = discord.Embed(
                    description="Wrong country selected.",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
                embed.set_author(
                    name=f"{ctx.prefix}track",
                    icon_url=self.bot.author_thumb
                )
        embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
        embed.set_footer(
            text="coronavirus.jessicoh.com/api/",
            icon_url=ctx.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="region", aliases=["r"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def region(self, ctx, *params):
        if len(params):
            country, state = utils.parse_state_input(*params)
            try:
                if state == "all":
                    history_confirmed = await utils.get(self.bot.http_session, f"/history/confirmed/{country}/regions")
                    history_recovered = await utils.get(self.bot.http_session, f"/history/recovered/{country}/regions")
                    history_deaths = await utils.get(self.bot.http_session, f"/history/deaths/{country}/regions")
                    embeds = utils.region_format(
                        history_confirmed, history_recovered, history_deaths)
                    for i, _embed in enumerate(embeds):
                        _embed.set_author(
                            name=f"All regions in {country}",
                            icon_url=self.bot.author_thumb
                        )
                        _embed.set_footer(
                            text=f"coronavirus.jessicoh.com/api/ | Page {i + 1}",
                            icon_url=ctx.me.avatar_url)
                        _embed.set_thumbnail(
                            url=self.bot.thumb + str(time.time()))
                        await ctx.send(embed=_embed)
                    return
                else:
                    path = state.lower().replace(" ", "_") + utils.STATS_PATH
                    history_confirmed = await utils.get(self.bot.http_session, f"/history/confirmed/{country}/{state}")
                    history_recovered = await utils.get(self.bot.http_session, f"/history/recovered/{country}/{state}")
                    history_deaths = await utils.get(self.bot.http_session, f"/history/deaths/{country}/{state}")
                    confirmed = list(history_confirmed["history"].values())[-1]
                    deaths = list(history_deaths["history"].values())[-1]

                    try:
                        is_us = False
                        recovered = list(
                            history_recovered["history"].values())[-1]
                        active = confirmed - (recovered + deaths)
                    except:
                        is_us = True
                        recovered = 0
                        active = 0

                    if not os.path.exists(path):
                        await plot_csv(
                            path,
                            history_confirmed,
                            history_recovered,
                            history_deaths,
                            is_us=is_us)

                    embed = discord.Embed(
                        description=utils.mkheader(),
                        timestamp=dt.datetime.utcnow(),
                        color=utils.COLOR
                    )
                    embed.set_author(
                        name=f"Coronavirus COVID-19 - {state.capitalize()}",
                        icon_url=self.bot.author_thumb
                    )
                    embed.add_field(
                        name="<:confirmed:688686089548202004> Confirmed",
                        value=f"{confirmed:,}"
                    )
                    embed.add_field(
                        name="<:_death:688686194917244928> Deaths",
                        value=f"{deaths:,} (**{utils.percentage(confirmed, deaths)}**)"
                    )
                    if recovered:
                        embed.add_field(
                            name="<:recov:688686059567185940> Recovered",
                            value=f"{recovered:,} (**{utils.percentage(confirmed, recovered)}**)"
                        )
                        embed.add_field(
                            name="<:bed_hospital:692857285499682878> Active",
                            value=f"{active:,} (**{utils.percentage(confirmed, active)}**)"
                        )

            except Exception as e:
                logger.exception(e, exc_info=True)
                raise utils.RegionNotFound(
                    "Region not found, it might be possible that the region isn't yet available in the data.")
        else:
            return await ctx.send("No arguments provided.")

        with open(path, "rb") as p:
            img = discord.File(p, filename=path)

        embed.set_footer(
            text=f"coronavirus.jessicoh.com/api/ | {list(history_confirmed['history'].keys())[-1]}",
            icon_url=ctx.me.avatar_url
        )
        embed.set_thumbnail(
            url=self.bot.thumb + str(time.time())
        )
        embed.set_image(url=f'attachment://{path}')
        await ctx.send(file=img, embed=embed)

    @commands.command(name="continent")
    # @commands.cooldown(3, 30, commands.BucketType.user)
    async def continent(self, ctx, continent="", graph_type=""):
        embed = discord.Embed(
            title="API REWORK",
            description="This command is down for now, sorry (all the command left in c!help are still available)",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
        embed.set_footer(
            text="coronavirus.jessicoh.com/api/",
            icon_url=ctx.me.avatar_url
        )
        await ctx.send(embed=embed)

    #     embed = discord.Embed(
    #         description="You can support me on <:kofi:693473314433138718>[Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot. <:github:693519776022003742> [Source code](https://github.com/takitsu21/covid-19-tracker)",
    #         timestamp=dt.datetime.utcnow(),
    #         color=utils.COLOR
    #     )
    #     if len(continent) and continent in self.continent_code:
    #         continent = continent.lower()
    #         data = utils.filter_continent(self.bot._data, continent)

    #         if graph_type == "log":
    #             graph_type = "logarihmic"
    #             is_log = True
    #             path = continent + utils.STATS_LOG_PATH
    #         else:
    #             graph_type = "linear"
    #             path = continent + utils.STATS_PATH
    #             is_log = False
    #         if not os.path.exists(path):
    #             history_confirmed = await utils.get(self.bot.http_session, f"/history/confirmed/{joined}")
    #             history_recovered = await utils.get(self.bot.http_session, f"/history/recovered/{joined}")
    #             history_deaths = await utils.get(self.bot.http_session, f"/history/deaths/{joined}")
    #             await plot_csv(
    #                 path,
    #                 history_confirmed,
    #                 history_recovered,
    #                 history_deaths,
    #                 logarithmic=is_log)

    #         embed.set_author(
    #             name=f"Coronavirus COVID-19 {graph_type} stats | {continent.upper()}",
    #             icon_url=self.bot.author_thumb
    #         )
    #         embed.set_thumbnail(
    #             url=self.bot.thumb + str(time.time())
    #             )
    #         embed.add_field(
    #             name="<:confirmed:688686089548202004> Confirmed",
    #             value=f"{data['total']['confirmed']}",
    #             )
    #         embed.add_field(
    #                 name="<:recov:688686059567185940> Recovered",
    #                 value=f"{data['total']['recovered']} (**{utils.percentage(data['total']['confirmed'], data['total']['recovered'])}**)",
    #             )
    #         embed.add_field(
    #             name="<:_death:688686194917244928> Deaths",
    #             value=f"{data['total']['deaths']} (**{utils.percentage(data['total']['confirmed'], data['total']['deaths'])}**)",
    #         )

    #         embed.add_field(
    #             name="<:_calendar:692860616930623698> Today confirmed",
    #             value=f"+{data['today']['confirmed']} (**{utils.percentage(data['total']['confirmed'], data['today']['confirmed'])}**)"
    #         )
    #         embed.add_field(
    #             name="<:_calendar:692860616930623698> Today recovered",
    #             value=f"+{data['today']['recovered']} (**{utils.percentage(data['total']['confirmed'], data['today']['recovered'])}**)"
    #         )
    #         embed.add_field(
    #             name="<:_calendar:692860616930623698> Today deaths",
    #             value=f"+{data['today']['deaths']} (**{utils.percentage(data['total']['confirmed'], data['today']['deaths'])}**)"
    #         )
    #         embed.add_field(
    #                 name="<:bed_hospital:692857285499682878> Active",
    #                 value=f"{data['total']['active']} (**{utils.percentage(data['total']['confirmed'], data['total']['active'])}**)"
    #             )
    #         with open(path, "rb") as p:
    #             img = discord.File(p, filename=path)

    #     else:
    #         embed.set_author(
    #             name=f"Coronavirus COVID-19 available continent",
    #             icon_url=self.bot.author_thumb
    #         )
    #         text = '**' + ', '.join(self.continent_code).upper() + '**'
    #         embed.description = "\n\n" + text

    #     embed.set_footer(
    #         text=utils.last_update(utils.DATA_PATH),
    #         icon_url=ctx.me.avatar_url
    #     )
    #     try:
    #         embed.set_image(url=f'attachment://{path}')
    #         await ctx.send(embed=embed, file=img)
    #     except:
    #         embed.set_image(url=self.bot.thumb + str(time.time()))
    #         await ctx.send(embed=embed)

    @commands.command(aliases=["d"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def daily(self, ctx: commands.Context, *country):
        embed = discord.Embed(
            description=utils.mkheader(),
            timestamp=dt.datetime.utcnow(),
            color=utils.COLOR
        )
        try:
            if country:
                data_confirmed = await utils.get(self.bot.http_session, f"/daily/confirmed/{' '.join(country).lower()}")
                data_recovered = await utils.get(self.bot.http_session, f"/daily/recovered/{' '.join(country).lower()}")
                data_deaths = await utils.get(self.bot.http_session, f"/daily/deaths/{' '.join(country).lower()}")
                path = data_confirmed["iso2"] + "daily.png"
                embed.set_author(
                    name=f"Coronavirus COVID-19 Daily cases graph - {data_confirmed['name']}",
                    icon_url=f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/png250px/{data_confirmed['iso2'].lower()}.png"
                )

            else:
                data_confirmed = await utils.get(self.bot.http_session, f"/daily/confirmed/total")
                data_recovered = await utils.get(self.bot.http_session, f"/daily/recovered/total")
                data_deaths = await utils.get(self.bot.http_session, f"/daily/deaths/total")
                path = "daily_world.png"
                embed.set_author(
                    name=f"Coronavirus COVID-19 Daily cases graph - World",
                    icon_url=self.bot.author_thumb
                )

            if not os.path.exists(path):
                await plot_bar_daily(path, data_confirmed, data_recovered, data_deaths)

        except Exception as e:
            traceback.print_exc()
            return await ctx.send("Please provide a valid country.")
        embed.add_field(
            name="<:confirmed:688686089548202004> Recent confirmed",
            value=f"{list(data_confirmed['daily'].keys())[-1]} : {list(data_confirmed['daily'].values())[-1]:,}"
        )
        embed.add_field(
            name="<:recov:688686059567185940> Recent recovered",
            value=f"{list(data_recovered['daily'].keys())[-1]} : {list(data_recovered['daily'].values())[-1]:,}"
        )
        embed.add_field(
            name="<:_death:688686194917244928> Recent deaths",
            value=f"{list(data_deaths['daily'].keys())[-1]} : {list(data_deaths['daily'].values())[-1]:,}",
            inline=False
        )
        embed.set_thumbnail(
            url=self.bot.thumb + str(time.time())
        )
        with open(path, "rb") as p:
            img = discord.File(p, filename=path)
        embed.set_image(url=f'attachment://{path}')
        embed.set_footer(
            text="coronavirus.jessicoh.com/api/",
            icon_url=ctx.me.avatar_url
        )
        await ctx.send(file=img, embed=embed)

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
