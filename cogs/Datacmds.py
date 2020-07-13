import asyncio
import datetime as dt
import os
import time
import uuid

import discord
from discord.ext import commands
from pymysql.err import IntegrityError

import src.utils as utils
from src.database import db
from src.plotting import PlotEmpty, plot_csv, plot_graph


class Datacmds(commands.Cog):
    """Help commands"""
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
        text = ""
        i = 1
        for c in self.bot._data["sorted"]:
            if c["statistics"]["confirmed"] > 0:
                length = len(text + c["country"]["name"] + ", ")

                if length >= utils.DISCORD_LIMIT:
                    embed = discord.Embed(
                        description=text.rstrip(","),
                        color=utils.COLOR,
                        timestamp=utils.discord_timestamp()
                    )
                    embed.set_author(
                        name=f"All countries affected by Coronavirus COVID-19 - Page {i}",
                        icon_url=self.bot.author_thumb
                    )
                    i += 1
                    text = ""
                    embed.set_footer(text=utils.last_update(utils.DATA_PATH),
                            icon_url=ctx.me.avatar_url)
                    embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
                    await ctx.send(embed=embed)

                try:
                    text += c["country"]["name"] + ", "
                except:
                    pass

        if len(text):
            embed = discord.Embed(
                description=text.rstrip(","),
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
            embed.set_author(
                name=f"All countries affected by Coronavirus COVID-19 - Page {i}",
                icon_url=self.bot.author_thumb
            )
            embed.set_footer(text=utils.last_update(utils.DATA_PATH),
                            icon_url=ctx.me.avatar_url)
            embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
            await ctx.send(embed=embed)

    @commands.command(name="info")
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def info(self, ctx):
        DATA = self.bot._data

        header, text = utils.string_formatting(DATA)
        embed = discord.Embed(
            description=header + "\n\n" + text,
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )

        embed.set_author(
            name=f"All countries affected by Coronavirus COVID-19",
            url="https://www.who.int/home",
            icon_url=self.bot.author_thumb
            )
        embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
        if not os.path.exists(utils.STATS_PATH):
            await plot_csv(utils.STATS_PATH, self.bot._data)
        embed.set_footer(text=utils.last_update(utils.DATA_PATH),
                        icon_url=ctx.me.avatar_url)

        with open(utils.STATS_PATH, "rb") as p:
            img = discord.File(p, filename=utils.STATS_PATH)
        embed.set_image(url=f'attachment://{utils.STATS_PATH}')
        await ctx.send(file=img, embed=embed)

    @commands.command(name="country", aliases=["c"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def country(self, ctx, *country):
        if not len(country):
            embed = discord.Embed(
                    description="No args provided, I can't tell you which country/region is affected if you won't tell me everything!",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        else:

            header, text = utils.string_formatting(self.bot._data, country)
            embed = discord.Embed(
                description=header + "\n\n" + text,
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
            if not len(text):
                embed = discord.Embed(
                    description="Wrong country selected",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        embed.set_author(name="Country affected by COVID-19",
                        url="https://www.who.int/home",
                        icon_url=self.bot.author_thumb)
        embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="stats", aliases=["stat", "statistic", "s"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def stats(self, ctx, *country):
        is_log = False
        data = self.bot._data["total"]
        embed = discord.Embed(
                description="You can support me on <:kofi:693473314433138718>[Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot. <:github:693519776022003742> [Source code](https://github.com/takitsu21/covid-19-tracker)",
                timestamp=dt.datetime.utcnow(),
                color=utils.COLOR
                )
        embed.set_author(
            name="Coronavirus COVID-19 linear stats",
            icon_url=self.bot.author_thumb
            )
        embed.set_thumbnail(
            url=self.bot.thumb + str(time.time())
            )
        embed.add_field(
            name="<:confirmed:688686089548202004> Confirmed",
            value=f"{data['confirmed']:,}",
            )
        embed.add_field(
                name="<:recov:688686059567185940> Recovered",
                value=f"{data['recovered']:,} (**{utils.percentage(data['confirmed'], data['recovered'])}**)",
            )
        embed.add_field(
            name="<:_death:688686194917244928> Deaths",
            value=f"{data['deaths']:,} (**{utils.percentage(data['confirmed'], data['deaths'])}**)",
        )

        embed.add_field(
            name="<:_calendar:692860616930623698> Today confirmed",
            value=f"+{data['today']['confirmed']:,} (**{utils.percentage(data['confirmed'], data['today']['confirmed'])}**)"
        )
        embed.add_field(
            name="<:_calendar:692860616930623698> Today recovered",
            value=f"+{data['today']['recovered']:,} (**{utils.percentage(data['confirmed'], data['today']['recovered'])}**)"
        )
        embed.add_field(
            name="<:_calendar:692860616930623698> Today deaths",
            value=f"+{data['today']['deaths']:,} (**{utils.percentage(data['confirmed'], data['today']['deaths'])}**)"
        )
        embed.add_field(
                name="<:bed_hospital:692857285499682878> Active",
                value=f"{data['active']:,} (**{utils.percentage(data['confirmed'], data['active'])}**)"
            )
        splited = country

        if len(splited) == 1 and splited[0].lower() == "log":
            embed.set_author(
                name="Coronavirus COVID-19 logarithmic stats",
                icon_url=self.bot.author_thumb
            )
            is_log = True
            version = utils.STATS_LOG_PATH
        elif not len(country):
            version = utils.STATS_PATH
        else:
            try:


                if splited[0].lower() == "log":
                    is_log = True
                    graph_type = "Logarithmic"
                    joined = ' '.join(country[1:]).lower()
                    stats = utils._get_country(self.bot._data, joined)
                    version = stats["country"]["code"].lower() + utils.STATS_LOG_PATH

                else:
                    graph_type = "Linear"
                    joined = ' '.join(country).lower()
                    stats = utils._get_country(self.bot._data, joined)
                    version = stats["country"]["code"].lower() + utils.STATS_PATH
                if not os.path.exists(version):
                    await plot_csv(version, self.bot._data, country=joined, logarithmic=is_log)


                today = stats["today"]
                confirmed = stats["statistics"]["confirmed"]
                recovered = stats["statistics"]["recovered"]
                deaths = stats["statistics"]["deaths"]
                active = stats["statistics"]["active"]
                embed = discord.Embed(
                    description="You can support me on <:kofi:693473314433138718>[Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot. <:github:693519776022003742> [Source code](https://github.com/takitsu21/covid-19-tracker)",
                    timestamp=dt.datetime.utcnow(),
                    color=utils.COLOR
                )
                embed.set_author(
                    name=f"Coronavirus COVID-19 {graph_type} graph - {stats['country']['name']}",
                    icon_url=f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/png250px/{stats['country']['code'].lower()}.png"
                )
                embed.add_field(
                    name="<:confirmed:688686089548202004> Confirmed",
                    value=f"{confirmed:,}"
                )
                embed.add_field(
                    name="<:recov:688686059567185940> Recovered",
                    value=f"{recovered:,} (**{utils.percentage(confirmed, recovered)}**)"
                )
                embed.add_field(
                    name="<:_death:688686194917244928> Deaths",
                    value=f"{deaths:,} (**{utils.percentage(confirmed, deaths)}**)"
                )

                embed.add_field(
                    name="<:_calendar:692860616930623698> Today confirmed",
                    value=f"+{today['confirmed']:,} (**{utils.percentage(confirmed, today['confirmed'])}**)"
                )
                embed.add_field(
                    name="<:_calendar:692860616930623698> Today recovered",
                    value=f"+{today['recovered']} (**{utils.percentage(confirmed, today['recovered'])}**)"
                )
                embed.add_field(
                    name="<:_calendar:692860616930623698> Today deaths",
                    value=f"+{today['deaths']:,} (**{utils.percentage(confirmed, today['deaths'])}**)"
                )
                embed.add_field(
                    name="<:bed_hospital:692857285499682878> Active",
                    value=f"{stats['statistics']['active']:,} (**{utils.percentage(confirmed, stats['statistics']['active'])}**)"
                )

            except Exception as e:
                version = utils.STATS_PATH

        if not os.path.exists(version):
            await plot_csv(version, self.bot._data, logarithmic=is_log)
        embed.set_footer(
            text=utils.last_update(version),
            icon_url=ctx.me.avatar_url
            )

        with open(version, "rb") as p:
            img = discord.File(p, filename=version)

        try:
            embed.set_thumbnail(url=stats["country"]["map"])
        except:
            embed.set_thumbnail(url=self.bot.thumb + str(time.time()))


        embed.set_image(url=f'attachment://{version}')
        await ctx.send(file=img, embed=embed)

    @commands.command(name="graph", aliases=["g"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def graph(self, ctx, *args):
        #c!graph <proportion | ...> <confirmed/recovered/deaths/active> <top | country[]>

        # graph is going to be store in files with names:
        # es_it_gb_us-proportion-deaths.png
        # most-proportion-confirmed.png

        types = ['proportion']

        description = {
            'proportion': "This shows the **percentage of the population** who have confirmed/recovered/died/active."
        }

        img = None

        ## START WITH INPUT VALIDATION
        if len(args) < 3:
            embed = discord.Embed(
                    description=f"Not enough args provided, I can't tell you which country/region/graph type if you won't tell me everything!\n\n__Examples:__\n `{ctx.prefix}g proportion deaths gb us it de fr`\n`{ctx.prefix}g proportion confirmed top`",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
            embed.set_author(name=f"Coronavirus COVID-19 Graphs",
                        url="https://www.who.int/home",
                        icon_url=self.bot.author_thumb)
        else:
            # at least 2 arguments have been provided
            if args[0] not in types:
                # 1st argument is not an available graph type
                embed = discord.Embed(
                    description="Your first argument should tell me which kind of graph you would like to see. (proportion/[WIP])",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
            elif args[1] not in ['confirmed', 'recovered', 'deaths', 'active']:
                # 2nd argument is not an available measure
                embed = discord.Embed(
                    description="Your second argument should tell me which kind of measure you would like to graph. (confirmed/recovered/deaths/active)",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
            else:
                # 1st and 2nd arguments are all good
                if args[2] == "top":
                    # user has requested a graph with the most or lease countries for that type
                    stats = self.bot._data["sorted"]
                    pop = self.bot._populations

                    calculatedData = {}

                    # loop through all stats
                    for i in range(len(stats)):
                        if args[0] == "proportion":
                            if pop[stats[i]["country"]["name"]] == 0:
                                continue
                            # calculate current proportion and add to dictionary
                            calculatedData[stats[i]["country"]["code"]] = int(stats[i]['statistics'][args[1]]) / pop[stats[i]["country"]["name"]] * 100

                    # sort dictionary smallest to largest value
                    calculatedData = {k: v for k, v in sorted(calculatedData.items(), key=lambda item: item[1], reverse=True)}

                    # get history stats for first x countries in the dict
                    graph = []

                    count = 6
                    for c in calculatedData:
                        if count > 0:
                            check = utils._get_country(self.bot._data, c.lower())
                            if check:
                                graph.append(check)
                        else:
                            break
                        count -= 1
                    for i in range(len(graph)):
                        if (args[0] == "proportion"):
                            for j in graph[i]['history']:
                                graph[i]['history'][j][args[0]] = int(graph[i]['history'][j][args[1]]) / pop[graph[i]["country"]["name"]] * 100
                            graph[i]['statistics'][args[0]] = int(graph[i]['statistics'][args[1]]) / pop[graph[i]["country"]["name"]] * 100
                        else:
                            await ctx.send("Not yet implemented: cogs/Datacmds.py:383")

                    path = args[2] + "-" + args[0] + "-" + args[1] + "-" + utils.STATS_PATH

                    embed = discord.Embed(
                        description=f"Here is a graph of the **{args[0].capitalize()}** of **{args[1].capitalize()}** of COVID-19. " + description[args[0]],
                        timestamp=dt.datetime.utcnow(),
                        color=utils.COLOR
                    )

                    for c in graph:
                        embed.add_field(
                            name=c['country']['name'],
                            value=str(round(c['statistics'][args[0]], 5)) + "%"
                        )

                    if not os.path.exists(path):
                        await plot_graph(path, graph, args[0], args[1])

                    with open(path, "rb") as p:
                        img = discord.File(p, filename=path)

                    embed.set_image(url=f'attachment://{path}')

                else:
                    # presumably the user has entered one or more countries
                    pop = self.bot._populations
                    # check all countries are valid
                    stats = []
                    for c in args[2:]:
                        check = utils._get_country(self.bot._data, c.lower())
                        if check:
                            stats.append(check)

                    for i in range(len(stats)):
                        # calculate proportion and store
                        ##print(stats[i]['history'])
                        if (args[0] == "proportion"):
                            for j in stats[i]['history']:
                                stats[i]['history'][j][args[0]] = int(stats[i]['history'][j][args[1]]) / pop[stats[i]["country"]["name"]] * 100
                            stats[i]['statistics'][args[0]] = int(stats[i]['statistics'][args[1]]) / pop[stats[i]["country"]["name"]] * 100
                        else:
                            await ctx.send("Not yet implemented: cogs/Datacmds.py:410")

                    # sort the stats in order of highest proportion
                    n = len(stats)
                    swapped = True
                    while swapped:
                        swapped = False
                        for i in range(0, n-1):
                            if stats[i]['statistics'][args[0]] > stats[i+1]['statistics'][args[0]]:
                                swapped = True
                                temp = stats[i]
                                stats[i] = stats[i+1]
                                stats[i+1] = temp
                    n = n-1

                    stats.reverse()

                    embed = discord.Embed(
                        description=f"Here is a graph of the **{args[0].capitalize()}** of **{args[1].capitalize()}** of COVID-19. " + description[args[0]],
                        timestamp=dt.datetime.utcnow(),
                        color=utils.COLOR
                    )

                    # add field with the data
                    # also create file path for graph
                    path = ""
                    for c in stats:
                        embed.add_field(
                            name=c['country']['name'],
                            value=str(round(c['statistics'][args[0]], 5)) + "%"
                        )

                        path += f"{c['country']['code'].lower()}_"
                    path += f"{args[0]}-{args[1]}-{utils.STATS_PATH}"

                    if not os.path.exists(path):
                        await plot_graph(path, stats, args[0], args[1])

                    with open(path, "rb") as p:
                        img = discord.File(p, filename=path)

                    embed.set_image(url=f'attachment://{path}')



            embed.set_author(name=f"Coronavirus COVID-19 Graphs - {args[0].capitalize()} of {args[1].capitalize()}",
                        url="https://www.who.int/home",
                        icon_url=self.bot.author_thumb)
        embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.me.avatar_url
        )
        if img != None:
            await ctx.send(file=img, embed=embed)
        else:
            await ctx.send(embed=embed)

    @staticmethod
    def _get_idx(args, val):
        try:
            return args.index(val)
        except ValueError:
            return -1

    def _unpack_notif(self, args, val):
        try:
            idx = int(self._get_idx(args, val))
            interval_type = args[len(args)-1].lower()
            interval = int(args[idx+1])
            if idx != -1 and interval >= 1 and interval <= 24:
                country = " ".join(args[0:idx])
            else:
                interval = 1
                country = " ".join(args)
        except:
            interval = 1
            country = " ".join(args)

        return country.lower(), interval * self._convert_interval_type(interval_type), interval_type

    def _convert_interval_type(self, _type):
        try:
            return {
                "hours": 1,
                "days": 24,
                "weeks": 168,
                "hour": 1,
                "day": 24,
                "week": 168
            }[_type]
        except KeyError:
            return 1

    @commands.command(name="notification", aliases=["notif", "notifications"])
    @commands.has_permissions(administrator=True)
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def notification(self, ctx, *state):
        if len(state):
            country, interval, interval_type = self._unpack_notif(state, "every")
            try:
                if country == "all":
                    pass
                else:
                    stats = utils._get_country(self.bot._data, country)
                try:
                    db.insert_notif(str(ctx.guild.id), str(ctx.channel.id), country, interval)

                except IntegrityError:
                    db.update_notif(str(ctx.guild.id), str(ctx.channel.id), country, interval)
                finally:
                    if country != "all":
                        embed = discord.Embed(
                            description=f"You will receive a notification in this channel on data update. `{ctx.prefix}notififcation disable` to disable the notifications"
                        )
                        embed.set_author(
                            name="Notifications successfully enabled",
                            icon_url=stats['country']['flag']['png']['100px']
                        )
                        embed.add_field(
                            name="Country",
                            value=f"**{stats['country']['name']}**"
                        )
                        embed.add_field(
                            name="Next update",
                            value=f"**{interval//self._convert_interval_type(interval_type)} {interval_type}**"
                        )
                    elif country == "all":
                        embed = discord.Embed(
                            description=f"You will receive a notification in this channel on data update. `{ctx.prefix}notififcation disable` to disable the notifications"
                        )
                        embed.set_author(
                            name="Notifications successfully enabled",
                            icon_url=self.bot.author_thumb
                        )
                        embed.add_field(
                            name="Country",
                            value=f"**Total stats**"
                        )
                        embed.add_field(
                            name="Next update",
                            value=f"**{interval//self._convert_interval_type(interval_type)} {interval_type}**"
                        )
            except Exception as e:
                embed = discord.Embed(
                    title=f"{ctx.prefix}notification",
                    description=f"Make sure that you didn't have made any mistake, please retry\n`{ctx.prefix}notification <country | disable> [every NUMBER] [hours | days | weeks]`\n__Examples__ : `{ctx.prefix}notification usa every 3 hours` (send a message to the current channel every 3 hours about United States), `{ctx.prefix}notification united states every 1 day`, `{ctx.prefix}notification disable`"
                )

            if country == "disable":
                db.delete_notif(str(ctx.guild.id))
                embed = discord.Embed(
                    title="Notifications successfully disabled",
                    description="Notifications are now interrupted in this channel."
                )
        else:
            embed = discord.Embed(
                title=f"{ctx.prefix}notification",
                description=f"Make sure that you didn't have made any mistake, please retry\n`{ctx.prefix}notification <country | disable> [every NUMBER] [hours | days | weeks]`\n__Examples__ : `{ctx.prefix}notification usa every 3 hours` (send a message to the current channel every 3 hours about United States), `{ctx.prefix}notification united states every 1 day`, `{ctx.prefix}notification disable`"
            )

        embed.color = utils.COLOR
        embed.timestamp = utils.discord_timestamp()
        embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.me.avatar_url
        )
        await ctx.send(embed=embed)

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
                db.delete_tracker(str(ctx.author.id))
            except:
                pass
        else:
            header, text = utils.string_formatting(self.bot._data, country)
            embed = discord.Embed(
                description=header + "\n\n" + text,
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
            if len(text) > 0:
                try:
                    db.insert_tracker(str(ctx.author.id), str(ctx.guild.id), ' '.join(country))
                except IntegrityError:
                    db.update_tracker(str(ctx.author.id), ' '.join(country))

                embed.set_author(
                    name="Tracker has been set up! You can see your tracked list. Updates will be send in DM",
                    icon_url=self.bot.author_thumb
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
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="region", aliases=["r"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def region(self, ctx, *params):
        if len(params):
            country, state = utils.parse_state_input(*params)
            header, text = utils.region_format(self.bot._data, country, state)
            embed = discord.Embed(
                color=utils.COLOR,
                timestamp=dt.datetime.utcnow()
            )
            if len(text):
                embed.description = header + text
            else:
                try:
                    available_states = ""
                    for c in utils.get_states(self.bot._data, country):
                        available_states += c["name"] + "\n"
                    if len(available_states):
                        embed = discord.Embed(
                            description=f"**Here is a list of available province/state for this country:**\n{available_states}",
                            color=utils.COLOR,
                            timestamp=utils.discord_timestamp()
                        )
                    else:
                        embed = discord.Embed(
                            description=f"Wrong province/state or country, see `{ctx.prefix}help`.",
                            color=utils.COLOR,
                            timestamp=utils.discord_timestamp()
                        )
                except Exception as e:
                    embed = discord.Embed(
                        description=f"Wrong province/state or country, see `{ctx.prefix}help`.",
                        color=utils.COLOR,
                        timestamp=utils.discord_timestamp()
                    )
        else:
            embed = discord.Embed(
                description=f"Missing args, see `{ctx.prefix}help`.\nSupported countries (**try your region if it doesn't work that mean this region is not yet supported**).",
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
        embed.set_author(
            name="Coronavirus COVID-19 (State/Province)",
            icon_url=self.bot.author_thumb
        )

        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.me.avatar_url
        )
        try:
            embed.set_thumbnail(url=stats["country"]["map"])
        except:
            embed.set_thumbnail(url=self.bot.thumb + str(time.time()))
        try:
            await ctx.send(file=img, embed=embed)
        except:
            await ctx.send(embed=embed)

    @commands.command(name="continent")
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def continent(self, ctx, continent="", graph_type=""):
        embed = discord.Embed(
            description="You can support me on <:kofi:693473314433138718>[Kofi](https://ko-fi.com/takitsu) and vote on [top.gg](https://top.gg/bot/682946560417333283/vote) for the bot. <:github:693519776022003742> [Source code](https://github.com/takitsu21/covid-19-tracker)",
            timestamp=dt.datetime.utcnow(),
            color=utils.COLOR
        )
        if len(continent) and continent in self.continent_code:
            continent = continent.lower()
            data = utils.filter_continent(self.bot._data, continent)

            if graph_type == "log":
                graph_type = "logarihmic"
                is_log = True
                version = continent + utils.STATS_LOG_PATH
            else:
                graph_type = "linear"
                version = continent + utils.STATS_PATH
                is_log = False
            if not os.path.exists(version):
                await plot_csv(version, self.bot._data, continent=data, logarithmic=is_log)


            embed.set_author(
                name=f"Coronavirus COVID-19 {graph_type} stats | {continent.upper()}",
                icon_url=self.bot.author_thumb
            )
            embed.set_thumbnail(
                url=self.bot.thumb + str(time.time())
                )
            embed.add_field(
                name="<:confirmed:688686089548202004> Confirmed",
                value=f"{data['total']['confirmed']}",
                )
            embed.add_field(
                    name="<:recov:688686059567185940> Recovered",
                    value=f"{data['total']['recovered']} (**{utils.percentage(data['total']['confirmed'], data['total']['recovered'])}**)",
                )
            embed.add_field(
                name="<:_death:688686194917244928> Deaths",
                value=f"{data['total']['deaths']} (**{utils.percentage(data['total']['confirmed'], data['total']['deaths'])}**)",
            )

            embed.add_field(
                name="<:_calendar:692860616930623698> Today confirmed",
                value=f"+{data['today']['confirmed']} (**{utils.percentage(data['total']['confirmed'], data['today']['confirmed'])}**)"
            )
            embed.add_field(
                name="<:_calendar:692860616930623698> Today recovered",
                value=f"+{data['today']['recovered']} (**{utils.percentage(data['total']['confirmed'], data['today']['recovered'])}**)"
            )
            embed.add_field(
                name="<:_calendar:692860616930623698> Today deaths",
                value=f"+{data['today']['deaths']} (**{utils.percentage(data['total']['confirmed'], data['today']['deaths'])}**)"
            )
            embed.add_field(
                    name="<:bed_hospital:692857285499682878> Active",
                    value=f"{data['total']['active']} (**{utils.percentage(data['total']['confirmed'], data['total']['active'])}**)"
                )
            with open(version, "rb") as p:
                img = discord.File(p, filename=version)


        else:
            embed.set_author(
                name=f"Coronavirus COVID-19 available continent",
                icon_url=self.bot.author_thumb
            )
            text = '**' + ', '.join(self.continent_code).upper() + '**'
            embed.description = "\n\n" + text

        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.me.avatar_url
        )
        try:
            embed.set_image(url=f'attachment://{version}')
            await ctx.send(embed=embed, file=img)
        except:
            embed.set_image(url=self.bot.thumb + str(time.time()))
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Datacmds(bot))
