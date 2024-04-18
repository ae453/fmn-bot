import calendar
from datetime import datetime, timedelta

import discord
import pytz
from discord import app_commands
from discord.ext import commands

from utils.db_connection import db_connector

exception_str = "*Well... This is awkward! There seems to be an issue, please message <@315336291581558804> with error information for further instruction.*"

image_file = discord.File("./assets/fmn.png", filename="image.png")
color_hex = 0xff3333
current_time = datetime.now(tz=pytz.timezone('UTC'))

class mod_commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    #TODO: Make Custom Check for Permissions / Role
    #TODO: Setup DB for Modlogs









    @app_commands.command(name="ban", description="Ban a User from the Guild")
    @app_commands.describe(
        user='The User to Ban (Select / UID)',
        reason='Reason for the Ban',
        delete_message_history='History of Messages from the User to be Delete'
    )
    @app_commands.choices(delete_message_history=[
        app_commands.Choice(name="Don't Delete Any",    value=0),
        app_commands.Choice(name="Previous Hour",       value=1),
        app_commands.Choice(name="Previous 6 Hours",    value=2),
        app_commands.Choice(name="Previous 12 Hours",   value=3),
        app_commands.Choice(name="Previous 24 Hours",   value=4),
        app_commands.Choice(name="Previous 3 Days",     value=5),
        app_commands.Choice(name="Previous 7 Days",     value=6),
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str, delete_message_history: app_commands.Choice[int]) -> None:
        #* Check if member passed is the command user, if true return    
        if user == interaction.user:
            return await interaction.response.send_message(content="You cannot ban yourself!", ephemeral=True)
        
        #* Embed creation for log
        embed=discord.Embed(title="User Banned", description=f"> User: {user.mention} (`{user.name}` | `{user.id}`)\n> Reason: {reason}", color=color_hex)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.timestamp = current_time

        #* List for delete_message_history
        #* When passed into the ban, the value of the choice selected gets inputted as the index of the list
        seconds_list = [0, 3600, 21600, 43200, 86400, 259200, 604800]

        #* Commit log to database
        db = db_connector()
        log = await db.add_logs(uid=user.id, type="Ban", reason=reason, mod_id=interaction.user.id)
        
        if not log:
            return await interaction.response.send_message(content=f"{exception_str}\n> *There was an error while committing committing to the database. THE USER HAS NOT BEEN PUNISHED.*", ephemeral=True)

        #* Ban the user from the server
        await interaction.guild.ban(user=user, reason=reason, delete_message_days=seconds_list[delete_message_history.value])
        await interaction.response.send_message(content=f"*{user.mention} has been banned from {interaction.guild.name} with reason \"{reason}\".*", ephemeral=True)
        
        #* Send embed to log channel
        channel = self.client.get_channel(1227893605658791937)
        await channel.send(embed=embed)

    #* Exception handling for the ban command
    #* NotFound, Forbidden, HTTPException, TypeError
    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.errors.NotFound):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure you selected the correct user / inputted the correct user id! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, discord.errors.Forbidden):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure the bot has the correct permissions to undergo this process! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *There was an error while undergoing this process. ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, TypeError):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *This error shouldn't be happening, please notify the developer! ({error})*\
", ephemeral=True)
            print(error)
        else:
            await interaction.response.send_message(content=exception_str, ephemeral=True)
            print(error)








    @app_commands.command(name="kick", description="Kick a Member from the Guild")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        member='The Member to Kick (Select / UID)',
        reason='Reason for the Kick'
    )
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str) -> None:
        #* Check if member passed is the command user, if true return
        if member == interaction.user:
            return await interaction.response.send_message(content="You cannot kick yourself!", ephemeral=True)

        #* Embed creation for log
        embed=discord.Embed(title="Member Kicked", description=f"> User: {member.mention} (`{member.name}` | `{member.id}`)\n> Reason: {reason}", color=color_hex)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.timestamp = current_time
        
        #* Commit log to database
        db = db_connector()
        log = await db.add_logs(uid=member.id, type="Kick", reason=reason, mod_id=interaction.user.id)
        
        if not log:
            return await interaction.response.send_message(content=f"{exception_str}\n> *There was an error while committing committing to the database. THE USER HAS NOT BEEN PUNISHED.*", ephemeral=True)        

        #* Kick the member from the server
        await interaction.guild.kick(user=member, reason=reason)
        await interaction.response.send_message(content=f"*{member.mention} has been kicked from {interaction.guild.name} with reason \"{reason}\".*", ephemeral=True)
        
        #* Send embed to log channel
        channel = self.client.get_channel(1227893605658791937)
        await channel.send(embed=embed)

    #* Exception handler for kick command
    #* Forbidden, TransformerError, HTTPException
    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.errors.Forbidden):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure the bot has the correct permissions to undergo this process! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, discord.app_commands.errors.TransformerError):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure the user is a member of the guild! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *There was an error while undergoing this process. ({error})*\
