from typing import Optional

import discord
from discord.ext import commands

import jeebee.gb
from jeebee.constants import TOKEN
from jeebee.log import logger
from jeebee.help_msg import help_msg
from jeebee.cogs.match import Match


bot = commands.Bot(command_prefix="jeebee ")
bot.remove_command("help")
bot.add_cog(Match(bot))


@bot.command(name="help")
async def _help(ctx):
    await ctx.send(help_msg)


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_command_error(ctx, error):
    async with ctx.typing():
        if isinstance(error, commands.CommandNotFound):
            msg = "Sorry, I don't understand ¯\_(ツ)_/¯"

        else:
            msg = "Sorry, it looks like there been an error :cry:"
    await ctx.send(msg)


@bot.command(name="win-perc")
async def win_perc(ctx, num_games: Optional[int] = None):
    async with ctx.typing():
        win_perc_str = (
            "All time win percentage: "
            if num_games is None
            else f"Win percentage over last {num_games} games: "
        )
        response = f"{jeebee.gb.get_win_percentage(num_games):.2f}%"
    await ctx.send(win_perc_str + response)


@bot.group()
async def match(ctx):
    async with ctx.typing():
        if ctx.invoked_subcommand is None:
            embed = discord.Embed()
            response = jeebee.gb.get_current_active_match()
            for field in response:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field.get("inline", False),
                )
            embed.set_footer(
                text="jeebee",
                icon_url="https://gamebattles.majorleaguegaming.com/gb-web/assets/favicon.ico",
            )
            await ctx.send(embed=embed)
            return


@match.command()
async def last(ctx):
    async with ctx.typing():
        embed = discord.Embed()
        response = jeebee.gb.get_last_completed_match()
        for field in response:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", False),
            )
        embed.set_footer(
            text="jeebee",
            icon_url="https://gamebattles.majorleaguegaming.com/gb-web/assets/favicon.ico",
        )
    await ctx.send(embed=embed)


@bot.command()
async def find(ctx, *args):
    embed = discord.Embed()
    async with ctx.typing():
        logger.info(args)
        all_matches = True if "all" in args else False
        kbm_only = True if "kbm" in args else False
        response = jeebee.gb.find_matches(all_matches=all_matches, kbm_only=kbm_only)

        for field in response:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", False),
            )
        embed.set_footer(
            text="jeebee",
            icon_url="https://gamebattles.majorleaguegaming.com/gb-web/assets/favicon.ico",
        )
    await ctx.send(embed=embed)


bot.run(TOKEN)
