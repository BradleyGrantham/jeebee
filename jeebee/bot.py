from typing import Optional

import discord
from discord.ext import commands

import jeebee.gb
from jeebee.constants import TOKEN
from jeebee.log import logger


bot = commands.Bot(command_prefix="jeebee ")


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


@bot.command()
async def post(ctx, *args):
    async with ctx.typing():
        if len(args) < 3 or len(args) > 4:
            await ctx.send(
                "You need to give me at least 3 (and no more than 4) GameBattles usernames\ne.g. jeebee post ntsfbrad JaAnTr JIMBOB108"
            )
            return
        else:
            embed = discord.Embed()
            response = jeebee.gb.post_match(args)
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


@bot.command()
async def accept(ctx, *args):
    kbm_only = True if "kbm" in args else False
    roster = [a for a in args if a != "kbm"]
    async with ctx.typing():
        if len(roster) < 3 or len(roster) > 4:
            await ctx.send(
                "You need to give me at least 3 (and no more than 4) GameBattles usernames\ne.g. jeebee post ntsfbrad JaAnTr JIMBOB108"
            )
            return
        else:
            embed = discord.Embed()
            response = jeebee.gb.accept_match(args, kbm_only=kbm_only)
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


bot.run(TOKEN)
