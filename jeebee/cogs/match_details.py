from typing import Optional

import discord
from discord.ext import commands

import jeebee.gb
from jeebee.utils import build_embed, logger


class MatchDetails(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def match(self, ctx):
        async with ctx.typing():
            if ctx.invoked_subcommand is None:
                response = jeebee.gb.get_current_active_match()
                embed = build_embed(response)
                await ctx.send(embed=embed)
                return

    @commands.command(name="last-match")
    async def last(self, ctx):
        async with ctx.typing():
            response = jeebee.gb.get_last_completed_match()
            embed = build_embed(response)
        await ctx.send(embed=embed)

    @commands.command()
    async def find(self, ctx, *args):
        async with ctx.typing():
            logger.info(args)
            all_matches = True if "all" in args else False
            kbm_only = True if "kbm" in args else False
            response = jeebee.gb.find_matches(
                all_matches=all_matches, kbm_only=kbm_only
            )
            embed = build_embed(response)
        await ctx.send(embed=embed)

    @commands.command(name="win-perc")
    async def win_perc(self, ctx, num_games: Optional[int] = None):
        async with ctx.typing():
            win_perc_str = (
                "All time win percentage: "
                if num_games is None
                else f"Win percentage over last {num_games} games: "
            )
            response = f"{jeebee.gb.get_win_percentage(num_games):.2f}%"
        await ctx.send(win_perc_str + response)
