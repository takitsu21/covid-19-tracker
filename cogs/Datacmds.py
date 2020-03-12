import asyncio
import discord
from discord.ext import commands
import os
import datetime as dt
from pymysql.err import IntegrityError

import src.utils as utils
from src.database import db
from src.country_code import CD


class Datacmds(commands.Cog):
    """Help commands"""
    def __init__(self, bot):
        self.bot = bot
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langen-1000px-COVID-19_Outbreak_World_Map.svg.png"
        self.author_thumb = "https://www.stickpng.com/assets/images/5bd08abf7aaafa0575d8502b.png"

    # def generate_pages(self, data, header_length):
    #     length = header_length
    #     basic_length = 16
    #     max_length = utils.DISCORD_LIMIT - 50
    #     text = ""
    #     pages = []
    #     buffer = []
    #     my_csv = utils.data_reader(utils._CONFIRMED_PATH)
    #     for k, v in data.items():
    #         part = f"**{k}** {v['confirmed']} [**+{utils.diff_confirmed(my_csv, k, v)}**]\n"
    #         text += part
    #         length = len(text) + header_length
    #         if length >= max_length:
    #             pages.append([''.join(buffer)])
    #             buffer = []
    #             length = 0
    #         buffer.append(part)
    #     return pages

    @commands.command(name="info")
    @utils.trigger_typing
    async def info(self, ctx):
        DATA = utils.from_json(utils.DATA_PATH)
        header, text = utils.string_formatting(DATA)
        # pages = self.generate_pages(DATA, len(header))
        # index = 0

        # page_length = len(pages)
        # print(page_length)
        # if page_length > 1:
            # page_left = "⬅️"
            # page_right = "➡️"
            # base_reactions = [page_left, page_right]
            # embed.set_author(
            #         name=f"Page {index + 1}",
            #         url="https://www.who.int/home",
            #         icon_url=self.author_thumb
            #         )
            # pagination = await ctx.send(embed=embed)
            # for reaction in base_reactions:
            #     await pagination.add_reaction(reaction)
            # while True:
            #     def check(reaction, user):
            #         return user == ctx.message.author and str(reaction.emoji) in base_reactions
            #     try:
            #         reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=300.0)
            #         emoji = str(reaction.emoji)
            #     except asyncio.TimeoutError:
            #         try:
            #             await ctx.message.delete()
            #         except:
            #             pass
            #         return await pagination.delete()
            #     if page_left in emoji and index > 0:
            #         index -= 1
            #     elif page_right in emoji and index < page_length:
            #         index += 1
            #     if index >= 0 and index <= page_length:
            #         embed = discord.Embed(
            #             description=pages[0][index]
            #         )
            #         embed.set_author(
            #             name=f"Page {index + 1}",
            #             url="https://www.who.int/home",
            #             icon_url=self.author_thumb
            #             )
            #         embed.color = utils.COLOR
            #         embed.timestamp = utils.discord_timestamp()
            #         embed.set_thumbnail(url=self.thumb)
            #         embed.set_footer(text=utils.last_update(utils.DATA_PATH),
            #                         icon_url=ctx.guild.me.avatar_url)

            #         await pagination.edit(embed=embed)
        #     for i, _p in enumerate(pages):
        #         embed = discord.Embed(
        #             description=header + "\n" + _p[i],
        #             color=utils.COLOR,
        #             timestamp=utils.discord_timestamp()
        #         )
        #         embed.set_author(
        #                 name=f"Coronavrius COVID-19 Pages {i + 1}/{page_length} (Cases confirmed)",
        #                 url="https://www.who.int/home",
        #                 icon_url=self.author_thumb
        #                 )
        #         embed.color = utils.COLOR
        #         embed.timestamp = utils.discord_timestamp()
        #         embed.set_thumbnail(url=self.thumb)
        #         embed.set_footer(text=utils.last_update(utils.DATA_PATH),
        #                         icon_url=ctx.guild.me.avatar_url)
        #         with open("stats.png", "rb") as p:
        #             img = discord.File(p, filename="stats.png")
        #         embed.set_image(url=f'attachment://stats.png')
        #         await ctx.send(file=img, embed=embed)
        # else:
        embed = discord.Embed(
            description=header + "\n" + text,
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.set_author(
                name=f"Country/Region affected by Coronavirus COVID-19 (Cases confirmed)",
                url="https://www.who.int/home",
                icon_url=self.author_thumb
                )
        embed.color = utils.COLOR
        embed.timestamp = utils.discord_timestamp()
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(text=utils.last_update(utils.DATA_PATH),
                        icon_url=ctx.guild.me.avatar_url)
        with open("stats.png", "rb") as p:
            img = discord.File(p, filename="stats.png")
        embed.set_image(url=f'attachment://stats.png')
        await ctx.send(file=img, embed=embed)

    @info.error
    async def info_error(self, ctx, error):
        DATA = utils.from_json(utils.DATA_PATH)
        header, text = utils.string_formatting(DATA)
        embed = discord.Embed(
            description=header + "\n" + text,
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

    @commands.command(name="country")
    @utils.trigger_typing
    async def country(self, ctx, *country):
        if not len(country):
            embed = discord.Embed(
                    description="No args provided, I can't tell you which country/region is affected if you won't tell me everything!",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        else:
            DATA = utils.from_json(utils.DATA_PATH)
            header, text = utils.string_formatting(
                    DATA,
                    country
                )
            if len(text) > 0:
                embed = discord.Embed(
                    description=header + "\n" + text,
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
            else:
                embed = discord.Embed(
                    description="Wrong country selected or this country/region is not affected by Coronavirus COVID-19",
                    color=utils.COLOR,
                    timestamp=utils.discord_timestamp()
                )
        embed.set_author(name="Current Region/Country affected by Coronavirus COVID-19",
                        url="https://www.who.int/home",
                        icon_url=self.author_thumb)
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=utils.last_update(utils.DATA_PATH),
            icon_url=ctx.guild.me.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(name="stats", aliases=["stat", "statistic", "s"])
    @utils.trigger_typing
    async def stats(self, ctx):
        DATA = utils.from_json(utils.DATA_PATH)
        my_csv = utils.from_json(utils.CSV_DATA_PATH)
        t, r, c = utils.difference_on_update(my_csv, DATA)
        confirmed = DATA['total']['confirmed']
        recovered = DATA['total']['recovered']
        deaths = DATA['total']['deaths']
        embed = discord.Embed(
                            description="`[current_update-morning_update]`",
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
            name="Confirmed",
            value=f"**{confirmed}** [+**{t}**]",
            inline=False
            )
        embed.add_field(
                    name="Recovered",
                    value=f"**{recovered}** ({utils.percentage(confirmed, recovered)}) [+**{r}**]",
                    inline=False
                    )
        embed.add_field(
            name="Deaths",
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
    @utils.trigger_typing
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
                description="You are missing permissions (Administrator required)"
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
    @utils.trigger_typing
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
                    name="Tracker has been setted up! You can see your tracked list. Update will be send in DM",
                    icon_url=self.author_thumb
                )
            else:
                embed = discord.Embed(
                    description="Wrong country selected or this country/region is not affected by Coronavirus COVID-19",
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

def setup(bot):
    bot.add_cog(Datacmds(bot))