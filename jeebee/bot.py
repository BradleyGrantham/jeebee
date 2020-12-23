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

        try:

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

            elif "match" in message.content:
                if "last" in message.content:
                    response = jeebee.gb.get_last_completed_match()
                else:
                    response = jeebee.gb.get_current_active_match()
                embed = discord.Embed()
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
                await message.channel.send(embed=embed)

            elif "find" in message.content:
                if message.content.split(" ")[-1] == "all":
                    response = jeebee.gb.find_matches(all_matches=True, kbm_only=False)
                elif message.content.split(" ")[-1] == "kbm":
                    response = jeebee.gb.find_matches(all_matches=False, kbm_only=True)
                else:
                    response = jeebee.gb.find_matches(all_matches=False, kbm_only=False)
                embed = discord.Embed()
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
                await message.channel.send(embed=embed)

            elif "test" in message.content:
                response = discord.Embed()

                response.title = "hello"
                response.url = "https://news.ycombinator.com"
                await message.channel.send(embed=response)

            else:
                response = "Sorry, I don't understand ¯\_(ツ)_/¯"
                await message.channel.send(response)
        except Exception as e:
            response = "There's been an error :cry:"
            await message.channel.send(response)
            # raise e


client.run(TOKEN)