", ephemeral=True)
            print(error)
        else:
            await interaction.response.send_message(content=exception_str, ephemeral=True)
            print(error) 









    @app_commands.command(name="softban", description="Softban a Member from the Guild")
    @app_commands.describe(
        member='The Member to Softban (Select / UID)',
        reason='Reason for the Softban'
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def softban(self, interaction: discord.Interaction, member: discord.Member, reason: str) -> None:
        #* Check if member passed is the command user, if true return
        if member == interaction.user:
            return await interaction.response.send_message(content="You cannot softban yourself!", ephemeral=True)

        #* Embed creation for log
        embed=discord.Embed(title="Member Softbanned", description=f"> Member: {member.mention} (`{member.name}` | `{member.id}`)\n> Reason: {reason}", color=color_hex)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.timestamp = current_time

        #* Commit log to database
        db = db_connector()
        log = await db.add_logs(uid=member.id, type="Soft Ban", reason=reason, mod_id=interaction.user.id)
        
        if not log:
            return await interaction.response.send_message(content=f"{exception_str}\n> *There was an error while committing committing to the database. THE USER HAS NOT BEEN PUNISHED.*", ephemeral=True)

        #* Ban the member from the server, then unban
        await interaction.guild.ban(user=member, reason=reason, delete_message_days=3)
        await interaction.guild.unban(user=member, reason=f"Softbanned with Reason: \"{reason}\"")
        await interaction.response.send_message(content=f"*{member.mention} has been softbanned from {interaction.guild.name} with reason \"{reason}\".*", ephemeral=True)
        
        #* Send embed to log channel
        channel = self.client.get_channel(1227893605658791937)
        await channel.send(embed=embed)

            
    #* Exception handling for the softban command
    #* NotFound, Forbidden, HTTPException, TypeError, TransformerError
    @softban.error
    async def softban_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.errors.NotFound):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure you selected the correct user / inputted the correct user id! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, discord.errors.Forbidden):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure the bot has the correct permissions to undergo this process! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *There was an error while undergoing this process. ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, TypeError):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *This error shouldn't be happening, please notify the developer! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, discord.app_commands.errors.TransformerError):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure the user is a member of the guild! ({error})*\
", ephemeral=True)
            print(error)
        else:
            await interaction.response.send_message(content=exception_str, ephemeral=True)
            print(error)










    @app_commands.command(name="timeout", description="Timeout a Member of the Guild")
    @app_commands.describe(
        member='The Member to Timeout (Select / UID)',
        seconds='Length of the Timeout (seconds)',
        minutes='Length of the Timeout (minutes)',
        hours='Length of the Timeout (hours)',
        days='Length of the Timeout (days)',
        reason='Reason for the Timeout'
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, reason: str, seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0) -> None:
        #* Check if member passed is the command user, if true return
        if member == interaction.user:
            return await interaction.response.send_message(content="You cannot timeout yourself!", ephemeral=True)
        if seconds + minutes + hours + days == 0:
            return await interaction.response.send_message(content="You must specify a timeout length!", ephemeral=True)
        
        #* Get unix code for embed (dynamic time string)      
        timeout_end = current_time + timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)
        unix_code = calendar.timegm(timeout_end.utctimetuple())
        
        #* Embed creation for log
        embed=discord.Embed(title="Member Timed Out", description=f"> Member: {member.mention} (`{member.name}` | `{member.id}`)\n> Reason: {reason}\n> Until: <t:{unix_code}:f>", color=color_hex)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.timestamp = current_time

        #* Commit log to database
        db = db_connector()
        log = await db.add_logs(uid=member.id, type="Timeout", reason=reason, mod_id=interaction.user.id)
        
        if not log:
            return await interaction.response.send_message(content=f"{exception_str}\n> *There was an error while committing committing to the database. THE USER HAS NOT BEEN PUNISHED.*", ephemeral=True)

        #* Time the member out
        await member.timeout(timeout_end, reason=reason)
        await interaction.response.send_message(content=f"*{member.mention} has been timed out until <t:{unix_code}:f> with reason \"{reason}\"*", ephemeral=True)
        
        #* Send embed to log channel
        channel = self.client.get_channel(1227893605658791937)
        await channel.send(embed=embed)
    
    #* Exception handling for the timeout command
    #* TransformerError, TypeError
    @timeout.error
    async def timeout_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.TransformerError):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure the user is a member of the guild! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, TypeError):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure you specified the correct time! (s / m / h / d | seconds / minutes / hours / days) ({error})*\
