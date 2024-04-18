from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

exception_str = "*Well... This is awkward! There seems to be an issue, please message <@315336291581558804> with error information for further instruction.*"

current_time = datetime.now()

class sticky_message(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        channel = message.channel
        message_dict = {
            1212967379630428182: "This is a sticky message. (TBA)"
        }
        
        if channel.id not in [key for key in message_dict.keys()]: return
        if message.author == self.client.user: return

        async for message in channel.history():
            if message.author == self.client.user: await message.delete()
        
        try:
            await channel.send(content=message_dict[channel.id])
        except KeyError:
            await channel.send("This is a stick message. (TBA)")
            


async def setup(client: commands.Bot):
    await client.add_cog(sticky_message(client))    
