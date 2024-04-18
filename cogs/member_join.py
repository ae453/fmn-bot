from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

exception_str = "*Well... This is awkward! There seems to be an issue, please message <@315336291581558804> with error information for further instruction.*"

color_hex = 0xff3333
current_time = datetime.now()

class member_join(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        if not member.guild.id == 1176980339684548748:
            return
        await member.add_roles(member.guild.get_role(1179283490601185340), reason="Recently Joined Member.")


async def setup(client: commands.Bot):
    await client.add_cog(member_join(client))