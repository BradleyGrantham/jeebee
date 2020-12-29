import discord
import logging


def build_embed(response):
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
    return embed


logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)
