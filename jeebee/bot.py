from discord.ext import commands

from jeebee.constants import TOKEN
from jeebee.cogs.basic import Basic
from jeebee.cogs.match import Match
from jeebee.cogs.match_details import MatchDetails


if __name__ == "__main__":
    bot = commands.Bot(command_prefix=commands.when_mentioned_or("jeebee "))
    bot.remove_command("help")

    bot.add_cog(Basic(bot))
    bot.add_cog(Match(bot))
    bot.add_cog(MatchDetails(bot))

    bot.run(TOKEN)
