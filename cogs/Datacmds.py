import asyncio
import discord
from discord.ext import commands
import os
import datetime as dt
from pymysql.err import IntegrityError

import src.utils as utils
from src.database import db


class Datacmds(commands.Cog):
    """Help commands"""
    def __init__(self, bot):
        self.bot = bot
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langen-1000px-COVID-19_Outbreak_World_Map.svg.png"
        self.author_thumb = "https://cdn2.iconfinder.com/data/icons/cornavirus-covid-19/64/_bat_night_animal_virus_disease-256.png"

    @commands.command(name="info")
    async def info(self, ctx):
        DATA = utils.from_json(utils.DATA_PATH)
        embed = utils.make_tab_embed_all()
        embed.set_author(
                name=f"All countries affected by Coronavirus COVID-19",
                url="https://www.who.int/home",
                icon_url=self.author_thumb
                )
        c, r, d = utils.difference_on_update(utils.from_json(utils.CSV_DATA_PATH), DATA)
        tot = DATA['total']
        header = "NOTE: [+**(CURRENT_UPDATE-MORNING_UPDATE)**]\nConfirmed **{}** [+**{}**]\nRecovered **{}** (**{}**) [+**{}**]\nDeaths **{}** (**{}**) [+**{}**]"
        header = header.format(
            tot["confirmed"],
            c,
            tot["recovered"],
            utils.percentage(tot["confirmed"], tot["recovered"]),
            r,
            tot["deaths"],
            utils.percentage(tot["confirmed"], tot["deaths"]),
            d
        )
        embed.description = header
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(text=utils.last_update(utils.DATA_PATH),
                        icon_url=ctx.guild.me.avatar_url)
        with open("stats.png", "rb") as p:
            img = discord.File(p, filename="stats.png")
        embed.set_image(url=f'attachment://stats.png')
        await ctx.send(file=img, embed=embed)

    @info.error
    async def info_error(self, ctx, error):
        return await ctx.send(str(error))
        DATA = utils.from_json(utils.DATA_PATH)
        header, text = utils.string_formatting(DATA)
        embed = discord.Embed(
            description="NOTE: [+**(CURRENT_UPDATE-LAST_HOUR_UPDATE)**]\n" + header + "\n" + text,
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.set_author(name="Country/Region affected by Coronavirus COVID-19 (Cases confirmed)",
                         url="https://www.who.int/home",
                         icon_url=self.author_thumb)
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        with open("stats.png", "rb") as p:
            img = discord.File(p, filename="stats.png")
        embed.set_image(url=f'attachment://stats.png')
        await ctx.send(file=img, embed=embed)

    @commands.command(name="country", aliases=["c"])
    async def country(self, ctx, *country):
        if not len(country):
            embed = discord.Embed(
                    description="No args provided, I can't tell you which country/region is affected if you won't tell me everything!",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        else:
            try:
                embed = utils.make_tab_embed_all(is_country=True, params=country)
                DATA = utils.from_json(utils.DATA_PATH)
                c, r, d = utils.difference_on_update(utils.from_json(utils.CSV_DATA_PATH), DATA)
                tot = DATA['total']
                header = "NOTE: [+**(CURRENT_UPDATE-MORNING_UPDATE)**]\nConfirmed **{}** [+**{}**]\nRecovered **{}** (**{}**) [+**{}**]\nDeaths **{}** (**{}**) [+**{}**]"
                header = header.format(
                    tot["confirmed"],
                    c,
                    tot["recovered"],
                    utils.percentage(tot["confirmed"], tot["recovered"]),
                    r,
                    tot["deaths"],
                    utils.percentage(tot["confirmed"], tot["deaths"]),
                    d
                )
                embed.description = header
            except:
                embed = discord.Embed(
                    description="Wrong country selected.\nViews information about multiple chosen country/region. You can either use autocompletion or country code. Valid country/region are listed in `c!info`.\nExample : `c!country fr germ it poland`",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        embed.set_author(name="Country affected by COVID-19",
                        url="https://www.who.int/home",
                        icon_url=self.author_thumb)
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="stats", aliases=["stat", "statistic", "s"])
    async def stats(self, ctx):
        DATA = utils.from_json(utils.DATA_PATH)
        my_csv = utils.from_json(utils.CSV_DATA_PATH)
        t, r, c = utils.difference_on_update(my_csv, DATA)
        confirmed = DATA['total']['confirmed']
        recovered = DATA['total']['recovered']
        deaths = DATA['total']['deaths']
        embed = discord.Embed(
                            description="NOTE: `[+(CURRENT_UPDATE-MORNING_UPDATE)]`",
                            timestamp=utils.discord_timestamp(),
                            color=utils.COLOR,
                            )
        embed.set_author(
            name="Coronavirus COVID-19 Stats",
            icon_url=self.author_thumb
            )
        embed.set_thumbnail(
            url=self.thumb
            )
        embed.add_field(
            name="<:confirmed:688686089548202004> Confirmed",
            value=f"**{confirmed}** [+**{t}**]",
            inline=False
            )
        embed.add_field(
                    name="<:recov:688686059567185940> Recovered",
                    value=f"**{recovered}** ({utils.percentage(confirmed, recovered)}) [+**{r}**]",
                    inline=False
                    )
        embed.add_field(
            name="<:_death:688686194917244928> Deaths",
            value=f"**{deaths}** ({utils.percentage(confirmed, deaths)}) [+**{c}**]",
            inline=False
            )
        embed.set_footer(
            text=utils.last_update("stats.png"),
            icon_url=ctx.guild.me.avatar_url
            )
        with open("stats.png", "rb") as p:
            img = discord.File(p, filename="stats.png")
        embed.set_image(url=f'attachment://stats.png')
        await ctx.send(file=img, embed=embed)

    @commands.command(name="notification", aliases=["notif", "notifications"])
    @commands.has_permissions(administrator=True)
    async def notification(self, ctx, state=None):
        if state is None:
            embed = discord.Embed(
                title="c!notification",
                description="c!nofitication <enable | disable>"
            )
        elif state.lower() == "enable":
            try:
                db.insert_notif(str(ctx.guild.id), str(ctx.channel.id))
            except IntegrityError:
                db.update_notif(str(ctx.guild.id), str(ctx.channel.id))
            embed = discord.Embed(
                title="Notifications successfully enabled",
                description="You will receive a notification in this channel on data update."
            )
        elif state.lower() == "disable":
            db.delete_notif(str(ctx.guild.id))
            embed = discord.Embed(
                title="Notifications successfully disabled",
                description="Notifications are now interrupted in this channel."
            )

        embed.color = utils.COLOR
        embed.timestamp = utils.discord_timestamp()
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

    @notification.error
    async def notif_perm_err(self, ctx, error):
        embed = discord.Embed(
                title="c!notification",
                description=f"Something went wrong! :/ {error}"
            )
        embed.color = utils.COLOR
        embed.timestamp = utils.discord_timestamp()
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="track", aliases=["tracker"])
    async def track(self, ctx, *country):
        if not len(country):
            embed = discord.Embed(
                description="No country provided. **`c!track <COUNTRY>`** work like **`c!country <COUNTRY>`** see `c!help`",
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
            embed.set_author(
                name="c!track",
                icon_url=self.author_thumb
            )
        elif ''.join(country) == "disable":
            embed = discord.Embed(
                description="If you want to reactivate the tracker : **`c!track <COUNTRY>`**",
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
            embed.set_author(
                name="Tracker has been disabled!",
                icon_url=self.author_thumb
            )
            try:
                db.delete_tracker(str(ctx.author.id))
            except:
                pass
        else:
            header, text = utils.string_formatting(utils.from_json(utils.DATA_PATH), country)
            if len(text):
                try:
                    db.insert_tracker(str(ctx.author.id), str(ctx.guild.id), ' '.join(country))
                except IntegrityError:
                    db.update_tracker(str(ctx.author.id), ' '.join(country))

                embed = discord.Embed(
                        description=header + "\n" + text,
                        color=utils.COLOR,
                        timestamp=utils.discord_timestamp()
                    )
                embed.set_author(
                    name="Tracker has been set up! You can see your tracked list. Updates will be send in DM",
                    icon_url=self.author_thumb
                )
            else:
                embed = discord.Embed(
                    description="Wrong country selected.",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
                embed.set_author(
                    name="`c!track`",
                    icon_url=self.author_thumb
                )
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="region", aliases=["r"])
    async def region(self, ctx, *params):
        if len(params):
            embed = utils.make_tab_embed_region(*params)
            if len(embed.fields[0].value) > 0:
                pass
            else:
                embed = discord.Embed(
                    description="Wrong province/state or country, see `c!help`.",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        else:
            embed = discord.Embed(
                description="Missing args, see `c!help`",
                color=utils.COLOR,
                timestamp=utils.discord_timestamp()
            )
        embed.set_author(
            name="Coronavirus COVID-19 (State/Province)",
            icon_url=self.author_thumb
        )
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Datacmds(bot))