", ephemeral=True)
            print(error)
        else:
            await interaction.response.send_message(content=exception_str, ephemeral=True)
            print(error)









 
    @app_commands.command(name="warn", description="Warn a Member of the Guild")
    @app_commands.describe(
        member='The Member to Warn (Select / UID)',
        reason='Reason for the Warn'
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str) -> None:
        #* Check if member passed is the command user, if true return
        if member == interaction.user:
            return await interaction.response.send_message(content="You cannot warn yourself!", ephemeral=True)
        #* Check if user is a member of the server, if false return
        if not member:
            return await interaction.response.send_message(content="This user is not inside the current guild!", ephemeral=True)
        
        #* Embed creation for log
        embed=discord.Embed(title="Member Warned", description=f"> Member: {member.mention} (`{member.name}` | `{member.id}`)\n> Reason: {reason}", color=color_hex)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.timestamp = current_time

        #* Commit log to database
        db = db_connector()
        log = await db.add_logs(uid=member.id, type="Warn", reason=reason, mod_id=interaction.user.id)
        
        if not log:
            return await interaction.response.send_message(content=f"{exception_str}\n> *There was an error while committing committing to the database. THE USER HAS NOT BEEN PUNISHED.*", ephemeral=True)

        #* Add warn to user in DB
        channel = self.client.get_channel(1227893605658791937)
        await channel.send(embed=embed)
        await interaction.response.send_message(content=f"*{member.mention} has been warning with reason \"{reason}\"*", ephemeral=True)

    #* Exception handling for the timeout command
    #* TransformerError
    @warn.error
    async def warn_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.TransformerError):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure the user is a member of the guild! ({error})*\
", ephemeral=True)
            print(error)
        else:
            await interaction.response.send_message(content=exception_str, ephemeral=True)
            print(error)









 
    @app_commands.command(name="unban", description="Unban a User from the Guild")
    @app_commands.describe(
        user='The User to Unban (Select / UID)',
        reason='Reason for the Unban'
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str) -> None:
        #* Check if member passed is the command user, if true return
        if user == interaction.user:
            return await interaction.response.send_message(content="You cannot unban yourself!", ephemeral=True)
        
        #* Embed creation for log
        embed=discord.Embed(title="User Unbanned", description=f"> User: {user.mention} (`{user.name}` | `{user.id}`)\n> Reason: {reason}", color=color_hex)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.timestamp = current_time
        
        #* Commit log to database
        db = db_connector()
        log = await db.add_logs(uid=user.id, type="Unban", reason=reason, mod_id=interaction.user.id)
        
        if not log:
            return await interaction.response.send_message(content=f"{exception_str}\n> *There was an error while committing committing to the database. THE USER HAS NOT BEEN PUNISHED.*", ephemeral=True)
        
        #* Unban user from the server
        await interaction.guild.unban(user=user, reason=reason)
        
        channel = self.client.get_channel(1227893605658791937)
        await channel.send(embed=embed)
        await interaction.response.send_message(content=f"{user.mention} has been unbanned with reason \"{reason}\".", ephemeral=True)

    #* Exception handling for the unban command
    #* NotFound, Forbidden, HTTPException
    @unban.error
    async def unban_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.errors.NotFound):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure you selected the correct user / inputted the correct user id! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, discord.errors.Forbidden):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure the bot has the correct permissions to undergo this process! ({error})*\
", ephemeral=True)
            print(error)
        elif isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *There was an error while undergoing this process. ({error})*\
", ephemeral=True)
            print(error)
        else:
            await interaction.response.send_message(content=exception_str, ephemeral=True)
            print(error)









    @app_commands.command(name="modlogs", description="Get the modlogs of a user")
    @app_commands.describe(
        user='The User in Question (Select / UID)'
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def modlogs(self, interaction: discord.Interaction, user: discord.User) -> None:
        #* Get DB Connection
        db = db_connector()
        
        #* Get the logs from the DB
        logs = await db.get_logs(user_id=user.id)
        
        #* Check if dict is empty        
        if not logs:
            return await interaction.response.send_message(content=f"{user.name} has no logged moderation history.")
        #* If returned false, there was an error
        elif isinstance(logs, bool) and not logs:
            return await interaction.response.send_message(content=f"{exception_str}n> *There was an error while undergoing this process.*", ephemeral=True)

       
        #* Make the embed to respond with
        embed=discord.Embed(title=f"{user.name} Modlogs", description=f"{user.mention}\n`{user.id}`", color=color_hex)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.timestamp = current_time
        
        #* For every case, make a new field
        for case in logs.keys():
            embed.add_field(name=f"Case #{case}", value=f"> Type: {logs[case]["type"]}\n> Reason: {logs[case]["reason"]}\n> Moderator: <@{logs[case]["mod_id"]}>", inline=False)

        #* Respond with embed including the mod log info
        await interaction.response.send_message(embed=embed)
    
    
    @modlogs.error
    async def modlogs_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.TransformerError):
            await interaction.response.send_message(content=f"\
{exception_str}\
\n> *Please ensure you specified the correct User ID! ({error})*\
", ephemeral=True)
            print(error)
        else:
            await interaction.response.send_message(content=exception_str, ephemeral=True)
            print(error)

async def setup(client: commands.Bot):
    await client.add_cog(mod_commands(client))    
