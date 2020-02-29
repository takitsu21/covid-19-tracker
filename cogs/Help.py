import asyncio
import discord
from discord.ext import commands
import os
import datetime as dt
import src.utils as utils


class Help(commands.Cog):
    """Help commands"""
    def __init__(self, bot):
        self.bot = bot
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langfr-280px-COVID-19_Outbreak_World_Map.svg.png"

    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx):
        last_csv_update = dt.datetime.utcfromtimestamp(os.path.getctime(utils._CONFIRMED_PATH))

        embed = discord.Embed(
            title=":newspaper: Coronavirus COVID-19 Commands",
            description="[Wold Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)",
            color=utils.COLOR,
            timestamp=utils.discord_timestamp()
        )
        embed.add_field(
            name="**`c!info`**",
            value="Views every confirmed cases, deaths and recovery",
            inline=False
        )
        embed.add_field(
            name="**`c!country [COUNTRY]`**",
            value="Views informations about country choosen",
            inline=False
        )
        embed.add_field(
            name="**`c!about`**",
            value="Views informations about the bot",
            inline=False
        )
        embed.set_thumbnail(url=self.thumb)
        embed.set_footer(
            text=f"Last update {last_csv_update.year}-{last_csv_update.month}-{last_csv_update.day} {last_csv_update.hour}H:{last_csv_update.minute}M",
            icon_url=ctx.guild.me.avatar_url
        )

        await ctx.send(embed=embed)

    @commands.command(name="about")
    async def about(self, ctx):
        data = utils.format_csv(
                    utils.data_reader(utils._CONFIRMED_PATH),
                    utils.data_reader(utils._RECOVERED_PATH),
                    utils.data_reader(utils._DEATH_PATH)
                )
        embed = discord.Embed(
                description="[Wold Health Organization advices](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)",
                timestamp=utils.discord_timestamp(),
                color=utils.COLOR
            )
        embed.set_author(name="Coronavirus COVID-19 Tracker", icon_url=ctx.guild.me.avatar_url)
        embed.set_thumbnail(url=self.thumb)
        embed.add_field(name="Vote",
                        value="[Click here](https://top.gg/bot/682946560417333283/vote)")
        embed.add_field(name="Invite Coronavirus COVID-19",
                        value="[Click here](https://discordapp.com/oauth2/authorize?client_id=682946560417333283&scope=bot&permissions=313408)")
        embed.add_field(name="Discord Support",
                        value="[Click here](https://discordapp.com/invite/wTxbQYb)")
        embed.add_field(name = "Source code", value="[Click here](https://github.com/takitsu21/covid-19-tracker)")
        embed.add_field(name="Help command",value="c!help")
        embed.add_field(name="Prefix",value="c!")
        nb_users = 0
        for s in self.bot.guilds:
            nb_users += len(s.members)
        embed.add_field(name="Total confirmed", value=data["total"]["total_confirmed"], inline=False)
        embed.add_field(name="Total recovered", value=data["total"]["total_recovered"], inline=False)
        embed.add_field(name="Total deaths", value=data["total"]["total_deaths"], inline=False)
        embed.add_field(name="Servers", value=len(self.bot.guilds))
        embed.add_field(name="Members", value=nb_users)
        embed.set_footer(text="Made by Taki#0853 (WIP)",
                        icon_url=ctx.guild.me.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx):
        self.bot._unload_extensions()
        self.bot._load_extensions()

def setup(bot):
    bot.add_cog(Help(bot))