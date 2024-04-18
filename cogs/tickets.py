from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

exception_str = "*Well... This is awkward! There seems to be an issue, please message <@315336291581558804> with error information for further instruction.*"

image_file = discord.File("./assets/fmn.png", filename="image.png")
color_hex = 0xff3333
current_time = datetime.now()

class tickets(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client



async def setup(client: commands.Bot):
    await client.add_cog(tickets(client))
