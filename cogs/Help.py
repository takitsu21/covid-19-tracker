from discord.ext import commands

from src.commands import help


class Help(commands.Cog):
    """Class for Help commands"""
    __slots__ = ("bot", "_id", "thumb")

    def __init__(self, bot):
        self.bot = bot
        self._id = 162200556234866688
        self.thumb = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/COVID-19_Outbreak_World_Map.svg/langen-1000px-COVID-19_Outbreak_World_Map.svg.png"

    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx, help_type=""):
        await help.help_command(self.bot, ctx, help_type)

    @commands.command(name="vote")
    async def vote(self, ctx):
        await help.vote_command(self.bot, ctx)

    @commands.command(name="invite")
    async def invite(self, ctx):
        await help.invite_command(self.bot, ctx)

    @commands.command()
    @commands.is_owner()
    async def avatar(self, ctx, fpath):
        with open(fpath, "rb") as f:
            await self.bot.user.edit(avatar=f.read())

    @commands.command(name="about")
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def about(self, ctx):
        await help.about_command(self.bot, ctx)

    @commands.command(name="sources", aliases=["source"])
    async def sources(self, ctx):
        await help.sources_command(self.bot, ctx)

    @commands.command()
    @commands.is_owner()
    async def debug(self, ctx, clear="n"):
        await ctx.send(f"current size : {self.bot.pool.size}\nfreesize : {self.bot.pool.freesize}\nmaxsize : {self.bot.pool.maxsize}")
        if clear == "y":
            await self.bot.pool.clear()
        # print(f"{self.bot.pool.__dict__}")

    @commands.command(name="ping")
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def ping(self, ctx):
        await help.ping_command(self.bot, ctx)

    @commands.command(name="suggestion")
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def suggestion(self, ctx, *message):
        await help.suggestion_command(self.bot, ctx, message)

    @commands.command(name="bug")
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def bug(self, ctx, *message):
        await help.bug_command(self.bot, ctx, message)

    @commands.command(name="setprefix")
    @commands.cooldown(3, 30, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setprefix(self, ctx, new_prefix):
        await help.setprefix_command(self.bot, ctx, new_prefix)

    @commands.command(name="getprefix", aliases=["get_prefix"])
    @commands.cooldown(3, 30, commands.BucketType.user)
    @commands.guild_only()
    async def getprefix(self, ctx):
        await help.get_guild_prefix_command(self.bot, ctx)

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx):
        self.bot._unload_extensions()
        self.bot._load_extensions()
        await ctx.send("Reloaded")

    # @commands.command()
    # @commands.is_owner()
    # async def gc(self, ctx):
    #     gc.collect()
    #     await ctx.send("garbage collected")


def setup(bot):
    bot.add_cog(Help(bot))
