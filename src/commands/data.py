import datetime as dt
import logging
import os
import time
from typing import Union

import discord
from discord.ext import commands
from discord_slash.context import SlashContext
from aiomysql import IntegrityError
import src.utils as utils
from src.plotting import plot_bar_daily, plot_csv

logger = logging.getLogger("covid-19")


async def list_countries_command(bot, ctx: Union[commands.Context, SlashContext]):
    text = ""
    i = 1
    data = await utils.get(bot.http_session, "/all")
    text = ""
    overflow_text = ""
    embeds = []
    for c in data:
        overflow_text += c["country"] + ", "
        if len(overflow_text) >= utils.DISCORD_LIMIT:
            embed = discord.Embed(
                description=text.rstrip(", "),
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
            text = overflow_text
            overflow_text = ""
            embeds.append(embed)
        text = overflow_text

    if text:
        embed = discord.Embed(
            description=text.rstrip(", "),
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )

        embeds.append(embed)

    for i, _embed in enumerate(embeds):
        _embed.set_author(
            name=f"All countries affected by Coronavirus COVID-19 - Page {i + 1}",
            icon_url=bot.author_thumb
        )
        _embed.set_footer(text=utils.last_update(data[0]["lastUpdate"]),
                          icon_url=bot.user.avatar_url)
        _embed.set_thumbnail(url=bot.thumb + str(time.time()))
        await ctx.send(embed=_embed)


async def info_command(bot, ctx: Union[commands.Context, SlashContext]):
    data = await utils.get(bot.http_session, "/all")

    text = utils.string_formatting(data)
    embed = discord.Embed(
        description=text,
        color=utils.COLOR,
        timestamp=utils.discord_timestamp()
    )

    embed.set_author(
        name=f"All countries affected by Coronavirus COVID-19",
        url="https://www.who.int/home",
        icon_url=bot.author_thumb
    )
    embed.set_thumbnail(url=bot.thumb + str(time.time()))
    embed.set_footer(text="coronavirus.jessicoh.com/api | " + utils.last_update(data[0]["lastUpdate"]),
                     icon_url=bot.user.avatar_url)

    if not os.path.exists(utils.STATS_PATH):
        history_confirmed = await utils.get(bot.http_session, f"/history/confirmed/total")
        history_recovered = await utils.get(bot.http_session, f"/history/recovered/total")
        history_deaths = await utils.get(bot.http_session, f"/history/deaths/total")
        await plot_csv(
            utils.STATS_PATH,
            history_confirmed,
            history_recovered,
            history_deaths)
    with open(utils.STATS_PATH, "rb") as p:
        img = discord.File(p, filename=utils.STATS_PATH)
    embed.set_image(url=f'attachment://{utils.STATS_PATH}')
    await ctx.send(file=img, embed=embed)


async def country_command(bot, ctx: Union[commands.Context, SlashContext], countries):
    if len(countries):
        data = await utils.get(bot.http_session, "/all")
        embeds = []
        text = overflow_text = ""
        i = 0
        stack = []
        countries = list(map(lambda x: x.lower(), countries))
        for d in data:
            for country in countries:
                bold = "**" if i % 2 == 0 else ""
                data_country = d['country'].lower()
                if (data_country.startswith(country) or
                    d['iso2'].lower() == country or
                    d['iso3'].lower() == country) \
                        and data_country not in stack:
                    overflow_text += f"{bold}{d['country']} : {d['totalCases']:,} confirmed [+{d['newCases']:,}] - {d['totalRecovered']:,} recovered - {d['totalDeaths']:,} deaths [+{d['newDeaths']:,}]{bold}\n"
                    stack.append(data_country)
                    i += 1
                if len(overflow_text) >= utils.DISCORD_LIMIT:
                    embed = discord.Embed(
                        title="Countries affected",
                        description=text,
                        timestamp=utils.discord_timestamp(),
                        color=utils.COLOR
                    )
                    overflow_text = ""
                text = overflow_text
        if text:
            embed = discord.Embed(
                description=text,
                timestamp=utils.discord_timestamp(),
                color=utils.COLOR
            )
            embeds.append(embed)
        for i, _embed in enumerate(embeds):
            _embed.set_author(
                name=f"Countries affected",
                icon_url=bot.author_thumb
            )
            _embed.set_footer(
                text=f"coronavirus.jessicoh.com/api/ | {utils.last_update(data[0]['lastUpdate'])} | Page {i + 1}",
                icon_url=bot.user.avatar_url)
            _embed.set_thumbnail(url=bot.thumb + str(time.time()))
            await ctx.send(embed=_embed)
    else:
        await ctx.send("No country provided")


async def stats_command(bot, ctx: Union[commands.Context, SlashContext], country):
    is_log = False
    graph_type = "Linear"
    embed = discord.Embed(
        description=utils.mkheader(),
        timestamp=dt.datetime.utcnow(),
        color=utils.COLOR
    )
    if len(country) == 1 and country[0].lower() == "log" or not len(country):
        data = await utils.get(bot.http_session, f"/all/world")
    splited = country

    if len(splited) == 1 and splited[0].lower() == "log":
        embed.set_author(
            name="Coronavirus COVID-19 logarithmic stats",
            icon_url=bot.author_thumb
        )
        is_log = True
        path = utils.STATS_LOG_PATH
        graph_type = "Logarithmic"
    elif not len(country):
        path = utils.STATS_PATH
    else:
        try:
            if splited[0].lower() == "log":
                is_log = True

                joined = ' '.join(country[1:]).lower()
                data = await utils.get(bot.http_session, f"/all/{joined}")
                path = data["iso2"].lower() + utils.STATS_LOG_PATH

            else:
                joined = ' '.join(country).lower()
                data = await utils.get(bot.http_session, f"/all/{joined}")
                path = data["iso2"].lower() + utils.STATS_PATH
            if not os.path.exists(path):
                history_confirmed = await utils.get(bot.http_session, f"/history/confirmed/{joined}")
                history_recovered = await utils.get(bot.http_session, f"/history/recovered/{joined}")
                history_deaths = await utils.get(bot.http_session, f"/history/deaths/{joined}")
                await plot_csv(
                    path,
                    history_confirmed,
                    history_recovered,
                    history_deaths,
                    logarithmic=is_log)

        except Exception as e:
            path = utils.STATS_PATH

    confirmed = data["totalCases"]
    recovered = data["totalRecovered"]
    deaths = data["totalDeaths"]
    active = data["activeCases"]
    if data['iso2']:
        embed.set_author(
            name=f"Coronavirus COVID-19 {graph_type} graph - {data['country']}",
            icon_url=f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/png250px/{data['iso2'].lower()}.png"
        )
    else:
        embed.set_author(
            name=f"Coronavirus COVID-19 {graph_type} graph - {data['country']}",
            icon_url=bot.author_thumb
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
        value=f"+{data['newCases']:,} (**{utils.percentage(confirmed, data['newCases'])}**)"
    )
    embed.add_field(
        name="<:_calendar:692860616930623698> Today deaths",
        value=f"+{data['newDeaths']:,} (**{utils.percentage(confirmed, data['newDeaths'])}**)"
    )
    embed.add_field(
        name="<:bed_hospital:692857285499682878> Active",
        value=f"{active:,} (**{utils.percentage(confirmed, active)}**)"
    )
    embed.add_field(
        name="<:critical:752228850091556914> Serious critical",
        value=f"{data['seriousCritical']:,} (**{utils.percentage(confirmed, data['seriousCritical'])}**)"
    )
    if data["totalTests"]:
        percent_pop = ""
        if data["population"]:
            percent_pop = f"(**{utils.percentage(data['population'], data['totalTests'])}**)"

        embed.add_field(
            name="<:test:752252962532884520> Total test",
            value=f"{data['totalTests']:,} {percent_pop}"
        )
        embed.add_field(
            name="<:population:768055030813032499> Population",
            value=f"{data['population']:,}"
        )

    if not os.path.exists(path):
        history_confirmed = await utils.get(bot.http_session, f"/history/confirmed/total")
        history_recovered = await utils.get(bot.http_session, f"/history/recovered/total")
        history_deaths = await utils.get(bot.http_session, f"/history/deaths/total")
        await plot_csv(
            path,
            history_confirmed,
            history_recovered,
            history_deaths,
            logarithmic=is_log)

    with open(path, "rb") as p:
        img = discord.File(p, filename=path)

    embed.set_footer(
        text="coronavirus.jessicoh.com/api/ | " +
        utils.last_update(data["lastUpdate"]),
        icon_url=bot.user.avatar_url
    )
    embed.set_thumbnail(
        url=bot.thumb + str(time.time())
    )
    embed.set_image(url=f'attachment://{path}')
    await ctx.send(file=img, embed=embed)


def get_idx(args, val):
    try:
        return args.index(val)
    except ValueError:
        return -1


def convert_interval_type(_type):
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


def unpack_notif(args, val):
    try:
        idx = int(get_idx(args, val))
        interval_type = args[len(args) - 1].lower()
        interval = int(args[idx + 1])
        if idx != -1 and interval >= 1 and interval <= 24:
            country = " ".join(args[0:idx])
        else:
            interval = 1
            country = " ".join(args)
    except:
        interval = 1
        country = " ".join(args)

    return country.lower(), interval * convert_interval_type(interval_type), interval_type


async def notification_command(bot, ctx: Union[commands.Context, SlashContext], country=None, interval: int = None, interval_type=None, *state):
    if len(state) and isinstance(ctx, commands.Context):
        country, interval, interval_type = unpack_notif(
            state, "every")
        guild_permissions = ctx.message.author.guild_permissions
    elif isinstance(ctx, SlashContext):
        interval = int(interval)
        guild_permissions = ctx.author.guild_permissions
    if not guild_permissions.administrator:
        return await ctx.send("You need to have Administrator permission to set notification on !")
    try:
        prefix = await bot.getg_prefix(ctx.guild.id)
    except:
        prefix = "c!"
    if len(state) or country is not None:
        all_data = await utils.get(bot.http_session, "/all/")
        try:
            data = utils.get_country(all_data, country)
            try:
                await bot.insert_notif(str(ctx.guild.id), str(ctx.channel.id), country, interval)

            except IntegrityError:
                await bot.update_notif(str(ctx.guild.id), str(ctx.channel.id), country, interval)
            finally:
                if country != "all":
                    embed = discord.Embed(
                        description=f"You will receive a notification in this channel on data update. `{prefix}notififcation disable` to disable the notifications"
                    )
                    embed.set_author(
                        name="Notifications successfully enabled",
                        icon_url=bot.author_thumb
                    )
                    embed.add_field(
                        name="Country",
                        value=f"**{data['country']}**"
                    )
                    embed.add_field(
                        name="Next update",
                        value=f"**{interval // convert_interval_type(interval_type)} {interval_type}**"
                    )
                elif country == "all":
                    embed = discord.Embed(
                        description=f"You will receive a notification in this channel on data update. `{prefix}notififcation disable` to disable the notifications"
                    )
                    embed.set_author(
                        name="Notifications successfully enabled",
                        icon_url=f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/png250px/{data['iso2'].lower()}.png"
                    )

                    embed.add_field(
                        name="Country",
                        value=f"**World stats**"
                    )
                    embed.add_field(
                        name="Next update",
                        value=f"**{interval // convert_interval_type(interval_type)} {interval_type}**"
                    )
        except Exception as e:
            embed = discord.Embed(
                title=f"{prefix}notification",
                description=f"Make sure that you didn't have made any mistake, please retry\n`{prefix}notification <country | disable> [every NUMBER] [hours | days | weeks]`\n__Examples__ : `{prefix}notification usa every 3 hours` (send a message to the current channel every 3 hours about United States), `{prefix}notification united states every 1 day`, `{prefix}notification disable`"
            )
            print(e)

        if country == "disable":
            await bot.delete_notif(str(ctx.guild.id))
            embed = discord.Embed(
                title="Notifications successfully disabled",
                description="Notifications are now interrupted in this channel."
            )
    else:
        embed = discord.Embed(
            title=f"{prefix}notification",
            description=f"Make sure that you didn't have made any mistake, please retry\n`{prefix}notification <country | disable> [every NUMBER] [hours | days | weeks]`\n__Examples__ : `{prefix}notification usa every 3 hours` (send a message to the current channel every 3 hours about United States), `{prefix}notification united states every 1 day`, `{prefix}notification disable`"
        )

    embed.color = utils.COLOR
    embed.timestamp = utils.discord_timestamp()
    embed.set_thumbnail(url=bot.thumb + str(time.time()))
    embed.set_footer(
        text="coronavirus.jessicoh.com/api/ | " +
        utils.last_update(all_data[0]["lastUpdate"]),
        icon_url=bot.user.avatar_url
    )
    await ctx.send(embed=embed)


async def track_command(bot, ctx: Union[commands.Context, SlashContext], *country):
    try:
        prefix = await bot.getg_prefix(ctx.guild.id)
    except:
        prefix = "c!"
    if not len(country):
        embed = discord.Embed(
            description=f"No country provided. **`{prefix}track <COUNTRY>`** work like **`{prefix}country <COUNTRY>`** see `{prefix}help`",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.set_author(
            name=f"{prefix}track",
            icon_url=bot.author_thumb
        )
    elif ''.join(country) == "disable":
        embed = discord.Embed(
            description=f"If you want to reactivate the tracker : **`{prefix}track <COUNTRY>`**",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.set_author(
            name="Tracker has been disabled!",
            icon_url=bot.author_thumb
        )
        try:
            await bot.delete_tracker(str(ctx.author.id))
        except:
            pass
    else:

        all_data = await utils.get(bot.http_session, "/all/")
        country = ' '.join(country)
        data = utils.get_country(all_data, country)
        if data is not None:
            try:
                await bot.insert_tracker(str(ctx.author.id), str(ctx.guild.id), country)
            except IntegrityError:
                await bot.update_tracker(str(ctx.author.id), country)
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
                name=f"{prefix}track",
                icon_url=bot.author_thumb
            )
    embed.set_thumbnail(url=bot.thumb + str(time.time()))
    embed.set_footer(
        text="coronavirus.jessicoh.com/api/",
        icon_url=bot.user.avatar_url
    )
    await ctx.send(embed=embed)


async def region_command(bot, ctx: Union[commands.Context, SlashContext], *params):
    if len(params):
        country, state = utils.parse_state_input(*params)
        try:
            if state == "all":
                history_confirmed = await utils.get(bot.http_session, f"/history/confirmed/{country}/regions")
                history_recovered = await utils.get(bot.http_session, f"/history/recovered/{country}/regions")
                history_deaths = await utils.get(bot.http_session, f"/history/deaths/{country}/regions")
                embeds = utils.region_format(
                    history_confirmed, history_recovered, history_deaths)
                for i, _embed in enumerate(embeds):
                    _embed.set_author(
                        name=f"All regions in {country}",
                        icon_url=bot.author_thumb
                    )
                    _embed.set_footer(
                        text=f"coronavirus.jessicoh.com/api/ | Page {i + 1}",
                        icon_url=bot.user.avatar_url)
                    _embed.set_thumbnail(
                        url=bot.thumb + str(time.time()))
                    await ctx.send(embed=_embed)
                return
            else:
                path = state.lower().replace(" ", "_") + utils.STATS_PATH
                history_confirmed = await utils.get(bot.http_session, f"/history/confirmed/{country}/{state}")
                history_recovered = await utils.get(bot.http_session, f"/history/recovered/{country}/{state}")
                history_deaths = await utils.get(bot.http_session, f"/history/deaths/{country}/{state}")
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
                    icon_url=bot.author_thumb
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
        icon_url=bot.user.avatar_url
    )
    embed.set_thumbnail(
        url=bot.thumb + str(time.time())
    )
    embed.set_image(url=f'attachment://{path}')
    await ctx.send(file=img, embed=embed)


async def daily_command(bot, ctx: Union[commands.Context, SlashContext], *country):
    embed = discord.Embed(
        description=utils.mkheader(),
        timestamp=dt.datetime.utcnow(),
        color=utils.COLOR
    )
    try:
        if country:
            data_confirmed = await utils.get(bot.http_session, f"/daily/confirmed/{' '.join(country).lower()}")
            data_recovered = await utils.get(bot.http_session, f"/daily/recovered/{' '.join(country).lower()}")
            data_deaths = await utils.get(bot.http_session, f"/daily/deaths/{' '.join(country).lower()}")
            path = data_confirmed["iso2"] + "daily.png"
            embed.set_author(
                name=f"Coronavirus COVID-19 Daily cases graph - {data_confirmed['name']}",
                icon_url=f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/png250px/{data_confirmed['iso2'].lower()}.png"
            )

        else:
            data_confirmed = await utils.get(bot.http_session, f"/daily/confirmed/total")
            data_recovered = await utils.get(bot.http_session, f"/daily/recovered/total")
            data_deaths = await utils.get(bot.http_session, f"/daily/deaths/total")
            path = "daily_world.png"
            embed.set_author(
                name=f"Coronavirus COVID-19 Daily cases graph - World",
                icon_url=bot.author_thumb
            )

        if not os.path.exists(path):
            await plot_bar_daily(path, data_confirmed, data_recovered, data_deaths)

    except Exception as e:
        logger.exception(e)
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
        url=bot.thumb + str(time.time())
    )
    with open(path, "rb") as p:
        img = discord.File(p, filename=path)
    embed.set_image(url=f'attachment://{path}')
    embed.set_footer(
        text="coronavirus.jessicoh.com/api/",
        icon_url=bot.user.avatar_url
    )
    await ctx.send(file=img, embed=embed)


async def news_command(bot, ctx: Union[commands.Context, SlashContext]):
    if bot.news is None:
        bot.news = utils.load_news()
    embed = discord.Embed(
        title=":newspaper: Recent news about Coronavirus COVID-19 :newspaper:",
        timestamp=utils.discord_timestamp(),
        color=utils.COLOR
    )
    sources = []
    length = 0
    max_size = 5800
    for n in bot.news["articles"]:
        source = n["source"]["name"]
        if source not in sources:
            sources.append(source)
        else:
            continue
        try:
            length += len(
                f"🞄 **{source}** : {n['title']} {n['description']}  [Link]({n['url']})")
            if length >= max_size:
                break
            embed.add_field(name=f"🞄 **{source}** : {n['title']}",
                            value=f"{n['description']}  [Link]({n['url']})",
                            inline=False)
        except discord.errors.HTTPException:
            break
    embed.set_thumbnail(
        url="https://avatars2.githubusercontent.com/u/32527401?s=400&v=4")
    embed.set_footer(text="newsapi.org",
                     icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)
