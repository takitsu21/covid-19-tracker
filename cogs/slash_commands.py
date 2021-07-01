import logging

import discord
from discord.ext import commands
from discord_slash import (ButtonStyle, ComponentContext, SlashContext,
                           cog_ext, manage_commands, manage_components)

from src.commands import data, help

logger = logging.getLogger("covid-19")


class SlashCommands(commands.Cog):
    """Class to use slash commands in guilds."""
    __slots__ = ("bot")

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="help",
        description="Shows information about Coronavirus bot",
        options=[
            manage_commands.create_option(
                name="help_type",
                description="Options about how to use the bot",
                option_type=3,
                required=False,
                choices=[
                     manage_commands.create_choice(
                         name="📈Statistics",
                         value="stats"
                     ),
                    manage_commands.create_choice(
                         name="⚙️Bot utilities",
                         value="utilities"
                     )
                ]
            )
        ],
        guild_ids=[627261287881113620]
    )
    async def _help(self, ctx: SlashContext, help_type=""):
        await help.help_command(self.bot, ctx, help_type)

    @cog_ext.cog_slash(
        name="getprefix",
        description="Shows current guild prefix",
        guild_ids=[627261287881113620]
    )
    async def _getg_prefix(self, ctx: SlashContext):
        await help.get_guild_prefix_command(self.bot, ctx)

    @cog_ext.cog_slash(
        name="setprefix",
        description="Set new prefix for your guild",
        guild_ids=[627261287881113620],

    )
    async def _set_prefix(self, ctx: SlashContext, new_prefix):
        await help.setprefix_command(self.bot, ctx, new_prefix)

    @cog_ext.cog_slash(
        name="list",
        description="List all the countries that the bot can find",
        guild_ids=[627261287881113620]
    )
    async def _list_countries(self, ctx):
        await data.list_countries_command(self.bot, ctx)

    @cog_ext.cog_slash(
        name="info",
        description="Shows some symbolic numbers about the pandemic",
        guild_ids=[627261287881113620]
    )
    async def _info(self, ctx):
        await data.info_command(self.bot, ctx)

    @cog_ext.cog_slash(
        name="country",
        description="Shows information about country.ies",
        guild_ids=[627261287881113620]
    )
    async def _country(self, ctx, countries):
        countries = countries.split(" ")
        # TODO: adapt the aux func to avoid split usage
        # temporary fix to use slash commands
        await data.country_command(self.bot, ctx, countries)

    @cog_ext.cog_slash(
        name="stats",
        description="Shows statistics about a country",
        guild_ids=[627261287881113620]
    )
    async def _stats(self, ctx, country):
        country = country.split(" ")
        await data.stats_command(self.bot, ctx, country)

    @cog_ext.cog_slash(
        name="notification",
        description="Shows statistics about a country",
        options=[
            manage_commands.create_option(
                name="country",
                description="Country to set the notification for",
                option_type=3,
                required=True
            ),
            manage_commands.create_option(
                name="interval",
                description="Interval between each updates",
                option_type=3,
                required=True
            ),
            manage_commands.create_option(
                name="interval_type",
                description="Interval type",
                option_type=3,
                required=True,
                choices=[
                     manage_commands.create_choice(
                         name="Hours",
                         value="hours"
                     ),
                     manage_commands.create_choice(
                         name="Days",
                         value="days"
                     ),
                    manage_commands.create_choice(
                         name="Weeks",
                         value="weeks"
                     )
                ]
            )
        ],
        guild_ids=[627261287881113620]
    )
    async def _notification(self, ctx: SlashContext, country, interval, interval_type):
        await data.notification_command(
            self.bot,
            ctx,
            country=country,
            interval=interval,
            interval_type=interval_type
        )

    @cog_ext.cog_slash(
        name="track",
        description="Track a specific country",
        guild_ids=[627261287881113620]
    )
    async def _track(self, ctx, country):
        country = country.split(" ")
        await data.track_command(self.bot, ctx, *country)

    @cog_ext.cog_slash(
        name="region",
        description="Get stats about a region",
        guild_ids=[627261287881113620]
    )
    async def _region(self, ctx, country):
        country = country.split(" ")
        await data.region_command(self.bot, ctx, country)

    @cog_ext.cog_slash(
        name="daily",
        description="Daily stats",
        guild_ids=[627261287881113620]
    )
    async def _daily(self, ctx, country):
        country = country.split(" ")
        await data.daily_command(self.bot, ctx, *country)

    @cog_ext.cog_slash(
        name="news",
        description="Get the latest news about Covid 19",
        guild_ids=[627261287881113620]
    )
    async def _news(self, ctx: SlashContext):
        await data.news_command(self.bot, ctx)

    # @cog_ext.cog_slash(
    #     name="components",
    #     description="Components test",
    #     guild_ids=[627261287881113620]
    # )
    # async def _slashes_test(self, ctx: SlashContext):
    #     buttons = [
    #         # manage_components.create_button(
    #         #     style=ButtonStyle.red,
    #         #     label="A Red Button",
    #         #     custom_id="redButton"
    #         # ),
    #         # manage_components.create_button(
    #         #     style=ButtonStyle.blue,
    #         #     label="A Blue Button",
    #         #     custom_id="blueButton",
    #         # ),
    #         # manage_components.create_button(
    #         #     style=ButtonStyle.green,
    #         #     label="A Green Button",
    #         #     custom_id="greenButton",
    #         #     disabled=True
    #         # ),
    #         # manage_components.create_button(
    #         #     style=ButtonStyle.grey,
    #         #     label="A Grey Button",
    #         #     custom_id="greyButton",
    #         #     disabled=True
    #         # ),
    #         # manage_components.create_button(
    #         #     style=ButtonStyle.primary,
    #         #     label="A Primary Button",
    #         #     custom_id="primaryButton"
    #         # ),
    #         manage_components.create_select(
    #             options=[manage_components.create_select_option(
    #                 label="label",
    #                 value="value",
    #                 description="You have a label and a value"
    #             ),
    #                 manage_components.create_select_option(
    #                 label="label 2",
    #                 value="value 2",
    #                 description="You have a label and a value 2"
    #             ),
    #             ]
    #         ),
    #     ]
    #     action_row = manage_components.create_actionrow(*buttons)
    #     action_row2 = manage_components.create_actionrow(*buttons)
    #     await ctx.send("test", components=[action_row, action_row2])
        # button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[action_row, action_row2])
        # button_ctx.component
        # if button_ctx.custom_id == "redButton":

        #     await button_ctx.edit_origin(content=f"You pressed the red button! {button_ctx.author}")
        # elif button_ctx.custom_id == "blueButton":
        #     await button_ctx.edit_origin(content=f"You pressed the blue button! {button_ctx.author.mention}")

    # @cog_ext.cog_slash(
    #     name="test",
    #     description="test slash commands",
    #     options=[
    #         manage_commands.create_option(
    #             name="optone",
    #             description="This is the first option we have.",
    #             option_type=3,
    #             required=True,
    #             choices=[
    #                  manage_commands.create_choice(
    #                      name="ChoiceOne",
    #                      value="DOGE!"
    #                  ),
    #                 manage_commands.create_choice(
    #                      name="ChoiceTwo",
    #                      value="NO DOGE"
    #                  )
    #             ]
    #         )
    #     ],
    #     guild_ids=[627261287881113620]
    # )
    # async def _test_slash_commands(self, ctx: SlashContext, optone):
    #     await ctx.send(f"{ctx.__dict__}")

    # @cog_ext.cog_subcommand(
    #     base="group",
    #     name="subtest1",
    #     description="subtest command",
    #     guild_ids=[627261287881113620]
    # )
    # async def _sub_command_group_test(self, ctx: SlashContext, msg):
    #     await ctx.send(msg)

    # @cog_ext.cog_subcommand(
    #     base="group",
    #     name="subtest2",
    #     description="subtest2 command",
    #     guild_ids=[627261287881113620]
    # )
    # @commands.command()
    # async def _sub_command_group_test2(self, ctx: SlashContext, msg):
    #     await ctx.send(msg)


def setup(bot):
    bot.add_cog(SlashCommands(bot))
