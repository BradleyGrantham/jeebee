import discord
from discord.ext import commands, tasks

import jeebee.gb


class Match(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.match_posted = False
        self.match_posted_ctx = None
        self.check_for_match.start()

    @commands.command()
    async def post(self, ctx, *args):
        async with ctx.typing():
            kbm_only = True if "kbm" in args else False
            roster = [a for a in args if a != "kbm"]
            if len(args) < 3 or len(args) > 4:
                await ctx.send(
                    "You need to give me at least 3 (and no more than 4) GameBattles usernames\ne.g. jeebee post ntsfbrad JaAnTr JIMBOB108"
                )
                return
            else:
                embed = discord.Embed()
                response = jeebee.gb.post_match(roster, kbm_only=kbm_only)
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
                self.match_posted = True
                self.match_posted_ctx = ctx
                await ctx.send(embed=embed)
                return

    @commands.command()
    async def accept(self, ctx, *args):
        async with ctx.typing():
            self.match_posted = False
            kbm_only = True if "kbm" in args else False
            roster = [a for a in args if a != "kbm"]
            if len(roster) < 3 or len(roster) > 4:
                await ctx.send(
                    "You need to give me at least 3 (and no more than 4) GameBattles usernames\ne.g. jeebee accept ntsfbrad JaAnTr JIMBOB108"
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

    @commands.command()
    async def report(self, ctx, win):
        self.match_posted = False
        win = True if win in ("w", "win", "wi", "victory", "dub") else False
        async with ctx.typing():
            response = jeebee.gb.report_last_match(win)
            if response:
                await ctx.send("Reported. :slight_smile:")
                return
            else:
                await ctx.send("Sorry, it looks like there been an error :cry:")
                return

    @tasks.loop(seconds=8.0)
    async def check_for_match(self):
        print("checking for match")
        if self.match_posted:
            print("we have a match posted")
            match = jeebee.gb.get_current_active_match(return_status=True)
            if match in ("PENDING", "ACTIVE", "SCHEDULED"):
                print("MATCH FOUND")
                self.match_posted = False
                await self.match_posted_ctx.send("FOUND A MATCH")
            else:
                print("no match found yet")


