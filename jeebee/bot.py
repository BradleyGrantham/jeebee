import os

import discord
import dotenv

import jeebee.gb

dotenv.load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()


@client.event
async def on_ready():
    print(f"{client.user.name} has connected to Discord!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("jeebee"):

        if "win-perc" in message.content:
            if message.content[-1].isdigit():
                num_games = int(message.content.split(" ")[-1])
            else:
                num_games = None

            win_perc_str = (
                "All time win percentage: "
                if num_games is None
                else f"Win percentage over last {num_games} games: "
            )
            response = f"{jeebee.gb.get_win_percentage(num_games):.2f}%"
            await message.channel.send(win_perc_str + response)

        if "match" in message.content:
            if "last" in message.content:
                response = jeebee.gb.get_last_completed_match()
            else:
                response = jeebee.gb.get_current_active_match()
            embed = discord.Embed()
            for field in response:
                embed.add_field(name=field["name"], value=field["value"], inline=field.get("inline", False))
            await message.channel.send(embed=embed)

        if "test" in message.content:
            response = discord.Embed()
            response.title = "hello"
            response.url = "https://news.ycombinator.com"
            await message.channel.send(embed=response)


client.run(TOKEN)
