import discord
from discord.ext import commands
import src.utils as utils
import time
import datetime as dt
from pymysql import IntegrityError
from src.plotting import plot_bar_daily, plot_csv
import os


async def list_countries_command(bot, ctx):
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


async def info_command(bot, ctx):
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


async def country_command(bot, ctx, countries):
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


async def stats_command(bot, ctx, country):
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


async def notification_command(bot, ctx, state):
    if not bot.userssage.author.guild_permissions.administrator():
        return await ctx.send("You need to have Administrator permission to set notification on !")
    try:
        prefix = await bot.getg_prefix(ctx.guild.id)
    except:
        prefix = "c!"
    if len(state):
        all_data = await utils.get(bot.http_session, "/all/")
        country, interval, interval_type = unpack_notif(
            state, "every")
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
                        icon_url=bot.author_thumb
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
