from discord.ext import commands

from jeebee.help_msg import help_msg


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def _help(self, ctx):
        await ctx.send(help_msg)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user.name} has connected to Discord!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        async with ctx.typing():
            if isinstance(error, commands.CommandNotFound):
                msg = "Sorry, I don't understand ¯\_(ツ)_/¯"

            else:
                msg = "Sorry, it looks like there been an error :cry:"
        await ctx.send(msg)
